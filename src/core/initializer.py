"""
initializer.py - Modul untuk inisialisasi state awal Bin Packing Problem

Menyediakan berbagai metode heuristik untuk membuat solusi awal:
1. First Fit (FF) - Masukkan ke kontainer pertama yang cukup
2. Best Fit (BF) - Masukkan ke kontainer dengan sisa ruang paling kecil yang cukup
3. Worst Fit (WF) - Masukkan ke kontainer dengan sisa ruang paling besar
4. Next Fit (NF) - Masukkan ke kontainer terakhir, jika tidak cukup buat baru
5. Random - Masukkan secara random

Semua metode support sorting items (biasanya descending untuk hasil lebih baik)
"""

from typing import Dict, List, Optional
import random
from core.state import State


class BinPackingInitializer:
    """
    Class untuk membuat state awal menggunakan berbagai heuristik.
    
    Semua method bersifat static dan return instance State.
    """
    
    @staticmethod
    def first_fit(items: Dict[str, int], 
                  capacity: int, 
                  sort_items: bool = False) -> State:
        """
        First Fit Algorithm: Masukkan barang ke kontainer pertama yang cukup.
        
        Algoritma:
        1. Untuk setiap barang (bisa diurutkan terlebih dahulu)
        2. Cari kontainer pertama yang cukup untuk menampung barang
        3. Jika tidak ada, buat kontainer baru
        4. Masukkan barang ke kontainer tersebut
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
            sort_items: Jika True, sort items descending by size (First Fit Decreasing)
        
        Returns:
            State: State awal dengan First Fit allocation
            
        Complexity:
            Time: O(n²) - untuk setiap item, cek semua kontainer
            Space: O(n) - untuk menyimpan containers
        """
        # Sort items jika diminta (FFD - First Fit Decreasing)
        item_list = list(items.items())
        if sort_items:
            item_list.sort(key=lambda x: x[1], reverse=True)
        
        containers = []
        
        for item_id, item_size in item_list:
            placed = False
            
            # Cari kontainer yang cukup
            for container in containers:
                current_load = sum(items[iid] for iid in container)
                if current_load + item_size <= capacity:
                    container.append(item_id)
                    placed = True
                    break
            
            # Jika tidak ada kontainer yang cukup, buat baru
            if not placed:
                containers.append([item_id])
        
        return State(items=items, capacity=capacity, containers=containers)
    
    @staticmethod
    def best_fit(items: Dict[str, int], 
                 capacity: int, 
                 sort_items: bool = False) -> State:
        """
        Best Fit Algorithm: Masukkan barang ke kontainer dengan sisa ruang terkecil yang cukup.
        
        Algoritma:
        1. Untuk setiap barang (bisa diurutkan terlebih dahulu)
        2. Cari kontainer dengan sisa ruang terkecil yang masih bisa menampung barang
        3. Jika tidak ada, buat kontainer baru
        4. Masukkan barang ke kontainer tersebut
        
        Tujuan: Meminimalkan waste space dengan memilih kontainer yang paling pas.
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
            sort_items: Jika True, sort items descending by size (Best Fit Decreasing)
        
        Returns:
            State: State awal dengan Best Fit allocation
            
        Complexity:
            Time: O(n²) - untuk setiap item, cek semua kontainer
            Space: O(n)
        """
        # Sort items jika diminta (BFD - Best Fit Decreasing)
        item_list = list(items.items())
        if sort_items:
            item_list.sort(key=lambda x: x[1], reverse=True)
        
        containers = []
        
        for item_id, item_size in item_list:
            # Cari kontainer dengan sisa ruang terkecil yang cukup
            best_container_idx = -1
            min_remaining = float('inf')
            
            for idx, container in enumerate(containers):
                current_load = sum(items[iid] for iid in container)
                remaining = capacity - current_load
                
                # Cek apakah cukup dan apakah lebih baik dari best sejauh ini
                if remaining >= item_size and remaining < min_remaining:
                    best_container_idx = idx
                    min_remaining = remaining
            
            # Masukkan ke best container atau buat baru
            if best_container_idx != -1:
                containers[best_container_idx].append(item_id)
            else:
                containers.append([item_id])
        
        return State(items=items, capacity=capacity, containers=containers)
    
    @staticmethod
    def worst_fit(items: Dict[str, int], 
                  capacity: int, 
                  sort_items: bool = False) -> State:
        """
        Worst Fit Algorithm: Masukkan barang ke kontainer dengan sisa ruang terbesar.
        
        Algoritma:
        1. Untuk setiap barang (bisa diurutkan terlebih dahulu)
        2. Cari kontainer dengan sisa ruang terbesar
        3. Jika tidak ada kontainer atau tidak cukup, buat kontainer baru
        4. Masukkan barang ke kontainer tersebut
        
        Tujuan: Menyebarkan beban lebih merata (meskipun biasanya tidak optimal).
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
            sort_items: Jika True, sort items descending by size
        
        Returns:
            State: State awal dengan Worst Fit allocation
            
        Complexity:
            Time: O(n²)
            Space: O(n)
        """
        # Sort items jika diminta
        item_list = list(items.items())
        if sort_items:
            item_list.sort(key=lambda x: x[1], reverse=True)
        
        containers = []
        
        for item_id, item_size in item_list:
            # Cari kontainer dengan sisa ruang terbesar
            worst_container_idx = -1
            max_remaining = -1
            
            for idx, container in enumerate(containers):
                current_load = sum(items[iid] for iid in container)
                remaining = capacity - current_load
                
                # Cek apakah cukup dan apakah lebih buruk dari worst sejauh ini
                if remaining >= item_size and remaining > max_remaining:
                    worst_container_idx = idx
                    max_remaining = remaining
            
            # Masukkan ke worst container atau buat baru
            if worst_container_idx != -1:
                containers[worst_container_idx].append(item_id)
            else:
                containers.append([item_id])
        
        return State(items=items, capacity=capacity, containers=containers)
    
    @staticmethod
    def next_fit(items: Dict[str, int], 
                 capacity: int, 
                 sort_items: bool = False) -> State:
        """
        Next Fit Algorithm: Masukkan barang ke kontainer terakhir, jika tidak cukup buat baru.
        
        Algoritma:
        1. Untuk setiap barang (bisa diurutkan terlebih dahulu)
        2. Coba masukkan ke kontainer terakhir
        3. Jika tidak cukup, buat kontainer baru dan masukkan ke sana
        4. Tidak pernah kembali ke kontainer sebelumnya
        
        Karakteristik:
        - Paling sederhana dan cepat O(n)
        - Biasanya hasil paling buruk (paling banyak kontainer)
        - Bagus untuk online scenario (barang datang streaming)
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
            sort_items: Jika True, sort items descending by size
        
        Returns:
            State: State awal dengan Next Fit allocation
            
        Complexity:
            Time: O(n) - paling cepat!
            Space: O(n)
        """
        # Sort items jika diminta
        item_list = list(items.items())
        if sort_items:
            item_list.sort(key=lambda x: x[1], reverse=True)
        
        containers = [[]]  # Start dengan satu kontainer kosong
        
        for item_id, item_size in item_list:
            current_container = containers[-1]
            current_load = sum(items[iid] for iid in current_container)
            
            # Cek apakah kontainer terakhir cukup
            if current_load + item_size <= capacity:
                current_container.append(item_id)
            else:
                # Buat kontainer baru
                containers.append([item_id])
        
        # Hapus kontainer kosong (jika ada)
        containers = [c for c in containers if len(c) > 0]
        
        return State(items=items, capacity=capacity, containers=containers)
    
    @staticmethod
    def random_fit(items: Dict[str, int], 
                   capacity: int, 
                   seed: Optional[int] = None) -> State:
        """
        Random Fit: Masukkan barang secara random ke kontainer yang valid.
        
        Algoritma:
        1. Shuffle urutan items
        2. Untuk setiap barang:
        3. Ambil list kontainer yang valid (cukup untuk menampung barang)
        4. Pilih random dari kontainer valid
        5. Jika tidak ada kontainer valid, buat baru
        
        Berguna untuk:
        - Random restart hill climbing
        - Membandingkan dengan metode deterministik
        - Generating diverse initial solutions
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
            seed: Random seed untuk reproducibility (optional)
        
        Returns:
            State: State awal dengan random allocation
        """
        if seed is not None:
            random.seed(seed)
        
        # Shuffle items
        item_list = list(items.items())
        random.shuffle(item_list)
        
        containers = []
        
        for item_id, item_size in item_list:
            # Cari semua kontainer yang valid
            valid_containers = []
            for idx, container in enumerate(containers):
                current_load = sum(items[iid] for iid in container)
                if current_load + item_size <= capacity:
                    valid_containers.append(idx)
            
            # Pilih random atau buat baru
            if valid_containers:
                chosen_idx = random.choice(valid_containers)
                containers[chosen_idx].append(item_id)
            else:
                containers.append([item_id])
        
        return State(items=items, capacity=capacity, containers=containers)
    
    @staticmethod
    def greedy_fit(items: Dict[str, int], 
                   capacity: int) -> State:
        """
        Greedy Fit: Kombinasi Best Fit Decreasing untuk hasil optimal.
        
        Ini adalah alias untuk best_fit dengan sort_items=True, yang umumnya
        memberikan hasil terbaik di antara metode heuristik sederhana.
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
        
        Returns:
            State: State awal dengan Best Fit Decreasing allocation
        """
        return BinPackingInitializer.best_fit(items, capacity, sort_items=True)
    
    @staticmethod
    def empty_state(items: Dict[str, int], capacity: int) -> State:
        """
        Buat state kosong (semua kontainer kosong).
        
        Berguna untuk:
        - Testing
        - Custom initialization logic
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
        
        Returns:
            State: State dengan containers kosong
        """
        return State(items=items, capacity=capacity, containers=[[]])
    
    @staticmethod
    def single_container_per_item(items: Dict[str, int], capacity: int) -> State:
        """
        Buat state dengan setiap item di kontainer terpisah.
        
        Ini adalah solusi terburuk (maximum containers), berguna untuk:
        - Upper bound testing
        - Baseline comparison
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
        
        Returns:
            State: State dengan setiap item di kontainer sendiri
        """
        containers = [[item_id] for item_id in items.keys()]
        return State(items=items, capacity=capacity, containers=containers)
    
    @staticmethod
    def analyze_initializers(items: Dict[str, int], capacity: int) -> Dict[str, int]:
        """
        Analyze dan compare berbagai initializer untuk dataset tertentu.
        
        Returns dict dengan jumlah kontainer untuk setiap metode.
        Berguna untuk memilih initializer terbaik untuk dataset tertentu.
        
        Args:
            items: Dict {item_id: size}
            capacity: Kapasitas kontainer
        
        Returns:
            Dict: {method_name: num_containers}
        """
        results = {}
        
        # Test semua metode
        methods = [
            ('First Fit', lambda: BinPackingInitializer.first_fit(items, capacity, False)),
            # ('First Fit Decreasing', lambda: BinPackingInitializer.first_fit(items, capacity, True)),
            ('Best Fit', lambda: BinPackingInitializer.best_fit(items, capacity, False)),
            # ('Best Fit Decreasing', lambda: BinPackingInitializer.best_fit(items, capacity, True)),
            ('Worst Fit', lambda: BinPackingInitializer.worst_fit(items, capacity, False)),
            # ('Worst Fit Decreasing', lambda: BinPackingInitializer.worst_fit(items, capacity, True)),
            ('Next Fit', lambda: BinPackingInitializer.next_fit(items, capacity, False)),
            # ('Next Fit Decreasing', lambda: BinPackingInitializer.next_fit(items, capacity, True)),
        ]
        
        for name, method in methods:
            state = method()
            results[name] = state.num_containers()
        
        return results


