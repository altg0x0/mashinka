#include <boost/geometry.hpp>
#include <boost/geometry/geometries/point.hpp>

#include "car.hpp"

void Car::frame (double t, double command) {
    bg::add_point(pos, vel);
    angle += std::clamp(command, -1., 1.) * angAcc * t;
    auto dv_vector = Point(cos(angle), sin(angle));  // |v| = 1 at this point
    bg::multiply_value(dv_vector, acc * t);
    bg::add_point(vel, dv_vector);
    bg::multiply_value(vel, friction);
}

Point Car::getPos() {
    return pos;
}


bool Car::isCrashed(const MultiChain& track) {
    return bg::intersects(getCollisionBox(), track);
}

Linestring Car::getCollisionBox()
{
    // Create a rectangle with the specified width and height, centered at (0, 0)
    Linestring rectangle;
    bg::append(rectangle, Point(-width / 2, -height / 2));
    bg::append(rectangle, Point(width / 2, -height / 2));
    bg::append(rectangle, Point(width / 2, height / 2));
    bg::append(rectangle, Point(-width / 2, height / 2));
    bg::append(rectangle, Point(-width / 2, -height / 2)); // Close the rectangle

    bg::strategy::transform::matrix_transformer<double, 2, 2>
        rotation_and_translation(
            std::cos(angle), -std::sin(angle), pos.x(),
            std::sin(angle), std::cos(angle), pos.y(),
            0, 0, 1
        );

    Linestring rotated_rectangle;
    bg::transform(rectangle, rotated_rectangle, rotation_and_translation);
    // std::cerr << "Coords: " << rotated_rectangle.at(1).x() << " " << rotated_rectangle.at(1).y() << "\n";
    return rotated_rectangle;
}
