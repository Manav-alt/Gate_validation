import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pandas as pd
import math
from io import BytesIO

try:
    from temp import (
        bw_scanner,
        extract_gate_info
    )
except ImportError as e:
    st.error(f"Error importing functions from temp.py: {str(e)}")
    st.stop()

try:
    from db import (
        store_extracted_data,
        get_extraction_history,
        delete_record,
        get_record_by_filename,
        filter_records,
        delete_all_records
    )
except ImportError as e:
    st.error(f"Error importing functions from db.py: {str(e)}")
    st.stop()

ADMIN_PASSWORD = "admin123"
ITEMS_PER_PAGE = 10

def admin_login():
    st.sidebar.title("Admin Login")
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        return True
    else:
        if password:
            st.sidebar.error("Invalid Password")
        return False

def export_data(records, format_type):
    if not records:
        return None, None

    df = pd.DataFrame(records)
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
        column_order = [
                    'filename', 
                    'name',
                    'registration_number',
                    'date_of_birth',
                    'gate_score',
                    'all_india_rank',
                    'examination_paper',
                    'exam_year'
                ]
                
        df = df[[col for col in column_order if col in df.columns]]

    if format_type == 'csv':
        data = df.to_csv(index=False).encode('utf-8')
        mime = 'text/csv'
        file_extension = 'csv'
    elif format_type == 'json':
        data = df.to_json(orient='records').encode('utf-8')
        mime = 'application/json'
        file_extension = 'json'
    elif format_type == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Gate Records', index=False)
        data = output.getvalue()
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_extension = 'xlsx'
    else:
        return None, None

    return data, (mime, file_extension)

def implement_export_options():
    st.write("### Export Data")
    export_format = st.selectbox(
        "Choose export format",
        ["CSV", "JSON", "Excel"],
        key="export_format"
    )
    
    records = get_extraction_history()
    if records:
        format_type = export_format.lower()
        data, format_info = export_data(records, format_type)
        
        if data and format_info:
            mime, file_extension = format_info
            st.download_button(
                label=f"Download as {export_format}",
                data=data,
                file_name=f'gate_extraction_data.{file_extension}',
                mime=mime
            )
    else:
        st.write("No data available for export.")

def paginate_records(records, page, items_per_page):
    start = (page - 1) * items_per_page
    end = start + items_per_page
    return records[start:end]

