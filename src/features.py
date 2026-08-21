import numpy as np


def normalize_landmarks(row):
    """
    row: list/array of 63 values (x0,y0,z0, ..., x20,y20,z20)
    Returns 63 normalized values, invariant to position and scale.
    """
    points = np.array(row, dtype=float).reshape(21, 3)

    # 1. Translate: wrist (point 0) becomes the origin
    points = points - points[0]

    # 2. Scale: divide by the largest distance from the wrist
    max_dist = np.linalg.norm(points, axis=1).max()
    if max_dist > 0:
        points = points / max_dist

    return points.flatten()