# Convenience function untuk quick testing
def quick_test():
    """
    Quick test untuk semua initializer methods.
    Run dengan: python -c "from src.core.initializer import quick_test; quick_test()"
    """
    # Sample data
    # Generate items kompleks dan acak
    import random
    random.seed(42)
    capacity = 100
    items = {}
    for i in range(1, 16):
        # Ukuran acak antara 10 dan 80
        items[f'BARANG-{i:02d}'] = random.randint(10, 80)
    # Acak urutan items
    items = dict(random.sample(list(items.items()), len(items)))

    print("=" * 70)
    print("INITIALIZER TESTING")
    print("=" * 70)
    print(f"Items: {items}")
    print(f"Capacity: {capacity}")
    print(f"Total size: {sum(items.values())}")
    print(f"Theoretical minimum: {sum(items.values()) / capacity:.2f}")
    print()

    # Simpan semua state hasil inisialisasi
    states = {
        "First Fit": BinPackingInitializer.first_fit(items, capacity, sort_items=False),
        "Best Fit": BinPackingInitializer.best_fit(items, capacity, sort_items=False),
        "Worst Fit": BinPackingInitializer.worst_fit(items, capacity, sort_items=False),
        "Next Fit": BinPackingInitializer.next_fit(items, capacity, sort_items=False),
    }

    print("Results:")
    print("-" * 70)
    for method, state in states.items():
        print(f"{method:15} : {state.num_containers()} containers")
    print("-" * 70)

    # Tampilkan detail isi setiap kontainer untuk semua metode
    for method, state in states.items():
        print(f"\n{method} result:")
        print(state)


if __name__ == "__main__":
    quick_test()
