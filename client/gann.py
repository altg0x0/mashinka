import math
import random
import socket
import time
import sys
import numpy as np

from score import ScoreCounter
from network import send_and_receive, send_message, receive_message, reset_command
from map_reader import read_chains
from graphics import draw_rotated_rect
import build.protocol_pb2 as protocol

import pygame
import pygad.gann

line_strings = read_chains("../map.txt")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("localhost", 8100)
sock.connect(server_address)


def exit_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


def game(sock):
    pygame.init()
    WIDTH, HEIGHT = 700, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mashinka gann client")
    GANN_instance = pygad.gann.GANN(
        num_solutions=500,
        num_neurons_input=17,
        num_neurons_hidden_layers=[12],
        num_neurons_output=1,
        hidden_activations=["sigmoid"],
        output_activation="sigmoid",
    )

    def draw_pos(pos):
        screen.fill((0, 0, 0))
        draw_rotated_rect(screen, pos[:2], (30, 10), pos[2])
        for ls in line_strings:
            pygame.draw.lines(screen, (0, 255, 0), False, ls, 2)
        pygame.display.flip()

    def callback_generation(ga_instance):        
        population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks,
                                                                population_vectors=ga_instance.population)

        GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)

    def fitness_function(ga, solution, sol_idx):
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
                if sc > 7 or random.randint(0, 10) == 1:
                    print(sc)
                return scorer.get_score()
            resp = send_and_receive(sock, predictions[0][0] * 2 - 1, 1/60)
            if random.randint(0, 10000) == 1: 
                print(predictions)
            pos = (resp.car_x, resp.car_y, resp.car_angle)
            if sol_idx == 100 or sc > 100:
                draw_pos(pos)
            scorer.update(pos)
            exit_events()
            if sc > 100:
                time.sleep(0.005)
    population_vectors = pygad.gann.population_as_vectors(population_networks=GANN_instance.population_networks)
    ga_instance = pygad.GA(
        num_generations=5000,
        initial_population=population_vectors.copy(),
        fitness_func=fitness_function,
        mutation_percent_genes=2,
        num_parents_mating = 4,
        # init_range_low=-1.,
        # init_range_high=1.,
        # parent_selection_type=parent_selection_type,
        # crossover_type=crossover_type,
        # mutation_type=mutation_type,
        keep_parents=2,
        on_generation=callback_generation
    )
    ga_instance.run()

try:
    game(sock)
finally:
    sock.close()
