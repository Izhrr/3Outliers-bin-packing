"""
simulated_annealing.py - Implementasi Simulated Annealing untuk Bin Packing Problem

Algoritma:
1. Mulai dengan initial state (Best Fit) dan temperature tinggi
2. Generate random neighbor (50% move, 50% swap)
3. Jika neighbor lebih baik → TERIMA
4. Jika neighbor lebih buruk → TERIMA dengan probabilitas e^(-ΔE/T)
5. Turunkan temperature (T = T × cooling_rate)
6. Ulangi sampai max_iterations

Parameter:
- initial_temp: 100
- cooling_rate: 0.99
- max_iterations: 1000
"""

from algorithms.base_algorithm import BaseLocalSearchAlgorithm
import random
import math
import time

class SimulatedAnnealing(BaseLocalSearchAlgorithm):
    """
    Simulated Annealing Algorithm
    
    Parameters:
    - max_iterations: Jumlah iterasi maksimal (default: 1000)
    - initial_temp: Temperature awal (default: 100)
    - cooling_rate: Laju penurunan temperature (default: 0.99)
    """
    
    def __init__(self, initial_state, objective_function, 
                 max_iterations=1000, initial_temp=100, cooling_rate=0.99):
        super().__init__(initial_state, objective_function)
        self.max_iterations = max_iterations
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.stuck_count = 0  # Frekuensi stuck di local optima
        self.acceptance_probs = []  # e^(ΔE/T)
        self.temperatures = []  # Temperature per iterasi
        self.accepted_worse_count = 0  # Frekuensi terima solusi lebih buruk
        
    def get_name(self) -> str:
        return f"Simulated Annealing"
    
    def solve(self):
        """
        Main algorithm untuk Simulated Annealing.
        
        Returns:
            State: Best state yang ditemukan
        """
        start_time = time.perf_counter()
        
        # Inisialisasi
        current_state = self.current_state.copy()
        current_value = self.evaluate_state(current_state)
        temperature = self.initial_temp
        
        # Variabel deteksi stuck di local optima
        prev_best_value = self.best_value
        stuck_counter = 0
        
        for iteration in range(self.max_iterations):
            # Generate random neighbor
            neighbor_state = self._generate_random_neighbor(current_state)
            neighbor_value = self.evaluate_state(neighbor_state)
            
            # Hitung delta E
            delta = neighbor_value - current_value
            
            # Decision
            accepted = False
            acceptance_prob = 0.0
            
            if delta < 0:
                # Kondisi neighbor > current
                current_state = neighbor_state
                current_value = neighbor_value
                accepted = True
                acceptance_prob = 1.0
                
            elif delta == 0:
                # Kondisi neighbor = current
                current_state = neighbor_state
                current_value = neighbor_value
                accepted = True
                acceptance_prob = 1.0 
                
            else:
                # Kondisi neighbor > current
                # Hitung probabilitas acceptance: e^(-delta / T)
                if temperature > 0:
                    acceptance_prob = math.exp(-delta / temperature)
                else:
                    acceptance_prob = 0.0
                
                if random.random() < acceptance_prob:
                    current_state = neighbor_state
                    current_value = neighbor_value
                    accepted = True
                    self.accepted_worse_count += 1
                else:
                    accepted = False
            
            # Deteksi stuck di local optima
            if not accepted or (current_value >= prev_best_value):
                stuck_counter += 1
            else:
                stuck_counter = 0
            
            # Stuck dihitung ketika 10 iterasi, masih sama hasilnya
            if stuck_counter >= 10:
                self.stuck_count += 1
                stuck_counter = 0 
            
            # Update best state
            prev_best_value = self.best_value
            self.update_best_state(current_state, current_value)
            
            # Record history dan metrics
            self.record_iteration(current_value)
            self.acceptance_probs.append(acceptance_prob)
            self.temperatures.append(temperature)
            
            # Cooling Temperature
            temperature *= self.cooling_rate
            
        
        self.duration = time.perf_counter() - start_time
        self._auto_save_metrics()
        
        return self.best_state
    
    def _auto_save_metrics(self):
        """
        Auto-save SA metrics setelah solve().
        Dipanggil otomatis di akhir solve(), tidak perlu manual call dari luar.
        """
        # Default output directory
        output_dir = './output/sa_metrics'
        
        # Save metrics
        try:
            self.save_sa_metrics(output_dir)
        except Exception as e:
            print(f"Warning: Failed to auto-save SA metrics: {e}")
    
    def _generate_random_neighbor(self, state):
        """
        Generate random neighbor dengan cara:
        - 80% chance: Move random item ke container lain
        - 20% chance: Swap 2 random items
        """
        if random.random() < 0.8:
            return self._random_move(state)
        else:
            return self._random_swap(state)
    
    def _random_move(self, state):
        """
        Helper function: Pilih random item dan container
        
        Steps:
        1. Pilih random container source (yang tidak kosong)
        2. Pilih random item dari container tersebut
        3. Pilih random container destination (selain source)
        4. Panggil state.move_item() ← Method dari State class
        """

        # Cek container  tidak kosong
        non_empty = [i for i, c in enumerate(state.containers) if len(c) > 0]
        if len(non_empty) == 0:
            return state.copy()
        
        # Pilih random container source
        from_idx = random.choice(non_empty)
        
        # Pilih random item dari container source
        item_id = random.choice(state.containers[from_idx])
        
        # Pilih random destination (selain source)
        candidates = [i for i in range(len(state.containers)) if i != from_idx]
        if candidates:
            to_idx = random.choice(candidates)
            # move_item
            return state.move_item(item_id, from_idx, to_idx)
        else:
            return state.copy()
    
    def _random_swap(self, state):
        """
        Helper function: Pilih random 2 items dari 2 container berbeda,
        lalu panggil state.swap_items() yang sudah ada.
        
        Catatan: Minimal harus ada 2 container yang tidak kosong
        
        Steps:
        1. Pilih 2 random container yang berbeda (tidak kosong)
        2. Pilih random item dari masing-masing container
        3. Panggil state.swap_items() ← Method dari State class
        """
        # Cek minimal 2 container tidak kosong
        non_empty = [i for i, c in enumerate(state.containers) if len(c) > 0]
        if len(non_empty) < 2:
            # Tidak bisa swap, return copy
            return state.copy()
        
        # Pilih 2 container berbeda secara random
        idx1, idx2 = random.sample(non_empty, 2)
        
        # Pilih random item dari masing-masing container
        item1 = random.choice(state.containers[idx1])
        item2 = random.choice(state.containers[idx2])
        
        # Swap
        return state.swap_items(item1, idx1, item2, idx2)
    
    def get_statistics(self) -> dict:
        """
        Extend parent statistics dengan SA-specific metrics.
        
        Tambahan untuk SA:
        - initial_temperature
        - cooling_rate
        - stuck_count (frekuensi stuck di local optima)
        - acceptance_probs (list e^(ΔE/T) per iterasi)
        - temperatures (list temperature per iterasi)
        - accepted_worse_count
        """
        stats = super().get_statistics()
        stats['initial_temperature'] = self.initial_temp
        stats['cooling_rate'] = self.cooling_rate
        stats['stuck_count'] = self.stuck_count
        stats['acceptance_probs'] = self.acceptance_probs
        stats['temperatures'] = self.temperatures
        stats['accepted_worse_count'] = self.accepted_worse_count
        stats['final_temperature'] = self.temperatures[-1] if self.temperatures else 0
        
        return stats
    
    def get_result_dict(self) -> dict:
        result = super().get_result_dict()
        
        #SA-specific section
        result['sa_metrics'] = {
            'initial_temperature': self.initial_temp,
            'cooling_rate': self.cooling_rate,
            'max_iterations': self.max_iterations,
            'stuck_count': self.stuck_count,
            'accepted_worse_count': self.accepted_worse_count,
            'final_temperature': self.temperatures[-1] if self.temperatures else 0,
            'acceptance_probabilities': self.acceptance_probs,
            'temperatures': self.temperatures
        }
        
        return result
    
    def save_sa_metrics(self, output_dir: str):
        import json
        import csv
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Get data dari result dict
        result_dict = self.get_result_dict()
        sa_metrics = result_dict['sa_metrics']
        
        # Save acceptance probabilities ke CSV
        csv_path = os.path.join(output_dir, 'sa_acceptance_probs.csv')
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['iteration', 'acceptance_probability', 'temperature', 'objective_value'])
            
            # Skip first history value (initial state)
            history_values = result_dict['history'][1:] if len(result_dict['history']) > 1 else result_dict['history']
            
            for i, (prob, temp, obj) in enumerate(zip(
                sa_metrics['acceptance_probabilities'],
                sa_metrics['temperatures'],
                history_values
            )):
                writer.writerow([i+1, prob, temp, obj])
        
        
        # Save summary ke JSON
        json_path = os.path.join(output_dir, 'sa_summary.json')
        
        summary = {
            'algorithm': result_dict['algorithm'],
            'parameters': {
                'initial_temperature': sa_metrics['initial_temperature'],
                'cooling_rate': sa_metrics['cooling_rate'],
                'max_iterations': sa_metrics['max_iterations']
            },
            'results': {
                'stuck_count': sa_metrics['stuck_count'],
                'accepted_worse_count': sa_metrics['accepted_worse_count'],
                'final_temperature': sa_metrics['final_temperature'],
                'initial_objective': result_dict['objective_function']['initial'],
                'final_objective': result_dict['objective_function']['final'],
                'improvement': result_dict['objective_function']['improvement'],
                'improvement_percent': result_dict['objective_function']['improvement_percent'],
                'num_containers_initial': result_dict['solution']['num_containers_initial'],
                'num_containers_final': result_dict['solution']['num_containers_final'],
                'duration': result_dict['execution']['duration_seconds']
            }
        }
        
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
