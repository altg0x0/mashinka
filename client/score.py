import math


def tuple_substract(a, b):
    return tuple(x1 - x2 for x1, x2 in zip(a, b))

class ScoreCounter():
    DEFAULT_POS = (277, 603)  # default position of the car
    frames = 0
    center = (309, 377) 
    internal_score = 0
    prev_angle = None

    @classmethod
    def get_angle(cls, pos):
        dx, dy = tuple_substract(pos, cls.center)
        return math.atan2(dy, dx)
    
    @classmethod
    def get_default_angle(cls):
        return cls.get_angle(cls.DEFAULT_POS)
    
    def update(self, newPos):
        self.frames += 1
        new_angle = self.get_angle(newPos)
        angle_delta = new_angle - (self.prev_angle or self.get_default_angle())
        self.internal_score += angle_delta if angle_delta > -math.pi else angle_delta + 2 * math.pi  # todo make more elegant
        self.prev_angle = new_angle

    def get_score(self):
        return 1e6 * self.internal_score / (1e6 + math.log(max(2, self.frames)))
