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
    
    def print_results(self, verbose: bool = True):
        """
        Print hasil algoritma dengan detail lengkap.
        Menggunakan instance variables yang sudah ada.
        
        Args:
            verbose: Jika True, tampilkan initial/final state ASCII
        """
        if verbose:
            # Import di sini untuk avoid circular import
            from src.utils.visualizer import ResultVisualizer
            
            print("\n" + "="*80)
            print(f"RESULTS - {self.get_name()}")
            print("="*80)
            
            # ===== STATE AWAL =====
            print("\n" + "─"*80)
            print(">>> INITIAL STATE")
            print("─"*80)
            ResultVisualizer.visualize_containers_ascii(self.initial_state, "Initial State")
            initial_value = self.history[0] if self.history else self.evaluate_state(self.initial_state)
            print(f"\n➤ Initial Objective: {initial_value:.2f}")
            print(f"➤ Initial Containers: {self.initial_state.num_containers()}")
            
            # ===== STATE AKHIR =====
            print("\n" + "─"*80)
            print(">>> FINAL STATE")
            print("─"*80)
            ResultVisualizer.visualize_containers_ascii(self.best_state, "Final State")
            print(f"\n➤ Final Objective: {self.best_value:.2f}")
            print(f"➤ Final Containers: {self.best_state.num_containers()}")
            print(f"➤ Valid Solution: {'✓ YES' if self.best_state.is_valid() else '✗ NO'}")
            
            # ===== IMPROVEMENT =====
            print("\n" + "─"*80)
            print(">>> IMPROVEMENT")
            print("─"*80)
            obj_improvement = initial_value - self.best_value
            container_reduction = self.initial_state.num_containers() - self.best_state.num_containers()
            improvement_pct = (obj_improvement / initial_value * 100) if initial_value > 0 else 0
            
            print(f"Objective Improvement: {obj_improvement:.2f} ({improvement_pct:.2f}%)")
            print(f"Container Reduction: {container_reduction} containers")
        
        # ===== STATISTICS =====
        print("\n" + "─"*80)
        print(">>> STATISTICS")
        print("─"*80)
        print(f"➤ Algorithm: {self.get_name()}")
        print(f"➤ Duration: {self.duration:.4f} seconds")
        print(f"➤ Total Iterations: {len(self.history)}")
        print(f"➤ Best Objective: {self.best_value:.2f}")
        
        # Stuck info
        if self.stuck_iteration is not None:
            print(f"➤ Stuck at Iteration: {self.stuck_iteration}")
            print(f"➤ Stuck Reason: local_optimum")
        
        if verbose:
            print("\n" + "="*80)

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
    
    def print_results(self, verbose: bool = True):
        if verbose:
            from src.utils.visualizer import ResultVisualizer
            
            print("\n" + "="*80)
            print(f"RESULTS - {self.get_name()}")
            print("="*80)
            
            # ===== STATE AWAL =====
            print("\n" + "─"*80)
            print(">>> INITIAL STATE")
            print("─"*80)
            ResultVisualizer.visualize_containers_ascii(self.initial_state, "Initial State")
            initial_value = self.history[0] if self.history else self.evaluate_state(self.initial_state)
            print(f"\n➤ Initial Objective: {initial_value:.2f}")
            print(f"➤ Initial Containers: {self.initial_state.num_containers()}")
            
            # ===== STATE AKHIR =====
            print("\n" + "─"*80)
            print(">>> FINAL STATE")
            print("─"*80)
            ResultVisualizer.visualize_containers_ascii(self.best_state, "Final State")
            print(f"\n➤ Final Objective: {self.best_value:.2f}")
            print(f"➤ Final Containers: {self.best_state.num_containers()}")
            print(f"➤ Valid Solution: {'YES' if self.best_state.is_valid() else 'NO'}")
            
            # ===== IMPROVEMENT =====
            print("\n" + "─"*80)
            print(">>> IMPROVEMENT")
            print("─"*80)
            obj_improvement = initial_value - self.best_value
            container_reduction = self.initial_state.num_containers() - self.best_state.num_containers()
            improvement_pct = (obj_improvement / initial_value * 100) if initial_value > 0 else 0
            
            print(f"Objective Improvement: {obj_improvement:.2f} ({improvement_pct:.2f}%)")
            print(f"Container Reduction: {container_reduction} containers")
        
        # ===== STATISTICS =====
        print("\n" + "─"*80)
        print(">>> STATISTICS")
        print("─"*80)
        print(f"➤ Algorithm: {self.get_name()}")
        print(f"➤ Duration: {self.duration:.4f} seconds")
        print(f"➤ Total Iterations: {len(self.history)}")
        print(f"➤ Best Objective: {self.best_value:.2f}")
        
        # Stuck info
        if self.stuck_iteration is not None:
            print(f"➤ Stuck at Iteration: {self.stuck_iteration}")
        
        # Seed info
        print(f"➤ Random Seed: {self.seed if self.seed is not None else 'None (truly random)'}")
        
        if verbose:
            print("\n" + "="*80)

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
    
    def print_results(self, verbose: bool = True):
        if verbose:
            from src.utils.visualizer import ResultVisualizer
            
            print("\n" + "="*80)
            print(f"RESULTS - {self.get_name()}")
            print("="*80)
            
            # ===== STATE AWAL =====
            print("\n" + "─"*80)
            print(">>> INITIAL STATE")
            print("─"*80)
            ResultVisualizer.visualize_containers_ascii(self.initial_state, "Initial State")
            initial_value = self.history[0] if self.history else self.evaluate_state(self.initial_state)
            print(f"\n➤ Initial Objective: {initial_value:.2f}")
            print(f"➤ Initial Containers: {self.initial_state.num_containers()}")
            
            # ===== STATE AKHIR =====
            print("\n" + "─"*80)
            print(">>> FINAL STATE")
            print("─"*80)
            ResultVisualizer.visualize_containers_ascii(self.best_state, "Final State")
            print(f"\n➤ Final Objective: {self.best_value:.2f}")
            print(f"➤ Final Containers: {self.best_state.num_containers()}")
            print(f"➤ Valid Solution: {'✓ YES' if self.best_state.is_valid() else '✗ NO'}")
            
            # ===== IMPROVEMENT =====
            print("\n" + "─"*80)
            print(">>> IMPROVEMENT")
            print("─"*80)
            obj_improvement = initial_value - self.best_value
            container_reduction = self.initial_state.num_containers() - self.best_state.num_containers()
            improvement_pct = (obj_improvement / initial_value * 100) if initial_value > 0 else 0
            
            print(f"Objective Improvement: {obj_improvement:.2f} ({improvement_pct:.2f}%)")
            print(f"Container Reduction: {container_reduction} containers")
        
        # ===== STATISTICS =====
        print("\n" + "─"*80)
        print(">>> STATISTICS")
        print("─"*80)
        print(f"➤ Algorithm: {self.get_name()}")
        print(f"➤ Duration: {self.duration:.4f} seconds")
        print(f"➤ Total Iterations: {len(self.history)}")
        print(f"➤ Best Objective: {self.best_value:.2f}")
        
        # Stuck info
        if self.stuck_iteration is not None:
            print(f"➤ Stuck at Iteration: {self.stuck_iteration}")
            print(f"➤ Stuck Reason: {self.stuck_reason}")
        
        # Sideways specific info
        print(f"➤ Total Sideways Moves: {self.sideways_count}")
        print(f"➤ Maximum Sideways Allowed: {self.max_sideways_moves}")
        if self.sideways_count >= self.max_sideways_moves:
            print(f"Maximum sideways limit reached!")
        
        if verbose:
            print("\n" + "="*80)

