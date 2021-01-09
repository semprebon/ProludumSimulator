class FixedDicePool:

    roll_value = 0

    def __init__(self, count):
        self.count = count

    def roll(self):
        return self.roll_value

