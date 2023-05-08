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
    return rotated_rectangle;
}

std::vector<Segment> Car::getLidarSegments(unsigned int num_segments, double length, double rotation_angle)
{
    auto& center = pos;
    double angle_step = 2.0 * M_PI / num_segments;
    double angle = 0.0;

    Point end_point(length, 0.0);

    bg::strategy::transform::rotate_transformer<bg::radian, double, 2, 2> rotator(rotation_angle);
    bg::strategy::transform::rotate_transformer<bg::radian, double, 2, 2> step_rotator(angle_step);

    std::vector<Segment> star;
    
    for (unsigned int i = 0; i < num_segments; ++i)
    {
        Point rotated_point;
        bg::transform(end_point, rotated_point, rotator);
        Point translated_point(rotated_point.x() + center.x(), rotated_point.y() + center.y());
        star.emplace_back(center, translated_point);

        // Rotate the endpoint by the angle step for the next iteration
        bg::transform(end_point, end_point, step_rotator);
    }

    return star;
}

std::vector<double> Car::getLidarDistances(const MultiChain& track) {
    auto& pos_ref = pos;
    std::vector<double> ret(Car::nLidars, Car::lidarsMaxDistance);
    auto lidarSegments = getLidarSegments(nLidars, lidarsMaxDistance, angle);
    for (std::size_t ind = 0 ; auto& lidarSeg: lidarSegments) {
        MultiPoint intersection_points;
        Linestring lidarSegLinestring;
        lidarSegLinestring.push_back(lidarSeg.first);
        lidarSegLinestring.push_back(lidarSeg.second);  // FIXME inefficient
        bg::intersection(lidarSegLinestring, track, intersection_points);
        if (intersection_points.empty()) {
            continue;
        }
        auto closest_intersection = std::transform_reduce(
            intersection_points.begin(), intersection_points.end(),
            std::numeric_limits<double>::max(),
            [](double a, double b) { return std::min(a, b); },
            [pos_ref](Point& a) {return bg::distance(a, pos_ref);}
        );
        ret[ind++] = closest_intersection;
    }
    return ret;
}
