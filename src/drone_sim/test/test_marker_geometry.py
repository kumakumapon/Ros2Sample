"""Test the cuboid topology used by the geofence marker."""

from drone_sim.marker_geometry import box_edges


def test_box_has_twelve_distinct_axis_aligned_edges():
    """Every corner has degree three and each edge changes one coordinate."""
    edges = box_edges((-1.0, -2.0, 0.0), (3.0, 4.0, 5.0))
    assert len(edges) == len(set(edges)) == 12
    corners = [point for edge in edges for point in edge]
    assert len(set(corners)) == 8
    assert all(corners.count(point) == 3 for point in corners)
    assert all(sum(a != b for a, b in zip(start, end)) == 1 for start, end in edges)
