from app import app
import io

client = app.test_client()

# Create a dummy image using cv2
import cv2
import numpy as np

img = np.zeros((100, 100, 3), dtype=np.uint8)
# add some text so tesseract finds something
cv2.putText(img, "TID: 12345", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
_, buf = cv2.imencode('.png', img)

data = {
    'file': (io.BytesIO(buf.tobytes()), 'test.png')
}

response = client.post('/upload', data=data, content_type='multipart/form-data')

print("Status Code:", response.status_code)
print("Response Data:", response.data.decode('utf-8'))