def main():
    st.set_page_config(page_title="GATE Scorecard Extractor", layout="wide")
    st.title("GATE Scorecard Information Extractor")

    is_admin = admin_login()

    if not is_admin:
        st.subheader("Upload GATE Scorecards")
        uploaded_files = st.file_uploader("Choose GATE scorecard images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        if uploaded_files:            
            for uploaded_file in uploaded_files:
                image = Image.open(uploaded_file)
                img_array = np.array(image)

                col1, col2 = st.columns([1, 1])  
                with col1:
                    st.image(image, caption=f"Image: {uploaded_file.name}", use_column_width=True)
                
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                result = bw_scanner(gray)

                extracted_text_gray = pytesseract.image_to_string(gray)
                extracted_text_result = pytesseract.image_to_string(result)
                combined_text = extracted_text_gray + "\n" + extracted_text_result
                extracted_info = extract_gate_info(combined_text)
                store_extracted_data(extracted_info, uploaded_file.name)
                with col2:
                    st.subheader(f"Extracted Information for {uploaded_file.name}")
                    for key, value in extracted_info.items():
                        st.write(f"**{key}:** {value}")

    if is_admin:
        st.sidebar.title("Admin Panel")
        admin_options = ["View Extraction History", "Search Record by name", "Delete Record by name", "Export Data", "Filter Records", "Delete All Records"]
        admin_choice = st.sidebar.selectbox("Choose Action", admin_options)

        if admin_choice == "View Extraction History":
            records = get_extraction_history()
            if records:
                st.write("### Extraction History")
                
                total_pages = math.ceil(len(records) / ITEMS_PER_PAGE)
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
                
                paginated_records = paginate_records(records, page, ITEMS_PER_PAGE)
                
                df = pd.DataFrame(paginated_records)
                if '_id' in df.columns:
                    df = df.drop(columns=['_id'])
                
                column_order = [
                    'filename', 
                    'name',
                    'registration_number',
                    'date_of_birth',
                    'gate_score',
                    'all_india_rank',
                    'examination_paper',
                    'exam_year'
                ]
                
                df = df[[col for col in column_order if col in df.columns]]                
                st.dataframe(df)
                
                st.write(f"Page {page} of {total_pages}")
            else:
                st.write("No extraction records found.")

        elif admin_choice == "Search Record by name":
            file_to_search = st.text_input("Enter the name to search:").upper()
            if st.button("Search Record"):
                if file_to_search:
                    record = get_record_by_filename(file_to_search)
                    if record:
                        st.write("### Record Found")
                        column_order = [
                            'filename',
                            'name',
                            'registration_number',
                            'date_of_birth',
                            'gate_score',
                            'all_india_rank',
                            'examination_paper',
                            'exam_year'
                        ]

                        ordered_record = {key: record[key] for key in column_order if key in record}

                        for key, value in ordered_record.items():
                            st.write(f"**{key}:** {value}")
                    else:
                        st.error(f"No record found for filename '{file_to_search}'.")
                else:
                    st.error("Please provide a filename to search.")

        elif admin_choice == "Delete Record by name":
            file_to_delete = st.text_input("Enter the name to delete:") 
            if st.button("Delete Record"):
                if file_to_delete:
                    delete_record(file_to_delete)
                    st.success(f"Record for file '{file_to_delete}' deleted successfully.")
                else:
                    st.error("Please provide a filename to delete.")

        elif admin_choice == "Export Data":
            implement_export_options()
                
        elif admin_choice == "Filter Records":
            st.write("### Filter Records")
            filter_by = st.selectbox("Filter by", ["Name", "Registration Number", "GATE Score", "date_of_birth", "exam_year", "examination_paper"])
            filter_value = st.text_input(f"Enter {filter_by}:")
            if st.button("Apply Filter"):
                if filter_by == "Name":
                    filter_value = filter_value.upper()
                filtered_records = filter_records(filter_by, filter_value)
                if filtered_records:
                    total_pages = math.ceil(len(filtered_records) / ITEMS_PER_PAGE)
                    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
                    
                    paginated_records = paginate_records(filtered_records, page, ITEMS_PER_PAGE)
                    
                    df = pd.DataFrame(paginated_records)
                    if '_id' in df.columns:
                        df = df.drop(columns=['_id'])
                    
                    column_order = [
                        'filename', 
                        'name',
                        'registration_number',
                        'date_of_birth',
                        'gate_score',
                        'all_india_rank',
                        'examination_paper',
                        'exam_year'
                    ]
                    
                    df = df[[col for col in column_order if col in df.columns]]                
                    st.dataframe(df)
                    
                    st.write(f"Page {page} of {total_pages}")
                else:
                    st.write(f"No records found for {filter_by} = '{filter_value}'.")
                    
        elif admin_choice == "Delete All Records":
            st.write("### Delete All Records")
            st.warning("This will permanently delete **all records** from the database. This action cannot be undone.")
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            if st.button("Delete All Records"):
                st.error("Are you sure you want to delete all records? This action cannot be undone.")
                st.session_state.confirm_delete = True
            if st.session_state.confirm_delete:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete All"):
                        delete_all_records()  
                        st.success("All records have been deleted.")
                        st.session_state.confirm_delete = False
                with col2:
                    if st.button("No, Cancel"):
                        st.info("Operation cancelled.")
                        st.session_state.confirm_delete = False

if __name__ == "__main__":
    main()