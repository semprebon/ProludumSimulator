# Use genetic algorithm to develop an effective decision tree for a character
#
# TODO: Use multiple scenarios

import argparse

from simulator.data_loader import load_data
from training.evolve_tactics import ActorTacticsEvolver

parser = argparse.ArgumentParser()
parser.add_argument("--iterations", "-i", default="1", help="number of iterations", type=int)
parser.add_argument("--gauntlet", "-g", default="gauntlet", help="guantlet file", type=str)
parser.add_argument("--hero", "-z", default="Brutus", help="hero name", type=str)
parser.add_argument("--scenarios", "-s", help="scenario files", nargs="*")

args = parser.parse_args()
iterations = args.iterations

if args.scenarios:
     scenario_files = load_data(args.scenarios, directory="data/scenarios")
else:
    scenario_files = load_data(args.gauntlet, directory="data/scenarios")[0]
subject = args.hero
evolver = ActorTacticsEvolver(subject, scenario_files)
hof = evolver.run()
print("winning tactics are:\n" + '\n'.join([ f"{t.fitness} {t}" for t in hof ]))
