"""
visualizer.py - Modul untuk visualisasi hasil algoritma INDIVIDUAL

Menyediakan fungsi visualisasi untuk SATU algoritma per eksekusi:
1. Plot objective function vs iterations (semua algoritma)
2. Visualisasi kontainer ASCII art (console display)
3. Algorithm-specific plots:
   - SA: acceptance probability, temperature cooling
   - GA: progression (best & avg fitness)

TIDAK ADA comparison plots - setiap algoritma dijalankan terpisah.
"""

import matplotlib.pyplot as plt
from typing import Dict


class ResultVisualizer:
    """Class untuk visualisasi hasil INDIVIDUAL algorithm"""
    
    @staticmethod
    def visualize_containers_ascii(state, title: str = "Container Table"):
        """
        Visualisasi ringkas semua kontainer dalam bentuk tabel per baris.
        Cocok untuk screenshot banyak container.
        """

        width = 100
        
        # Header
        print("\n" + "┌" + "─" * (width - 4) + "┐")
        print(f"│ {title:^{width-6}} │")
        print("├" + "─" * (width - 4) + "┤")
        
        print(f"│ {'No':>4} │ {'Load':>8} │ {'Sisa':>8} │ {'Isi Barang':<65} │")
        print("├" + "─" * 6 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 67 + "┤")
        
        # Data rows
        empty_count = 0
        for i, container in enumerate(state.containers):
            if len(container) == 0:
                empty_count += 1
                continue
            
            load = state.get_container_load(i)
            remaining = state.get_container_remaining(i)
            
            items_str = ', '.join(f"{item}:{state.items[item]}" for item in container)
            
            if len(items_str) > 65:
                items_str = items_str[:62] + "..."
            
            print(f"│ {i+1:>4} │ {load:>8.1f} │ {remaining:>8.1f} │ {items_str:<65} │")
        
        # Footer
        print("└" + "─" * 6 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 67 + "┘")
    
    @staticmethod
    def plot_single_objective_history(result: Dict,
                                    title: str = None,
                                    save_path: str = None):
        """
        Plot objective function history - UNIVERSAL untuk semua algoritma.
        Support Random Restart dengan restart points visualization.
        
        Args:
            result: Result dictionary dari algorithm.get_result_dict()
            title: Custom title (optional)
            save_path: Path untuk save plot (optional, auto-save jika diberikan)
        
        Returns:
            None
        """
        # ===== VALIDASI DATA =====
        history = result.get('history', [])
        if not history or len(history) == 0:
            print("No history data available for plotting")
            return
        
        algo_name = result.get('algorithm', 'Unknown Algorithm')
        
        # ===== CREATE FIGURE =====
        plt.figure(figsize=(12, 6))
        
        iterations = list(range(len(history)))
        
        # ===== PLOT MAIN LINE =====
        plt.plot(iterations, history, linewidth=2, marker='o', 
                markersize=3, markevery=max(1, len(history)//20), 
                color='dodgerblue', label='Objective Value', zorder=3)
        
        # ===== MARK BEST VALUE =====
        best_value = min(history)
        best_iter = history.index(best_value)
        plt.plot(best_iter, best_value, 'g*', markersize=15, 
                label=f'Best: {best_value:.2f} @iter {best_iter}', zorder=4)
        
        # ===== RANDOM RESTART: MARK RESTART POINTS =====
        if 'runs_history' in result:
            runs_history = result['runs_history']
            cumulative_iter = 0
            restart_count = 0
            
            for i, run in enumerate(runs_history[:-1]):  # Exclude last run
                cumulative_iter += run.get('iterations', 0)
                if cumulative_iter < len(history):
                    plt.axvline(x=cumulative_iter, color='orange', linestyle='--', 
                            linewidth=1.5, alpha=0.6, zorder=2)
                    restart_count += 1
            
            # Add legend untuk restart lines (hanya sekali)
            if restart_count > 0:
                plt.plot([], [], color='orange', linestyle='--', linewidth=1.5, 
                    label=f'Restart Points ({restart_count})')
        
        # ===== LABELS =====
        plt.xlabel('Iteration', fontsize=12, fontweight='bold')
        plt.ylabel('Objective Function Value', fontsize=12, fontweight='bold')
        plt.title(title or f'{algo_name} - Objective Function vs Iterations', 
                fontsize=14, fontweight='bold')
        plt.legend(fontsize=10, loc='upper right')
        plt.grid(True, alpha=0.3)
        
        # ===== INFO BOX (untuk Random Restart) =====
        stats = result.get('statistics', {})
        if 'total_restarts_executed' in stats or 'runs_history' in result:
            info_lines = [
                f"Total Iterations: {len(history)}",
                f"Final Objective: {history[-1]:.2f}",
                f"Best Objective: {best_value:.2f}"
            ]
            
            # Random Restart specific info
            if 'total_restarts_executed' in stats:
                total_restarts = stats['total_restarts_executed']
                avg_iter = stats.get('average_iterations_per_run', 0)
                info_lines.append(f"Total Restarts: {total_restarts}")
                if avg_iter > 0:
                    info_lines.append(f"Avg Iter/Run: {avg_iter:.1f}")
            
            info_text = '\n'.join(info_lines)
            plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes,
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
                family='monospace')
        
        plt.tight_layout()
    
    # ===== SAVE DAN CLOSE =====
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"   ✓ Objective history saved: {save_path}")
    
    plt.close()  

    @staticmethod
    def plot_sa_acceptance_probability(result: Dict,
                                       title: str = None,
                                       save_path: str = None):
        """
        Plot acceptance probability e^(ΔE/T) untuk Simulated Annealing.
        
        Args:
            result: Result dictionary dengan 'sa_metrics'
            save_path: Path untuk save plot
        """
        if 'sa_metrics' not in result:
            print("Warning: Not a SA result, skipping acceptance probability plot")
            return
        
        sa_metrics = result['sa_metrics']
        acceptance_probs = sa_metrics['acceptance_probabilities']
        iterations = list(range(1, len(acceptance_probs) + 1))
        
        plt.figure(figsize=(12, 6))
        
        # Plot acceptance probability
        plt.plot(iterations, acceptance_probs, linewidth=1, color='red', alpha=0.7)
        
        # Add average line sebagai reference
        avg_prob = sum(acceptance_probs) / len(acceptance_probs)
        plt.axhline(y=avg_prob, color='blue', linestyle='--', 
                   label=f'Average: {avg_prob:.4f}', linewidth=2)
        
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('e^(ΔE/T) - Acceptance Probability', fontsize=12)
        plt.title(title or 'Simulated Annealing - Acceptance Probability Over Time', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.ylim([0, 1.05])
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.close()
    
    @staticmethod
    def plot_ga_progression(result: Dict,
                           title: str = None,
                           save_path: str = None):
        """
        Plot GA progression (best & avg fitness per generation).
        
        Args:
            result: Result dictionary dengan 'ga_metrics'
            save_path: Path untuk save plot
        """
        if 'ga_metrics' not in result:
            print("Warning: Not a GA result, skipping progression plot")
            return
        
        ga_metrics = result['ga_metrics']
        generations_data = ga_metrics.get('generations_data', [])
        
        if not generations_data:
            print("Warning: No generations data, skipping plot")
            return
        
        generations = [d['generation'] for d in generations_data]
        best_fitness = [d['best_fitness'] for d in generations_data]
        avg_fitness = [d.get('avg_fitness', None) for d in generations_data]

        plt.figure(figsize=(12, 6))
        
        # Plot best fitness
        plt.plot(generations, best_fitness, label='Best Fitness', 
                color='blue', linewidth=2)
        
        # Plot average fitness
        if any(f is not None for f in avg_fitness):
            plt.plot(generations, avg_fitness, label='Average Fitness', 
                    color='orange', linestyle='--', linewidth=2)

        plt.xlabel('Generation', fontsize=12)
        plt.ylabel('Objective Function (Fitness)', fontsize=12)
        plt.title(title or 'Genetic Algorithm - Progression', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Add best value info
        min_best = min(best_fitness)
        min_gen = generations[best_fitness.index(min_best)]
        plt.figtext(0.99, 0.01, f"Best: {min_best:.2f} @Gen-{min_gen}",
                    ha='right', va='bottom', fontsize=12, color='blue', 
                    bbox=dict(facecolor='white', alpha=0.85, edgecolor='blue', 
                             boxstyle='round,pad=0.3'))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

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
