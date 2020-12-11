from simulator.text import bcolors
from simulator.actor import Actor

class Simulator:

    def __init__(self, heroes, villains):
        self.combatants = [ Actor(c, "heroes") for c in heroes ] + [ Actor(c, "villains") for c in villains ]
        self.round = 0

    def run_turn(self, combatant):
        print(combatant.describe())
        if combatant.health <= 0:
            print(f"{combatant.name()} is dead")
            self.combatants.remove(combatant)
        else:
            combatant.take_turn(self.combatants)

    def run_round(self):
        for c in self.combatants:
            self.run_turn(c)

    def factions(self):
        factions = {}
        for actor in self.combatants:
            factions[actor.faction] = factions.get(actor, []).append(actor)
        return factions

    def winner(self):
        return list(self.factions())[0] if len(self.factions()) == 1 else None

    def run_until_done(self):
        max_rounds = 20
        while self.winner() == None and self.round < max_rounds:
            self.round = self.round + 1
            print(f"{bcolors.BOLD}Round {self.round}{bcolors.ENDC}")
            self.run_round()
