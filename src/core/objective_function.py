"""
objective_function.py - Fungsi Objektif untuk Bin Packing Problem

Tujuan: MINIMISASI jumlah kontainer dengan memaksimalkan kepadatan
Constraint: Tidak boleh ada kontainer yang overload (sangat diprioritaskan)
"""

class ObjectiveFunction:
    """
    Fungsi objektif untuk evaluasi state dalam Bin Packing Problem.
    
    Komponen:
    1. Penalty overload (sangat besar) - mencegah solusi tidak valid
    2. Jumlah kontainer (prioritas utama) - meminimalkan kontainer
    3. Bonus kepadatan (prioritas sekunder) - memaksimalkan utilisasi
    
    Catatan: Karena menggunakan MINIMISASI, nilai lebih kecil = lebih baik
    """
    
    def __init__(self, 
                 penalty_overload_weight: float = 10000.0,
                 container_count_weight: float = 100.0,
                 density_bonus_weight: float = -10.0):
        """
        Args:
            penalty_overload_weight: Bobot penalty untuk overload (BESAR)
            container_count_weight: Bobot untuk jumlah kontainer
            density_bonus_weight: Bobot untuk bonus kepadatan (negatif = bonus)
        
        Rasionalisasi bobot:
        - penalty_overload_weight = 10000: Memastikan solusi tidak valid SELALU
          lebih buruk dari solusi valid. Dengan kapasitas 100 dan overload 
          maksimal ~100, penalty bisa mencapai 10000 × 100 = 1,000,000.
          
        - container_count_weight = 100: Mengurangi 1 kontainer memberikan 
          improvement sebesar 100 poin. Ini lebih besar dari density bonus
          maksimal (sekitar 10-20 poin), sehingga prioritas tetap mengurangi
          kontainer, bukan hanya meningkatkan kepadatan.
          
        - density_bonus_weight = -10: Bonus untuk kepadatan. Negatif karena
          kita minimisasi (semakin padat = nilai lebih kecil = lebih baik).
          Dengan weight 10, kontainer dengan density 0.9 vs 0.5 berbeda
          sekitar 4 poin. Cukup untuk membedakan, tapi tidak mengalahkan
          pengurangan kontainer.
        """
        self.penalty_overload_weight = penalty_overload_weight
        self.container_count_weight = container_count_weight
        self.density_bonus_weight = density_bonus_weight
    
    def calculate(self, state) -> float:
        """
        Hitung nilai objektif dari sebuah state.
        Nilai lebih kecil = lebih baik (minimisasi).
        
        Returns:
            float: Nilai objektif
        """
        penalty_overload = self._calculate_overload_penalty(state)
        container_count = state.num_containers()
        density_score = self._calculate_density_score(state)
        
        # Formula final: minimisasi
        objective_value = (
            penalty_overload * self.penalty_overload_weight +
            container_count * self.container_count_weight +
            density_score * self.density_bonus_weight
        )
        
        return objective_value
    
    def _calculate_overload_penalty(self, state) -> float:
        """
        Hitung total penalty untuk kontainer yang overload.
        
        Penalty dihitung sebagai kuadrat dari jumlah kelebihan kapasitas.
        Kuadrat digunakan agar pelanggaran besar jauh lebih buruk.
        
        Contoh:
        - Overload 10: penalty = 10² = 100
        - Overload 50: penalty = 50² = 2500 (jauh lebih buruk!)
        """
        total_penalty = 0.0
        for i in range(len(state.containers)):
            load = state.get_container_load(i)
            if load > state.capacity:
                overload = load - state.capacity
                total_penalty += overload ** 2
        return total_penalty
    
    def _calculate_density_score(self, state) -> float:
        """
        Hitung skor kepadatan total dari semua kontainer.
        
        Density = total_ukuran / kapasitas (0.0 - 1.0)
        Semakin tinggi density, semakin baik.
        
        Kita mengembalikan NEGATIF dari sum densities karena menggunakan
        minimisasi (density tinggi = nilai negatif besar = objective kecil).
        """
        total_density = 0.0
        for i in range(len(state.containers)):
            if len(state.containers[i]) > 0:
                density = state.get_container_load(i) / state.capacity
                # Bisa gunakan density biasa atau density kuadrat untuk
                # memberikan bonus lebih besar pada kontainer yang sangat padat
                total_density += density ** 2  # Lebih agresif
        
        # Return negatif (untuk bonus saat minimisasi)
        return -total_density
    
    def get_components(self, state) -> dict:
        """
        Return breakdown komponen objektif function untuk analisis.
        Berguna untuk debugging dan memahami kenapa suatu state lebih baik.
        """
        penalty = self._calculate_overload_penalty(state)
        num_containers = state.num_containers()
        density = -self._calculate_density_score(state)  # Kembalikan ke positif
        
        return {
            "penalty_overload": penalty,
            "penalty_overload_weighted": penalty * self.penalty_overload_weight,
            "num_containers": num_containers,
            "num_containers_weighted": num_containers * self.container_count_weight,
            "density_score": density,
            "density_score_weighted": -density * self.density_bonus_weight,
            "total": self.calculate(state),
            "is_valid": state.is_valid()
        }
    
    def __str__(self) -> str:
        """String representation untuk debugging"""
        return (f"ObjectiveFunction("
                f"penalty={self.penalty_overload_weight}, "
                f"container={self.container_count_weight}, "
                f"density={self.density_bonus_weight})")


