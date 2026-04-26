import cv2
import os
import time
import pytesseract

def parse_ocr_text(ocr_text):
    """
    Parses the OCR text to extract specific transaction fields.
    This implementation uses a regex/heuristic fallback, but the instructions provided
    are best suited for an LLM. You can plug in an LLM (like Google Gemini, OpenAI, or 
    a local model like Ollama) inside this function.
    """
    # If using an LLM (e.g., Gemini or OpenAI), you would pass this exact prompt:
    prompt = f"""
    From the OCR text, extract and display ONLY:

    Transaction ID
    Sender Name
    Receiver Name
    Amount
    Date / Time

    ❌ Important Restrictions:
    Do NOT perform fraud detection or analysis
    Do NOT add explanations or reasoning
    Do NOT classify transactions
    Do NOT include extra fields

    ⚙️ Output Requirement:
    Return clean, structured output exactly in this format:

    Transaction ID:
    Sender Name:
    Receiver Name:
    Amount:
    Date/Time:

    🧠 Handling Rules:
    If any field is missing, write "Not Found"
    If OCR has minor errors but meaning is clear, correct it
    Keep output minimal, clean, and consistent

    OCR Text:
    {ocr_text}
    """
    
    # --- LLM API Call Example (Uncomment and configure to use) ---
    # import google.generativeai as genai
    # genai.configure(api_key="YOUR_API_KEY")
    # model = genai.GenerativeModel('gemini-1.5-flash')
    # response = model.generate_content(prompt)
    # return response.text.strip()
    
    # --- Basic Offline/Regex Fallback ---
    import re
    
    # Helper to get the line immediately following a keyword
    def get_next_line(text, keyword):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower() and i + 1 < len(lines):
                return lines[i + 1]
        return "Not Found"

    # Transaction ID (e.g., ID# 42164546468)
    tid_match = re.search(r"(?:1D|ID|TID|Transaction ID)\s*[#:\-]?\s*([A-Za-z0-9]{8,})", ocr_text, re.IGNORECASE)
    tid = tid_match.group(1).strip() if tid_match else "Not Found"

    # Amount (Handling multiline like "Total Amount \n Rs. 10000000 .00")
    amount_match = re.search(r"(?:Total Amount|Amount)\s*(?:Rs\.?)?\s*([\d,]+\s*\.?\s*\d*)", ocr_text, re.IGNORECASE)
    if amount_match:
        amount = amount_match.group(1).replace(" ", "") # Clean up spaces like '10000 .00'
    else:
        amount = "Not Found"

    # Date/Time (e.g., 14 Oct 2025 1:09 am)
    date_time_match = re.search(r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\s+\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)", ocr_text, re.IGNORECASE)
    date_time = date_time_match.group(1).strip() if date_time_match else "Not Found"
    
    # Sender and Receiver (Easypaisa format puts name on the line after 'Sent by' / 'Sent to')
    sender = get_next_line(ocr_text, "Sent by")
    receiver = get_next_line(ocr_text, "Sent to")

    return f"Transaction ID: {tid}\nSender Name: {sender}\nReceiver Name: {receiver}\nAmount: {amount}\nDate/Time: {date_time}"

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
                extracted_text = pytesseract.image_to_string(gray_frame).strip()
                print(extracted_text)
                
                print("\n--- Parsed Information ---")
                parsed_info = parse_ocr_text(extracted_text)
                print(parsed_info)
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
