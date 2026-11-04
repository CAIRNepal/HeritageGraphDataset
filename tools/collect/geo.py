"""Point-in-polygon for many points at once: the even-odd rule of tools/pilot/match.py's inside(), vectorised with
matplotlib's Path (province and district rings have thousands of vertices)."""
import numpy as np
from matplotlib.path import Path


def inside_many(points, rings):
    """points: [(lon, lat), ...]; rings: [[(lon, lat), ...], ...]. A list of booleans, even-odd over all rings."""
    if not points:
        return []
    pts = np.asarray(points, dtype=float)
    count = np.zeros(len(pts), dtype=int)
    for ring in rings:
        count += Path(np.asarray(ring, dtype=float)).contains_points(pts)
    return list(count % 2 == 1)


_paths = {}


def inside(lon, lat, rings):
    """One point; same rule. The rings' Paths are built once per rings list (kept alive by the caller)."""
    key = id(rings)
    if key not in _paths:
        _paths[key] = (rings, [Path(np.asarray(r, dtype=float)) for r in rings])
    return sum(p.contains_point((lon, lat)) for p in _paths[key][1]) % 2 == 1
