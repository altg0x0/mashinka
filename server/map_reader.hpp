#pragma once
#include <boost/geometry.hpp>

typedef boost::geometry::model::d2::point_xy<double> Point;
typedef boost::geometry::model::linestring<Point> Linestring;
typedef boost::geometry::model::multi_linestring<Linestring> MultiChain;

MultiChain read_chains(const std::string& filename);