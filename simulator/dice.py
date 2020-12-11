import random

class Die:
    SIDES = [0,0,0,0,1,2]

    def roll(self):
        return random.choice(self.SIDES)

class DicePool:

    def __init__(self, count):
        self.count = count

    def roll(self):
        die = Die()
        return sum([ die.roll() for i in range(self.count)])