import numpy as np


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def is_coordinate_zero(c1, c2, c3):
    if c1 == [0, 0] and c2 == [0, 0] and c3 == [0, 0]:
        return True
    else:
        return False


def calculate_iou(box1, box2):
    # Calculate intersection coordinates
    x1_inter = max(box1[0], box2[0])
    y1_inter = max(box1[1], box2[1])
    x2_inter = min(box1[2], box2[2])
    y2_inter = min(box1[3], box2[3])

    # Calculate area of intersection
    area_inter = max(0, x2_inter - x1_inter + 1) * max(0, y2_inter - y1_inter + 1)

    # Calculate area of individual bounding boxes
    area_box1 = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    area_box2 = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)

    # Calculate union area
    area_union = area_box1 + area_box2 - area_inter

    # Calculate IoU
    iou = area_inter / area_union if area_union > 0 else 0.0
    return iou


def centroid(box):
    return [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]


def distance(box1, box2):
    centroid1 = centroid(box1)
    centroid2 = centroid(box2)
    return np.sqrt((centroid1[0] - centroid2[0]) ** 2 + (centroid1[1] - centroid2[1]) ** 2)


def group_bounding_boxes(boxes, threshold_iou, threshold_distance):
    groups = []

    for box in boxes:
        merged = False
        for group in groups:
            for member in group:
                if calculate_iou(box, member) > threshold_iou:
                    group.append(box)
                    merged = True
                    break
                elif distance(box, member) < threshold_distance:
                    group.append(box)
                    merged = True
                    break
            if merged:
                break

        if not merged:
            # Check if this box intersects with any existing group,
            # or if it's close enough to the centroid of any existing group,
            # if so, merge them
            new_group = [box]
            for existing_group in groups:
                for existing_box in existing_group:
                    if (calculate_iou(box, existing_box) > threshold_iou) or (
                            distance(box, existing_box) < threshold_distance):
                        new_group.extend(existing_group)
                        groups.remove(existing_group)
                        break
                if new_group != [box]:
                    break
            groups.append(new_group)

    return groups


def get_interaction_box(boxes, xyn, confs, threshold_iou=0, threshold_distance=100):
    groups = group_bounding_boxes(boxes, threshold_iou, threshold_distance)
    interaction_boxes = []
    for group in groups:
        interaction_box = create_interaction_box(group)
        num_person = len(group)
        xyn_group = [xyn[i] for i in range(len(xyn)) if boxes[i] in group]
        conf_group = [confs[i] for i in range(len(confs)) if boxes[i] in group]
        interaction_boxes.append((interaction_box, num_person, xyn_group, conf_group))
    return interaction_boxes


def create_interaction_box(group):
    min_x = min(box[0] for box in group)
    min_y = min(box[1] for box in group)
    max_x = max(box[2] for box in group)
    max_y = max(box[3] for box in group)
    return [min_x, min_y, max_x, max_y]
