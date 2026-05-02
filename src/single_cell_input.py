"""
src/single_cell_input.py
Input to a graph via a specific cell index.

Created: 2025-06-01
 Author: Maxence Morel Dierckx
"""
from cells import Graph


from pynput import keyboard


class SingleCellInput:
    def __init__(self, graph: Graph, cell_index: int):
        self.graph = graph
        self.cell_index = cell_index


    def __repr__(self):
        return self.graph.cells[self.cell_index].value


    # Override
    def read(self) -> int:
        raise NotImplementedError


    def write(self):
        self.graph.cells[self.cell_index].value = self.read()




class KeyInput(SingleCellInput):
    def __init__(self, graph, cell_index):
        super().__init__(graph, cell_index)
        self.pressed = False
        self.listener = keyboard.Listener(
            on_press=self.on_key_down,
            on_release=self.on_key_up
        )
        self.listener.start()


    def on_key_down(self):
        self.pressed = True


    def on_key_up(self):
        self.pressed = False


    def read(self) -> int:
        return -1 if self.pressed else 0
