import cv2
import pytesseract
import re
import pandas as pd
from prettytable import PrettyTable

# Load the image
image_path = 'images/Scorecard3.jpeg'  # Replace with your image path
image = cv2.imread(image_path)

# Convert to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding
_, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY_INV)

# Specify the path to the Tesseract executable if necessary
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # Update this path as needed

# Use Tesseract to do OCR on the image
extracted_text = pytesseract.image_to_string(thresh_image)

# Print the extracted text for debugging
print("Extracted Text:")
print(extracted_text)

# Parse the extracted text
try:
    name = re.search(r'Name:\s*(.*)', extracted_text, re.IGNORECASE).group(1).strip()
    fathers_name = re.search(r"Father's Name:\s*(.*)", extracted_text, re.IGNORECASE).group(1).strip()
    registration_number = re.search(r'Registration Number:\s*(.*)', extracted_text, re.IGNORECASE).group(1).strip()
    date_of_birth = re.search(r'Date of Birth:\s*(.*)', extracted_text, re.IGNORECASE).group(1).strip()
    gate_score = re.search(r'Gate Score:\s*(.*)', extracted_text, re.IGNORECASE).group(1).strip()
except AttributeError:
    print("Error: Could not parse some fields from the extracted text.")
    exit()

# Create a DataFrame
data_fields = {
    "Name": name,
    "Father's Name": fathers_name,
    "Registration Number": registration_number,
    "Date of Birth": date_of_birth,
    "Gate Score": gate_score
}
df = pd.DataFrame([data_fields])

# Display the DataFrame
print("\nData extracted using pandas:")
print(df)

# Create a PrettyTable object
table = PrettyTable()

# Define the columns
table.field_names = ["Field", "Value"]

# Add rows for each extracted field
table.add_row(["Name", data_fields["Name"]])
table.add_row(["Father's Name", data_fields["Father's Name"]])
table.add_row(["Registration Number", data_fields["Registration Number"]])
table.add_row(["Date of Birth", data_fields["Date of Birth"]])
table.add_row(["Gate Score", data_fields["Gate Score"]])

# Print the table
print("\nData extracted using PrettyTable:")
print(table)