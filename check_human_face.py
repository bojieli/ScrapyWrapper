#/usr/bin/python3
# -*- coding:utf-8 -*-
import cv2
import sys

def is_human_face(image_path, new_image_path, cascasdepath="haarcascade_frontalface_default.xml"):
    image = cv2.imread(image_path)
    if image is None:
        return False
    (h, w) = image.shape[:2]
    if h >= w * 2 or w >= h * 2:  # aspect ratio does not look like a face
        return False

    min_face_pixels = int(max(50, h / 10, w / 10))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cascasdepath)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (min_face_pixels, min_face_pixels)
        )

    print(faces)
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imwrite(new_image_path, image)
    return len(faces) == 1

is_human_face(sys.argv[1], sys.argv[2])
