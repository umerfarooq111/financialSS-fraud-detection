import cv2
import os
import time
import pytesseract

def main():
    # Note: On Windows, you might need to specify the tesseract executable path 
    # if it's not in your system PATH. Uncomment and update the path below if needed:
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Create the uploads folder if it doesn't exist already
    os.makedirs("uploads", exist_ok=True)

    # Initialize the webcam (0 is usually the default built-in camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open the webcam.")
        return

    print("Webcam successfully opened.")
    print("Press 'c' to capture a frame and perform OCR.")
    print("Press 'q' to exit the video feed.")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to grab a frame from the webcam.")
            break

        # Display the resulting frame in a window
        cv2.imshow('Live Payment Verification Feed', frame)

        # Wait for 1 ms and get the user's key press
        key = cv2.waitKey(1) & 0xFF

        # Check for 'q' to exit
        if key == ord('q'):
            print("Exit signal received. Closing the feed.")
            break
        
        # Check for 'c' to capture and extract text
        elif key == ord('c'):
            # Create a unique filename using a timestamp
            timestamp = int(time.time())
            filename = os.path.join("uploads", f"capture_{timestamp}.jpg")
            
            # Save the current frame to the uploads folder
            cv2.imwrite(filename, frame)
            
            # Convert frame to grayscale (improves OCR accuracy)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            print("\n--- Extracting Text ---")
            try:
                # Extract text using pytesseract
                extracted_text = pytesseract.image_to_string(gray_frame)
                print(extracted_text.strip())
            except Exception as e:
                print("OCR Error:", e)
                print("\nMake sure Tesseract-OCR is installed on your system.")
                print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("-----------------------\n")
            
            # Give feedback in the console
            print(f"Successfully captured and saved to: {filename}")

    # Once the loop breaks, release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
