import cv2
import face_recognition
import argparse

# print("starting..")

ap = argparse.ArgumentParser()
ap.add_argument('imgs', type=str, nargs='+')
args = ap.parse_args()
img1 = args.imgs[0]
img2 = args.imgs[1]

image = cv2.imread(img1)
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

boxes = face_recognition.face_locations(rgb, model="cnn")
encodings1 = face_recognition.face_encodings(rgb, boxes)

# read 2nd image and store encodings
image = cv2.imread(img2)
rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

boxes = face_recognition.face_locations(rgb, model="cnn")
encodings2 = face_recognition.face_encodings(rgb, boxes)


# now you can compare two encodings
# optionally you can pass threshold, by default it is 0.6
matches = face_recognition.compare_faces(encodings1, encodings2[0])
print(matches)