from flask import Flask, render_template, request
import pytesseract
import cv2
import os

app = Flask(__name__)

# Function to extract text from an image
def extract_text_from_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Tesseract to extract text
    extracted_text = pytesseract.image_to_string(gray)
    
    return extracted_text

# Function to extract fields from the text
def extract_fields(extracted_text):
    lines = extracted_text.split('\n')
    
    # Initialize empty variables to store extracted values
    name = None
    father_name = None
    registration_number = None
    date_of_birth = None
    gate_score = None
    marks = None

    # Iterate through each line to search for the patterns
    for i, line in enumerate(lines):
        if "Name of Candidate" in line:
            name = line.split(':')[-1].strip()
        elif "Candidate's Name" in line:
            name = line.split(':')[-1].strip()
        
        if "Parent's/Guardian’s" in line or "Parent's/Guardian's" in line:
            if ':' in line:
                father_name = line.split(':')[-1].strip()
            elif i + 1 < len(lines):
                potential_father_name = lines[i + 1].strip()
                if potential_father_name and not any(char.isdigit() for char in potential_father_name):
                    father_name = potential_father_name
        
        if "Registration Number" in line:
            registration_number = line.split(':')[-1].strip()
        
        if "Date of Birth" in line:
            date_of_birth = line.split(':')[-1].strip()
            if 'Date of Birth' in date_of_birth:
                date_of_birth = date_of_birth.replace('Date of Birth', '').strip()
        
        if "GATE Score" in line or "GATE score" in line:
            gate_score = line.split()[-1].strip()
        
        if "Marks out of 100" in line:
            marks = line.split(':')[-1].strip()

    return {
        "Name of Candidate": name,
        "Parent's/Guardian's": father_name,
        "Registration Number": registration_number,
        "Date of Birth": date_of_birth,
        "GATE Score": gate_score,
        "Marks out of 100": marks
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form fields
        form_data = {
            "Name of Candidate": request.form.get('name'),
            "Parent's/Guardian's": request.form.get('parent_name'),
            "Registration Number": request.form.get('registration_number'),
            "Date of Birth": request.form.get('dob'),
            "GATE Score": request.form.get('gate_score'),
            "Marks out of 100": request.form.get('marks')
        }

        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            image_path = os.path.join('static', image.filename)
            image.save(image_path)

            # Extract fields from image
            extracted_text = extract_text_from_image(image_path)
            image_data = extract_fields(extracted_text)
        else:
            image_data = {}

        return render_template('result.html', form_data=form_data, image_data=image_data)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
