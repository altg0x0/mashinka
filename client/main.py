import random
import socket
import time
import sys

from score import ScoreCounter
from network import send_and_receive_pos, send_message
from map_reader import read_chains
from graphics import draw_rotated_rect
import build.protocol_pb2 as protocol

import pygame
from pygame.locals import *
line_strings = read_chains("../map.txt")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8100)
sock.connect(server_address)


def game(sock):
    pygame.init()

    WIDTH, HEIGHT = 700, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mashinka client")

    clock = pygame.time.Clock()    
    pos = send_and_receive_pos(sock, 0, 0)
    score_counter = ScoreCounter()
    while True:
        dt = clock.tick(120)  # ms since last frame
        screen.fill((0, 0, 0))
        draw_rotated_rect(screen, pos[:2], (30, 10), pos[2])
        
        for ls in line_strings:
            pygame.draw.lines(screen, (0, 255, 0), False, ls, 2)

        steer = 0
        keys = pygame.key.get_pressed()
        if keys[K_a]:
            steer = -1
        if keys[K_d]:
            steer = 1
        if keys[K_r]:
            msg = protocol.ClientToServerMessage()
            msg.reset.CopyFrom(protocol.Reset())
            send_message(sock, msg)
            time.sleep(0.2)
        pos = send_and_receive_pos(sock, steer, dt / 1000)
        score_counter.update(pos[:2])
        if random.randint(0, 10) == 2:
            print(score_counter.get_score())

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = event.pos
                    print("Screen coordinates of user click: ({}, {})".format(x, y))

try:
    game(sock)
finally:
    sock.close()
