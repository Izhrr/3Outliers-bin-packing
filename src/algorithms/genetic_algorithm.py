import random
import time
from typing import Optional
from src.algorithms.base_algorithm import BaseLocalSearchAlgorithm
from src.core.state import State
from src.core.objective_function import ObjectiveFunction
from src.core.initializer import BinPackingInitializer


class GeneticAlgorithm(BaseLocalSearchAlgorithm):
    def __init__(self, initial_state, objective_function, items, capacity, mutation_probability=0.5, population_size=50, max_iterations=1000,):
        super().__init__(initial_state, objective_function)
        self.items = items
        self.capacity = capacity
        self.population = []
        self.mutation_probability = mutation_probability
        self.population_size = population_size
        self.max_iterations = max_iterations

    def get_name(self):
        return "Genetic"

    def initialize_population(self):
        for i in range(self.population_size):
            initial_state_choice = random.randint(1,6)
            if initial_state_choice == 1:
                state = BinPackingInitializer.best_fit(self.items, self.capacity)
            elif initial_state_choice == 2:
                state = BinPackingInitializer.first_fit(self.items, self.capacity)
            elif initial_state_choice == 3:
                state = BinPackingInitializer.worst_fit(self.items, self.capacity)
            elif initial_state_choice == 4:
                state = BinPackingInitializer.next_fit(self.items, self.capacity)
            elif initial_state_choice == 5:
                state = BinPackingInitializer.random_fit(self.items, self.capacity, seed=i)
            elif initial_state_choice == 6:
                state = BinPackingInitializer.greedy_fit(self.items, self.capacity)

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
        if len(parent_1.containers) > len(parent_2.containers):
            size = len(parent_2.containers)
        else:
            size = len(parent_1.containers)
        if size < 2:
            return [parent_1.copy(), parent_2.copy()]
        
        random_cut = random.randint(1, size-1)

        containers_1 = parent_1.containers[:random_cut] + parent_2.containers[random_cut:]
        containers_2 = parent_2.containers[:random_cut] + parent_1.containers[random_cut:]
        child_1 = State(self.items, self.capacity, containers_1)
        child_2 = State(self.items, self.capacity, containers_2)

        return [child_1.copy(), child_2.copy()]
        
    def mutation(self, child):
        new_state = child.copy()
        containers = new_state.containers

        if random.random() < self.mutation_probability:
            choice = random.randint(1,2)
            random_index = random.randint(0,len(containers)-1)
            if len(containers) < 2:
                return new_state
            random_index = random.randint(0,len(containers)-1)
            if len(containers[random_index]) == 0:
                return new_state

            choice = random.randint(1,3)

            if choice == 1:
                move = random.randint(0,len(containers[random_index])-1)
                random_container = random.randint(0,len(containers)-1)
                while random_container == random_index:
                    random_container = random.randint(0,len(containers)-1)
                selected_item = containers[random_index][move]
                containers[random_index].remove(selected_item)
                containers[random_container].append(selected_item)

            elif choice == 2:
                saved_container = containers[random_index][:]
                del containers[random_index]
                for item in saved_container:
                    move = random.randint(0,len(containers)-1)
                    containers[move].append(item)

            elif choice == 3:
                move = random.randint(0, len(containers[random_index])-1)
                selected_item = containers[random_index][move]
                containers[random_index].remove(selected_item)
                containers.append([selected_item])

            containers = [c for c in containers if len(c) > 0]
            new_state = State(self.items, self.capacity, containers)
        return new_state

    def get_best_solution(self):

        fitness_list = self.fitness_function()
        best_idx = min(range(len(fitness_list)), key=lambda i: fitness_list[i])
        return self.population[best_idx]

    def solve(self):
        start_time = time.perf_counter()
        self.initialize_population()
        fitness_list = self.fitness_function()
        for _ in range(self.max_iterations):
            parents = self.tournament_selection(fitness_list=fitness_list)
            children = self.crossover(parents=parents)

            for i in range(len(children)):
                children[i] = self.mutation(children[i])

            self.population = children
            children_fitness = self.fitness_function()

            fitness_list = children_fitness
        end_time = time.perf_counter()
        return self.get_best_solution(), end_time - start_time
    
def run_genetic_demo():
    # Setup problem
    items = {
        "BRG001": 40, "BRG002": 55, "BRG003": 25,
        "BRG004": 60, "BRG005": 30, "BRG006": 45, "BRG007": 50
    }
    capacity = 100

    # Initial state bisa dipilih bebas (tidak akan digunakan langsung oleh Genetic, hanya untuk base)
    initial_state = BinPackingInitializer.best_fit(items, capacity)
    obj_func = ObjectiveFunction()
    
    print("="*60)
    print("DEMO GENETIC ALGORITHM")
    print("="*60)
    ga = GeneticAlgorithm(
        initial_state=initial_state,
        objective_function=obj_func,
        items=items,
        capacity=capacity,
        mutation_probability=0.2,
        population_size=30,
        max_iterations=100
    )
    best_state, exec_time = ga.solve()

    print("\nHASIL AKHIR GENETIC ALGORITHM")
    print("-"*60)
    print(f"Best State (container configuration):\n{best_state}")
    print(f"Objective value: {obj_func.calculate(best_state)}")
    print(f"Execution time: {exec_time:.4f} seconds")
    # Tambahkan statistik lain jika ada
    # Contoh: jumlah container, sisa kapasitas, dsb

if __name__ == "__main__":
    run_genetic_demo()