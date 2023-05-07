#include <iostream>
#include <fstream>
#include <boost/program_options.hpp>

#include "map_reader.hpp"
#include "server.hpp"
#include "car.hpp"

struct Args {
    int num_forks;
    int port_range_start;
};

void start_function(const Args& args) {
    auto track = read_chains("../../map.txt");
    setTrack(track);
    serve(args.port_range_start);
}

int main(int argc, char** argv) {
    Args args = {1, 8100};
    
    boost::program_options::options_description desc("Allowed options");
    desc.add_options()
        ("help", "produce help message")
        ("num_forks,n", boost::program_options::value<int>(&args.num_forks)->default_value(1), "number of forks to do in the launched function")
        ("port_range_start,p", boost::program_options::value<int>(&args.port_range_start)->default_value(8100), "range of ports to start listening to");

    boost::program_options::variables_map vm;
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);
    boost::program_options::notify(vm);

    if (vm.count("help")) {
        std::cout << desc << std::endl;
        return 1;
    }

    start_function(args);
    return 0;
}

