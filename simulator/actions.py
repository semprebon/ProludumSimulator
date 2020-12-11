# Condition Severities
from simulator.conditions import Condition


class Fleeting:
    severity = 0

    def __init__(self, name):
        self.name = name

    def recovered(self, target):
        return True

# Various attack actions
def by_name(name):
    from importlib import import_module
    import sys
    module = sys.modules[__name__]
    return getattr(module, name)
    # print(f"class is {Attack.__file__}")
    # return Attack

class Action:
    def __init__(self, actor):
        self.actor = actor
        from simulator.dice import DicePool
        self.roll = DicePool(self.actor.health).roll()

    def difficulty(self):
        return 0

    def successes(self):
        return True

class Attack(Action):
    def __init__(self, actor, target):
        self.target = target
        self.actor = actor
        from simulator.dice import DicePool
        self.roll = DicePool(self.actor.health).roll()

    def difficulty(self):
        result = self.target.defense()
        if self.actor.has_condition("hindered"):
            result = result + 1
        if self.target.has_condition("defending against", self.actor):
            result = result + 1
        return result

    def successes(self):
        return self.roll - self.difficulty()

    def wound_target(self, wounds):
        if self.roll == 1:
            self.target.add_condition(Condition("staggered"))
            print(f"{self.target.name()} is staggered")
        elif self.roll > 1:
            self.target.takes_damage(self.roll-1)
            print(f"{self.target.name()} takes {self.roll-1} damage")
        else:
            print(f"{self.actor.name()} misses")

class Wait(Action):
    def __init__(self, actor, target=None):
        self.actor = actor

    def resolve(selfs):
        pass

    def describe(self):
        return f"{self.actor.name()} waits"


# Basic attack:
#   * 1 wound for every 2 successes
#   * staggerd for 1 success
class BasicAttack(Attack):
    def __init__(self, actor, target):
        super().__init__(actor, target)

    def resolve(self):
        if self.roll > 0:
            if self.successes() >= 1:
                self.wound_target(self.successes()/2)
                if self.successes() % 2 == 1:
                    self.target.add_condition(Condition("staggered"))

    def describe(self):
        return f"{self.actor.name()} Attacks {self.target.name()}, rolling {self.roll} vs {self.difficulty()} for {self.successes()} successes"

# Defensive attack
#   * 1 success increases target's difficulty of attacking actor by 1
#   * every 2 successes after inflicts a wound
class DefensiveAttack(Attack):
    def __init__(self, actor, target):
        super().__init__(actor, target)

    def resolve(self):
        if self.roll > 0:
            if self.successes() >= 0:
                self.target.add_condition(Condition("hindered", Condition.FLEETING, self.actor))
                self.wound_target((self.successes()-1)/2)

    def describe(self):
        return f"{self.actor.name()} defensively Attacks {self.target.name()}, rolling {self.roll} vs {self.difficulty()} for {self.successes()} successes"

# Defend
#   * 1 success increases actor's difficulty of being attacked by 1
#   * every 2 successes after increases the difficulty by 1
class Defend(Attack):
    def __init__(self, actor, target):
        super().__init__(actor, target)

    def resolve(self):
        if self.roll > 0:
            if self.successes() >= 0:
                self.actor.add_condition(Condition("defending", Condition.FLEETING, self.target))
                self.wound_target((self.successes()-1)/2)
                if self.successes() % 2 == 1:
                    self.target.add_condition(Condition("staggered"))

    def describe(self):
        return f"{self.actor.name()} defensively Aatacks {self.target.name()}, rolling {self.roll} vs {self.difficulty()} for {self.successes()} successes"

# Remove condition
class RemoveCondition():
    def __init__(self, actor, target=None):
        self.actor = actor
        self.target = target

    def resolve(self):
        if self.roll > 0:
            if self.successes() >= 0:
                self.actor.add_condition(Condition("defending", Condition.FLEETING, self.target))
                self.wound_target((self.successes()-1)/2)
                if self.successes() % 2 == 1:
                    self.target.add_condition(Condition("staggered"))

    def describe(self):
        return f"{self.actor.name()} removes conditions (Not implemented)"

# Light attack
#   * 1 wound for every 2 successes
#   * hindered for 1 success
class LightAttack(Attack):
    def __init__(self, actor, target):
        super().__init__(actor, target)

    def resolve(self):
        if self.roll > 0:
            if self.successes() >= 1:
                self.wound_target(self.successes()/2)
                if self.successes() % 2 == 1:
                    self.target.add_condition(Condition("hindered"))

    def describe(self):
       return f"{self.actor.name()} Attacks {self.target.name()}, rolling {self.roll} vs {self.difficulty()} for {self.successes()} successes"
