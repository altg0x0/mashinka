import random
from multiprocessing import set_start_method

import pygad.gann
import numpy as np

import learner
from learner import play_game, build_inputs_arr
import build.protocol_pb2 as protocol

NUM_FORKS = 16
GANN_instance = None


def fitness_function(ga, solution, sol_idx):
    def calc_steer(resp: protocol.ServerState):
        data_inputs = build_inputs_arr(resp)
        predictions = pygad.nn.predict(
            problem_type="regression",
            last_layer=GANN_instance.population_networks[sol_idx],
            data_inputs=np.array([data_inputs])
        )
        steer = predictions[0][0] * 2 - 1
        return steer

    scorer = play_game(8100 + sol_idx % NUM_FORKS, calc_steer)
    sc = scorer.get_score()
    if random.randint(1, 50) == 1:
        print(f"s={sc:.02f}", flush=True)
    return sc


def callback_generation(ga_instance):        
    population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks,
                                                            population_vectors=ga_instance.population)

    GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)


if __name__ == "__main__":
    learner.VERY_GOOD_SCORE = 100
    set_start_method('fork', force=True)
    GANN_instance = pygad.gann.GANN(
        num_solutions=64,
        num_neurons_input=17,
        num_neurons_hidden_layers=[12, 6],
        num_neurons_output=1,
        hidden_activations=["sigmoid", "relu"],
        output_activation="sigmoid",
    )

    population_vectors = pygad.gann.population_as_vectors(population_networks=GANN_instance.population_networks)
    ga_instance = pygad.GA(
        num_generations=5000,
        initial_population=population_vectors.copy(),
        fitness_func=fitness_function,
        mutation_percent_genes=5,
        num_parents_mating = 4,
        # init_range_low=-1.,
        # init_range_high=1.,
        # parent_selection_type=parent_selection_type,
        # crossover_type=crossover_type,
        # mutation_type=mutation_type,
        keep_parents=2,
        on_generation=callback_generation,
        parallel_processing=("process", 16),
    )
    ga_instance.run()
