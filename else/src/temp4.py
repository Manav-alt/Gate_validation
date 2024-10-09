import os
import re
import logging
from typing import Dict, Optional, Tuple
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class ScoreCardInfo:
    candidate_name: Tuple[str, float]
    parent_guardian_name: Tuple[str, float]
    registration_number: Tuple[str, float]
    date_of_birth: Tuple[str, float]
    gate_score: Tuple[str, float]
    gate_paper_code: Tuple[str, float]
    exam_year: Tuple[str, float]

def preprocess_image(image_path: str) -> Image.Image:
    """
    Preprocess the image for better OCR accuracy.
    """
    try:
        img = Image.open(image_path)
        gray_img = img.convert('L')
        enhancer = ImageEnhance.Contrast(gray_img)
        contrast_img = enhancer.enhance(2.0)
        threshold_img = contrast_img.point(lambda p: p > 140 and 255)
        resized_img = threshold_img.resize((threshold_img.width * 2, threshold_img.height * 2), Image.Resampling.LANCZOS)
        denoised_img = resized_img.filter(ImageFilter.MedianFilter())
        return denoised_img
    except Exception as e:
        logging.error(f"Error preprocessing image: {str(e)}")
        raise

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using OCR.
    """
    try:
        preprocessed_img = preprocess_image(image_path)
        extracted_text = pytesseract.image_to_string(preprocessed_img)
        return extracted_text
    except Exception as e:
        logging.error(f"Error extracting text from image: {str(e)}")
        raise

def extract_info(text: str) -> ScoreCardInfo:
    """
    Extract specific information from the OCR text using regular expressions.
    """
    # Clean text from any non-ASCII characters to reduce OCR noise
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    patterns = {
        'candidate_name': [
            r'Name of Candidate\s*[:|]?\s*([A-Z][A-Z\s]+)',
            r'Candidate Name\s*[:|]?\s*([A-Z][A-Z\s]+)'
        ],
        'parent_guardian_name': [
            r"(?:Parent['’]s/Guardian['’]s\s*Name|Parent/Guardian\s*Name)\s*[:|]?\s*([A-Z][A-Z\s]+)",
            r"(?:Father's|Mother's)\s*Name\s*[:|]?\s*([A-Z][A-Z\s]+)"
        ],
        'registration_number': [
            r'Registration Number\s*[:|]?\s*([A-Z0-9]+)',
            r'Enrollment Number\s*[:|]?\s*([A-Z0-9]+)'
        ],
        'date_of_birth': [
            r'Date of Birth\s*[:|]?\s*(\d{1,2}[-/]\w{3}[-/]\d{4})',
            r'DOB\s*[:|]?\s*(\d{1,2}[-/]\w{3}[-/]\d{4})'
        ],
        'gate_score': [
            r'GATE Score\s*[:|]?\s*(\d{1,4})',
            r'Score\s*[:|]?\s*(\d{1,4})'
        ],
        'gate_paper_code': [
            r'Paper Code\s*[:|]?\s*([A-Z]{2,3})',
            r'GATE Paper\s*[:|]?\s*([A-Z]{2,3})'
        ],
        'exam_year': [
            r'GATE\s+(\d{4})',
            r'(\d{4})\s+Scorecard',
            r'Examination\s+Year\s*[:|]?\s*(\d{4})'
        ]
    }

    extracted_info = {}
    for key, pattern_list in patterns.items():
        best_match = ('Not found', 0.0)
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                confidence = len(match.group(1)) / len(pattern)  # Simple confidence score
                if confidence > best_match[1]:
                    best_match = (match.group(1).strip(), confidence)
        extracted_info[key] = best_match

    return ScoreCardInfo(**extracted_info)

def clean_extracted_info(info: ScoreCardInfo) -> ScoreCardInfo:
    """
    Clean and format the extracted information.
    """
    # Clean and format names
    info.candidate_name = (re.sub(r'PARENT', '', info.candidate_name[0].upper()), info.candidate_name[1])
    info.parent_guardian_name = (re.sub(r'[^A-Z\s]', '', info.parent_guardian_name[0].upper()), info.parent_guardian_name[1])

    # Clean and format date of birth
    if info.date_of_birth[0] != 'Not found':
        try:
            day, month, year = re.split(r'[-/]', info.date_of_birth[0])
            info.date_of_birth = (f"{day.zfill(2)}-{month[:3].capitalize()}-{year}", info.date_of_birth[1])
        except ValueError:
            info.date_of_birth = ('Not found', 0.0)

    # Clean registration number
    if info.registration_number[0].lower() == 'date':
        info.registration_number = ('Not found', 0.0)

    return info

def validate_extracted_info(info: ScoreCardInfo) -> None:
    """
    Validate the extracted information and log warnings for potential issues.
    """
    if info.candidate_name[0] == 'Not found' or len(info.candidate_name[0]) < 3:
        logging.warning(f"Candidate name not found or too short. Confidence: {info.candidate_name[1]:.2f}")
    
    if not re.match(r'\d{4}', info.exam_year[0]):
        logging.warning(f"Extracted exam year '{info.exam_year[0]}' doesn't look valid. Confidence: {info.exam_year[1]:.2f}")
    
    if not info.gate_score[0].isdigit():
        logging.warning(f"Extracted GATE score '{info.gate_score[0]}' is not a valid number. Confidence: {info.gate_score[1]:.2f}")
    
    if not re.match(r'\d{2}-[A-Z][a-z]{2}-\d{4}', info.date_of_birth[0]):
        logging.warning(f"Extracted date of birth '{info.date_of_birth[0]}' doesn't match the expected format. Confidence: {info.date_of_birth[1]:.2f}")

def process_scorecard(image_path: str) -> Optional[ScoreCardInfo]:
    """
    Process a GATE scorecard image and return extracted information.
    """
    try:
        logging.info(f"Processing scorecard: {image_path}")
        extracted_text = extract_text_from_image(image_path)
        extracted_info = extract_info(extracted_text)
        cleaned_info = clean_extracted_info(extracted_info)
        validate_extracted_info(cleaned_info)
        return cleaned_info
    except Exception as e:
        logging.error(f"Error processing scorecard: {str(e)}")
        return None

def main():
    image_directory = "/Users/manavpathak/Gate_Validation/images/"
    
    for filename in os.listdir(image_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_directory, filename)
            extracted_info = process_scorecard(image_path)
            
            if extracted_info:
                print(f"\nExtracted Information for {filename}:")
                for field, (value, confidence) in extracted_info.__dict__.items():
                    print(f"{field.replace('_', ' ').title()}: {value} (Confidence: {confidence:.2f})")
            else:
                print(f"\nFailed to process {filename}")

if __name__ == "__main__":
    main()
