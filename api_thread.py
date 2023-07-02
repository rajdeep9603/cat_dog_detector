import requests
from PIL import Image as im
import io
import threading
import cv2


class ApiCallThread(threading.Thread):
	def __init__(self,_idx,frame,confidence,url):
		self._idx = _idx
		self.frame = frame
		self.confidence = confidence
		self.url=url
		threading.Thread.__init__(self)

	def run(self):
		try:
			image_type = 'CAT' if self._idx == 8 else 'DOG'
			imageRGB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
			image_bytes = im.fromarray(imageRGB)
			buf = io.BytesIO()
			image_bytes.save(buf, format="JPEG")
			buf.seek(0)
			files = [('image', (f'{image_type}.jpeg', buf.read(), 'image/jpeg'))]
			payload = {'image_type': image_type, 'accuracy': self.confidence * 100}
			response = requests.request("POST", self.url, data=payload, files=files)
			print(response.text)
		except Exception as e:
			print("Error >>>>>>>>> ", e)
