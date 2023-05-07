#include <iostream>
#include <boost/asio.hpp>
#include <protocol.pb.h>

#include "car.hpp"
#include "server.hpp"

using boost::asio::ip::tcp;

using namespace server_client_protocol;

namespace Server {

  static Car car;
  static MultiChain track;

  void constructResponse(ClientToServerMessage& request, ServerToClientMessage& response) {
    switch (request.message_case()) {
      case ClientToServerMessage::kFrameCommand: {
        auto command = request.frame_command();
        car.frame(command.t(), command.steer());
        response.mutable_response()->set_car_x(car.pos.x());
        response.mutable_response()->set_car_y(car.pos.y());
        response.mutable_response()->set_car_angle(car.angle);
        response.mutable_response()->set_dead(car.isCrashed(track));
        auto lidarDistances = car.getLidarDistances(track);
        *response.mutable_response()->mutable_lidar_distances() = {lidarDistances.begin(), lidarDistances.end()};
        break;
      }
      case ClientToServerMessage::kReset: {
        Server::car = Car(277, 603, 3.1);
        break;
      }
      default: break;
    }
  }

  void process_messages(tcp::socket& socket) {
    while (true) {
      uint32_t message_size = 0;
      boost::asio::read(socket, boost::asio::buffer(&message_size, sizeof(message_size)));
      std::vector<char> message_buffer(message_size);
      boost::asio::read(socket, boost::asio::buffer(message_buffer));

      ClientToServerMessage request;
      if (request.ParseFromArray(message_buffer.data(), message_size)) {
        ServerToClientMessage response;
        constructResponse(request, response);
        std::vector<char> response_buffer(response.ByteSizeLong());
        response.SerializeToArray(response_buffer.data(), response_buffer.size());

        // Write the response message size (uint32_t) to the socket
        uint32_t response_size = response_buffer.size();
        boost::asio::write(socket, boost::asio::buffer(&response_size, sizeof(response_size)));
        boost::asio::write(socket, boost::asio::buffer(response_buffer));
      } else {
        std::cerr << "Failed to parse incoming message" << std::endl;
      }
    }
  }
}

void serve(int port) {
  GOOGLE_PROTOBUF_VERIFY_VERSION;
  Server::car = Car(277, 603, 1.2);
  boost::asio::io_context io_context;
  tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), port));
  std::cerr << "Serving at " << port << "\n";
  while (true) {
    try {
      tcp::socket socket(io_context);
      acceptor.accept(socket);
      Server::process_messages(socket);
    }
    catch (boost::system::system_error er) {
      std::cerr << "Error: " << er.what() << "\n";
      continue;
    }
  }
}

void setTrack(MultiChain& track) {
  Server::track = track;
}
