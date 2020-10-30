# USAGE
# python3 real_time_detection.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel

# import the necessary packages
from traffic_light import light_timer
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", type=str, default='MobileNetSSD_deploy.prototxt',
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", type=str, default='MobileNetSSD_deploy.caffemodel',
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
	# 취약한 탐지를 필터링할 최소 확률
ap.add_argument("-u", "--movidius", type=bool, default=0,
	help="boolean indicating if the Movidius should be used")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
fps = FPS().start()

# loop over the frames from the video stream
# 비디오 스트림에서 프레임을 반복한다.
# 하나의 영상속 사진에서 for문 계속 돌아간다.
while True:

	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	# 나사산 비디오 스트림에서 프레임을 잡고 크기 조정
	# 최대 너비 400픽셀
	frame = vs.read()
	frame = imutils.resize(frame, width=800)

	# grab the frame dimensions and convert it to a blob
	# 프레임 치수를 잡아 블롭으로 변환
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

	# pass the blob through the network and obtain the detections and
	# predictions
	# 네트워크를 통과해 탐지를 얻고
	# 예측
	net.setInput(blob)
	detections = net.forward()
	
	Lcount = 0	# 왼쪽 도로 자동차 수 세기
	Rcount = 0	# 오른쪽 도로 자동차 수 세기

	# loop over the detections
	for i in np.arange(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the prediction
		# 관련 신뢰(즉, 확률)를 추출
		# 예측
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
		# 'confidence`을 보장하여 취약한 탐지를 걸러낸다.
		# 최소 confidence 이상

		if confidence > args["confidence"]:
			# extract the index of the class label from the
			# `detections`, then compute the (x, y)-coordinates of
			# the bounding box for the object
			# detections에서 클래스 라벨의 색인을 추출한 다음, 객체에 대한 경계 상자의 (x, y)-값을 계산한다.
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# 왼쪽, 오른쪽 각각의 도로위에 자동차 수 세기 
			if 0 <= startX <= 400 and 0 <= endX <= 400:
				Lcount += 1
			elif 0 <= startX <= 400 and 400 < endX <= 800:	
				if 800 > startX + endX:
					Lcount += 1
				else:	# 800 > startX + endX
					Rcount += 1	
			else:	# 400 < startX <= 800 and 400 < endX <= 800
				Rcount += 1	

			# draw the prediction on the frame
			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
			# print("label : "+ label + ", startX : " + str(startX) + ", startY : " + str(startY)
			# 	+ ", endX : " + str(endX) + ", endY : " + str(endY))	

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# 각각의 자동차 수 출력하기
	print("Lcount : " + str(Lcount))
	print("Rcount : " + str(Rcount))

	if Lcount > Rcount:	# count 차이값을 제시해도 좋을 듯
		extratimeL = 3 # 15초간 초록불 시간 추가
		extratimeR = 0 
	elif Lcount < Rcount:
		extratimeL = 0 
		extratimeR = 3 
	else:
		extratimeL = 0 
		extratimeR = 0

	# 신호등 array 
	leftRed = True
	leftBlue = False
	rightRed = False
	rightBlue = True
	trafficLight = [leftRed, leftBlue, rightRed, rightBlue]
	# True-light on/ False-light off
	# 왼쪽은 빨간불(멈춤)/ 오른쪽은 파란불(직진) 상태부터 시작
	light_timer(trafficLight, extratimeR)
	print("change light!")
	trafficLight = [False, True, True, False]
	light_timer(trafficLight, extratimeL)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()