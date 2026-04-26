from app import app
import io
import cv2
import numpy as np

client = app.test_client()

# Create a large dummy image
img = np.random.randint(0, 255, (2000, 2000, 3), dtype=np.uint8)
_, buf = cv2.imencode('.png', img)

data = {
    'file': (io.BytesIO(buf.tobytes()), 'test.png')
}

response = client.post('/upload', data=data, content_type='multipart/form-data')

print("Status Code:", response.status_code)
print("Response Data Length:", len(response.data))
try:
    import json
    print("Parsed JSON:", json.loads(response.data.decode('utf-8'))['success'])
except Exception as e:
    print("Error parsing JSON:", str(e))
    print("Data:", response.data.decode('utf-8')[:200])
