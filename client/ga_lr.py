from functools import wraps
import io
import math
import random
import socket
import time
import sys
from multiprocessing import set_start_method
import traceback

from score import ScoreCounter
from network import send_and_receive, send_message, receive_message, reset_command
from map_reader import read_chains
import build.protocol_pb2 as protocol

import pygad.gann
import numpy as np

line_strings = read_chains("../map.txt")

GANN_instance = None
set_start_method('fork', force=True)
def fitness_function(ga, solution, sol_idx):
    buffer = io.BytesIO()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 8100 + sol_idx % 16)
    sock.connect(server_address)
    resp = reset_command(sock)
    scorer = ScoreCounter()
    while True:
        normalized_lidar = [x / 300 - 0.05 for x in resp.lidar_distances]
        data_inputs=np.array(normalized_lidar + [
            resp.velocity / 100, 
            resp.car_x / 700, 
            resp.car_y / 700,
            (resp.car_angle % (2 * math.pi)) / (2 * math.pi), 
            1
        ]),
        steer = np.sum(solution * data_inputs)
        sc = scorer.get_score()
        if sc > 10 and scorer.frames % 60 == 0:
            print(f"VERY GOOD! score={sc:.01f}", flush=True)
            print(solution, flush=True)
            with open(f"sol_{sol_idx}.bin", "wb") as f:
                f.write(buffer.getvalue())
        if resp.dead:
            if sc > 8e9 or random.randint(0, 50) == 1:
                print(f"s={sc:.02f}", flush=True)
            return scorer.get_score()
        resp = send_and_receive(sock, steer, 1/60, logger_buffer=buffer)
        pos = (resp.car_x, resp.car_y, resp.car_angle)
        scorer.update(pos)


def game():
    ga_instance = pygad.GA(
        num_generations=5000,
        sol_per_pop=128,
        fitness_func=fitness_function,
        mutation_percent_genes=30,
        num_parents_mating = 4,
        num_genes=17,
        # init_range_low=-1.,
        # init_range_high=1.,
        # parent_selection_type=parent_selection_type,
        # crossover_type=crossover_type,
        # mutation_type=mutation_type,
        keep_parents=2,
        parallel_processing=("process", 16),
    )
    ga_instance.run()

game()