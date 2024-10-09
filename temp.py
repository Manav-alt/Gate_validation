import re
import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pytesseract import Output
from prettytable import PrettyTable


def bw_scanner(image):
    
    if len(image.shape) == 3:  
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image  

   
    pil_img = Image.fromarray(gray)
    threshold_img = pil_img.point(lambda p: p > 190 and 255)
    threshold_img_np = np.array(threshold_img)

    return threshold_img_np


def convert_to_paragraph(text):
    return ', '.join(line.strip() for line in text.split('\n') if line.strip())


def extract_registration_number(text):
    patterns = [
        r'Registration\s*Number\s*:?\s*([A-Z]{2}\d{2}[A-Z]\d{8})',
        r'([A-Z]{2}\d{2}[A-Z]\d{8})',
        r'Registration\s*Number\s*:?\s*(\S+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "Not found"


def extract_name(text):
    patterns = [
        r'Name of Candidate\s*[:|]\s*([\w\s.]+?)(?:\n|$)',
        r"Candidate['']s Name\s*[:|]\s*([\w\s.]+?)(?:\n|$)",
        r'Name\s*[:|]\s*([\w\s.]+?)(?:\n|$)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Not found"

def extract_parent_name(text):
    patterns = [
        r"Parent's/Guardian's\s*(?:Name\s*)?\s*([A-Z\s]+(?:\s+[A-Z\s]+){1,3})",
        r"Parent's/Guardian's\s*\n\s*([A-Z\s]+(?:\s+[A-Z\s]+){1,3})",
        r"Parent's/Guardian's\s*([A-Z][A-Z\s]+(?:\s+[A-Z][A-Z\s]+){1,2})",
        r"Parent's/Guardian's\s*([A-Z][a-z]+\s+(?:[A-Z][a-z]+\s+){1,2}[A-Z][a-z]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return "Not found"


def extract_gate_score(text):
    pattern = r'GATE Score\s*:?\s*(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else "Not found"

def extract_date_of_birth(text):
    pattern = r'Date of Birth\s*:?\s*(\d{1,2})[-\s](\w{3})[-\s](\d{4})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        day, month, year = match.groups()
        return f"{day} {month} {year}"
    return "Not found"

def extract_examination_paper(text):
    pattern = r'Examination Paper\s*(.*?)(?=\n)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else "Not found"


def extract_all_india_rank(text):
    pattern = r'All\s*India\s*Rank\s*in\s*this\s*paper\s*[:|]?\s*(\d{2,4})'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else "Not found"

def extract_exam_year(text):
    patterns = [
        r'GATE\s+(\d{4})',
        r'Examination Year:\s*(\d{4})',
        r'Year of Examination:\s*(\d{4})'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "Not found"

def extract_gate_info(text):
    return {
        'Name': extract_name(text),
        # "Parent's/Guardian's Name": extract_parent_name(text),
        'Registration Number': extract_registration_number(text),
        'Date of Birth': extract_date_of_birth(text),
        'GATE Score': extract_gate_score(text),
        'Examination Paper': extract_examination_paper(text),
        'All India Rank': extract_all_india_rank(text),
        'Exam Year': extract_exam_year(text)
    }

# Display extracted results in tabular format
# def display_results(results):
#     table = PrettyTable()
#     table.field_names = ["Field", "Value"]
#     table.align["Field"] = "l"
#     table.align["Value"] = "l"
    
#     for key, value in results.items():
#         table.add_row([key, value])
    
#     print(table)

# Main code block
# img_name = '/Users/manavpathak/Gate_Validation/images/Scorecard2.jpeg'
# image = cv2.imread(img_name)

# Convert image to grayscale and process for better OCR
# grayi = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# result = bw_scanner(grayi)

# Extract text from the grayscale and processed image
# extracted_text_grayi = pytesseract.image_to_string(grayi)
# extracted_text_result = pytesseract.image_to_string(result)

# Combine both texts for comprehensive extraction
# combined_text = extracted_text_grayi + "\n" + extracted_text_result

# Extract GATE information from the combined text
# extracted_info = extract_gate_info(combined_text)

# Display the extracted information in a table format
# display_results(extracted_info)
