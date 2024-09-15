from PIL import Image, ImageFilter, ImageOps
import pytesseract
import re

# Function to preprocess the image for better OCR accuracy
def preprocess_image(image_path):
    # Load image
    img = Image.open(image_path)

    # Convert to grayscale
    gray_img = img.convert('L')

    # Apply thresholding to binarize the image (removing noise)
    threshold_img = gray_img.point(lambda p: p > 150 and 255)

    # Resize the image for better OCR accuracy (optional)
    resized_img = threshold_img.resize((threshold_img.width * 2, threshold_img.height * 2), Image.Resampling.LANCZOS)

    # Apply median filter to remove noise
    denoised_img = resized_img.filter(ImageFilter.MedianFilter())

    return denoised_img

# Function to extract text from an image
def extract_text_from_image(image_path):
    # Preprocess the image
    preprocessed_img = preprocess_image(image_path)

    # Extract text using pytesseract
    extracted_text = pytesseract.image_to_string(preprocessed_img)

    return extracted_text

# Function to extract specific information using regular expressions
def extract_info(text):
    # Improved regex patterns to handle variations in the text
    candidate_name = re.search(r'Name of Candidate\s*[:|]?\s*([A-Z\s]+)', text, re.IGNORECASE)
    parent_name = re.search(r"Parent’s/Guardian’s\s*Name\s*[:|]?\s*([A-Z\s]+)", text, re.IGNORECASE)
    registration_number = re.search(r'Registration Number\s*[:|]?\s*([A-Z0-9$]+)', text, re.IGNORECASE)
    date_of_birth = re.search(r'Date of Birth\s*[:|]?\s*([0-9\-A-Za-z]+)', text, re.IGNORECASE)
    gate_score = re.search(r'GATE Score\s*[:|]?\s*([0-9]+)', text, re.IGNORECASE)

    # Extract and clean the information
    extracted_info = {
        'Candidate Name': candidate_name.group(1).strip() if candidate_name else 'Not found',
        'Parent/Guardian Name': parent_name.group(1).strip() if parent_name else 'Not found',
        'Registration Number': registration_number.group(1).strip() if registration_number else 'Not found',
        'Date of Birth': date_of_birth.group(1).strip() if date_of_birth else 'Not found',
        'GATE Score': gate_score.group(1).strip() if gate_score else 'Not found'
    }

    return extracted_info

# Main function to process the GATE scorecard
def main():
    # Path to the scorecard image
    image_path = "images/Scorecard8.jpg"

    # Extract text from the image
    extracted_text = extract_text_from_image(image_path)

    # Display extracted text for debugging
    print("Extracted Text:\n", extracted_text)

    # Extract specific information from the text
    extracted_info = extract_info(extracted_text)

    # Print the extracted information
    print("\nExtracted Information:")
    for key, value in extracted_info.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
