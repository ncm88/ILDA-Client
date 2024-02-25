import math

class IldaFrame:
    MAX_POINT_VALUE = 2**15 - 1
    MAPPED_MAX = 4096
    POINT_COUNT = 500

    def __init__(self, points):
        self.points = points
        self.length = len(points)

    def get_length(self):
        return self.length

    def get_points(self):
        for (x, y, z), blank in self.points:
            yield {"x": x, "y": y, "z": z, "blank": blank}

    def get_mapped_points(self):
        def map_pt(p):
            return int((((math.asin(p / IldaFrame.MAX_POINT_VALUE) / math.asin(1.0)) + 1) / 2) * IldaFrame.MAPPED_MAX)
        
        for (x, y, z), blank in self.points:
            yield {"x": map_pt(x), "y": map_pt(y), "blank": blank}

    @classmethod
    def SqWaveTestPattern(cls, x_axis=True):
        pts = []
        max_val = cls.MAX_POINT_VALUE // 2
        step_size = max_val * 2 / cls.POINT_COUNT

        for i in range(-max_val, max_val, int(step_size)):
            if x_axis:
                pts.append(((i, -max_val if i % (max_val*2) < max_val else max_val, 0), False))
            else:
                pts.append(((-max_val if i % (max_val*2) < max_val else max_val, i, 0), False))

        # Generate blank return pass to origin
        for i in range(max_val, -max_val, -int(step_size * 2)):
            pts.append(((i, -max_val, 0), True) if x_axis else ((-max_val, i, 0), True))
        pts.append(((-max_val, -max_val, 0), True))

        return cls(pts)
