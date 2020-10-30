
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", type=str, default='MobileNetSSD_deploy.prototxt',
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", type=str, default='MobileNetSSD_deploy.caffemodel',
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
ap.add_argument("-u", "--movidius", type=bool, default=0,
	help="boolean indicating if the Movidius should be used")
args = vars(ap.parse_args())

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

print("[INFO] starting video stream...")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
fps = FPS().start()

while True:

	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

	net.setInput(blob)
	detections = net.forward()

	Lcount = 0	# 왼쪽 도로 자동차 수 세기
	Rcount = 0	# 오른쪽 도로 자동차 수 세기
	
	for i in np.arange(0, detections.shape[2]):

		confidence = detections[0, 0, i, 2]

		if confidence > args["confidence"]:
	
			idx = int(detections[0, 0, i, 1])
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# 왼쪽, 오른쪽 각각의 도로위에 자동차 수 세기 
			if 0 <= startX <= 200 and 0 <= endX <= 200:
				Lcount += 1
			elif 0 <= startX <= 200 and 200 < endX <400:	
				if 400 > startX + endX:
					Lcount += 1
				else:	# 400 > startX + endX
					Rcount += 1	
			else:	# 200 < startX <= 400 and 200 < endX <= 400
				Rcount += 1	

			label = "{}: {:.2f}%".format(CLASSES[idx],
				confidence * 100)
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				COLORS[idx], 2)
			y = startY - 15 if startY - 15 > 15 else startY + 15
			cv2.putText(frame, label, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
			# print("label : "+ label + ", startX : " + str(startX) + ", startY : " + str(startY)
			# 	+ ", endX : " + str(endX) + ", endY : " + str(endY))	

	# 각각의 자동차 수 출력하기
	print("Lcount : " + str(Lcount))
	print("Rcount : " + str(Rcount))
	
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

	fps.update()

fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()