"""
visualizer.py - Modul untuk visualisasi hasil algoritma

Menyediakan berbagai fungsi visualisasi:
1. Print hasil ke console (formatted)
2. Plot objective function vs iterations
3. Visualisasi kontainer (ASCII art sederhana)
4. Comparison chart antar algoritma
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict

class ResultVisualizer:
    """Class untuk visualisasi hasil eksperimen"""
    
    @staticmethod
    def print_state_comparison(initial_state, final_state, algorithm_name: str):
        """Print perbandingan state awal vs akhir"""
        print("\n" + "=" * 70)
        print(f"PERBANDINGAN STATE - {algorithm_name}")
        print("=" * 70)
        
        print("\n--- STATE AWAL ---")
        print(f"Jumlah Kontainer: {initial_state.num_containers()}")
        ResultVisualizer._print_state_detail(initial_state)
        
        print("\n--- STATE AKHIR ---")
        print(f"Jumlah Kontainer: {final_state.num_containers()}")
        ResultVisualizer._print_state_detail(final_state)
        
        improvement = initial_state.num_containers() - final_state.num_containers()
        print(f"\nPengurangan Kontainer: {improvement}")
    
    @staticmethod
    def _print_state_detail(state):
        """Helper untuk print detail state"""
        for i, container in enumerate(state.containers):
            if len(container) > 0:
                load = state.get_container_load(i)
                remaining = state.get_container_remaining(i)
                percentage = (load / state.capacity) * 100
                
                items_str = ", ".join([f"{item}({state.items[item]})" 
                                      for item in container])
                
                # Visual bar
                bar_length = 40
                filled = int((load / state.capacity) * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                print(f"  Kontainer {i+1:2d} [{bar}] {load:3d}/{state.capacity:3d} ({percentage:5.1f}%)")
                print(f"                {items_str}")
    
    @staticmethod
    def plot_objective_history(algorithm_results: List[Dict], 
                               title: str = "Objective Function vs Iterations",
                               save_path: str = None):
        """
        Plot objective function history untuk satu atau lebih algoritma.
        
        Args:
            algorithm_results: List of result dictionaries dari get_result_dict()
            title: Judul plot
            save_path: Path untuk save plot (optional)
        """
        plt.figure(figsize=(12, 6))
        
        for result in algorithm_results:
            algo_name = result['algorithm']
            history = result['history']
            
            plt.plot(history, label=algo_name, linewidth=2, marker='o', 
                    markersize=3, markevery=max(1, len(history)//20))
        
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Objective Function Value', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_comparison_bar(algorithm_results: List[Dict], 
                           metric: str = 'num_containers',
                           title: str = None,
                           save_path: str = None):
        """
        Plot bar chart untuk membandingkan metrik antar algoritma.
        
        Args:
            algorithm_results: List of result dictionaries
            metric: Metrik yang akan dibandingkan 
                   ('num_containers', 'duration', 'iterations')
            title: Custom title (optional)
            save_path: Path untuk save plot (optional)
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract data
        algorithms = [r['algorithm'] for r in algorithm_results]
        
        if metric == 'num_containers':
            values = [r['solution']['num_containers_final'] for r in algorithm_results]
            ylabel = 'Number of Containers'
            default_title = 'Comparison: Number of Containers Used'
        elif metric == 'duration':
            values = [r['execution']['duration_seconds'] for r in algorithm_results]
            ylabel = 'Duration (seconds)'
            default_title = 'Comparison: Execution Time'
        elif metric == 'iterations':
            values = [r['execution']['iterations'] for r in algorithm_results]
            ylabel = 'Number of Iterations'
            default_title = 'Comparison: Iterations Count'
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        # Create bar chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(algorithms)))
        bars = ax.bar(algorithms, values, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Algorithm', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title or default_title, fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_multiple_runs(runs_data: List[List], 
                          algorithm_name: str,
                          title: str = None,
                          save_path: str = None):
        """
        Plot multiple runs dari algoritma yang sama (untuk analisis konsistensi).
        
        Args:
            runs_data: List of histories, [[run1_history], [run2_history], ...]
            algorithm_name: Nama algoritma
            title: Custom title
            save_path: Path untuk save plot
        """
        plt.figure(figsize=(12, 6))
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(runs_data)))
        
        for i, history in enumerate(runs_data):
            plt.plot(history, label=f'Run {i+1}', 
                    color=colors[i], alpha=0.7, linewidth=2)
        
        # Calculate and plot average
        max_len = max(len(h) for h in runs_data)
        avg_history = []
        for j in range(max_len):
            values = [h[j] for h in runs_data if j < len(h)]
            avg_history.append(np.mean(values))
        
        plt.plot(avg_history, label='Average', 
                color='red', linewidth=3, linestyle='--')
        
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Objective Function Value', fontsize=12)
        plt.title(title or f'{algorithm_name} - Multiple Runs', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    @staticmethod
    def visualize_containers_ascii(state, title: str = "Container Visualization"):
        """
        Visualisasi kontainer menggunakan ASCII art.
        Sederhana tapi informatif untuk quick check.
        """
        print("\n" + "=" * 70)
        print(f"{title}")
        print("=" * 70)
        
        for i, container in enumerate(state.containers):
            if len(container) == 0:
                continue
            
            load = state.get_container_load(i)
            percentage = (load / state.capacity) * 100
            
            # Header
            print(f"\n┌─ Kontainer {i+1} ─── {load}/{state.capacity} ({percentage:.1f}%) " + 
                  "─" * (50 - len(f"Kontainer {i+1}") - len(f"{load}/{state.capacity}") - 10) + "┐")
            
            # Items
            for item_id in container:
                item_size = state.items[item_id]
                bar_len = int((item_size / state.capacity) * 40)
                bar = "▓" * bar_len
                print(f"│ {item_id:8s} [{bar:<40s}] {item_size:3d} │")
            
            # Footer
            remaining = state.get_container_remaining(i)
            print(f"│ {'':8s} {'':<40s} Sisa: {remaining:3d} │")
            print("└" + "─" * 68 + "┘")
    
    @staticmethod
    def print_summary_table(algorithm_results: List[Dict]):
        """
        Print tabel summary untuk membandingkan semua algoritma.
        """
        print("\n" + "=" * 120)
        print("SUMMARY TABLE - ALGORITHM COMPARISON")
        print("=" * 120)
        
        # Header
        print(f"{'Algorithm':<35s} | {'Containers':>11s} | {'Duration':>10s} | {'Iterations':>10s} | {'Valid':>6s} | {'Improvement':>12s}")
        print("-" * 120)
        
        # Rows
        for result in algorithm_results:
            algo = result['algorithm']
            containers = result['solution']['num_containers_final']
            duration = result['execution']['duration_seconds']
            iterations = result['execution']['iterations']
            valid = "Yes" if result['solution']['is_valid'] else "NO"
            improvement = result['objective_function']['improvement_percent']
            
            print(f"{algo:<35s} | {containers:>11d} | {duration:>9.4f}s | {iterations:>10d} | {valid:>6s} | {improvement:>11.2f}%")
        
        print("=" * 120)
    
    @staticmethod
    def create_experiment_report(algorithm_results: List[Dict], 
                                output_dir: str = "./output"):
        """
        Generate complete experiment report dengan semua visualisasi.
        
        Args:
            algorithm_results: List of result dictionaries
            output_dir: Directory untuk save plots
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Print summary table
        ResultVisualizer.print_summary_table(algorithm_results)
        
        # 2. Plot objective histories
        ResultVisualizer.plot_objective_history(
            algorithm_results,
            title="Objective Function Comparison",
            save_path=f"{output_dir}/objective_comparison.png"
        )
        
        # 3. Plot container comparison
        ResultVisualizer.plot_comparison_bar(
            algorithm_results,
            metric='num_containers',
            save_path=f"{output_dir}/containers_comparison.png"
        )
        
        # 4. Plot duration comparison
        ResultVisualizer.plot_comparison_bar(
            algorithm_results,
            metric='duration',
            save_path=f"{output_dir}/duration_comparison.png"
        )
        
        # 5. Print final states
        for result in algorithm_results:
            print(f"\n{'='*70}")
            print(f"FINAL STATE - {result['algorithm']}")
            print(f"{'='*70}")
            print(f"Containers: {result['solution']['num_containers_final']}")
            print(f"Valid: {result['solution']['is_valid']}")
            print(f"Objective: {result['objective_function']['final']:.2f}")
        
        print(f"\n✓ Report generated successfully!")
        print(f"  Plots saved to: {output_dir}/")

    @staticmethod
    def plot_genetic_progression(generations_data: List[Dict], 
                                title: str = "Genetic Algorithm Progression",
                                save_path: str = None):
        import matplotlib.pyplot as plt

        generations = [d['generation'] for d in generations_data]
        best_fitness = [d['best_fitness'] for d in generations_data]
        avg_fitness = [d.get('avg_fitness', None) for d in generations_data]

        plt.figure(figsize=(12, 6))
        plt.plot(generations, best_fitness, label='Best Fitness', color='blue', linewidth=2)
        if any(f is not None for f in avg_fitness):
            plt.plot(generations, avg_fitness, label='Average Fitness', color='orange', linestyle='--', linewidth=2)

        plt.xlabel('Banyaknya Terasi (Generasi)', fontsize=12)
        plt.ylabel('Objective Function (Fitness)', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Tambahkan info best di pojok kanan bawah luar grafik
        min_best = min(best_fitness)
        min_gen = generations[best_fitness.index(min_best)]
        plt.figtext(0.99, 0.01, f"Best Obj Function: {min_best:.2f} @Gen-{min_gen}",
                    ha='right', va='bottom', fontsize=12, color='blue', 
                    bbox=dict(facecolor='white', alpha=0.85, edgecolor='blue', boxstyle='round,pad=0.3'))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")

        plt.show()
    
    @staticmethod
    def plot_hill_climbing_progress(algorithm_stats: dict, 
                                    history: list,
                                    title: str = None,
                                    save_path: str = None):
        """
        Plot UNIVERSAL untuk semua varian Hill Climbing.
        Auto-detect varian dan tampilkan info yang relevan.
        
        Args:
            algorithm_stats: Dict dari get_statistics()
            history: List of objective values per iteration
            title: Custom title (optional)
            save_path: Path untuk save plot (optional)
        
        Returns:
            matplotlib Figure object
        """
        if not history or len(history) == 0:
            print("No history data available for plotting")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # ===== PLOT UTAMA =====
        iterations = range(len(history))
        ax.plot(iterations, history, marker='o', linestyle='-', 
                color='dodgerblue', linewidth=2, markersize=4, 
                label='Objective Function', zorder=3)
        
        # ===== HIGHLIGHT: Stuck Iteration =====
        stuck_iter = algorithm_stats.get('stuck_at_iteration')
        if stuck_iter is not None and stuck_iter < len(history):
            ax.axvline(x=stuck_iter, color='red', linestyle='--', 
                      linewidth=2, alpha=0.7, 
                      label=f'Stuck at iteration {stuck_iter}', zorder=2)
            ax.plot(stuck_iter, history[stuck_iter], 'r*', 
                   markersize=15, label='Stuck Point', zorder=4)
        
        # ===== HIGHLIGHT: Best Value =====
        best_value = min(history)
        best_iter = history.index(best_value)
        ax.plot(best_iter, best_value, 'g*', markersize=15, 
               label=f'Best (iter {best_iter})', zorder=4)
        
        # ===== LABELS =====
        ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        ax.set_ylabel('Objective Function Value', fontsize=12, fontweight='bold')
        
        algo_name = algorithm_stats.get('algorithm', 'Hill Climbing')
        ax.set_title(title or f'{algo_name} - Progress', 
                    fontsize=14, fontweight='bold')
        
        ax.legend(fontsize=10, loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.4)
        
        # ===== INFO BOX =====
        info_lines = []
        info_lines.append(f"Algorithm: {algo_name}")
        info_lines.append(f"Duration: {algorithm_stats.get('duration', 0):.4f}s")
        info_lines.append(f"Total Iterations: {len(history)}")
        info_lines.append(f"Final Objective: {history[-1]:.2f}")
        info_lines.append(f"Best Objective: {best_value:.2f}")
        
        # Auto-detect variant dan tambahkan info
        if 'seed' in algorithm_stats:
            seed_val = algorithm_stats.get('seed')
            info_lines.append(f"Seed: {seed_val if seed_val is not None else 'Random'}")
        
        if 'max_sideways_moves' in algorithm_stats:
            sideways = algorithm_stats.get('total_sideways_moves', 0)
            max_sideways = algorithm_stats.get('max_sideways_moves', 0)
            info_lines.append(f"Sideways: {sideways}/{max_sideways}")
        
        if 'max_restarts' in algorithm_stats:
            restarts = algorithm_stats.get('total_restarts_executed', 0)
            max_restarts = algorithm_stats.get('max_restarts', 0)
            avg_iter = algorithm_stats.get('average_iterations_per_run', 0)
            info_lines.append(f"Restarts: {restarts}/{max_restarts}")
            info_lines.append(f"Avg Iter/Run: {avg_iter:.1f}")
        
        if stuck_iter is not None:
            reason = algorithm_stats.get('stuck_reason', 'local_optimum')
            reason_map = {
                'local_optimum': 'Local Optimum',
                'max_sideways_reached': 'Max Sideways',
                'max_iterations': 'Max Iterations'
            }
            info_lines.append(f"Stuck: {reason_map.get(reason, reason)}")
        
        # Render info box
        info_text = '\n'.join(info_lines)
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
               family='monospace')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"   ✓ Plot saved: {save_path}")
        
        plt.show()
        return fig

# Demo
def demo_visualizer():
    """Demo penggunaan visualizer"""
    from core.state import State
    from core.objective_function import ObjectiveFunction
    from core.initializer import BinPackingInitializer
    
    # Setup
    items = {
        "BRG001": 40, "BRG002": 55, "BRG003": 25,
        "BRG004": 60, "BRG005": 30, "BRG006": 45, "BRG007": 50
    }
    capacity = 100
    
    initial_state = BinPackingInitializer.best_fit(items, capacity)
    
    print("Demo Visualizer")
    print("=" * 70)
    
    # 1. ASCII visualization
    ResultVisualizer.visualize_containers_ascii(initial_state, "Initial State")
    
    # 2. State comparison (simulasi)
    final_state = initial_state.copy()
    # Simulasi improvement
    if len(final_state.containers) > 2:
        # Gabungkan 2 kontainer terakhir jika muat
        last_container = final_state.containers[-1]
        second_last = final_state.containers[-2]
        
        total_size = sum(final_state.items[item] for item in last_container + second_last)
        if total_size <= capacity:
            final_state.containers[-2].extend(last_container)
            final_state.containers.pop()
    
    ResultVisualizer.print_state_comparison(initial_state, final_state, "Demo Algorithm")


if __name__ == "__main__":
    demo_visualizer()