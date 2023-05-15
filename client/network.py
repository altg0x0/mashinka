import struct
import build.protocol_pb2 as protocol


def send_message(sock, message):
    data = message.SerializeToString()
    length = struct.pack('I', len(data))
    sock.sendall(length + data)


def receive_message(sock, message_type, logger_buffer=None):
    length_data = sock.recv(4)
    length, = struct.unpack('I', length_data)
    data = sock.recv(length)
    message = message_type()
    message.ParseFromString(data)
    if logger_buffer:
        logger_buffer.write(length_data)
        logger_buffer.write(data)
        # print(1, len(logger_buffer.getvalue()))
    return message

def send_and_receive(sock, steer, frame_time=0, logger_buffer=None):
    wrapper_message = protocol.ClientToServerMessage()
    wrapper_message.frame_command.steer = steer
    wrapper_message.frame_command.t = frame_time
    send_message(sock, wrapper_message)
    msg = receive_message(sock, protocol.ServerToClientMessage, logger_buffer=logger_buffer)
    return msg.response

def send_and_receive_pos(sock, steer, frame_time=0):
    resp = send_and_receive(sock, steer, frame_time)
    return (resp.car_x, resp.car_y, resp.car_angle)


def reset_command(sock):
    msg = protocol.ClientToServerMessage()
    msg.reset.CopyFrom(protocol.Reset())
    send_message(sock, msg)
    return receive_message(sock, protocol.ServerToClientMessage).response
