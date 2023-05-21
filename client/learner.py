import io
import math
import socket
from typing import Callable

import numpy as np

from build.protocol_pb2 import ServerState
from network import send_and_receive, reset_command
from score import ScoreCounter

VERY_GOOD_SCORE = 25
SERVER = 'localhost'
DT = 1/60

def build_inputs_arr(resp: ServerState):
    normalized_lidar = [x / 300 - 0.05 for x in resp.lidar_distances]
    data_inputs=np.array(normalized_lidar + [
        resp.velocity / 100, 
        resp.car_x / 700, 
        resp.car_y / 700,
        (resp.car_angle % (2 * math.pi)) / (2 * math.pi), 
        1
    ])
    return data_inputs


def play_game(port: int, 
              calculate_steer: Callable[[ServerState], float],
              replay_name=''):
    buffer = io.BytesIO()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SERVER, port)
    sock.connect(server_address)
    resp = reset_command(sock)
    scorer = ScoreCounter()
    while True:
        sc = scorer.get_score()
        if replay_name and sc > VERY_GOOD_SCORE and scorer.frames % 60 == 0:
            print(f"VERY GOOD! score={sc:.01f}", flush=True)
            with open(replay_name, "wb") as f:
                f.write(buffer.getvalue())
        if resp.dead:
            return scorer
        steer = calculate_steer(resp)
        resp = send_and_receive(sock, steer, DT, logger_buffer=buffer)
        pos = (resp.car_x, resp.car_y, resp.car_angle)
        scorer.update(pos)
