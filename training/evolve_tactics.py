import random

import numpy
from deap import creator, gp
from deap import base
from deap import tools
from deap import algorithms

# This is a subclass of Actor that allows the decisions of the actor to be
# made by an evolved tactics function
from simulator.decision_state import DecisionState
from simulator.simulator import Simulator

class EvolvingDecisionState(DecisionState):
    def __init__(self, individual, pset, *args):
        super().__init__(*args)
        self.individual = individual
        self.tactics_code = gp.compile(individual, pset)

    def return_evaluator(self):
        return self.evaluate_tactics

    def execute_action(self):
        success = self.tactics_code()
        return (str(self.individual), success)

class EvolverSimulator(Simulator):
    """This is a version of Simulator that gets sets the decision state tactics for the
        actor being evolved to the evolving tactic"""

    def __init__(self, actor_name, individual, pset, *args):
        super().__init__(*args)
        self.actor_name = actor_name
        self.actor = next(a for a in self.combatants if a.name() == actor_name )
        self.individual = individual
        self.pset = pset

    def decision_state_for(self, combatant):
        if combatant.data['name'] == self.actor_name:
            decision_state = EvolvingDecisionState(self.individual, self.pset, combatant)
        else:
            decision_state = DecisionState(combatant)
        return decision_state

class ActorTacticsEvolver:

    def __init__(self, actor_name, scenarios, iterations=100):
        self.actor_name = actor_name
        self.scenarios = scenarios
        self.iterations = iterations

    def evaluate(self, individual):
        wins = 0.0
        rounds = 0.0
        wounds = 0.0
        for i in range(self.iterations):
            scenario = random.choice(self.scenarios)
            simulator = EvolverSimulator(self.actor_name, individual, self.pset, scenario)

            simulator.run_until_done()
            if len(simulator.foes_of(simulator.actor)) == 0:
                wins = wins + 1
            rounds = rounds + simulator.round
            wounds = wounds + simulator.actor.data['level'] - simulator.actor.health
        result = wins / self.iterations, rounds / self.iterations
        return result

    def actor(self):
        simulator = Simulator(scenario=self.scenarios[0])
        return simulator.combatant_by_name(self.actor_name)

    def setup(self, toolbox):
        # Define fitness function
        creator.create("FitnessMax", base.Fitness, weights=(1.0,-1.0/6.0))

        # Define individual
        decision_state = DecisionState(self.actor())
        self.pset = gp.PrimitiveSet("MAIN", 0)
        for observation in decision_state.observations():
            self.pset.addPrimitive(observation, 2)
        for name, action in decision_state.actions().items():
            self.pset.addTerminal(action, name=name)

        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax, pset=self.pset)
        IND_SIZE = 2
        toolbox.register("attr_float", lambda: random.uniform(-4.0, 4.0))

        # Attribute generator
        toolbox.register("expr_init", gp.genFull, pset=self.pset, min_=1, max_=2)

        toolbox.register("Individual", tools.initIterate, creator.Individual,
                         toolbox.expr_init)

        # define population
        toolbox.register("population", tools.initRepeat, list, toolbox.Individual)

        # define evolution
        toolbox.register("evaluate", self.evaluate)
        toolbox.register("select", tools.selTournament, tournsize=7)
        toolbox.register("mate", gp.cxOnePoint)
        toolbox.register("expr_mut", gp.genFull, min_=0, max_=1, pset=self.pset)
        toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=self.pset)

    def run(self):
        toolbox = base.Toolbox()
        self.setup(toolbox)
        pop = toolbox.population(n=100)
        hof = tools.HallOfFame(5)

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        algorithms.eaSimple(pop, toolbox, 0.5, 0.2, 50, stats, halloffame=hof)
        return hof
