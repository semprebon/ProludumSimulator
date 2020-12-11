# create a simulator and run it
import argparse

from simulator.data_loader import load_data
from simulator.simulator import Simulator
import logging

logging.basicConfig(filename="simulation.log", level=logging.INFO)
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

wins = 0.0
rounds = 0.0
for i in range(iterations):
    simulator = Simulator(heroes, villains)
    simulator.run_until_done()
    print(f"winner is {simulator.winner()}")
    if simulator.winner() == "heroes":
        wins = wins + 1.0
    rounds = rounds + simulator.round
print(f"Success Rate: {wins/iterations}")
print(f"Mean duration: {rounds/iterations}")
print(f"Mean turns: {rounds*(len(heroes)+len(villains))/iterations}")
