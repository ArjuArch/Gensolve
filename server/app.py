import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from skimage.measure import approximate_polygon
import cv2
from PIL import Image
from flask import Flask, request, jsonify, send_file
from shapely.geometry import Polygon as ShapelyPolygon
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def read_csv_(csv_path):
    print(f"Reading CSV file from: {csv_path}")  # Debug statement
    np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
    path_XYs = []
    for i in np.unique(np_path_XYs[:, 0]):
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []
        for j in np.unique(npXYs[:, 0]):
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)
        path_XYs.append(XYs)
    print(f"Path XYs: {path_XYs}")  # Debug statement
    return path_XYs

def is_closed_path(XY, tol=1e-2):
    closed = np.linalg.norm(XY[0] - XY[-1]) < tol
    print(f"Path closed: {closed}")  # Debug statement
    return closed

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
    corners = len(approx_poly)
    
    print(f"Shape details: Circularity={circularity:.2f}, Corners={corners}, Aspect Ratio={aspect_ratio:.2f}")  # Debug statement
    
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
                else:
                    print(f"Shape classification failed: {shape}")  # Debug statement
    
    ax.set_aspect('equal')
    ax.set_title(f"{title} - Detected: {shape_count['Circle']} Circles, {shape_count['Rectangle']} Rectangles, {shape_count['Square']} Squares, {shape_count['Star']} Stars, {shape_count['Unknown']} Unknown Shapes")
    ax.legend()

def complete_image(image_path, axis='vertical'):
    print(f"Completing image at: {image_path} along {axis} axis")  # Debug statement
    img = Image.open(image_path)
    img_np = np.array(img)
    width, height = img.size
    
    if axis == 'vertical':
        half_img = img_np[:, :width//2]
        mirrored_half = np.fliplr(half_img)
        completed_img_np = np.concatenate((half_img, mirrored_half), axis=1)
    elif axis == 'horizontal':
        half_img = img_np[:height//2, :]
        mirrored_half = np.flipud(half_img)
        completed_img_np = np.concatenate((half_img, mirrored_half), axis=0)
    else:
        raise ValueError("Axis must be either 'vertical' or 'horizontal'.")
    
    completed_img = Image.fromarray(completed_img_np)
    return completed_img

def plot_images(original_image, completed_image, axis='vertical'):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    axes[0].imshow(original_image)
    axes[0].set_title(f"Original Half Image ({axis})")
    axes[0].axis('off')
    
    axes[1].imshow(completed_image)
    axes[1].set_title("Completed Image")
    axes[1].axis('off')
    
    plt.show()

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
            patch = plt.Polygon(hull_points, closed=True, edgecolor='none', facecolor=c, linewidth=2)
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

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    file_path = os.path.join('static', file.filename)
    print(f"Saving CSV file to: {file_path}")  # Debug statement
    file.save(file_path)
    
    paths_XYs = read_csv_(file_path)
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_and_classify_closed_shapes(paths_XYs, 'Uploaded Data', ax)
    plt_path = os.path.join('static', 'plot.png')
    plt.savefig(plt_path)
    plt.close()
    
    print(f"Plot saved to: {plt_path}")  # Debug statement
    return jsonify({"plotUrl": '/get_plot'})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file']
    file_path = os.path.join('static', file.filename)
    print(f"Saving image file to: {file_path}")  # Debug statement
    file.save(file_path)
    
    completed_img = complete_image(file_path, axis='vertical')
    completed_img_path = os.path.join('static', 'completed_' + file.filename)
    completed_img.save(completed_img_path)
    
    print(f"Completed image saved to: {completed_img_path}")  # Debug statement
    return send_file(completed_img_path, mimetype='image/jpeg')

@app.route('/identify_shape', methods=['POST'])
def identify_shape_route():
    file = request.files['file']
    file_path = os.path.join('static', file.filename)
    print(f"Saving CSV file for shape identification to: {file_path}")  # Debug statement
    file.save(file_path)
    
    paths_XYs = read_csv_(file_path)
    shapes = []
    for XYs in paths_XYs:
        for XY in XYs:
            shape = identify_shape(XY)
            shapes.append(shape)
    
    print(f"Identified shapes: {shapes}")  # Debug statement
    return jsonify({"shapes": shapes})

@app.route('/get_plot', methods=['GET'])
def get_plot():
    plot_path = os.path.join('static', 'plot.png')
    
    if os.path.exists(plot_path):
        return send_file(plot_path, mimetype='image/png')
    else:
        print(f"Plot not found at: {plot_path}")  # Debug statement
        return jsonify({"error": "Plot not found"}), 404

@app.route('/', methods=['GET'])
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
