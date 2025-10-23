"""
file_handler.py - Handler untuk membaca dan menulis file

Mendukung:
- Membaca input dari JSON
- Menulis hasil eksperimen ke JSON
- Export results untuk analisis
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime

class FileHandler:
    """Class untuk handle file I/O operations"""
    
    @staticmethod
    def read_input(filepath: str) -> Dict:
        """
        Membaca input dari file JSON.
        
        Format input:
        {
            "kapasitas_kontainer": 100,
            "barang": [
                {"id": "BRG001", "ukuran": 40},
                {"id": "BRG002", "ukuran": 55},
                ...
            ]
        }
        
        Returns:
            Dict dengan keys: 'capacity' dan 'items'
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            capacity = data.get('kapasitas_kontainer')
            barang_list = data.get('barang', [])
            
            # Convert list to dict
            items = {item['id']: item['ukuran'] for item in barang_list}
            
            return {
                'capacity': capacity,
                'items': items
            }
        
        except FileNotFoundError:
            raise FileNotFoundError(f"File tidak ditemukan: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Format JSON tidak valid: {filepath}")
        except KeyError as e:
            raise ValueError(f"Format input tidak sesuai, missing key: {e}")
    
    @staticmethod
    def write_results(results: List[Dict], output_path: str, 
                     metadata: Dict = None):
        """
        Menulis hasil eksperimen ke file JSON.
        
        Args:
            results: List of result dictionaries dari get_result_dict()
            output_path: Path untuk output file
            metadata: Additional metadata (optional)
        """
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'results': results
        }
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✓ Results saved to: {output_path}")
    
    @staticmethod
    def create_sample_input(output_path: str, 
                          num_items: int = 10, 
                          capacity: int = 100,
                          min_size: int = 10,
                          max_size: int = 80):
        """
        Generate sample input file untuk testing.
        
        Args:
            output_path: Path untuk save sample input
            num_items: Jumlah barang
            capacity: Kapasitas kontainer
            min_size: Ukuran minimum barang
            max_size: Ukuran maksimum barang
        """
        import random
        
        barang = []
        for i in range(1, num_items + 1):
            barang.append({
                'id': f'BRG{i:03d}',
                'ukuran': random.randint(min_size, max_size)
            })
        
        data = {
            'kapasitas_kontainer': capacity,
            'barang': barang
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Sample input created: {output_path}")
    
    @staticmethod
    def export_csv(results: List[Dict], output_path: str):
        """
        Export hasil ke CSV untuk analisis di spreadsheet.
        
        Args:
            results: List of result dictionaries
            output_path: Path untuk CSV file
        """
        import csv
        
        if not results:
            print("No results to export")
            return
        
        # Define CSV columns
        fieldnames = [
            'algorithm',
            'num_containers_final',
            'num_containers_initial',
            'objective_final',
            'objective_initial',
            'improvement_percent',
            'duration_seconds',
            'iterations',
            'is_valid'
        ]
        
        # Extract data
        rows = []
        for result in results:
            row = {
                'algorithm': result['algorithm'],
                'num_containers_final': result['solution']['num_containers_final'],
                'num_containers_initial': result['solution']['num_containers_initial'],
                'objective_final': result['objective_function']['final'],
                'objective_initial': result['objective_function']['initial'],
                'improvement_percent': result['objective_function']['improvement_percent'],
                'duration_seconds': result['execution']['duration_seconds'],
                'iterations': result['execution']['iterations'],
                'is_valid': result['solution']['is_valid']
            }
            rows.append(row)
        
        # Write CSV
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ CSV exported to: {output_path}")


# Demo
def demo_file_handler():
    """Demo penggunaan FileHandler"""
    
    print("=" * 60)
    print("DEMO FILE HANDLER")
    print("=" * 60)
    
    # 1. Create sample input
    print("\n1. Creating sample input...")
    FileHandler.create_sample_input(
        './data/input/sample_demo.json',
        num_items=7,
        capacity=100,
        min_size=20,
        max_size=60
    )
    
    # 2. Read input
    print("\n2. Reading input...")
    input_data = FileHandler.read_input('./data/input/sample_demo.json')
    print(f"   Capacity: {input_data['capacity']}")
    print(f"   Items: {len(input_data['items'])}")
    
    # 3. Create mock results
    print("\n3. Creating mock results...")
    mock_results = [
        {
            'algorithm': 'Hill Climbing',
            'execution': {
                'duration_seconds': 0.123,
                'iterations': 50
            },
            'objective_function': {
                'initial': 450.0,
                'final': 320.5,
                'improvement_percent': 28.8
            },
            'solution': {
                'is_valid': True,
                'num_containers_initial': 5,
                'num_containers_final': 4
            }
        }
    ]
    
    # 4. Save results
    print("\n4. Saving results...")
    FileHandler.write_results(
        mock_results,
        './data/output/demo_results.json',
        metadata={'test': 'demo'}
    )
    
    # 5. Export CSV
    print("\n5. Exporting to CSV...")
    FileHandler.export_csv(
        mock_results,
        './data/output/demo_results.csv'
    )
    
    print("\n✓ Demo completed!")


if __name__ == "__main__":
    demo_file_handler()