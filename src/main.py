"""
main.py - Entry point untuk menjalankan program Bin Packing Local Search

Usage:
    python main.py --input data/input/sample.json --algorithm all
    python main.py --input data/input/sample.json --algorithm hc
    python main.py --demo
"""

import argparse
import sys
import os
from typing import List
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.state import State
from core.objective_function import ObjectiveFunction
from core.initializer import BinPackingInitializer
from algorithms.hill_climbing import (
    SteepestAscentHillClimbing,
    StochasticHillClimbing,
    SidewaysMoveHillClimbing
)
from utils.file_handler import FileHandler
from utils.visualizer import ResultVisualizer
from utils.timer import Timer


def run_single_algorithm(algo_class, initial_state, obj_func, **kwargs):
    """
    Helper function untuk menjalankan satu algoritma.
    
    Args:
        algo_class: Class dari algoritma (e.g., SteepestAscentHillClimbing)
        initial_state: State awal
        obj_func: ObjectiveFunction instance
        **kwargs: Parameter tambahan untuk algoritma
    
    Returns:
        Dict: Result dictionary
    """
    print(f"\nRunning {algo_class.__name__}...")
    
    algorithm = algo_class(initial_state, obj_func, **kwargs)
    
    with Timer(verbose=True):
        algorithm.solve()
    
    algorithm.print_results(verbose=False)
    
    return algorithm.get_result_dict()


def run_experiment(input_file: str, algorithms: List[str], 
                   output_dir: str = "./output"):
    """
    Menjalankan eksperimen dengan algoritma yang dipilih.
    
    Args:
        input_file: Path ke file input JSON
        algorithms: List algoritma yang akan dijalankan
        output_dir: Directory untuk output
    """
    print("=" * 70)
    print("BIN PACKING PROBLEM - LOCAL SEARCH SOLVER")
    print("=" * 70)
    
    # 1. Read input
    print(f"\n📁 Reading input from: {input_file}")
    input_data = FileHandler.read_input(input_file)
    
    capacity = input_data['capacity']
    items = input_data['items']
    
    print(f"   Capacity: {capacity}")
    print(f"   Items: {len(items)}")
    print(f"   Total size: {sum(items.values())}")
    print(f"   Theoretical minimum containers: {sum(items.values()) / capacity:.2f}")
    
    # 2. Initialize
    print(f"\n🔧 Initializing with Best Fit...")
    initial_state = BinPackingInitializer.best_fit(items, capacity)
    obj_func = ObjectiveFunction()
    
    print(f"   Initial containers: {initial_state.num_containers()}")
    print(f"   Initial objective: {obj_func.calculate(initial_state):.2f}")
    
    ResultVisualizer.visualize_containers_ascii(initial_state, "Initial State")
    
    # 3. Run algorithms
    print(f"\n🚀 Running algorithms...")
    results = []
    algo_list = []
    if 'steepest' in algorithms or 'all' in algorithms:
        algo_list.append(("Steepest Ascent Hill Climbing", SteepestAscentHillClimbing, {"max_iterations": 1000}))
    if 'stochastic' in algorithms or 'all' in algorithms:
        algo_list.append(("Stochastic Hill Climbing", StochasticHillClimbing, {"max_iterations": 1000, "seed": 42}))
    if 'sideways' in algorithms or 'all' in algorithms:
        algo_list.append(("Sideways Move Hill Climbing", SidewaysMoveHillClimbing, {"max_iterations": 1000, "max_sideways_moves": 100}))

    for algo_name, algo_class, kwargs in algo_list:
        print(f"\n{'='*70}\nAlgoritma: {algo_name}\n{'='*70}")
        result = run_single_algorithm(
            algo_class,
            initial_state,
            obj_func,
            **kwargs
        )
        results.append(result)

        # Ambil state akhir
        final_state = result.get('final_state', None)
        if final_state is None:
            print("Tidak ada state akhir yang tersedia.")
            continue

        print(f"Jumlah kontainer akhir: {final_state.num_containers()}")
        print(f"Detail isi setiap kontainer:")
        for idx, container in enumerate(final_state.containers):
            load = final_state.get_container_load(idx)
            items_str = ', '.join([f"{item_id}({final_state.items[item_id]})" for item_id in container])
            print(f"  - Kontainer {idx+1} ({load}/{final_state.capacity}): {items_str}")
        print('-'*70)
    
    # 4. Visualize results
    # print(f"\n📊 Generating visualizations...")
    # ResultVisualizer.create_experiment_report(results, output_dir)
    
    # 5. Save results
    print(f"\n💾 Saving results...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # FileHandler.write_results(
    #     results,
    #     f"{output_dir}/results_{timestamp}.json",
    #     metadata={
    #         'input_file': input_file,
    #         'capacity': capacity,
    #         'num_items': len(items)
    #     }
    # )
    
    # FileHandler.export_csv(
    #     results,
    #     f"{output_dir}/results_{timestamp}.csv"
    # )
    
    print(f"\n✅ Experiment completed!")
    print(f"   Results saved to: {output_dir}/")


def run_demo():
    """Run demo dengan sample data"""
    print("=" * 70)
    print("DEMO MODE - Bin Packing Local Search")
    print("=" * 70)
    
    # Create sample input
    sample_file = "./data/input/sample_xlarge.json"
    os.makedirs("./data/input", exist_ok=True)
    
    print("\n📝 Creating sample input...")
    FileHandler.create_sample_input(
        sample_file,
        num_items=10,
        capacity=100,
        min_size=20,
        max_size=70
    )
    
    # Run experiment
    run_experiment(
        sample_file,
        algorithms=['all'],
        output_dir="./output/demo"
    )


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Bin Packing Problem Solver using Local Search Algorithms'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Path to input JSON file'
    )
    
    parser.add_argument(
        '--algorithm',
        type=str,
        default='all',
        choices=['all', 'steepest', 'stochastic', 'sideways', 'sa', 'ga'],
        help='Algorithm to run (default: all)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Output directory (default: ./output)'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo with sample data'
    )
    
    args = parser.parse_args()
    
    try:
        if args.demo:
            run_demo()
        elif args.input:
            algorithms = [args.algorithm] if args.algorithm != 'all' else ['all']
            run_experiment(args.input, algorithms, args.output)
        else:
            parser.print_help()
            print("\n⚠️  Error: Please provide --input or use --demo flag")
            sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    from datetime import datetime
    from typing import List
    main()