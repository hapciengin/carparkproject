import cv2
import numpy as np
import json

# Kullanıcının seçtiği noktaları saklamak için bir liste
current_points = []

# Kullanıcının seçtiği alanları saklamak için bir liste
all_areas = []

# Silinecek köşenin ve alana ait index'lerini tutacak değişken
replacement_point_index = None

# Dosya yolu
areas_file = 'areas.json'

# JSON dosyasından dikdörtgen bilgilerini yükle
def load_areas():
    try:
        with open(areas_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# JSON dosyasına dikdörtgen bilgilerini kaydet
def save_areas(areas):
    with open(areas_file, 'w') as file:
        json.dump(areas, file)

# Fare olayı işleyici fonksiyonu
def mouse_callback(event, x, y, flags, param):
    global current_points, all_areas, replacement_point_index
    if event == cv2.EVENT_LBUTTONDOWN:
        if replacement_point_index is not None:
            # Replace the deleted corner with a new point
            area_index, point_index = replacement_point_index
            all_areas[area_index][point_index] = (x, y)
            replacement_point_index = None
            save_areas(all_areas)
        elif len(current_points) < 3:
            current_points.append((x, y))
        else:
            current_points.append((x, y))
            all_areas.append(current_points)
            current_points = []
            save_areas(all_areas)
        draw_all_areas()

    elif event == cv2.EVENT_RBUTTONDOWN:
        # First check for point removal or replacement
        if not remove_or_replace_point(x, y):
            # If no point is close enough, check if the click is near any edge
            remove_area_if_edge_clicked(x, y)

def remove_or_replace_point(x, y):
    global replacement_point_index, all_areas
    for i, area in enumerate(all_areas):
        for j, point in enumerate(area):
            if abs(point[0] - x) <= 5 and abs(point[1] - y) <= 5:
                replacement_point_index = (i, j)
                draw_all_areas()
                return True
    return False

def remove_area_if_edge_clicked(x, y):
    global all_areas
    for i, area in enumerate(all_areas):
        # Create an edge list and check each edge
        edges = [(area[k], area[(k + 1) % len(area)]) for k in range(len(area))]
        for pt1, pt2 in edges:
            if point_on_line(pt1, pt2, (x, y)):
                all_areas.pop(i)
                save_areas(all_areas)
                draw_all_areas()
                return

def point_on_line(pt1, pt2, pt, threshold=5):
    """ Check if point pt is on the line pt1-pt2 within a certain threshold """
    line_mag = np.linalg.norm(np.array(pt1) - np.array(pt2))
    dist = np.abs(np.cross(np.array(pt2)-np.array(pt1), np.array(pt1)-np.array(pt))) / line_mag
    return dist <= threshold

# Tüm alanları çiz
def draw_all_areas():
    global image
    image = cv2.imread(image_path)
    for area in all_areas:
        cv2.polylines(image, [np.array(area)], True, (128, 0, 128), 1)
        for point in area:
            cv2.circle(image, point, 3, (128, 0, 128), -1)
    # Draw temporary points
    for i, point in enumerate(current_points):
        cv2.circle(image, point, 3, (128, 0, 128), -1)
        if i > 0:
            cv2.line(image, current_points[i - 1], point, (128, 0, 128), 1)
    if len(current_points) == 4:
        cv2.line(image, current_points[0], current_points[-1], (128, 0, 128), 1)
    cv2.imshow("Car Park Image", image)

# Görseli yükle ve dikdörtgenleri göster
image_path = "carParkImg.png"
image = cv2.imread(image_path)

all_areas = load_areas()

cv2.namedWindow("Car Park Image")
cv2.setMouseCallback("Car Park Image", mouse_callback)

draw_all_areas()

cv2.waitKey(0)
cv2.destroyAllWindows()
