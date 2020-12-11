import argparse
import random

from genetic_algorithm.genetic_algorithm import GeneticAlgorithm
from simulator.data_loader import load_data
from simulator.simulator import Simulator

parser = argparse.ArgumentParser()
parser.add_argument("--iterations", "-i", default="1", help="number of iterations", type=int)
parser.add_argument("--scenario", "-s", help="scenario file", type=str)
parser.add_argument("--goodguys", "-g", help="hero files", nargs="*")
parser.add_argument("--badguys", "-b", help="villain files", nargs="*")

args = parser.parse_args()
iterations = args.iterations

if args.scenario:
    scenario = load_data(args.scenario, directory="data/scenarios")[0]
    heroes = load_data(scenario["heroes"], directory="data/actors")
    villains = load_data(scenario["villains"], directory="data/actors")
else:
    heroes = load_data(args.goodguys, directory="data/actors")
    villains = load_data(args.badguys, directory="data/actors")

ga = GeneticAlgorithm(
    generator=lambda: (random.uniform(min_value, max_value), random.uniform(min_value, max_value)),
    mixer=lambda p1, p2: ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2),
    mutator=lambda p: (self.limit(p[0] + random.uniform(-0.05, 0.05)),
                       self.limit(p[1] + random.uniform(-0.05, 0.05))),
    fitness=fitness

)
