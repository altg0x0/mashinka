import math
import random
import socket
import struct
import sys
import time
import build.protocol_pb2 as protocol

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 8100)
sock.connect(server_address)

def tuple_substract(a, b):
    return tuple(x1 - x2 for x1, x2 in zip(a, b))

class ScoreCounter():
    DEFAULT_POS = (277, 603)  # default position of the car
    frames = 0
    center = (309, 377) 
    internal_score = 0
    prev_angle = None

    @classmethod
    def get_angle(cls, pos):
        dx, dy = tuple_substract(pos, cls.center)
        return math.atan2(dy, dx)
    
    @classmethod
    def get_default_angle(cls):
        return cls.get_angle(cls.DEFAULT_POS)
    
    def update(self, newPos):
        self.frames += 1
        new_angle = self.get_angle(newPos)
        angle_delta = - new_angle + (self.prev_angle or self.get_default_angle())
        self.internal_score += angle_delta if angle_delta > -math.pi else angle_delta + 2 * math.pi  # todo make more elegant

    def get_score(self):
        return 1e6 * self.internal_score / (1e6 + math.log(min(2, self.frames)))


def send_message(sock, message):
    data = message.SerializeToString()
    length = struct.pack('I', len(data))
    sock.sendall(length + data)


def receive_message(sock, message_type):
    length_data = sock.recv(4)
    length, = struct.unpack('I', length_data)
    data = sock.recv(length)
    message = message_type()
    message.ParseFromString(data)
    return message

from pygame.locals import *
from map_reader import read_chains
line_strings = read_chains("../map.txt")

def send_and_receive(sock, steer, frame_time=0):
    wrapper_message = protocol.ClientToServerMessage()
    wrapper_message.frame_command.steer = steer
    wrapper_message.frame_command.t = frame_time
    send_message(sock, wrapper_message)
    msg = receive_message(sock, protocol.ServerToClientMessage)
    # if msg.response.dead and random.randint(0, 10) == 2:
    #     print("deadge")
    # if random.randint(0, 5) == 2:
    #     print(msg.response.lidar_distances[0])
    return (msg.response.car_x, msg.response.car_y, msg.response.car_angle)

import pygame
def create_rotated_rect(center, angle, width, height):
    rect = pygame.Rect(0, 0, width, height)
    rotated_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    rotated_surface.fill((255, 50, 0))
    rotated_rect = rect.copy()
    rotated_rect.center = center
    rotated_surface = pygame.transform.rotate(rotated_surface, -angle * 180 / math.pi)
    return rotated_surface, rotated_rect

def draw_rotated_rect(surface, center, size, angle):
    rect = pygame.Surface(size, pygame.SRCALPHA)
    rect.fill((255, 200, 0))
    rotated_rect = pygame.transform.rotate(rect, -angle * 180 / math.pi)
    rect_center = (center[0] - rotated_rect.get_width() // 2, center[1] - rotated_rect.get_height() // 2)
    surface.blit(rotated_rect, rect_center)
    return pygame.Rect(rect_center, rotated_rect.get_size())


def game(sock):
    import sys

    pygame.init()

    WIDTH, HEIGHT = 700, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mashinka client")

    clock = pygame.time.Clock()

    rectangle = pygame.Rect(200, 200, 100, 50)
    angle = 0
    
    pos = send_and_receive(sock, 0, 0)
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
        pos = send_and_receive(sock, steer, dt / 1000)
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
    wrapper_message = protocol.ClientToServerMessage()
    game(sock)
finally:
    # close the socket
    sock.close()
