"""
hill_climbing.py - Implementasi berbagai varian Hill Climbing

Varian yang diimplementasikan:
1. Steepest Ascent Hill Climbing - Pilih neighbor terbaik setiap iterasi
2. Stochastic Hill Climbing - Pilih neighbor random yang lebih baik
3. Hill Climbing with Sideways Move - Izinkan sideways move sampai batas tertentu
4. Random Restart Hill Climbing - Restart dengan initial state baru
"""

import random
import time
from typing import Optional
from .base_algorithm import HillClimbingBase

class SteepestAscentHillClimbing(HillClimbingBase):
    """
    Steepest Ascent Hill Climbing (Hill Climbing Murni).
    
    Algoritma:
    1. Mulai dari initial state
    2. Generate semua neighbors
    3. Pilih neighbor dengan nilai objektif TERBAIK
    4. Jika neighbor terbaik lebih baik dari current, pindah ke sana
    5. Jika tidak ada neighbor yang lebih baik, STOP (local optimum)
    6. Ulangi sampai stuck atau max_iterations
    
    Karakteristik:
    - Greedy: selalu pilih yang terbaik
    - Cepat converge
    - Mudah stuck di local optimum
    - Deterministic (hasil sama untuk initial state yang sama)
    """
    
    def __init__(self, initial_state, objective_function, max_iterations: int = 1000):
        super().__init__(initial_state, objective_function, max_iterations)
        self.stuck_iteration = None  # Iterasi saat stuck
    
    def get_name(self) -> str:
        return "Steepest Ascent Hill Climbing"
    
    def solve(self):
        """Main algorithm"""
        start_time = time.perf_counter()
        
        current_value = self.evaluate_state(self.current_state)
        
        for iteration in range(self.max_iterations):
            # Generate semua neighbors
            neighbors = self.generate_all_neighbors(self.current_state)
            
            if len(neighbors) == 0:
                break
            
            # Evaluasi semua neighbors, cari yang terbaik
            best_neighbor = None
            best_neighbor_value = current_value
            
            for neighbor_state, move_desc in neighbors:
                neighbor_value = self.evaluate_state(neighbor_state)
                
                # Cari neighbor dengan nilai TERKECIL (minimisasi)
                if neighbor_value < best_neighbor_value:
                    best_neighbor = neighbor_state
                    best_neighbor_value = neighbor_value
            
            # Jika tidak ada neighbor yang lebih baik, STUCK!
            if best_neighbor is None:
                self.stuck_iteration = iteration
                break
            
            # Pindah ke neighbor terbaik
            self.current_state = best_neighbor
            current_value = best_neighbor_value
            
            # Update best state jika perlu
            self.update_best_state(self.current_state, current_value)
            
            # Record history
            self.record_iteration(current_value)
        else:
            # Jika loop selesai tanpa break (tidak stuck, tapi habis iterasi)
            self.stuck_iteration = self.max_iterations

        self.duration = time.perf_counter() - start_time
        return self.best_state
    
    def get_statistics(self) -> dict:
        stats = super().get_statistics()
        stats['stuck_at_iteration'] = self.stuck_iteration
        return stats


