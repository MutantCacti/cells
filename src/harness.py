"""
src/harness.py
The outer loop and evolutionary structure for cells.

Created: 2026-05-02
 Author: Maxence Morel Dierckx
"""
import sys
import time
from cells import Graph, DATA_WIDTH
from cellinput import CellInput, KeyInput
from evolver import Sample, Evolver


from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"


class Harness:
    def __init__(self, graph: Graph, evolver: Evolver, cell_input: CellInput, output_index: int, log_name: str, sample_rate: int):
        self.tick = 0
        self.graph = graph
        self.evolver = evolver
        self.input = cell_input
        self.output_index = output_index
        self.log_name = log_name
        self.sample_rate = sample_rate


    # Override
    def log(self) -> str:
        raise NotImplementedError


    # Override
    def current_error(self) -> float:
        raise NotImplementedError


    # Override
    def window_error(self, sample: 'Sample') -> float:
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
                self.evolver.update(self)
                self.graph.update()
                runtime = time.perf_counter() - start
                time.sleep(max(1 / self.sample_rate - runtime, 0))
        finally:
            self.shutdown()
            sys.stdout.write('\033[?1049l')
            print(last)




class SwitchHarness(Harness):
    def __init__(self, graph: Graph, evolver: Evolver, cell_input: CellInput, output_index: int, log_name: str, sample_rate: int):
        super().__init__(graph, evolver, cell_input, output_index, log_name, sample_rate)
        LOGS.mkdir(parents=True, exist_ok=True)
        log_path = LOGS / f"{log_name}.csv"
        self.log_file = open(log_path, 'w') # Closed in shutdown
        self.log_file.write("tick,input,output,error\n")


    def graph_switched(self) -> bool:
        return self.graph.cells[self.output_index].value >= 0


    def current_error(self) -> float:
        real_switch = self.input.read()
        pred_switch = -1 if self.graph_switched() else 0 # Mirrors cellinput:KeyInput:read()
        return abs(pred_switch - real_switch)


    def window_error(self, sample: 'Sample') -> float:
        return self.current_error() - sample.error


    def log(self) -> str:
        pred_on = self.graph_switched()
        rendered_text = self.render_text(pred_on)

        tick_input = self.input.read()
        self.log_file.write(','.join([
            str(self.tick),
            str(tick_input),
            '1' if pred_on else '0',
            '1' if tick_input == pred_on else '0'
        ]) + '\n')

        return rendered_text


    def render_text(self, pred_on) -> str:
        table = '\n'.join(
            ''.join(
                '█' if cell.value & (1 << b) else '░' for b in range(DATA_WIDTH - 1, -1, -1)
            )
            for cell in self.graph.cells
        ) + '\n\n\n'
        switch = '█' * DATA_WIDTH if pred_on else '░' * DATA_WIDTH
        error_state = str(self.evolver.count)
        key_space = f'\n{' ' * (DATA_WIDTH - 1)}' # space for terminal-rendered key press character

        output = table + switch + error_state + key_space
        sys.stdout.write('\033[H' + output)
        sys.stdout.flush()

        return output


    def shutdown(self):
        self.log_file.close()
