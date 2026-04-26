from flask import Flask, request, render_template, jsonify
import cv2
import numpy as np
import pytesseract
from step1_webcam import parse_ocr_text

app = Flask(__name__)

# Note: On Windows, you might need to specify the tesseract executable path 
# if it's not in your system PATH. Uncomment and update the path below if needed:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'})

        # Read the image file from memory
        in_memory_file = file.read()
        nparr = np.frombuffer(in_memory_file, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Invalid image format'})

        # Resize the image by 2x to help Tesseract read smaller text
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply a binary threshold. This forces light gray text to become pure black, 
        # and the white background to remain pure white. This prevents the gray names from washing out.
        _, thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY)
        
        # Extract text using Tesseract
        extracted_text = pytesseract.image_to_string(thresh).strip()
        
        # Parse the text using the function we built earlier
        parsed_info = parse_ocr_text(extracted_text)
        
        return jsonify({
            'success': True,
            'raw_text': extracted_text,
            'parsed_info': parsed_info
        })
    except pytesseract.pytesseract.TesseractNotFoundError:
        return jsonify({'error': 'Tesseract OCR is not installed or not in your system PATH. Please uncomment line 11 in app.py and set the correct path to tesseract.exe.'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("Starting Web Server. Access it at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
