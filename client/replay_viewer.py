import os
import random
import struct
import time
import sys

from score import ScoreCounter
from map_reader import read_chains
from graphics import draw_rotated_rect
import build.protocol_pb2 as protocol

import pygame
from pygame.locals import *
line_strings = read_chains("../map.txt")


def game():
    pygame.init()
    WIDTH, HEIGHT = 700, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mashinka replay")

    clock = pygame.time.Clock()
    with open("sol_55.bin", "rb") as f:  # FIXME hahahahaha
        total_size = os.path.getsize(f.name)

        while True:
            dt = clock.tick(60)  # ms since last frame
            size_bytes = f.read(4)
            if not size_bytes:
                break
            message_size = struct.unpack('I', size_bytes)[0]
            message_data = f.read(message_size)

            initial_position = f.tell()
            percentage = (initial_position / total_size) * 100
            print(f"Percentage: {percentage:.2f}%")
            print("\033[F", end="")  # ANSI escape sequence for moving the cursor up one line

            msg = protocol.ServerToClientMessage()
            msg.ParseFromString(message_data)
            resp = msg.response
            pos = (resp.car_x, resp.car_y, resp.car_angle)
        
            screen.fill((0, 0, 0))
            draw_rotated_rect(screen, pos[:2], (30, 10), pos[2])
            for ls in line_strings:
                pygame.draw.lines(screen, (0, 255, 0), False, ls, 2)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
game()