# create a simulator and run it

import argparse
import glob
import os

from simulator.data_loader import load_data, clear_data_cache
from simulator.simulator import Simulator
import logging
import tkinter as tk

logging.basicConfig(filename="simulation.log", level=logging.INFO)
parser = argparse.ArgumentParser()
parser.add_argument("--iterations", "-i", default="1", help="number of iterations", type=int)
parser.add_argument("--scenario", "-s", default="brutus_vs_goblins", help="scenario file", type=str)
parser.add_argument("--log", "-L", help="log options: action", type=str)

args = parser.parse_args()
iterations = args.iterations

log_options = args.log.split(',') if args.log else []

def run_simulation(actor, scenario):
    clear_data_cache()
    wins = 0.0
    rounds = 0.0
    for i in range(iterations):
        data = load_data(scenario, directory="data/scenarios")[0]
        idx = data['heroes'].index(actor)
        data['heroes'][idx] = actor
        simulator = Simulator(data, options={ f"log_{s}": True for s in log_options })

        simulator.run_until_done()
        if simulator.winner() == "heroes":
            wins = wins + 1.0
        rounds = rounds + simulator.round
    print(f"Success Rate: {wins/iterations}")
    print(f"Mean duration: {rounds/iterations}")
    print(f"Mean turns: {rounds*len(simulator.combatants)/iterations}")
    for a in simulator.combatants:
        averages = { label: a.average(label) for label in a.averages.keys() }
        print(f"{a.name()}: {averages}")

    print(30*"-")

def update_replacement(optionList, optionVar, scenario):
    optionList['menu'].delete(0, 'end')
    replacables = load_data(scenario, directory="data/scenarios")[0]['heroes']
    for s in replacables:
        optionList['menu'].add_command(label=s, command=tk._setit(optionVar, s))
    optionVar.set(replacables[0])


def form(root, actors, scenarios):
    tk.Label(root, text="New Actor").grid(row=0, column=0)
    actorVar = tk.StringVar(root)
    actorVar.set('Brutus')
    tk.OptionMenu(root, actorVar, *actors).grid(row=0, column=1)

    tk.Label(root, text="Secnario").grid(row=1, column=0)
    scenarioVar = tk.StringVar(root)
    scenarioVar.set(scenarios[0])
    tk.OptionMenu(root, scenarioVar, *scenarios).grid(row=1, column=1)

    tk.Label(root, text="Replaced Actor").grid(row=2, column=0)
    replacedVar = tk.StringVar(root)
    replacables = load_data(scenarioVar.get(), directory="data/scenarios")[0]['heroes']
    replacedVar.set(replacables[0])
    replaceOptionList = tk.OptionMenu(root, replacedVar, *replacables)
    replaceOptionList.grid(row=2, column=1)

    scenarioVar.trace('w', lambda *args: update_replacement(replaceOptionList, replacedVar, scenarioVar.get()))

    run = lambda a=actorVar, s=scenarioVar: run_simulation(a.get(), s.get())
    tk.Button(root, text='Quit', command=root.quit).grid(row=3, column=0, sticky=tk.E, pady=4)
    tk.Button(root, text='Run', command=run).grid(row=3, column=1, sticky=tk.W, pady=4)

def load_names(dir):
    return [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(dir + "/*.yaml")]

if __name__ == '__main__':
    root = tk.Tk()
    actors = load_names("data/actors")
    scenarios = load_names("data/scenarios")
    form(root, actors, scenarios)
    tk.mainloop()
