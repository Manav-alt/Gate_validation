from pymongo import MongoClient

# MongoDB setup
def get_database():

    client = MongoClient('mongodb+srv://pathakaman377:dbcluster123@cluster0.kkx1y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['gate_ocr_db']  # Database name
    return db

def store_extracted_data(gate_info, file_name):

    db = get_database()
    collection = db['extracted_data'] 

    document = {
        "filename": file_name,
        "name": gate_info.get('Name'),
        "registration_number": gate_info.get('Registration Number'),
        "date_of_birth": gate_info.get('Date of Birth'),
        "gate_score": gate_info.get('GATE Score'),
        "all_india_rank": gate_info.get('All India Rank'),
        "examination_paper": gate_info.get('Examination Paper'),
        "exam_year": gate_info.get('Exam Year'),
    }

    collection.update_one({"filename": file_name}, {"$set": document}, upsert=True)

def get_extraction_history():

    db = get_database()
    collection = db['extracted_data']
    
    records = list(collection.find({}))
    return records

def delete_record(Name):
    
    db = get_database()
    collection = db['extracted_data']
    
    collection.delete_one({"name": Name})

def get_record_by_filename(Name):
    
    db = get_database()
    collection = db['extracted_data']
    
    record = collection.find_one({"name": Name})
    return record

def filter_records(field_name, field_value):
    
    db = get_database()
    collection = db['extracted_data']

    query = {field_name.lower(): field_value}

    records = list(collection.find(query))
    return records

def delete_all_records():
    
    db = get_database()
    collection = db['extracted_data']
    
    collection.delete_many({})