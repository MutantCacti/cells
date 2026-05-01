"""
src/single_cell_input.py
Input to a space via a specific cell index.

Created: 2025-06-01
 Author: Maxence Morel Dierckx
"""
from space import Space


from pynput import keyboard


class SingleCellInput:
    def __init__(self, space: Space, cell_index: int):
        self.space = space
        self.cell_index = cell_index


    def __repr__(self):
        return self.space.cells[self.cell_index].value


    # Override
    def read(self) -> int:
        raise NotImplementedError


    def write(self):
        self.space.cells[self.cell_index].value = self.read()




class KeyInput(SingleCellInput):
    def __init__(self, space, cell_index):
        super().__init__(space, cell_index)
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
