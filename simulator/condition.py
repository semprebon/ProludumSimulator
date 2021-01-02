from enum import Enum


def key(name, other):
    '''Returns an indentifer for the condition to differentiates it from others'''
    return name if other == None else f"{name}|{id(other)}"

class ConditionType(Enum):

    # condition severities
    FLEETING = 0        # lasts until end of actors next turn after it is triggeed
    RECOVERABLE = 1     # lasts until actor successfully makes a recovery action
    ENCOUNTER = 2       # lasts until the end of the encounter

    STAGGERED = (),     # Adds 1 to successes of a successful attack on the actor. Note that a successful
                        # attack on a staggard foe will increase a 1 success to a 2, resulting in a major
                        # effect
    HINDERED = (),      # adds disadvantage (1 less dice rolled) to actions by the actor. Subsequent HINDERED
                        # effect results in a wound.
    BLEEDING = (),      # Foe takes 1 wound if they make an attack
    DEFENDING = (FLEETING, True, True),     # Adds disadvantage to attacks against the actor by the target
    PREPARED_FOR = (FLEETING, True, True)   # Improves subsequent action against specific foe, depending on weapon
                        # On ranged attacks, prepared (i.e. aim) adds advantage, making succes more likely
                        # On melee attacks, prepared adds to success, making damage more likely for a successful attack

    def __init__(self, duration=RECOVERABLE, directed=False, beneficial=False):
        self.duration = duration
        self.directed = directed
        self.beneficial = beneficial

class Condition:
    def __init__(self, condition, other=None):
        if condition.directed and other == None:
            raise ValueError(f"Condition type {condition.name} requires a subject but none given")
        if not condition.directed and other != None:
            raise ValueError(f"Condition type {condition.name} prohibits a subject but given {other.name()}")

        self.condition = condition
        self.other = other

    def key(self):
        return key(self.condition.name, self.other)

    def as_dict(self):
        other = self.other.name() if self.other else None
        return { 'name': self.name, 'severity': self.severity, 'other': other }

    def __str__(self):
        return f"{self.condition.name} { f'>{self.other.name()}' if self.other else ''}"
