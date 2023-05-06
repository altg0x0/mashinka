# Please don't copy that, it's really bad
cmake_minimum_required(VERSION 3.18)

project(mashinka)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Boost REQUIRED COMPONENTS program_options)
INCLUDE_DIRECTORIES( ${Boost_INCLUDE_DIR} )

include(FindProtobuf)
find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIR})

get_filename_component(VAR_PARENT .. ABSOLUTE)
PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS "${VAR_PARENT}/protocol.proto")
get_filename_component(PROTO_HEADERS_DIR ${PROTO_HDRS}/.. ABSOLUTE)
include_directories(${PROTO_HEADERS_DIR})


add_executable(mashinka main.cpp ${PROTO_SRCS} ${PROTO_HDRS} map_reader.cpp map_reader.hpp car.hpp car.cpp server.hpp server.cpp)

target_link_libraries(mashinka Boost::program_options ${PROTOBUF_LIBRARY})
