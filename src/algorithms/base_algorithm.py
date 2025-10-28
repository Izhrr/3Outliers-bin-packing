"""
base_algorithm.py - Base class untuk semua algoritma local search

Menyediakan interface yang konsisten untuk semua algoritma:
- Hill Climbing (Steepest Ascent, Stochastic, Sideways Move, Random Restart)
- Simulated Annealing
- Genetic Algorithm
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import time

class BaseLocalSearchAlgorithm(ABC):
    """
    Abstract base class untuk semua algoritma local search.
    
    Setiap algoritma yang inherit dari class ini harus implement:
    - solve(): Main algorithm logic
    - get_name(): Return nama algoritma
    
    Attributes yang tersedia:
    - initial_state: State awal
    - current_state: State saat ini
    - best_state: State terbaik yang pernah ditemukan
    - objective_function: Fungsi untuk evaluasi state
    - history: List nilai objektif setiap iterasi
    - iteration_count: Jumlah iterasi yang sudah dilakukan
    - duration: Waktu eksekusi (diisi setelah solve())
    """
    
    def __init__(self, initial_state, objective_function):
        """
        Args:
            initial_state: State awal (dari initializer)
            objective_function: Instance ObjectiveFunction
        """
        self.initial_state = initial_state.copy()
        self.current_state = initial_state.copy()
        self.best_state = initial_state.copy()
        self.objective_function = objective_function
        
        # Statistics
        self.history = []  # History nilai objektif per iterasi
        self.iteration_count = 0
        self.duration = 0.0
        
        # Initial evaluation
        self.best_value = self.objective_function.calculate(self.best_state)
        self.history.append(self.best_value)
    
    @abstractmethod
    def solve(self) -> 'State':
        """
        Main method untuk menjalankan algoritma.
        Harus diimplementasikan oleh setiap subclass.
        
        Returns:
            State: State terbaik yang ditemukan
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return nama algoritma"""
        pass
    
    def evaluate_state(self, state) -> float:
        """Helper method untuk evaluasi state"""
        return self.objective_function.calculate(state)
    
    def update_best_state(self, new_state, new_value: float):
        """Update best_state jika new_state lebih baik"""
        if new_value < self.best_value:  # Minimisasi
            self.best_state = new_state.copy()
            self.best_value = new_value
    
    def record_iteration(self, current_value: float):
        """Catat nilai objektif iterasi saat ini"""
        self.history.append(current_value)
        self.iteration_count += 1
    
    def get_statistics(self) -> dict:
        """
        Return statistik lengkap dari eksekusi algoritma.
        Berguna untuk analisis dan visualisasi.
        """
        return {
            "algorithm": self.get_name(),
            "iterations": self.iteration_count,
            "duration": self.duration,
            "duration_ms": self.duration * 1000,
            "initial_objective": self.history[0] if self.history else None,
            "final_objective": self.best_value,
            "improvement": self.history[0] - self.best_value if self.history else 0,
            "improvement_percent": ((self.history[0] - self.best_value) / abs(self.history[0]) * 100) 
                                   if self.history and self.history[0] != 0 else 0,
            "num_containers_initial": self.initial_state.num_containers(),
            "num_containers_final": self.best_state.num_containers(),
            "is_valid": self.best_state.is_valid(),
            "history": self.history.copy()
        }
    
    def print_results(self, verbose: bool = True):
        """Print hasil eksekusi algoritma"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print(f"HASIL ALGORITMA: {stats['algorithm']}")
        print("=" * 60)
        
        print(f"\nWaktu Eksekusi    : {stats['duration']:.4f} detik ({stats['duration_ms']:.2f} ms)")
        print(f"Jumlah Iterasi    : {stats['iterations']}")
        print(f"Solusi Valid      : {'Ya' if stats['is_valid'] else 'TIDAK'}")
        
        print(f"\n--- Performa ---")
        print(f"Objective Awal    : {stats['initial_objective']:.2f}")
        print(f"Objective Akhir   : {stats['final_objective']:.2f}")
        print(f"Improvement       : {stats['improvement']:.2f} ({stats['improvement_percent']:.2f}%)")
        
        print(f"\n--- Kontainer ---")
        print(f"Kontainer Awal    : {stats['num_containers_initial']}")
        print(f"Kontainer Akhir   : {stats['num_containers_final']}")
        print(f"Pengurangan       : {stats['num_containers_initial'] - stats['num_containers_final']} kontainer")
        
        if verbose:
            print(f"\n--- State Akhir ---")
            print(self.best_state)
    
    def get_result_dict(self) -> dict:
        """
        Return hasil dalam format dictionary untuk export ke JSON.
        """
        stats = self.get_statistics()
        
        return {
            "algorithm": stats['algorithm'],
            "execution": {
                "duration_seconds": stats['duration'],
                "duration_ms": stats['duration_ms'],
                "iterations": stats['iterations']
            },
            "objective_function": {
                "initial": stats['initial_objective'],
                "final": stats['final_objective'],
                "improvement": stats['improvement'],
                "improvement_percent": stats['improvement_percent']
            },
            "solution": {
                "is_valid": stats['is_valid'],
                "num_containers_initial": stats['num_containers_initial'],
                "num_containers_final": stats['num_containers_final'],
                "containers": self.best_state.to_dict()
            },
            "history": stats['history'],
            "final_state": self.best_state
        }


