import ast
import random

from deap.gp import PrimitiveSet
from deap import creator
from deap import base
from deap import tools
from deap import algorithms

from simulator.decision_tree import DecisionTree


class DecisionTreeGeneticAlgorithm:

    def __init__(self, actor):
        self.actor = actor
        self.attributes = actor.extract_situation(actor).keys
        self.actions = actor.data['acts']
        with open("../data/situations.dat", "w") as f:
            self.situations = [ ast.literal.eval(line) for line in f.readlines() ]

    def is_leaf(self, node_tag):
        return node_tag in self.actions

    def decode(self, individual):
        node_idx = 0
        node_tag = individual[node_idx]
        if self.is_leaf(node_tag):
            return DecisionTree.build_leaf(node_tag)
        else:
            return DecisionTree.build(node_tag,
                                      self.decode(individual, 2*node_idx),
                                      self.decode(individual, 2*node_idx+1))


    def random_tree(self, attributes):
        random.shuffle(attributes)
        subnodes = random.randrange(0,3) if len(attributes) > 1 else 0
        if subnodes == 0:
            random.shuffle(self.actions)
            return { 'tag': attributes[0], True: self.actions[0], False: self.actions[1] }
        elif subnodes == 1:
            return { 'tag': attributes[0], True: self.actions[0], False: self.random_tree(attributes[1:]) }
        elif subnodes == 2:
            return { 'tag': attributes[0], False: self.actions[0], True: self.random_tree(attributes[1:]) }
        elif subnodes == 3:
            return { 'tag': attributes[0], False: self.random_tree(attributes[1:]), True: self.random_tree(attributes[1:]) }

    def generate(self):
        tree = self.random_tree(self.attributes)
        pset = PrimitiveSet("decide", 2)
        for attr in self.attributes:
            pset.addPrimitive(attr, 2)


    class PickBranchByIndex:
        def __init__(self, index):
            self.count = 0
            self.index = index

        def visit(self, branch):
            if self.count == self.index:
                self.branch = branch
            self.count = self.count + 1

    def pick_branch(self, tree):
        index = random.randint(0, tree.branch_count-1)
        picker = DecisionTreeEvolver.PickBranchByIndex(index)
        tree.traverse(picker, None)
        return picker.branch

    def mutate(self, tree):
        branch = self.pick_branch(tree)

        return


    def cross_over(self, tree1, tree2):
        return self

    def fitness(self, decision_tree):
        pass

    def if_condition(self, cond):
        return lambda list, s1, s2: s1 if list[cond] else s2

    def optimize_decision_tree(self):


        # Define fitness function
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))

        # Define individual
        pset = PrimitiveSet("main", 4*[bool])
        pset.addPrimitive(self.if_condition("staggered"), [dict, str, str], str)
        pset.addPrimitive(self.if_condition("multiple_attackers"), [dict, str, str], str)
        pset.addPrimitive(self.if_condition("attack_advantage"), [dict, str, str], str)
        for a in self.actions:
            pset.addTerminal(a, str)

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
