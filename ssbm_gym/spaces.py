from .ssbm import actionTypes
import random

class DiagonalActionSpace():
    def __init__(self):
        self.actions = [a[0].real_controller for a in actionTypes['diagonal'].actions]
        self.n = len(self.actions)

    def __repr__(self):
        return "Discrete(%d)" % self.n

    def sample(self):
        return random.choice(self.actions)

    def from_index(self, n):
        return self.actions[n]

