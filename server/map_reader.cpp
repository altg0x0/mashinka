#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>
#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost::geometry;
namespace bg = boost::geometry;

typedef model::d2::point_xy<double> Point;
typedef model::linestring<Point> Linestring;
typedef model::multi_linestring<Linestring> MultiChain;

Point parse_to_point(const string& input) {
    std::vector<std::string> tokens;
    boost::split(tokens, input, boost::is_any_of(","));

    if (tokens.size() != 2) {
        throw std::runtime_error("Invalid input format");
    }

    double x = std::stod(tokens[0]);
    double y = std::stod(tokens[1]);

    return Point(x, y);
}

MultiChain read_chains(const string& filename)
{
    MultiChain chains;
    vector<Point> points;

    ifstream input(filename);
    if (!input)
    {
        cerr << "Error opening file " << filename << endl;
        return chains;
    }

    string line;
    while (getline(input, line))
    {
        if (line == "N")
        {
            if (!points.empty())
            {
                Linestring linestring (points.begin(), points.end());
                chains.push_back(linestring);
                points.clear();
            }
        }
        else if (line == "") continue;
        else
        {
            Point point = parse_to_point(line);
            points.push_back(point);
        }
    }
    return chains;
}
