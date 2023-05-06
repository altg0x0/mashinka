#pragma once

#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>

namespace bg = boost::geometry;

typedef bg::model::d2::point_xy<double> Point;
typedef bg::model::linestring<Point> Linestring;
typedef bg::model::multi_linestring<Linestring> MultiChain;
typedef bg::model::polygon<Point> Polygon;

class Car {
public:
    Car() : pos(0, 0), vel(0, 0), angle(0) {}
    Car(double x, double y, double angle) : pos(x, y), vel(0, 0), angle(angle) {}

    void frame(double t, double command);
    Point getPos();

    bool isCrashed(const MultiChain &track);

public:
    Point pos;          // position of the car
    Point vel;          // velocity of the car
    double angle;       // orientation of the car
    Linestring getCollisionBox();  // Actually a polygon but idk

public:
    static constexpr double width = 50;     // width of the car
    static constexpr double height = 15;    // height of the car
    static constexpr double acc = 7;       // acceleration of the car
    static constexpr double angAcc = 2;    // angular acceleration of the car
    static constexpr double friction = 0.97;    // angular acceleration of the car

};
