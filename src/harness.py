"""
src/harness.py
The outer loop and evolutionary structure for cells.

Created: 2026-05-02
 Author: Maxence Morel Dierckx
"""
import sys
import time
from cells import Graph, DATA_WIDTH
from cell_input import CellInput, KeyInput


from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"


class Harness:
    def __init__(self, graph: Graph, cell_input: CellInput, output_index: int, log_name: str, sample_rate: int):
        self.tick = 0
        self.graph = graph
        self.input = cell_input
        self.output_index = output_index
        self.log_name = log_name
        self.sample_rate = sample_rate


    # Override
    def log(self) -> str:
        raise NotImplementedError


    # Override
    def mutate(self):
        raise NotImplementedError


    # Override
    def shutdown(self):
        raise NotImplementedError


    def run(self):
        last = ""
        sys.stdout.write('\033[?1049h') # alternate screen buffer
        try:
            while True:
                self.tick += 1
                start = time.perf_counter()
                self.input.write()
                last = self.log()
                self.mutate()
                self.graph.update()
                runtime = time.perf_counter() - start
                time.sleep(max(1 / self.sample_rate - runtime, 0))
        finally:
            self.shutdown()
            sys.stdout.write('\033[?1049l')
            print(last)




class SwitchHarness(Harness):
    def __init__(self, graph: Graph, cell_input: CellInput, output_index: int, log_name: str, sample_rate: int):
        super().__init__(graph, cell_input, output_index, log_name, sample_rate)
        LOGS.mkdir(parents=True, exist_ok=True)
        log_path = LOGS / f"{log_name}.csv"
        self.log_file = open(log_path, 'w') # Closed in shutdown
        self.log_file.write("tick,input,output,error\n")


    def log(self) -> str:
        switched_on = self.graph.cells[self.output_index].value >= 0
        rendered_text = self.render_text(switched_on)

        tick_input = self.input.read()
        self.log_file.write(','.join([
            str(self.tick),
            str(tick_input),
            '1' if switched_on else '0',
            '1' if tick_input == switched_on else '0'
        ]) + '\n')

        return rendered_text


    def render_text(self, switched_on) -> str:
        table = '\n'.join(
            ''.join(
                '█' if cell.value & (1 << b) else '░' for b in range(DATA_WIDTH - 1, -1, -1)
            )
            for cell in self.graph.cells
        ) + '\n\n\n'
        switch = '█' * DATA_WIDTH if switched_on else '░' * DATA_WIDTH
        key_space = f'\n{' ' * (DATA_WIDTH - 1)}' # space for terminal-rendered key press character

        output = table + switch + key_space
        sys.stdout.write('\033[H' + output)
        sys.stdout.flush()

        return output


    def mutate(self):
        pass


    def shutdown(self):
        self.log_file.close()
