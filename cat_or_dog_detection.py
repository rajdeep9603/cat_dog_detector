from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import cv2
from api_thread import ApiCallThread
from dotenv import dotenv_values
import os
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.

BACKEND_URL=os.getenv("BACKEND_URL")

def detect_cat_dog(url):
	# initialize the list of class labels MobileNet SSD was trained to
	# detect, then generate a set of bounding box colors for each class
	CLASSES = ["cat", "dog"]
	COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

	# load our serialized model from disk
	print("[INFO] loading model...")
	net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

	# initialize the video stream, allow the cammera sensor to warmup,
	# and initialize the FPS counter
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(2.0)
	fps = FPS().start()
	api_call_every = 2.0  # seconds
	snap_time = time.time()

	# loop over the frames from the video stream
	while True:
		# grab the frame from the threaded video stream and resize it
		# to have a maximum width of 400 pixels
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		# print(type(frame))
		# grab the frame dimensions and convert it to a blob
		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
									 0.007843, (300, 300), 127.5)
		# pass the blob through the network and obtain the detections and
		# predictions
		net.setInput(blob)
		detections = net.forward()

		# loop over the detections
		for i in np.arange(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with
			# the prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the `confidence` is
			# greater than the minimum confidence
			if confidence > 0.2:
				# extract the index of the class label from the
				# `detections`, then compute the (x, y)-coordinates of
				# the bounding box for the object
				_idx = int(detections[0, 0, i, 1])
				# 8 for cat and 12 for dog
				if _idx in [8, 12]:
					new_time = time.time()
					if (new_time - snap_time) >= api_call_every and (confidence*100) > 70:  # Call API as per confidence level
						ApiCallThread(_idx, frame, confidence, url).start()
						snap_time = time.time()
					if _idx == 8:  # For cat detection
						idx = 0
					elif _idx == 12:  # For dog detection
						idx = 1
					box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
					(startX, startY, endX, endY) = box.astype("int")

					# draw the prediction on the frame
					label = "{}: {:.2f}%".format(CLASSES[idx],
												 confidence * 100)
					cv2.rectangle(frame, (startX, startY), (endX, endY),
								  COLORS[idx], 2)
					y = startY - 15 if startY - 15 > 15 else startY + 15
					cv2.putText(frame, label, (startX, y),
								cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

		# show the output frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

		# update the FPS counter
		fps.update()

	# stop the timer and display FPS information
	fps.stop()
	print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
	print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs.stop()


if __name__ == "__main__":
	# api_endpoint = "http://127.0.0.1:8000/image_detection/cat_or_dog_image/" # FOr local
	api_endpoint = f"{BACKEND_URL}/image_detection/cat_or_dog_image/" # For live
	detect_cat_dog(url=api_endpoint)