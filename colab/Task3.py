import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.ops import unary_union

def read_csv_(csv_path):
    np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
    path_XYs = []
    for i in np.unique(np_path_XYs[:, 0]):
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []
        for j in np.unique(npXYs[:, 0]):
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)
        path_XYs.append(XYs)
    return path_XYs

def plot(paths_XYs, title, ax):
    colours = ['red', 'green', 'blue', 'yellow', 'purple']  
    overlay_polygons = []
    
    for i, XYs in enumerate(paths_XYs):
        c = colours[i % len(colours)]
        for XY in XYs:
            if len(XY) < 3:
                continue
            
            hull = ConvexHull(XY)
            hull_points = XY[hull.vertices]
            current_poly = ShapelyPolygon(hull_points)
            
            if any(current_poly.intersects(p) for p in overlay_polygons):
                continue

            
            overlay_polygons.append(current_poly)
            patch = Polygon(hull_points, closed=True, edgecolor='none', facecolor=c, linewidth=2)
            ax.add_patch(patch)

    ax.set_aspect('equal')
    ax.set_title(title)
    ax.autoscale_view()

def identify_shape(XYs):
    if len(XYs) < 3:
        return "Unknown"

    if not np.allclose(XYs[0], XYs[-1]):
        return "Unknown"

    hull = ConvexHull(XYs)
    hull_points = XYs[hull.vertices]
    
    num_vertices = len(hull_points)
    if num_vertices == 3:
        return "Triangle"
    elif num_vertices == 4:
        edges = [np.linalg.norm(hull_points[i] - hull_points[(i+1) % 4]) for i in range(4)]
        angles = [np.arccos(np.clip(np.dot(hull_points[i] - hull_points[(i+1) % 4], hull_points[(i+2) % 4] - hull_points[(i+1) % 4]) /
                                    (np.linalg.norm(hull_points[i] - hull_points[(i+1) % 4]) * np.linalg.norm(hull_points[(i+2) % 4] - hull_points[(i+1) % 4])), -1.0, 1.0))
                   for i in range(4)]
        is_rectangle = np.allclose(np.array(angles), np.pi/2)
        is_square = np.allclose(edges[0], edges[1]) and is_rectangle
        return "Square" if is_square else "Rectangle"
    elif num_vertices == 5:
        return "Pentagon (Star)"
    elif num_vertices > 5:
        return "Star or Complex Shape"

    return "Unknown"

csv_path1 = "/content/occlusion2.csv"
csv_path2 = "/content/occlusion2_sol.csv"

output_data1 = read_csv_(csv_path1)
output_data2 = read_csv_(csv_path2)

fig, axs = plt.subplots(1, 2, tight_layout=True, figsize=(16, 8))
plot(output_data1, 'Original Data', axs[0])
plot(output_data2, 'Processed Data', axs[1])

for XYs in output_data2:
    for XY in XYs:
        shape = identify_shape(np.array(XY))
        print(f"Identified shape: {shape}")

plt.show()