class HillClimbingBase(BaseLocalSearchAlgorithm):
    """
    Base class untuk varian Hill Climbing.
    Menyediakan common methods untuk generate neighbors.
    """
    
    def __init__(self, initial_state, objective_function, max_iterations: int = 1000):
        super().__init__(initial_state, objective_function)
        self.max_iterations = max_iterations
    
    def generate_all_neighbors(self, state) -> List:
        """
        Generate semua possible neighbors dari state saat ini.
        
        Dua jenis move:
        1. Move: Pindahkan 1 barang ke kontainer lain
        2. Swap: Tukar 2 barang dari kontainer berbeda
        
        Returns:
            List of (neighbor_state, move_description)
        """
        neighbors = []
        
        # 1. MOVE: Pindahkan barang ke kontainer lain
        for from_idx, container in enumerate(state.containers):
            for item_id in container:
                # Coba pindah ke kontainer lain yang sudah ada
                for to_idx in range(len(state.containers)):
                    if to_idx != from_idx:
                        neighbor = state.move_item(item_id, from_idx, to_idx)
                        neighbors.append((neighbor, f"Move {item_id} from C{from_idx+1} to C{to_idx+1}"))
                
                # Coba pindah ke kontainer baru
                neighbor = state.move_item(item_id, from_idx, -1)
                neighbors.append((neighbor, f"Move {item_id} from C{from_idx+1} to new container"))
        
        # 2. SWAP: Tukar barang dari 2 kontainer berbeda
        for i, container1 in enumerate(state.containers):
            for item1 in container1:
                for j, container2 in enumerate(state.containers):
                    if j > i:  # Hindari duplikasi
                        for item2 in container2:
                            neighbor = state.swap_items(item1, i, item2, j)
                            neighbors.append((neighbor, f"Swap {item1}(C{i+1}) <-> {item2}(C{j+1})"))
        
        return neighbors
    
    def get_statistics(self) -> dict:
        """Extend parent statistics dengan max_iterations"""
        stats = super().get_statistics()
        stats['max_iterations'] = self.max_iterations
        return stats


# Demo
def demo_base_algorithm():
    """Demo struktur base algorithm"""
    from core.state import State
    from core.objective_function import ObjectiveFunction
    from core.initializer import BinPackingInitializer
    
    # Setup
    items = {"BRG001": 40, "BRG002": 55, "BRG003": 25, "BRG004": 60}
    capacity = 100
    
    initial_state = BinPackingInitializer.best_fit(items, capacity)
    obj_func = ObjectiveFunction()
    
    # Contoh menggunakan base class (biasanya tidak langsung dipakai)
    print("Initial State:")
    print(initial_state)
    print(f"Objective Value: {obj_func.calculate(initial_state):.2f}")


if __name__ == "__main__":
    demo_base_algorithm()