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
                if neighbor_value < best_neighbor_value:
                    best_neighbor = neighbor_state
                    best_neighbor_value = neighbor_value
            
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
    hc1.print_results(verbose=True)
    
    # 2. Stochastic
    print("\n2. Stochastic Hill Climbing")
    print("-" * 60)
    hc2 = StochasticHillClimbing(initial_state, obj_func, max_iterations=100, seed=42)
    hc2.solve()
    hc2.print_results(verbose=True)
    
    # 3. Sideways Move
    print("\n3. Hill Climbing with Sideways Move")
    print("-" * 60)
    hc3 = SidewaysMoveHillClimbing(initial_state, obj_func, max_iterations=100, max_sideways_moves=20)
    hc3.solve()
    hc3.print_results(verbose=True)


# if __name__ == "__main__":
#     demo_hill_climbing()