class Node:

    def __init__(self, state, parent=None, action=None, g=0, h=0):

        self.state = state
        self.parent = parent
        self.action = action

        self.g = g
        self.h = h

    @property
    def f(self):
        return self.g + self.h