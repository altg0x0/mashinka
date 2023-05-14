from functools import wraps
import math
import random
import socket
import time
import sys
from multiprocessing import Process, Lock, Queue, current_process, set_start_method
import traceback

from score import ScoreCounter
from network import send_and_receive, send_message, receive_message, reset_command
from map_reader import read_chains
# from graphics import draw_rotated_rect
import build.protocol_pb2 as protocol

# import pygame
import pygad.gann
import numpy as np

line_strings = read_chains("../map.txt")

GANN_instance = None
set_start_method('fork', force=True)
# if __name__ == "__main__":
#     lock = Lock()
#     queue = Queue()
#     socks = []
#     for i in range(1):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         socks.append(sock)
#         server_address = ("localhost", 8100 + i)
#         sock.connect(server_address)

# def process_socket(fn):
#     @wraps(fn)
#     def wrapper(a1, a2, a3, **kwargs):
#         lock.acquire()
#         try:
#             sock = queue.get()
#         except Exception as ex:  # Debug stuff, that sould not be like that
#             traceback.print_exc()
#             lock.release()
#             return None
#         print(f"Process {current_process().pid} acquired socket {sock}")
#         lock.release()
#         result = fn(sock, a1, a2, a3, **kwargs)
#         lock.acquire()
#         queue.put(sock)
#         lock.release()
#         return result
#     return wrapper

# def exit_events():
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()

# @process_socket
# def fitness_function(sock, ga, solution, sol_idx):
def fitness_function(ga, solution, sol_idx):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 8100 + sol_idx % 16)
    sock.connect(server_address)
    resp = reset_command(sock)
    scorer = ScoreCounter()
    while True:
        normalized_lidar = [x / 300 - 0.05 for x in resp.lidar_distances]
        predictions = pygad.nn.predict(
            problem_type="regression",
            last_layer=GANN_instance.population_networks[sol_idx],
            data_inputs=np.array([np.array(normalized_lidar + [
                resp.velocity / 100, 
                resp.car_x / 700, 
                resp.car_y / 700,
                (resp.car_angle % (2 * math.pi)) / (2 * math.pi), 
                1
                ])]),
        )
        sc = scorer.get_score()
        if resp.dead:
            if sc > 8e9 or random.randint(0, 50) == 1:
                print(sc, flush=True)
            # time.sleep(0.01)
            return scorer.get_score()
        resp = send_and_receive(sock, predictions[0][0] * 2 - 1, 1/60)
        pos = (resp.car_x, resp.car_y, resp.car_angle)
        # if sol_idx == 1000 or sc > 100:
        #     draw_pos(pos)
        scorer.update(pos)
        # exit_events()
        if sc > 100:
            time.sleep(0.005)

def callback_generation(ga_instance):        
    population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks,
                                                            population_vectors=ga_instance.population)

    GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)

def game():
    global GANN_instance
    # pygame.init()
    # WIDTH, HEIGHT = 700, 700
    # screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # pygame.display.set_caption("Mashinka gann client")
    GANN_instance = pygad.gann.GANN(
        num_solutions=96,
        num_neurons_input=17,
        num_neurons_hidden_layers=[12, 6],
        num_neurons_output=1,
        hidden_activations=["sigmoid", "relu"],
        output_activation="sigmoid",
    )

    # def draw_pos(pos):
    #     screen.fill((0, 0, 0))
    #     draw_rotated_rect(screen, pos[:2], (30, 10), pos[2])
    #     for ls in line_strings:
    #         pygame.draw.lines(screen, (0, 255, 0), False, ls, 2)
    #     pygame.display.flip()
    
    # for sock in socks:
    #     queue.put(sock)
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

if __name__ == "__main__":
    try:
        game()
    finally:
        pass
        # for sock in socks:
        #     sock.close()