# Demo dan testing
def demo_objective_function():
    """Demo penggunaan ObjectiveFunction"""
    # Import di sini untuk avoid circular import
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    from core.state import State
    from core.initializer import BinPackingInitializer
    
    # Setup sample data
    items = {
        "BRG001": 40,
        "BRG002": 55,
        "BRG003": 25,
        "BRG004": 60,
        "BRG005": 30
    }
    capacity = 100
    
    print("=" * 70)
    print("DEMO OBJECTIVE FUNCTION")
    print("=" * 70)
    
    # Buat state dengan Best Fit
    state = BinPackingInitializer.best_fit(items, capacity)
    
    print("\n--- State ---")
    print(state)
    
    # Hitung objective
    obj_func = ObjectiveFunction()
    objective_value = obj_func.calculate(state)
    
    print("\n--- Objective Function ---")
    print(f"Total Objective Value: {objective_value:.2f}")
    
    # Get components
    components = obj_func.get_components(state)
    print("\n--- Components Breakdown ---")
    print(f"Penalty Overload       : {components['penalty_overload']:.2f} × {obj_func.penalty_overload_weight} = {components['penalty_overload_weighted']:.2f}")
    print(f"Num Containers         : {components['num_containers']} × {obj_func.container_count_weight} = {components['num_containers_weighted']:.2f}")
    print(f"Density Score          : {components['density_score']:.4f} × {obj_func.density_bonus_weight} = {components['density_score_weighted']:.2f}")
    print(f"Total                  : {components['total']:.2f}")
    print(f"Is Valid               : {components['is_valid']}")
    
    # Test dengan state invalid (overload)
    print("\n" + "=" * 70)
    print("TEST WITH INVALID STATE (Overload)")
    print("=" * 70)
    
    # Buat state yang overload
    invalid_containers = [
        ["BRG001", "BRG002", "BRG004"],  # 40 + 55 + 60 = 155 > 100 (OVERLOAD!)
        ["BRG003", "BRG005"]              # 25 + 30 = 55 (OK)
    ]
    invalid_state = State(items, capacity, invalid_containers)
    
    print("\n--- Invalid State ---")
    print(invalid_state)
    
    invalid_objective = obj_func.calculate(invalid_state)
    invalid_components = obj_func.get_components(invalid_state)
    
    print("\n--- Objective Function (Invalid State) ---")
    print(f"Total Objective Value: {invalid_objective:.2f}")
    print(f"Penalty Overload      : {invalid_components['penalty_overload_weighted']:.2f} (HUGE!)")
    print(f"Is Valid              : {invalid_components['is_valid']}")
    
    print("\n" + "=" * 70)
    print(f"PERBANDINGAN:")
    print(f"Valid State   : {objective_value:.2f}")
    print(f"Invalid State : {invalid_objective:.2f}")
    print(f"Difference    : {invalid_objective - objective_value:.2f}")
    print("Invalid state jauh lebih buruk karena penalty overload!")
    print("=" * 70)


if __name__ == "__main__":
    demo_objective_function()