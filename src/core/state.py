"""
state.py - Representasi State untuk Bin Packing Problem
Menggunakan List of List untuk merepresentasikan alokasi barang ke kontainer
"""

import copy
from typing import List, Dict, Tuple, Optional

class State:
    """
    Representasi state dalam Bin Packing Problem.
    State adalah alokasi barang ke kontainer.
    
    Attributes:
        containers: List[List[str]] - List of List berisi ID barang
        items: Dict[str, int] - Dictionary {id_barang: ukuran}
        capacity: int - Kapasitas maksimal setiap kontainer
    """
    
    def __init__(self, items: Dict[str, int], capacity: int, containers: Optional[List[List[str]]] = None):
        """
        Args:
            items: Dictionary berisi {id_barang: ukuran_barang}
            capacity: Kapasitas kontainer
            containers: (Optional) Inisialisasi containers, jika None akan dibuat kosong
        """
        self.items = items
        self.capacity = capacity
        self.containers = containers if containers is not None else [[]]
    
    def get_container_load(self, container_idx: int) -> int:
        """Hitung total ukuran barang dalam kontainer tertentu"""
        return sum(self.items[item_id] for item_id in self.containers[container_idx])
    
    def get_container_remaining(self, container_idx: int) -> int:
        """Hitung sisa kapasitas kontainer"""
        return self.capacity - self.get_container_load(container_idx)
    
    def is_valid(self) -> bool:
        """Cek apakah state valid (tidak ada kontainer yang overload)"""
        for i in range(len(self.containers)):
            if self.get_container_load(i) > self.capacity:
                return False
        return True
    
    def num_containers(self) -> int:
        """Return jumlah kontainer yang digunakan (tidak kosong)"""
        return len([c for c in self.containers if len(c) > 0])
    
    def move_item(self, item_id: str, from_idx: int, to_idx: int) -> 'State':
        """
        Pindahkan barang dari satu kontainer ke kontainer lain.
        Return state baru (immutable operation).
        
        Args:
            item_id: ID barang yang akan dipindah
            from_idx: Index kontainer asal
            to_idx: Index kontainer tujuan (bisa "new" untuk kontainer baru)
        """
        new_state = self.copy()
        
        # Hapus item dari kontainer asal
        new_state.containers[from_idx].remove(item_id)
        
        # Handle kontainer baru
        if to_idx == -1 or to_idx >= len(new_state.containers):
            new_state.containers.append([item_id])
        else:
            new_state.containers[to_idx].append(item_id)
        
        # Bersihkan kontainer kosong
        new_state.containers = [c for c in new_state.containers if len(c) > 0]
        
        return new_state
    
    def swap_items(self, item1_id: str, container1_idx: int, 
                   item2_id: str, container2_idx: int) -> 'State':
        """
        Tukar dua barang dari dua kontainer berbeda.
        Return state baru.
        """
        new_state = self.copy()
        
        # Hapus kedua item
        new_state.containers[container1_idx].remove(item1_id)
        new_state.containers[container2_idx].remove(item2_id)
        
        # Tukar posisi
        new_state.containers[container1_idx].append(item2_id)
        new_state.containers[container2_idx].append(item1_id)
        
        # Bersihkan kontainer kosong
        new_state.containers = [c for c in new_state.containers if len(c) > 0]
        
        return new_state
    
    def copy(self) -> 'State':
        """Deep copy state"""
        return State(
            items=self.items.copy(),
            capacity=self.capacity,
            containers=copy.deepcopy(self.containers)
        )
    
    def __str__(self) -> str:
        """String representation untuk debugging"""
        result = f"State dengan {self.num_containers()} kontainer:\n"
        for i, container in enumerate(self.containers):
            if len(container) > 0:
                load = self.get_container_load(i)
                items_str = ", ".join([f"{item}({self.items[item]})" for item in container])
                result += f"  Kontainer {i+1} ({load}/{self.capacity}): {items_str}\n"
        return result
    
    def to_dict(self) -> dict:
        """Konversi ke dictionary untuk output JSON"""
        return {
            "num_containers": self.num_containers(),
            "containers": [
                {
                    "id": i + 1,
                    "items": container,
                    "load": self.get_container_load(i),
                    "capacity": self.capacity
                }
                for i, container in enumerate(self.containers) if len(container) > 0
            ]
        }