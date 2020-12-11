import math
import random
import unittest

from genetic_algorithm.genetic_algorithm import GeneticAlgorithm


class GeneticAlgorithmTest(unittest.TestCase):

    def limit(self, x, low=-4.0, high=4.0):
        return max(min(x, high), low)

    def evaluate_fitness(self, individual):
        x, y = (individual[0], individual[1])
        return (math.sin(math.sqrt( x**2 + y**2)),)

    def mutate(self, individual):
        from deap import base
        constrain = lambda x: max(min(x, 4.0), x, -4.0)
        toolbox = base.Toolbox()
        mutant = toolbox.clone(individual)
        mutant[0] = constrain(mutant[0] + random.uniform(-0.05, 0.05))
        mutant[1] = constrain(mutant[1] + random.uniform(-0.05, 0.05))
        #del mutant.fitness.values
        return mutant

    def test_find_value(self):
        from deap import creator
        from deap import base
        from deap import tools
        from deap import algorithms

        # Define fitness function
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))

        # Define individual
        creator.create("Individual", list, fitness=creator.FitnessMax)
        IND_SIZE = 2
        toolbox = base.Toolbox()
        toolbox.register("attr_float", lambda: random.uniform(-4.0, 4.0))
        toolbox.register("Individual", tools.initRepeat, creator.Individual,
                         toolbox.attr_float, n=IND_SIZE)

        # define population
        toolbox.register("population", tools.initRepeat, list, toolbox.Individual)

        # define evolution
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", self.mutate)
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("evaluate", self.evaluate_fitness)

        # run ga
        pop = toolbox.population(n=10)
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        algorithms.eaSimple(pop, toolbox, 0.5, 0.2, 100)

        # find fittest
        max_fitness = max([ i.fitness.values[0] for i in pop ])
        self.assertAlmostEqual(1.0, max_fitness, 4, "should be close to the same")

if __name__ == '__main__':
    unittest.main()
