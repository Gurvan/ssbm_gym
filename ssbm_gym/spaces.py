from .ssbm import actionTypes
from .ssbm import SimpleController
import random
from itertools import product
from enum import IntEnum

class MinimalButton(IntEnum):
    NONE = 0
    A = 1
    Y = 4

class MinimalActionSpace():
    def __init__(self):
        self.controller = self.make_controller(3, 1, MinimalButton)
        self.actions = [a.real_controller for a in self.controller]
        self.n = len(self.controller)

    def __repr__(self):
        return "Discrete(%d)" % self.n

    def sample(self):
        return random.choice(self.actions)

    def from_index(self, n):
        return self.actions[n]

    def make_controller(self, x_dim, y_dim, buttons):
        if x_dim == 1:
            x_axis = [0.5]
        else:
            x_axis = [i/(x_dim-1) for i in range(x_dim)]
        if y_dim == 1:
            y_axis = [0.5]
        else:
            y_axis = [i/(y_dim-1) for i in range(y_dim)]
        stick = list(product(x_axis, y_axis))
        controller = [SimpleController.init(*args) for args in product(buttons, stick)]

        return controller




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

