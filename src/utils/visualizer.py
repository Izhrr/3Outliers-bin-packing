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
        Plot objective function
        
        Args:
            result: Result dictionary dari algorithm.get_result_dict()
            save_path: Path untuk save plot (REQUIRED untuk auto-save)
        """
        plt.figure(figsize=(12, 6))
        
        algo_name = result['algorithm']
        history = result['history']
        iterations = list(range(len(history)))
        
        # Plot line
        plt.plot(iterations, history, linewidth=2, marker='o', 
                markersize=3, markevery=max(1, len(history)//20), color='blue')
        
        # Mark best value dengan red dot
        best_value = min(history)
        best_iter = history.index(best_value)
        plt.plot(best_iter, best_value, 'ro', markersize=10, 
                label=f'Best: {best_value:.2f} @iter {best_iter}')
        
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Objective Function Value', fontsize=12)
        plt.title(title or f'{algo_name} - Objective Function vs Iterations', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
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

        plt.close()