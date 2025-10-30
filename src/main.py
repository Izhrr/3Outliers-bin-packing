"""
Usage:
    python src/main.py --input <file directory>
"""

import argparse
import sys
import os
from typing import List
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.state import State
from core.objective_function import ObjectiveFunction
from core.initializer import BinPackingInitializer
from algorithms.hill_climbing import (
    SteepestAscentHillClimbing,
    StochasticHillClimbing,
    SidewaysMoveHillClimbing,
    RandomRestartHillClimbing
)
from algorithms.simulated_annealing import SimulatedAnnealing
from algorithms.genetic_algorithm import GeneticAlgorithm
from utils.file_handler import FileHandler
from utils.visualizer import ResultVisualizer
from utils.timer import Timer


def print_welcome():
    """Print welcome banner"""
    print("\n" + "=" * 70)
    print("█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 15 + "WELCOME TO BIN PACKING SOLVER" + " " * 24 + "█")
    print("█" + " " * 10 + "Local Search Algorithms for Optimization" + " " * 18 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    print("=" * 70 + "\n")


def print_algorithm_menu():
    """Print algorithm selection menu"""
    print("\n" + "┌" + "─" * 68 + "┐")
    print("│" + " " * 20 + "SELECT AN ALGORITHM" + " " * 29 + "│")
    print("├" + "─" * 68 + "┤")
    print("│  1. Steepest Ascent Hill Climbing" + " " * 34 + "│")
    print("│  2. Stochastic Hill Climbing" + " " * 39 + "│")
    print("│  3. Sideways Move Hill Climbing" + " " * 36 + "│")
    print("│  4. Random Restart Hill Climbing" + " " * 35 + "│")
    print("│  5. Simulated Annealing" + " " * 44 + "│")
    print("│  6. Genetic Algorithm" + " " * 46 + "│")
    print("├" + "─" * 68 + "┤")
    print("│  Type 'EXIT' to quit the program" + " " * 35 + "│")
    print("└" + "─" * 68 + "┘\n")


def get_algorithm_choice():
    """
    Get algorithm choice from user.
    
    Returns:
        str: Algorithm code ('steepest', 'stochastic', etc.) or 'exit'
    """
    algorithm_map = {
        '1': 'steepest',
        '2': 'stochastic',
        '3': 'sideways',
        '4': 'restart',
        '5': 'sa',
        '6': 'ga'
    }
    
    while True:
        choice = input("Enter your choice (1-6 or EXIT): ").strip()
        
        if choice.upper() == 'EXIT':
            return 'exit'
        
        if choice in algorithm_map:
            return algorithm_map[choice]
        
        # Invalid input
        print("Invalid input! Please enter a number between 1-5 or type EXIT.\n")


def run_single_algorithm(algo_class, initial_state, obj_func, output_dir=None, plot_dir=None, **kwargs):
    """    
    Args:
        algo_class: Class algoritma
        initial_state: State awal
        obj_func: ObjectiveFunction
        output_dir: Directory untuk save SA metrics (khusus SA)
        plot_dir: Directory untuk save plots
        **kwargs: Parameter untuk algoritma
    
    Returns:
        dict: Result dictionary dengan '_final_state_object' (kebutuhan visualisasi)
    """
    print(f"\nRunning {algo_class.__name__}...")
    algorithm = algo_class(initial_state, obj_func, **kwargs)
    
    with Timer(verbose=True):
        algorithm.solve()
    algorithm.print_results(verbose=True)
    
    # Get result dict
    result = algorithm.get_result_dict()
    if 'history' not in result and hasattr(algorithm, 'history'):
        result['history'] = algorithm.history
    
    if 'statistics' not in result and hasattr(algorithm, 'get_statistics'):
        result['statistics'] = algorithm.get_statistics()
    if 'ga_metrics' in result:
        print()
        print(f"--- Genetic Algorithm Hyperparameters ---")
        print(f"Population Size      : {result['ga_metrics']['population_size']}")
        print(f"Mutation Rate        : {result['ga_metrics']['mutation_rate']:.2f}")

    # Untuk Simulated Annealing
    if 'sa_metrics' in result:
        print()
        print(f"--- Simulated Annealing Hyperparameters ---")
        print(f"Initial Temperature  : {result['sa_metrics']['initial_temperature']}")
        print(f"Cooling Rate         : {result['sa_metrics']['cooling_rate']}")
    
    # Simulated Annealing (nambahin print stuck count + accepted worse)
    if isinstance(algorithm, SimulatedAnnealing) and output_dir:
        algorithm.save_sa_metrics(output_dir)
        print(f"\n--- Simulated Annealing Additional Performance ---")
        print(f"  Stuck count: {algorithm.stuck_count}")
        print(f"  Accepted worse: {algorithm.accepted_worse_count}")

    # Show improvement untuk Random Restart
    if isinstance(algo_class, type) and issubclass(algo_class, RandomRestartHillClimbing):
        stats = result.get('statistics', {})
        if 'total_restarts_executed' in stats:
            print(f"   Total restarts: {stats['total_restarts_executed']}")
            print(f"   Average iterations per run: {stats.get('average_iterations_per_run', 0):.2f}")
    
    # Generate plots jika plot_dir disediakan
    if plot_dir:
        os.makedirs(plot_dir, exist_ok=True)
        algo_name_safe = result['algorithm'].replace(' ', '_').replace('(', '').replace(')', '').replace('=', '').replace(',', '').replace('.', '')
        
        print(f"\n📈 Generating plots...")
        # Untuk Genetic Algorithm
        
        # 1. Plot objective history
        obj_plot_path = os.path.join(plot_dir, f"{algo_name_safe}_objective.png")
        ResultVisualizer.plot_single_objective_history(result, save_path=obj_plot_path)
        print(f"  ✓ Objective history: {obj_plot_path}")
        
        # 2. Algorithm-specific plots
        if isinstance(algorithm, SimulatedAnnealing):
            # SA Acceptance Probability
            accept_plot_path = os.path.join(plot_dir, f"{algo_name_safe}_acceptance_prob.png")
            ResultVisualizer.plot_sa_acceptance_probability(result, save_path=accept_plot_path)
            print(f"  ✓ Acceptance probability: {accept_plot_path}")
        
        if isinstance(algorithm, GeneticAlgorithm):
            # GA Progression
            prog_plot_path = os.path.join(plot_dir, f"{algo_name_safe}_progression.png")
            ResultVisualizer.plot_ga_progression(result, save_path=prog_plot_path)
            print(f"  ✓ GA progression: {prog_plot_path}")

         #  Hill Climbing variants (termasuk Random Restart)
        if any(isinstance(algorithm, cls) for cls in [
            SteepestAscentHillClimbing, 
            StochasticHillClimbing, 
            SidewaysMoveHillClimbing,
            RandomRestartHillClimbing
        ]):
            # Hill Climbing Progress Plot
            hc_plot_path = os.path.join(plot_dir, f"{algo_name_safe}_progress.png")
            
            stats = result.get('statistics', {})
            hist = result.get('history', [])
            
            if hist and len(hist) > 0:
                ResultVisualizer.plot_hill_climbing_progress(
                    algorithm_stats=stats,
                    history=hist,
                    title=f"{result['algorithm']} - Objective Function Progress",
                    save_path=hc_plot_path
                )
                print(f"  ✓ HC progress: {hc_plot_path}")
            else:
                print(f" No history data for HC plot")
   
    return result


def run_single_experiment(algorithm_code: str, initial_state: State, obj_func: ObjectiveFunction, 
                         items: dict, capacity: int, output_dir: str = "./output"):
    """
    Run a single algorithm experiment.
    
    Args:
        algorithm_code: Code for algorithm
        initial_state: Initial state
        obj_func: Objective function
        items: Items dict
        capacity: Container capacity
        output_dir: Output directory
    """
    # Setup algorithm
    algo_class = None
    algo_name = ""
    kwargs = {}
    
    if algorithm_code == 'steepest':
        algo_name = "Steepest Ascent Hill Climbing"
        algo_class = SteepestAscentHillClimbing
        kwargs = {"max_iterations": 1000}
    
    elif algorithm_code == 'stochastic':
        algo_name = "Stochastic Hill Climbing"
        algo_class = StochasticHillClimbing
        kwargs = {"max_iterations": 1000, "seed": 42}
    
    elif algorithm_code == 'sideways':
        algo_name = "Sideways Move Hill Climbing"
        algo_class = SidewaysMoveHillClimbing
        kwargs = {"max_iterations": 100, "max_sideways_moves": 100}
    
    elif algorithm_code == 'restart':
        algo_name = "Random Restart Hill Climbing"
        algo_class = RandomRestartHillClimbing
        kwargs = {
            "max_restarts": 5,
            "base_algorithm": "steepest",
            "base_max_iterations": 1000  
        }

    elif algorithm_code == 'sa':
        algo_name = "Simulated Annealing"
        algo_class = SimulatedAnnealing
        kwargs = {
            "max_iterations": 10000,
            "initial_temp": 1000,
            "cooling_rate": 0.99
        }
    
    elif algorithm_code == 'ga':
        algo_name = "Genetic Algorithm"
        algo_class = GeneticAlgorithm
        kwargs = {
            "items": items,
            "capacity": capacity,
            "mutation_probability": 0.5,
            "population_size": 50,
            "max_iterations": 10000
        }
    
    
    # Setup directories
    algo_output_dir = None
    if algo_class == SimulatedAnnealing:
        algo_output_dir = os.path.join(output_dir, 'sa_metrics')
    
    plot_dir = os.path.join(output_dir, 'plots')
    
    result = run_single_algorithm(
        algo_class,
        initial_state,
        obj_func,
        output_dir=algo_output_dir,
        plot_dir=plot_dir,
        **kwargs
    )
    
    # Visualize final state
    final_state = result.get('_final_state_object', None)
    if final_state:
        print(f"\nFinal State Detail:")
        print(f"Jumlah kontainer akhir: {final_state.num_containers()}")
        
        # Visualisasi
        ResultVisualizer.visualize_containers_ascii(
            final_state,
            f"Final State - {algo_name}"
        )
    
    # Save result
    print(f"\nSaving results...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean result for JSON
    result_copy = result.copy()
    result_copy.pop('_final_state_object', None)
    
    FileHandler.write_results(
        [result_copy],
        f"{output_dir}/results_{algo_name.replace(' ', '_')}_{timestamp}.json",
        metadata={
            'capacity': capacity,
            'num_items': len(items)
        }
    )


def run_interactive(input_file: str, output_dir: str = "./output"):
    """
    Run interactive mode - memilih algoritma satu per satu.
    
    Args:
        input_file: Path to input JSON file
        output_dir: Output directory
    """
    # Print welcome banner
    print_welcome()
    
    # Read input once
    print(f"Reading input from: {input_file}\n")
    input_data = FileHandler.read_input(input_file)
    
    capacity = input_data['capacity']
    items = input_data['items']
    
    print(f"   Capacity: {capacity}")
    print(f"   Items: {len(items)}")
    print(f"   Total size: {sum(items.values())}")
    print(f"   Theoretical minimum containers: {sum(items.values()) / capacity:.2f}")
    
    # Initialize once
    initial_state = BinPackingInitializer.next_fit(items, capacity)
    obj_func = ObjectiveFunction()
    
    print(f"   Initial containers: {initial_state.num_containers()}")
    print(f"   Initial objective: {obj_func.calculate(initial_state):.2f}")
    
    ResultVisualizer.visualize_containers_ascii(initial_state, "Initial State")
    
     # Interactive loop
    while True:
        print_algorithm_menu()
        choice = get_algorithm_choice()
        
        if choice == 'exit':
            print("\n" + "=" * 70)
            print("Thank you for using Bin Packing Solver!")
            print("=" * 70 + "\n")
            break

        # Run selected algorithm
        try:
            run_single_experiment(choice, initial_state, obj_func, items, capacity, output_dir)
        except Exception as e:
            print(f"\nError running algorithm: {e}")
            import traceback
            traceback.print_exc()
        
        # Ask if continue
        print("\n" + "─" * 70)
        input("Press ENTER to continue...")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Bin Packing Problem Solver using Local Search Algorithms'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input JSON file'
    )
    
    parser.add_argument(
        '--algorithm',
        type=str,
        default='interactive',
        choices=['interactive', 'all', 'steepest', 'stochastic', 'sideways', 'restart', 'sa', 'ga'],
        help='Algorithm to run (default: interactive mode)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Output directory (default: ./output)'
    )
    
    args = parser.parse_args()
    
    try:
        # Interactive mode (default)
        if args.algorithm == 'interactive':
            run_interactive(args.input, args.output)
    
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Program interrupted by user")
        print("=" * 70 + "\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()