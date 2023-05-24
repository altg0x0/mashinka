import random
from multiprocessing import set_start_method

import pygad.gann
import numpy as np

import learner
from learner import play_game, build_inputs_arr
import build.protocol_pb2 as protocol

NUM_FORKS = 16
learner.VERY_GOOD_SCORE = 20


def fitness_function(ga, solution, sol_idx):
    def calc_steer(resp: protocol.ServerState):
        data_inputs = build_inputs_arr(resp)
        mat = np.matmul(np.transpose(np.atleast_2d(data_inputs)), np.atleast_2d(data_inputs))
        steer = (np.dot(mat.ravel(),  solution))
        return steer

    scorer = play_game(8100 + sol_idx % NUM_FORKS, calc_steer)
    sc = scorer.get_score()
    if random.randint(1, 100) == 1 or sc > 8:
        print(f"s={sc:.01f}", flush=True)
    return sc
if __name__ == "__main__":
    set_start_method('fork', force=True)
    ga_instance = pygad.GA(
        num_generations=5000,
        sol_per_pop=1024,
        fitness_func=fitness_function,
        mutation_percent_genes=30,
        num_parents_mating = 4,
        num_genes=289,
        # init_range_low=-1.,
        # init_range_high=1.,
        # parent_selection_type=parent_selection_type,
        # crossover_type=crossover_type,
        # mutation_type=mutation_type,
        keep_parents=2,
        parallel_processing=("process", NUM_FORKS),
    )
    ga_instance.run()