class StochasticHillClimbing(HillClimbingBase):
    """
    Stochastic Hill Climbing.
    
    Algoritma:
    1. Mulai dari initial state
    2. Generate semua neighbors
    3. Filter hanya neighbors yang LEBIH BAIK dari current
    4. Pilih RANDOM dari neighbors yang lebih baik
    5. Jika tidak ada neighbor yang lebih baik, STOP
    6. Ulangi sampai stuck atau max_iterations
    
    Karakteristik:
    - Less greedy dibanding Steepest Ascent
    - Non-deterministic (hasil bisa beda setiap run)
    - Bisa escape dari beberapa local optimum
    - Masih cukup cepat
    """
    
    def __init__(self, initial_state, objective_function, 
                 max_iterations: int = 1000, seed: Optional[int] = None):
        super().__init__(initial_state, objective_function, max_iterations)
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.stuck_iteration = None
    
    def get_name(self) -> str:
        return "Stochastic Hill Climbing"
    
    def solve(self):
        """Main algorithm"""
        start_time = time.perf_counter()
        
        current_value = self.evaluate_state(self.current_state)
        
        for iteration in range(self.max_iterations):
            # Generate semua neighbors
            neighbors = self.generate_all_neighbors(self.current_state)
            
            if len(neighbors) == 0:
                break
            
            # Filter hanya neighbors yang LEBIH BAIK
            better_neighbors = []
            for neighbor_state, move_desc in neighbors:
                neighbor_value = self.evaluate_state(neighbor_state)
                if neighbor_value < current_value:  # Minimisasi
                    better_neighbors.append((neighbor_state, neighbor_value))
            
            # Jika tidak ada neighbor yang lebih baik, STUCK
            if len(better_neighbors) == 0:
                self.stuck_iteration = iteration
                break
            
            # Pilih RANDOM dari neighbors yang lebih baik
            chosen_neighbor, chosen_value = random.choice(better_neighbors)
            
            # Pindah ke neighbor terpilih
            self.current_state = chosen_neighbor
            current_value = chosen_value
            
            # Update best state
            self.update_best_state(self.current_state, current_value)
            
            # Record history
            self.record_iteration(current_value)
        else:
            # Jika loop selesai tanpa break (tidak stuck, tapi habis iterasi)
            self.stuck_iteration = self.max_iterations

        self.duration = time.perf_counter() - start_time
        return self.best_state
    
    def get_statistics(self) -> dict:
        stats = super().get_statistics()
        stats['stuck_at_iteration'] = self.stuck_iteration
        stats['seed'] = self.seed
        return stats


class SidewaysMoveHillClimbing(HillClimbingBase):
    """
    Hill Climbing with Sideways Move.
    
    Algoritma:
    1. Mulai dari initial state
    2. Generate semua neighbors
    3. Pilih neighbor TERBAIK (bisa sama atau lebih baik)
    4. Jika neighbor lebih baik, pindah dan reset sideways counter
    5. Jika neighbor SAMA (sideways), pindah dan increment counter
    6. Jika sideways counter > max_sideways, STOP
    7. Jika tidak ada neighbor sama/lebih baik, STOP
    
    Karakteristik:
    - Bisa melewati "plateau" (datar area di landscape)
    - Mengurangi stuck di local optimum yang disebabkan plateau
    - Perlu tuning max_sideways_moves parameter
    """
    
    def __init__(self, initial_state, objective_function, 
                 max_iterations: int = 1000, max_sideways_moves: int = 100):
        super().__init__(initial_state, objective_function, max_iterations)
        self.max_sideways_moves = max_sideways_moves
        self.sideways_count = 0
        self.stuck_iteration = None
        self.stuck_reason = None
    
    def get_name(self) -> str:
        return f"Hill Climbing with Sideways Move (max={self.max_sideways_moves})"
    
    def solve(self):
        """Main algorithm"""
        start_time = time.perf_counter()
        
        current_value = self.evaluate_state(self.current_state)
        self.sideways_count = 0
        
        for iteration in range(self.max_iterations):
            # Generate semua neighbors
            neighbors = self.generate_all_neighbors(self.current_state)
            
            if len(neighbors) == 0:
                break
            
            # Cari neighbor terbaik (bisa sama atau lebih baik)
            best_neighbor = None
            best_neighbor_value = float('inf')
            
            for neighbor_state, move_desc in neighbors:
                neighbor_value = self.evaluate_state(neighbor_state)
                
                # Ambil yang terkecil (minimisasi)
                if neighbor_value <= best_neighbor_value:
                    best_neighbor = neighbor_state
                    best_neighbor_value = neighbor_value
            
             # Jika tidak ada neighbor yang sama atau lebih baik
            if best_neighbor is None:
                self.stuck_iteration = iteration
                self.stuck_reason = "local_optimum"
                break
            
            # Cek apakah ada improvement
            if best_neighbor_value < current_value:
                # Ada improvement, reset sideways counter
                self.sideways_count = 0
                self.current_state = best_neighbor
                current_value = best_neighbor_value
                
            elif best_neighbor_value == current_value:
                # Sideways move (nilai sama)
                self.sideways_count += 1
                
                if self.sideways_count >= self.max_sideways_moves:
                    # Sudah terlalu banyak sideways
                    self.stuck_iteration = iteration
                    self.stuck_reason = "max_sideways_reached"
                    break
                
                self.current_state = best_neighbor
                
            else:
                # Tidak ada neighbor yang lebih baik atau sama
                self.stuck_iteration = iteration
                self.stuck_reason = "local_optimum"
                break
            
            # Update best state
            self.update_best_state(self.current_state, current_value)
            
            # Record history
            self.record_iteration(current_value)
        
        self.duration = time.perf_counter() - start_time
        return self.best_state
    
    def get_statistics(self) -> dict:
        stats = super().get_statistics()
        stats['max_sideways_moves'] = self.max_sideways_moves
        stats['total_sideways_moves'] = self.sideways_count
        stats['stuck_at_iteration'] = self.stuck_iteration
        stats['stuck_reason'] = self.stuck_reason
        return stats

