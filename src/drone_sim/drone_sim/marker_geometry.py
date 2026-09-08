"""Pure geometry for the visualization-only geofence outline."""

from itertools import product


def box_edges(lower, upper):
    """Return the twelve bounding-box edges as pairs of XYZ tuples."""
    corners = list(product(*zip(lower, upper)))
    edges = []
    for index, corner in enumerate(corners):
        for axis in (1, 2, 4):
            other = index ^ axis
            if index < other:
                edges.append((corner, corners[other]))
    return edges
