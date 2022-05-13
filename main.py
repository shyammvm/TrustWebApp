from scipy.spatial import distance as dist   #for calculating euclidean distances
from imutils.video import VideoStream   #for image processing in OpenCV
from imutils import face_utils  #facedetection
from threading import Thread
import numpy as np   #numpy array
import argparse #optional argument parsing
import imutils
import time
import dlib     #python machine learning library
import cv2      #openCV
import time
import sys


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor",default="")
ap.add_argument("-a", "--alarm", type=str, default="")
ap.add_argument("-w", "--webcam", type=int, default=0)
args = vars(ap.parse_args())

def eye_aspect_ratio(eye):
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
	C = dist.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear


ear_thresh = 0.30
frame_thresh = 90

counter = 0
ear = 0

timer = 0

detector = dlib.get_frontal_face_detector()
args["shape_predictor"] ="shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(args["shape_predictor"])

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)

while True:
	timer += 1
	frame = vs.read()
	frame = imutils.resize(frame, width = 450)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	faces = detector(gray, 0)
	if len(faces) == 0:
		# print("No faces found!")
		cv2.putText(frame, "No faces found!", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	for face in faces:
		shape = predictor(gray, face)
		shape = face_utils.shape_to_np(shape)
		
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)

		ear = (leftEAR + rightEAR) / 2.0
		# print(ear)
		# print(counter)
		
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
		break

	if ear > ear_thresh:
		counter += 1
		if counter > frame_thresh:
			flag = 0	
			cv2.putText(frame, "SPOOF FACE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			
		
	
	else:
		counter = 0
		# print("real face")
		flag = 1


	if timer > 60:
		break
    


	cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF


if flag ==0:
	print("spoof")
	sys.exit(1)
else:
	sys.exit(0)



	