class RandomRestartHillClimbing(HillClimbingBase):
    """
    Random Restart Hill Climbing.
    
    Algoritma:
    1. Lakukan Hill Climbing (Steepest Ascent) dari initial state acak
    2. Simpan hasil terbaik dari run tersebut
    3. Restart dengan initial state acak yang baru
    4. Ulangi sampai max_restarts tercapai
    5. Return solusi terbaik dari semua restart
    
    Karakteristik:
    - Mengatasi masalah stuck di local optimum
    - Trade-off: waktu vs kualitas solusi
    - Non-deterministic (hasil berbeda setiap run)
    - Lebih robust dibanding single-run HC
    
    Catatan:
    - Menggunakan BinPackingInitializer.random_fit() untuk generate initial state baru
    - Setiap restart independen (tidak ada informasi yang dibawa dari restart sebelumnya)
    """
    
    def __init__(self, items: dict, capacity: int, objective_function, 
                 max_restarts: int = 10, max_iterations_per_run: int = 100,
                 seed: Optional[int] = None):
        """
        Args:
            items: Dictionary {item_id: size}
            capacity: Kapasitas bin
            objective_function: Fungsi objektif untuk evaluasi
            max_restarts: Jumlah restart maksimal
            max_iterations_per_run: Iterasi maksimal per restart
            seed: Random seed untuk reproducibility
        """
        # Import di sini untuk avoid circular import
        from src.core.initializer import BinPackingInitializer
        
        # Generate initial state pertama
        initial_state = BinPackingInitializer.random_fit(items, capacity)
        super().__init__(initial_state, objective_function, max_iterations_per_run)
        
        # Store items dan capacity untuk generate initial state baru
        self.items = items
        self.capacity = capacity
        self.initializer = BinPackingInitializer
        
        self.max_restarts = max_restarts
        self.max_iterations_per_run = max_iterations_per_run  
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Track best solution across all restarts
        self.best_state_overall = self.current_state.copy()
        self.best_value_overall = self.evaluate_state(self.best_state_overall)
        
        # History untuk setiap restart
        self.runs_history = []
        
    def get_name(self) -> str:
        return f"Random Restart Hill Climbing (restarts={self.max_restarts})"
    
    def solve(self):
        """Main algorithm"""
        start_time = time.perf_counter()
        
        for restart in range(self.max_restarts):
            # 1. Generate initial state acak baru untuk setiap restart
            if restart == 0:
                # Restart pertama gunakan initial state yang sudah ada
                new_initial_state = self.current_state.copy()
            else:
                # Restart selanjutnya gunakan random initial state baru
                new_initial_state = self.initializer.random_fit(self.items, self.capacity)
            
            # 2. Jalankan Steepest Ascent Hill Climbing dari initial state baru
            hc_run = SteepestAscentHillClimbing(
                new_initial_state, 
                self.objective_function, 
                max_iterations=self.max_iterations
            )
            final_state = hc_run.solve()
            final_value = self.evaluate_state(final_state)
            
            # 3. Ambil statistik dari run ini
            run_stats = hc_run.get_statistics()
            
            # 4. Simpan hasil run ke history
            self.runs_history.append({
                'restart': restart,
                'initial_value': self.evaluate_state(new_initial_state),
                'final_value': final_value,
                'iterations': run_stats.get('stuck_at_iteration', run_stats['iterations']),
                'improvement': self.evaluate_state(new_initial_state) - final_value
            })
            
            # 5. Update best state overall jika run ini lebih baik
            if final_value < self.best_value_overall:
                self.best_value_overall = final_value
                self.best_state_overall = final_state.copy()
            
            # 6. Record untuk plotting (track best value across restarts)
            self.record_iteration(self.best_value_overall)

        self.duration = time.perf_counter() - start_time
        
        # Set current_state dan best_state ke best overall
        self.current_state = self.best_state_overall.copy()
        self.best_state = self.best_state_overall.copy()
        self.best_value = self.best_value_overall
        
        return self.best_state_overall

    def get_statistics(self) -> dict:
        """Return statistik lengkap termasuk detail setiap restart"""
        stats = super().get_statistics()
        
        # Override beberapa stats untuk Random Restart
        stats['max_restarts'] = self.max_restarts
        stats['total_restarts_executed'] = len(self.runs_history)
        stats['best_value_overall'] = self.best_value_overall
        stats['seed'] = self.seed
        
        # Total iterasi per restart
        stats['max_iterations_per_run'] = self.max_iterations_per_run
        
        # Detail setiap restart
        stats['runs_history'] = self.runs_history
        
        # Summary total iterasi
        if len(self.runs_history) > 0:
            # Total iterasi dari semua restart
            total_iterations_all_runs = sum(run['iterations'] for run in self.runs_history)
            stats['total_iterations_all_runs'] = total_iterations_all_runs
            
            # Rata-rata iterasi per restart
            stats['average_iterations_per_run'] = total_iterations_all_runs / len(self.runs_history)
            
            # Min dan max iterasi per restart
            iterations_list = [run['iterations'] for run in self.runs_history]
            stats['min_iterations_per_run'] = min(iterations_list)
            stats['max_iterations_per_run_actual'] = max(iterations_list)
            
            # Summary final values
            final_values = [run['final_value'] for run in self.runs_history]
            stats['average_final_value'] = sum(final_values) / len(final_values)
            stats['worst_final_value'] = max(final_values)
            stats['best_final_value'] = min(final_values)
            
            # Summary improvements
            improvements = [run['improvement'] for run in self.runs_history]
            stats['average_improvement'] = sum(improvements) / len(improvements)
            stats['best_improvement'] = max(improvements)
        
        return stats

