from simulator.actor import Actor
from simulator.data_loader import load_data
from simulator.decision_state import DecisionState
from simulator.text import bcolors

def dict_differences(before, after):
    keys = set(before.keys()) | set(after.keys())
    diff = {}
    for key in keys:
        b = before.get(key, None)
        a = after.get(key, None)
        if b != a:
            diff[key] = (b, a)
    return diff

def format_difference(name, diffs):
    return f"{name}({','.join([f'{k}:{v[0]}→{v[1]}' for k, v in diffs.items()])})"

class Simulator:
    # TODO: move character substituion code to here
    def __init__(self, scenario, options={}):
        self.name_counters = {}
        self.scenario = load_data(scenario, directory="data/scenarios")[0] if isinstance(scenario, str) else scenario
        heroes = [self.instantiate_actor(c, "heroes") for c in self.scenario['heroes']]
        villains = [self.instantiate_actor(c, "villains") for c in self.scenario['villains']]
        self.combatants = heroes + villains

        self.round = 0
        self.options = options

    def instantiate_actor(self, data, faction):
        if isinstance(data, str):
            data = load_data(data, directory="data/actors")[0]
        actor = Actor(data.copy(), faction, self)
        name = actor.name()
        count = self.name_counters.get(name, 1)
        if count > 1:
            actor.suffix_name(count)
        self.name_counters[name] = count + 1
        return actor

    def decision_state_for(self, combatant):
        return DecisionState(combatant)

    def run_turn(self, combatant):
        if combatant.health <= 0:
            #print(f"{combatant.name()} is dead")
            self.combatants.remove(combatant)
        else:
            state = self.decision_state_for(combatant)
            state.take_turn()

    def run_round(self):
        for c in self.combatants:
            self.run_turn(c)

    def factions(self):
        factions = {}
        for actor in self.combatants:
            factions[actor.faction] = factions.get(actor, []).append(actor)
        return factions

    def foes_of(self, actor):
        return [ a for a in self.combatants if a.faction != actor.faction and a.health > 0 ]

    def combatant_by_name(self, name):
        return next(a for a in self.combatants if a.name() == name)

    def faction_position(self, faction):
        return self.scenario.get('positions', {}).get(faction, 0)

    def winner(self):
        return list(self.factions())[0] if len(self.factions()) == 1 else None

    def snapshot_state(self):
        return { a.name(): a.extract_data_hash() for a in self.combatants }

    def determine_state_change(self, before, after):
        diffs = { name: dict_differences(before[name], after[name]) for name in before.keys() }
        diffs = { name: diff for name, diff in diffs.items() if len(diff) != 0 }
        return ' '.join([format_difference(k, v) for k, v in diffs.items()])

    def run_until_done(self):
        max_rounds = 20
        while self.winner() == None and self.round < max_rounds:
            self.round = self.round + 1
            #print(f"{bcolors.BOLD}Round {self.round}{bcolors.ENDC}")
            self.run_round()