class RandomRestartHillClimbing(HillClimbingBase):
    """
    Random Restart Hill Climbing.
    
    Algoritma:
    1. Lakukan Hill Climbing dari initial state
    2. Simpan hasil terbaik dari run tersebut
    3. Restart dengan initial state acak yang baru (random shuffle items)
    4. Ulangi sampai max_restarts tercapai
    5. Return solusi terbaik dari semua restart
    
    Karakteristik:
    - Mengatasi masalah stuck di local optimum
    - Trade-off: waktu vs kualitas solusi
    - Non-deterministic (hasil berbeda setiap run)
    - Lebih robust dibanding single-run HC
    """
    
    def __init__(self, 
                 initial_state,                      #  UBAH: Terima initial_state
                 objective_function, 
                 max_restarts: int = 5,              #  DEFAULT: 5 restarts
                 base_algorithm: str = "steepest",   #  TAMBAH: Base algorithm type
                 base_max_iterations: int = 1000,    #  TAMBAH: Max iterations per run
                 base_max_sideways: int = 100,       #  TAMBAH: For sideways variant
                 seed: Optional[int] = None):
        """
        Args:
            initial_state: Initial state (akan di-copy untuk restart pertama)
            objective_function: Fungsi objektif untuk evaluasi
            max_restarts: Jumlah restart maksimal
            base_algorithm: Base HC variant ('steepest', 'stochastic', 'sideways')
            base_max_iterations: Max iterations per restart
            base_max_sideways: Max sideways moves (untuk sideways variant)
            seed: Random seed untuk reproducibility
        """
        super().__init__(initial_state, objective_function, base_max_iterations)
        
        self.items = {}
        for container in initial_state.containers:
            for item_id, size in container.items.items():
                self.items[item_id] = size
        self.capacity = initial_state.capacity
        
        # Parameters
        self.max_restarts = max_restarts
        self.base_algorithm = base_algorithm.lower()
        self.base_max_iterations = base_max_iterations
        self.base_max_sideways = base_max_sideways
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
        
        # Track best solution across all restarts
        self.best_state_overall = self.current_state.copy()
        self.best_value_overall = self.evaluate_state(self.best_state_overall)
        
        # History untuk setiap restart
        self.runs_history = []
    
    def _create_base_algorithm(self, state):
        """
        Create instance of base HC algorithm.
        
        Args:
            state: Initial state untuk run ini
            
        Returns:
            Instance of base HC algorithm
        """
        if self.base_algorithm == "steepest":
            return SteepestAscentHillClimbing(
                state, 
                self.objective_function,
                max_iterations=self.base_max_iterations
            )
        
        elif self.base_algorithm == "stochastic":
            return StochasticHillClimbing(
                state,
                self.objective_function,
                max_iterations=self.base_max_iterations,
                seed=self.seed
            )
        
        elif self.base_algorithm == "sideways":
            return SidewaysMoveHillClimbing(
                state,
                self.objective_function,
                max_iterations=self.base_max_iterations,
                max_sideways_moves=self.base_max_sideways
            )
        
        else:
            raise ValueError(f"Unknown base algorithm: {self.base_algorithm}")
    
    def _generate_random_initial_state(self):
        """
        Generate random initial state dengan random shuffle items.
        
        Returns:
            New random initial state
        """
        from src.core.initializer import BinPackingInitializer
        
        # Shuffle items
        item_list = list(self.items.items())
        random.shuffle(item_list)
        shuffled_items = dict(item_list)
        
        # Create new state dengan Next Fit
        new_state = BinPackingInitializer.next_fit(
            shuffled_items, 
            self.capacity
        )
        
        return new_state
    
    def get_name(self) -> str:
        return f"Random Restart Hill Climbing"
    
    def solve(self):
        """Main algorithm"""
        start_time = time.perf_counter()
        
        for restart in range(self.max_restarts):
            # 1. Generate initial state untuk run ini
            if restart == 0:
                # Restart pertama gunakan initial state yang sudah ada
                new_initial_state = self.current_state.copy()
            else:
                # Restart selanjutnya gunakan random initial state baru
                new_initial_state = self._generate_random_initial_state()
            
            # 2. Jalankan base HC algorithm dari initial state
            hc_run = self._create_base_algorithm(new_initial_state)
            final_state = hc_run.solve()
            final_value = self.evaluate_state(final_state)
            
            # 3. Ambil statistik dari run ini
            run_stats = hc_run.get_statistics()
            
            # 4. Simpan hasil run ke history
            initial_value = self.evaluate_state(new_initial_state)
            self.runs_history.append({
                'restart': restart,
                'initial_objective': initial_value,
                'final_objective': final_value,
                'iterations': len(hc_run.history),
                'improvement': initial_value - final_value
            })
            
            # 5. Update best state overall jika run ini lebih baik
            if final_value < self.best_value_overall:
                self.best_value_overall = final_value
                self.best_state_overall = final_state.copy()
            
            # 6. Extend global history dengan history dari run ini
            self.history.extend(hc_run.history)

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
        stats['best_objective'] = self.best_value_overall
        stats['seed'] = self.seed
        stats['base_algorithm'] = self.base_algorithm
        stats['base_max_iterations'] = self.base_max_iterations
        
        # Summary total iterasi
        if len(self.runs_history) > 0:
            # Total iterasi dari semua restart
            total_iterations = sum(run['iterations'] for run in self.runs_history)
            stats['total_iterations'] = total_iterations
            
            # Rata-rata iterasi per restart
            stats['average_iterations_per_run'] = total_iterations / len(self.runs_history)
            
            # Min dan max iterasi per restart
            iterations_list = [run['iterations'] for run in self.runs_history]
            stats['min_iterations'] = min(iterations_list)
            stats['max_iterations'] = max(iterations_list)
            
            # Summary improvements
            improvements = [run['improvement'] for run in self.runs_history]
            stats['average_improvement_per_run'] = sum(improvements) / len(improvements)
            stats['best_improvement'] = max(improvements)
        
        return stats
    
    def print_results(self, verbose: bool = True):
        """Print hasil dengan detail lengkap termasuk per-restart info"""
        if verbose:
            from src.utils.visualizer import ResultVisualizer
            
            print("\n" + "="*80)
            print(f"RESULTS - {self.get_name()} (restarts={self.max_restarts})")
            print("="*80)
            
            # ===== STATE AWAL (first restart) =====
            print("\n" + "─"*80)
            print("📦 INITIAL STATE (First Restart)")
            print("─"*80)
            if len(self.runs_history) > 0:
                print(f"➤ Initial Objective (First Restart): {self.runs_history[0]['initial_objective']:.2f}")
            
            # ===== STATE AKHIR (best overall) =====
            print("\n" + "─"*80)
            print("📦 FINAL STATE (Best Overall)")
            print("─"*80)
            ResultVisualizer.visualize_containers_ascii(self.best_state_overall, "Final State")
            print(f"\n➤ Final Objective (Best): {self.best_value_overall:.2f}")
            print(f"➤ Final Containers: {self.best_state_overall.num_containers()}")
            print(f"➤ Valid Solution: {'✓ YES' if self.best_state_overall.is_valid() else '✗ NO'}")
            
            # ===== PER-RESTART SUMMARY =====
            print("\n" + "─"*80)
            print("PER-RESTART SUMMARY")
            print("─"*80)
            for run in self.runs_history:
                print(f"Restart {run['restart']}: "
                      f"Initial={run['initial_objective']:.2f} → "
                      f"Final={run['final_objective']:.2f} "
                      f"(Improvement: {run['improvement']:.2f}, "
                      f"Iterations: {run['iterations']})")
        
        # ===== STATISTICS =====
        print("\n" + "─"*80)
        print(" STATISTICS")
        print("─"*80)
        stats = self.get_statistics()
        print(f"➤ Algorithm: {self.get_name()} (restarts={self.max_restarts})")
        print(f"➤ Duration: {self.duration:.4f} seconds")
        print(f"➤ Total Restarts Executed: {stats['total_restarts_executed']}")
        print(f"➤ Maximum Restarts: {stats['max_restarts']}")
        print(f"➤ Best Objective (Overall): {stats['best_objective']:.2f}")
        
        # Summary iterasi
        if 'total_iterations' in stats:
            print(f"➤ Total Iterations (All Runs): {stats['total_iterations']}")
            print(f"➤ Average Iterations per Run: {stats['average_iterations_per_run']:.2f}")
            print(f"➤ Iterations Range: {stats['min_iterations']} - {stats['max_iterations']}")
            print(f"➤ Average Improvement per Run: {stats['average_improvement_per_run']:.2f}")
            print(f"➤ Best Improvement (Single Run): {stats['best_improvement']:.2f}")
        
        if verbose:
            print("\n" + "="*80)

    def get_result_dict(self) -> dict:
        """
        Get result dictionary dengan data comprehensive.
        
        Returns:
            dict: Result dictionary
        """
        result = super().get_result_dict()
        
        result['runs_history'] = self.runs_history
        
        # Update algorithm name
        result['algorithm'] = f"{self.get_name()} (restarts={self.max_restarts}, base={self.base_algorithm})"
        
        return result