# Demo
def demo_hill_climbing():
    """Demo penggunaan Hill Climbing variants"""
    from src.core.state import State
    from src.core.objective_function import ObjectiveFunction
    from src.core.initializer import BinPackingInitializer
    
    # Setup problem
    items = {
        "BRG001": 40, "BRG002": 55, "BRG003": 25,
        "BRG004": 60, "BRG005": 30, "BRG006": 45, "BRG007": 50
    }
    capacity = 100
    
    initial_state = BinPackingInitializer.best_fit(items, capacity)
    obj_func = ObjectiveFunction()
    
    print("=" * 60)
    print("DEMO HILL CLIMBING VARIANTS")
    print("=" * 60)
    
    # 1. Steepest Ascent
    print("\n1. Steepest Ascent Hill Climbing")
    print("-" * 60)
    hc1 = SteepestAscentHillClimbing(initial_state, obj_func, max_iterations=100)
    hc1.solve()
    hc1.print_results(verbose=False)
    
    # 2. Stochastic
    print("\n2. Stochastic Hill Climbing")
    print("-" * 60)
    hc2 = StochasticHillClimbing(initial_state, obj_func, max_iterations=100, seed=42)
    hc2.solve()
    hc2.print_results(verbose=False)
    
    # 3. Sideways Move
    print("\n3. Hill Climbing with Sideways Move")
    print("-" * 60)
    hc3 = SidewaysMoveHillClimbing(initial_state, obj_func, max_iterations=100, max_sideways_moves=20)
    hc3.solve()
    hc3.print_results(verbose=False)

    # 4. Random Restart
    print("\n4. Random Restart Hill Climbing")
    print("-" * 60)
    hc4 = RandomRestartHillClimbing(
        items, capacity, obj_func, 
        max_restarts=5, 
        max_iterations_per_run=50,
        seed=42
    )
    hc4.solve()
    hc4.print_results(verbose=True)  

if __name__ == "__main__":
    demo_hill_climbing()