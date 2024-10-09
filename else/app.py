import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pandas as pd
from streamlit_image_zoom import image_zoom  # For zoomable image functionality

# Import functions from temp.py
try:
    from temp import (
        bw_scanner,
        extract_gate_info,
        extract_name,
        extract_parent_name,
        extract_registration_number,
        extract_date_of_birth,
        extract_gate_score,
        extract_examination_paper,
        extract_all_india_rank,
        extract_exam_year
    )
except ImportError as e:
    st.error(f"Error importing functions from temp.py: {str(e)}")
    st.error("Please make sure all required libraries are installed.")
    st.error("You may need to run: pip install scikit-image")
    st.stop()

def main():
    st.set_page_config(page_title="GATE Scorecard Info Extractor", layout="wide")
    st.title("GATE Scorecard Information Extractor")

    # File uploader to select the GATE scorecard image
    uploaded_file = st.file_uploader("Choose a GATE scorecard image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Open the uploaded image
        image = Image.open(uploaded_file)
        
        # Define the layout with two columns: one for the image and one for extracted info
        col1, col2 = st.columns([1, 1])  # Adjust the width ratio of columns as needed

        with col1:
            st.subheader("Preview Image")
            
            # Convert the image to an array to display it
            image_np = np.array(image)
            
            # Use the streamlit-image-zoom library to add zoom functionality to the preview image
            image_zoom(image_np, zoom_factor=2.0)  # Apply zoom functionality directly without st.image

        with col2:
            # When the submit button is clicked, process the image and extract information
            if st.button("Submit"):
                with st.spinner("Processing image..."):
                    img_array = np.array(image)
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    result = bw_scanner(gray)

                    extracted_text_gray = pytesseract.image_to_string(gray)
                    extracted_text_result = pytesseract.image_to_string(result)
                    combined_text = extracted_text_gray + "\n" + extracted_text_result

                    # Extract all GATE information using custom functions
                    extracted_info = extract_gate_info(combined_text)

                # Display extracted information in a table format
                st.subheader("Extracted Information")
                df = pd.DataFrame(list(extracted_info.items()), columns=["Field", "Value"])
                st.table(df)

if __name__ == "__main__":
    main()
