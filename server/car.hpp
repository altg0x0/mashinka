#pragma once

#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>

namespace bg = boost::geometry;

typedef bg::model::d2::point_xy<double> Point;
typedef bg::model::linestring<Point> Linestring;
typedef bg::model::multi_linestring<Linestring> MultiChain;
typedef bg::model::polygon<Point> Polygon;
typedef bg::model::segment<Point> Segment;
typedef bg::model::multi_point<Point> MultiPoint;


class Car {
public:
    Car() : pos(0, 0), vel(0, 0), angle(0) {}
    Car(double x, double y, double angle) : pos(x, y), vel(0, 0), angle(angle) {}

    void frame(double t, double command);

    bool isCrashed(const MultiChain &track);

public:
    Point pos;          // position of the car
    Point vel;          // velocity of the car
    double angle;       // orientation of the car
    Linestring getCollisionBox();  // Actually a polygon but idk
    std::vector<double> getLidarDistances(const MultiChain &track);

private:
    std::vector<Segment> getLidarSegments(unsigned int num_segments, double length, double rotation_angle);

public:
    static constexpr double width = 50;
    static constexpr double height = 15;
    static constexpr double acc = 7;       // acceleration of the car
    static constexpr double angAcc = 2;    // angular acceleration of the car
    static constexpr double friction = 0.97;
    static constexpr unsigned int nLidars = 12;
    static constexpr double lidarsMaxDistance = 200;
};
