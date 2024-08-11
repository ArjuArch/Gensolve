import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from skimage.measure import approximate_polygon
import cv2

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

def is_closed_path(XY, tol=1e-2):
    return np.linalg.norm(XY[0] - XY[-1]) < tol

def classify_basic_shape(XY):
    if len(XY) < 3:
        return None

    hull = ConvexHull(XY)
    hull_vertices = XY[hull.vertices]

    perimeter = np.sum(np.linalg.norm(np.diff(hull_vertices, axis=0), axis=1)) + np.linalg.norm(hull_vertices[-1] - hull_vertices[0])
    area = hull.volume

    circularity = 4 * np.pi * area / (perimeter ** 2)
    bbox = cv2.boundingRect(np.array(XY, dtype=np.float32))
    bbox_width, bbox_height = bbox[2], bbox[3]
    aspect_ratio = bbox_width / bbox_height

    approx_poly = approximate_polygon(XY, tolerance=0.01)
    corners = len(approx_poly)-1

    print(f"Shape details: Circularity={circularity:.2f}, Corners={corners}, Aspect Ratio={aspect_ratio:.2f}")

    if circularity > 0.85:
        return "Circle"
    elif corners == 4:
        if 0.8 < aspect_ratio < 1.2: 
            return "Square"
        else:
            return "Rectangle"
    elif corners >= 5:
            return "Star"
    return "Unknown"

def plot_and_classify_closed_shapes(paths_XYs, title, ax):
    colours = ['red', 'green', 'blue', 'yellow', 'purple']
    shape_count = {"Circle": 0, "Rectangle": 0, "Square": 0, "Star": 0, "Unknown": 0}

    for i, XYs in enumerate(paths_XYs):
        c = colours[i % len(colours)]
        for XY in XYs:
            if is_closed_path(XY):
                shape = classify_basic_shape(XY)
                if shape in shape_count:
                    shape_count[shape] += 1
                    ax.plot(XY[:, 0], XY[:, 1], c=c, linewidth=2, label=f'{shape} {shape_count[shape]}')

    ax.set_aspect('equal')
    ax.set_title(f"{title} - Detected: {shape_count['Circle']} Circles, {shape_count['Rectangle']} Rectangles, {shape_count['Square']} Squares, {shape_count['Star']} Stars, {shape_count['Unknown']} Unknown Shapes")
    ax.legend()

csv_path1 = "/content/drive/MyDrive/GenSolve/frag0.csv"
csv_path2 = "/content/drive/MyDrive/GenSolve/frag01_sol.csv"

output_data1 = read_csv_(csv_path1)
output_data2 = read_csv_(csv_path2)

fig, axs = plt.subplots(1, 2, tight_layout=True, figsize=(16, 8))
plot_and_classify_closed_shapes(output_data1, 'Original Data', axs[0])
plot_and_classify_closed_shapes(output_data2, 'Processed Data', axs[1])
plt.show()