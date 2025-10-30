import random
import time
from typing import Optional
from algorithms.base_algorithm import BaseLocalSearchAlgorithm
from core.state import State
from core.objective_function import ObjectiveFunction
from core.initializer import BinPackingInitializer


class GeneticAlgorithm(BaseLocalSearchAlgorithm):
    def __init__(self, initial_state, objective_function, items, capacity, mutation_probability=0.5, population_size=50, max_iterations=1000):
        super().__init__(initial_state, objective_function)
        self.items = items
        self.capacity = capacity
        self.population = []
        self.mutation_probability = mutation_probability
        self.population_size = population_size
        self.max_iterations = max_iterations

    def get_name(self):
        return "Genetic"


    def get_result_dict(self):
        stats = super().get_statistics()
        result = super().get_result_dict()
        result['ga_metrics'] = {
            "population_size": self.population_size,
            "mutation_probability": self.mutation_probability,
            "max_iterations": self.max_iterations,
            "generations_data": self.generations_data,
            "mutation_rate": self.mutation_probability,
            "population_size" : self.population_size

        }
        result["_final_state_object"] = self.best_state
        return result

    def initialize_population(self):
        self.population.append(self.initial_state)
        for i in range(self.population_size-1):
            initial_state_choice = random.randint(1,2)
            if initial_state_choice == 1:
                state = BinPackingInitializer.best_fit(self.items, self.capacity)
            elif initial_state_choice == 2:
                state = BinPackingInitializer.greedy_fit(self.items, self.capacity)
                
            # if initial_state_choice == 1:
            #     state = BinPackingInitializer.best_fit(self.items, self.capacity)
            # elif initial_state_choice == 2:
            #     state = BinPackingInitializer.first_fit(self.items, self.capacity)
            # elif initial_state_choice == 3:
            #     state = BinPackingInitializer.worst_fit(self.items, self.capacity)
            # elif initial_state_choice == 4:
            #     state = BinPackingInitializer.next_fit(self.items, self.capacity)
            # elif initial_state_choice == 5:
            #     state = BinPackingInitializer.random_fit(self.items, self.capacity, seed=i)
            # elif initial_state_choice == 6:
            #     state = BinPackingInitializer.greedy_fit(self.items, self.capacity)

            self.population.append(state)


    def fitness_function(self):
        fitness_list = []
        for state in self.population:
            fitness_score = self.objective_function.calculate(state)
            fitness_list.append(fitness_score)
        return fitness_list

    def tournament_selection(self, fitness_list, k=5):
        selected_list = []
        parents = []

        for i in range(k):
            random_number = random.randint(0,len(fitness_list)-1)
            selected_list.append((fitness_list[random_number], random_number))

        sorted_selected = sorted(selected_list, key=lambda x: x[0], reverse=True) # cari parent dgn fitness paling max

        parents.append(self.population[sorted_selected[0][1]])
        parents.append(self.population[sorted_selected[1][1]])


        return parents

    def crossover(self, parents):
        parent_1 = parents[0]
        parent_2 = parents[1]
        # Step 1: Gabungkan semua item dari kedua parent
        items_in_p1 = [item for container in parent_1.containers for item in container]
        items_in_p2 = [item for container in parent_2.containers for item in container]
        combined_items = list(dict.fromkeys(items_in_p1 + items_in_p2))  # urut, unik

        items_1 = combined_items[:]
        random.shuffle(items_1)
        containers_1 = []
        for item in items_1:
            placed = False
            for container in containers_1:
                current_load = sum(self.items[i] for i in container)
                if current_load + self.items[item] <= self.capacity:
                    container.append(item)
                    placed = True
                    break
            if not placed:
                containers_1.append([item])
        child_1 = State(self.items, self.capacity, containers_1)
        
        items_2 = combined_items[:]
        random.shuffle(items_2)
        containers_2 = []
        for item in items_2:
            placed = False
            for container in containers_2:
                current_load = sum(self.items[i] for i in container)
                if current_load + self.items[item] <= self.capacity:
                    container.append(item)
                    placed = True
                    break
            if not placed:
                containers_2.append([item])
        child_2 = State(self.items, self.capacity, containers_2)

        return [child_1, child_2]
        
    def mutation(self, child):
        new_state = child.copy()
        containers = new_state.containers

        if random.random() < self.mutation_probability:
            if len(containers) < 2:
                return new_state
            
            random_index = random.randint(0, len(containers) - 1)
            if len(containers[random_index]) == 0:
                return new_state

            choice = random.randint(1, 2)

            if choice == 1:
                # Pindahkan 1 item ke container lain yang cukup kapasitasnya
                move = random.randint(0, len(containers[random_index]) - 1)
                selected_item = containers[random_index][move]
                item_weight = self.items[selected_item]

                # Cari semua container yang cukup kapasitasnya (kecuali asal)
                valid_targets = []
                for i, c in enumerate(containers):
                    if i == random_index:
                        continue
                    current_load = sum(self.items[it] for it in c)
                    if current_load + item_weight <= self.capacity:
                        valid_targets.append(i)

                # Jika ada container yang cukup, pilih salah satu
                if valid_targets:
                    random_container = random.choice(valid_targets)
                else:
                    # Kalau tidak ada yang cukup, buat container baru
                    containers.append([])
                    random_container = len(containers) - 1

                # Pindah item
                containers[random_index].remove(selected_item)
                containers[random_container].append(selected_item)

            elif choice == 2:
                # Bongkar seluruh container dan tempatkan item ke container valid
                saved_container = containers[random_index][:]
                del containers[random_index]
                for item in saved_container:
                    item_weight = self.items[item]
                    # Cari container yang cukup kapasitasnya
                    valid_targets = []
                    for i, c in enumerate(containers):
                        current_load = sum(self.items[it] for it in c)
                        if current_load + item_weight <= self.capacity:
                            valid_targets.append(i)
                    if valid_targets:
                        move = random.choice(valid_targets)
                    else:
                        # Kalau tidak ada yang cukup, buat container baru
                        containers.append([])
                        move = len(containers) - 1
                    containers[move].append(item)

            # Bersihkan container kosong
            containers = [c for c in containers if len(c) > 0]
            new_state = State(self.items, self.capacity, containers)
        return new_state

    def get_best_solution(self):

        fitness_list = self.fitness_function()
        best_idx = min(range(len(fitness_list)), key=lambda i: fitness_list[i])
        return self.population[best_idx]

    def solve(self):
        import time
        start_time = time.perf_counter()
        self.initialize_population()
        fitness_list = self.fitness_function()

        self.generations_data = []
        self.global_best_value = float('inf')
        self.global_best_state = None

        for gen in range(self.max_iterations):
            parents = self.tournament_selection(fitness_list=fitness_list)
            children = self.crossover(parents=parents)

            for i in range(len(children)):
                children[i] = self.mutation(children[i])

            self.population = children
            children_fitness = self.fitness_function()
            fitness_list = children_fitness

            best_fitness = min(fitness_list)
            avg_fitness = sum(fitness_list) / len(fitness_list) if fitness_list else 0

            # Cari solusi terbaik di generasi ini
            best_idx = fitness_list.index(best_fitness)
            best_state_now = self.population[best_idx]

            # Jika ada solusi lebih baik dari global best, update
            if best_fitness < self.global_best_value:
                self.global_best_value = best_fitness
                self.global_best_state = best_state_now.copy()  # copy biar ga keubah

            # Simpan data generasi untuk visualisasi
            self.generations_data.append({
                'generation': gen + 1,  # Generasi mulai dari 1
                'best_fitness': best_fitness,
                'avg_fitness': avg_fitness
            })

            self.history.append(best_fitness)
            self.iteration_count += 1

        end_time = time.perf_counter()
        # Gunakan solusi terbaik global!
        self.best_state = self.global_best_state
        self.best_value = self.global_best_value
        self.duration = end_time - start_time

        # (Opsional) Jika ingin tetap cek dibanding initial_value:
        initial_value = self.objective_function.calculate(self.initial_state)
        if self.best_value > initial_value:
            self.best_state = self.initial_state
            self.best_value = initial_value

        return self.best_state, self.duration
    
    
