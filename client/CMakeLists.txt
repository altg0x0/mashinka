cmake_minimum_required(VERSION 3.18)
project(mashinka)

# Find the Python interpreter
find_package(Python3 3.11)

# Find the Protobuf compiler and libraries
find_package(Protobuf REQUIRED)

# Set the path to the protocol buffer file
set(PROTO_FILE "${CMAKE_CURRENT_SOURCE_DIR}/../protocol.proto")

# Generate the Python module from the protocol buffer file
protobuf_generate_python(PROTO_PYTHON_MODULE "${PROTO_FILE}")


# Set the sources for the Python executable
set(SOURCES main.py ${PROTO_PYTHON_MODULE})

# Add a custom target for the Python executable
add_custom_target(mashinka_client ALL
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/main.py
    SOURCES ${SOURCES}
)

# Add a dependency on the generated Python module
# add_dependencies(mashinka_client ${PROTO_PYTHON_MODULE})
