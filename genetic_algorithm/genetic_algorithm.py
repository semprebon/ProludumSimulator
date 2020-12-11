import random

from deap import base


class GeneticAlgorithm:

    def __init__(self, generator, mixer, mutator, fitness):
        self.generator = generator
        self.mixer = mixer
        self.mutator = mutator
        self.fitness = fitness

    def sort_by_fitness(self, population):
        sorted_pairs = [ (self.fitness(gene), gene) for gene in population ]
        sorted_pairs.sort(reverse=True, key=lambda p: p[0])
        return sorted_pairs

    def breed(self, population):
        return self.mutator(self.mixer(random.choice(population), random.choice(population)))

    def crossbreed(self, breeders, size):
        return [ self.breed(breeders) for i in range(size)  ]

    def optimize(self, size, max_iterations=1000, breeder_ratio=0.5):
        toolbox = base.toolbox()
        pop = toolbox.population(n=size)
        for g in range(max_iterations):
            # Select the next generation individuals
            offspring = toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = map(toolbox.clone, offspring)

            # Apply crossover on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.1:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation on the offspring
            for mutant in offspring:
                if random.random() < 0.05:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # The population is entirely replaced by the offspring
            pop[:] = offspring