# def run_genetic_demo():
#     # Setup problem
#     items = {
#         "BRG001": 40, "BRG002": 55, "BRG003": 25,
#         "BRG004": 60, "BRG005": 30, "BRG006": 45, "BRG007": 50
#     }
#     capacity = 100

#     # Initial state bisa dipilih bebas (tidak akan digunakan langsung oleh Genetic, hanya untuk base)
#     initial_state = BinPackingInitializer.best_fit(items, capacity)
#     obj_func = ObjectiveFunction()
    
#     print("="*60)
#     print("DEMO GENETIC ALGORITHM")
#     print("="*60)
#     ga = GeneticAlgorithm(
#         initial_state=initial_state,
#         objective_function=obj_func,
#         items=items,
#         capacity=capacity,
#         mutation_probability=0.2,
#         population_size=30,
#         max_iterations=100
#     )
#     best_state, exec_time = ga.solve()

#     print(f"Initial State:\n{initial_state}")
#     print("\nHASIL AKHIR GENETIC ALGORITHM")
#     print("-"*60)
#     print(f"Best State (container configuration):\n{best_state}")
#     print(f"Objective value: {obj_func.calculate(best_state)}")
#     print(f"Execution time: {exec_time:.4f} seconds")
#     # Tambahkan statistik lain jika ada
#     # Contoh: jumlah container, sisa kapasitas, dsb

# if __name__ == "__main__":
#     run_genetic_demo()