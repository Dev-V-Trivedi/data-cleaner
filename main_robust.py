from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
import io
import re
import uuid
import os
from typing import List, Dict, Any

# Try to import pandas and enhanced classifier
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print("✅ Pandas available")
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️ Pandas not available, using basic mode")

try:
    import openpyxl
    EXCEL_SUPPORT = True
    print("✅ Excel support available")
except ImportError:
    EXCEL_SUPPORT = False
    print("⚠️ Excel support not available")

try:
    if PANDAS_AVAILABLE:
        from enhanced_column_classifier import EnhancedColumnClassifier
        ENHANCED_CLASSIFIER_AVAILABLE = True
        print("✅ Enhanced classifier available")
    else:
        ENHANCED_CLASSIFIER_AVAILABLE = False
except ImportError:
    ENHANCED_CLASSIFIER_AVAILABLE = False
    print("⚠️ Enhanced classifier not available")

try:
    if PANDAS_AVAILABLE:
        from ai_enhanced_classifier import AIEnhancedColumnClassifier
        AI_CLASSIFIER_AVAILABLE = True
        print("✅ AI Enhanced classifier available")
    else:
        AI_CLASSIFIER_AVAILABLE = False
except ImportError:
    AI_CLASSIFIER_AVAILABLE = False
    print("⚠️ AI Enhanced classifier not available")

try:
    from column_classifier import ColumnClassifier
    BASIC_CLASSIFIER_AVAILABLE = True
    print("✅ Basic classifier available")
except ImportError:
    BASIC_CLASSIFIER_AVAILABLE = False
    print("⚠️ Basic classifier not available")

app = FastAPI(title="Data Cleaner API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for sessions
sessions = {}

# Initialize the column classifier
classifier = None
classifier_type = "none"

# Try AI Enhanced classifier first (best accuracy)
if AI_CLASSIFIER_AVAILABLE:
    try:
        classifier = AIEnhancedColumnClassifier()
        classifier_type = "ai_enhanced"
        print("🤖 Using AI Enhanced Column Classifier with OpenRouter API")
    except Exception as e:
        print(f"❌ Failed to initialize AI classifier: {e}")
        classifier = None

# Fallback to enhanced classifier
if classifier is None and ENHANCED_CLASSIFIER_AVAILABLE:
    try:
        classifier = EnhancedColumnClassifier()
        classifier_type = "enhanced"
        print("🚀 Using Enhanced Column Classifier")
    except Exception as e:
        print(f"❌ Failed to initialize enhanced classifier: {e}")
        classifier = None

# Fallback to basic classifier
if classifier is None and BASIC_CLASSIFIER_AVAILABLE:
    try:
        classifier = ColumnClassifier()
        classifier_type = "basic"
        print("📊 Using Basic Column Classifier")
    except Exception as e:
        print(f"❌ Failed to initialize basic classifier: {e}")
        classifier = None

if classifier is None:
    classifier_type = "simple"
    print("⚙️ Using Simple Built-in Classifier")

# No limits - free for everyone!
NO_LIMITS = {
    "max_file_size_mb": 100,  # 100MB
    "max_rows": 100000,       # 100k rows
    "max_columns": 1000,      # 1000 columns
    "daily_uploads": 1000,    # 1000 uploads per day
}

def classify_column_simple(data: List[str], column_name: str) -> Dict[str, Any]:
    """Simple column classification without external dependencies"""
    if not data:
        return {"type": "Unknown / Junk", "confidence": 0.0}
    
    # Remove empty/null values
    clean_data = [str(item).strip() for item in data if item and str(item).strip()]
    if not clean_data:
        return {"type": "Unknown / Junk", "confidence": 0.0}
    
    # Enhanced simple patterns
    phone_patterns = [
        r'\b\d{10}\b',  # 1234567890
        r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',  # 123-456-7890
        r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # (123) 456-7890
        r'\+?1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-123-456-7890
    ]
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    website_patterns = [
        r'https?://[^\s]+',
        r'www\.[^\s]+',
        r'[a-zA-Z0-9.-]+\.(com|org|net|edu|gov|co\.uk|co\.in)\b'
    ]
    
    business_keywords = [
        'restaurant', 'cafe', 'store', 'shop', 'market', 'hotel', 'motel',
        'hospital', 'clinic', 'pharmacy', 'bank', 'school', 'gym', 'spa',
        'salon', 'bar', 'pub', 'office', 'company', 'corp', 'inc', 'llc',
        'pizza', 'bakery', 'auto', 'repair', 'service', 'center'
    ]
    
    location_keywords = [
        'street', 'road', 'avenue', 'drive', 'lane', 'boulevard',
        'address', 'city', 'state', 'zip', 'postal', 'main st',
        'north', 'south', 'east', 'west', 'ave', 'blvd', 'dr'
    ]
    
    # Count matches
    phone_matches = 0
    email_matches = 0
    website_matches = 0
    business_matches = 0
    location_matches = 0
    
    sample_size = min(50, len(clean_data))
    sample_data = clean_data[:sample_size]
    
    for item in sample_data:
        item_lower = item.lower()
        
        # Phone patterns
        if any(re.search(pattern, item) for pattern in phone_patterns):
            phone_matches += 1
        
        # Email
        elif re.search(email_pattern, item):
            email_matches += 1
        
        # Website/Social
        elif any(re.search(pattern, item_lower) for pattern in website_patterns):
            website_matches += 1
        
        # Business categories
        elif any(keyword in item_lower for keyword in business_keywords):
            business_matches += 1
        
        # Location
        elif any(keyword in item_lower for keyword in location_keywords):
            location_matches += 1
    
    # Calculate percentages
    phone_pct = phone_matches / sample_size
    email_pct = email_matches / sample_size
    website_pct = website_matches / sample_size
    business_pct = business_matches / sample_size
    location_pct = location_matches / sample_size
    
    # Column name hints
    col_lower = column_name.lower()
    
    # Determine type with enhanced logic
    if phone_pct > 0.6 or 'phone' in col_lower or 'mobile' in col_lower:
        return {"type": "Phone Number", "confidence": max(0.8, phone_pct)}
    elif email_pct > 0.6 or 'email' in col_lower or 'mail' in col_lower:
        return {"type": "Email", "confidence": max(0.8, email_pct)}
    elif website_pct > 0.4 or 'website' in col_lower or 'url' in col_lower or 'link' in col_lower:
        return {"type": "Social Links", "confidence": max(0.7, website_pct)}
    elif business_pct > 0.4 or any(word in col_lower for word in ['type', 'category', 'service']):
        return {"type": "Category", "confidence": max(0.6, business_pct)}
    elif location_pct > 0.3 or any(word in col_lower for word in ['address', 'location', 'city', 'state']):
        return {"type": "Location", "confidence": max(0.7, location_pct)}
    elif 'name' in col_lower and 'business' in col_lower:
        return {"type": "Business Name", "confidence": 0.8}
    elif 'review' in col_lower or 'rating' in col_lower or 'comment' in col_lower:
        return {"type": "Review", "confidence": 0.8}
    elif 'hour' in col_lower or 'time' in col_lower or 'schedule' in col_lower:
        return {"type": "Hours", "confidence": 0.8}
    elif 'price' in col_lower or 'cost' in col_lower or '$' in col_lower:
        return {"type": "Price", "confidence": 0.8}
    else:
        return {"type": "Unknown / Junk", "confidence": 0.3}

@app.get("/")
async def root():
    return {
        "message": "Data Cleaner API is running!",
        "status": "healthy",
        "classifier": classifier_type,
        "pandas_available": PANDAS_AVAILABLE,
        "enhanced_classifier": ENHANCED_CLASSIFIER_AVAILABLE
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is running",
        "classifier_type": classifier_type,
        "features": {
            "pandas": PANDAS_AVAILABLE,
            "enhanced_classifier": ENHANCED_CLASSIFIER_AVAILABLE,
            "basic_classifier": BASIC_CLASSIFIER_AVAILABLE
        }
    }

@app.get("/pricing")
async def get_pricing():
    """Get service information and support links"""
    return {
        "service": {
            "name": "Data Cleaner",
            "description": "AI-powered CSV and Excel data cleaning service",
            "features": [
                "AI-powered column classification",
                "CSV and Excel file support",
                "Up to 100,000 rows per file",
                "Up to 1,000 columns per file", 
                "100MB file size limit",
                "Smart data cleaning",
                "Instant preview and download"
            ]
        },
        "buymeacoffee": {
            "url": "https://buymeacoffee.com/datacleaner",
            "message": "Support this project! ☕"
        }
    }

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze CSV/Excel file with intelligent classification"""
    try:
        # Check file extension
        file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if file_ext not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Read file content
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        # Check file size limits (generous limits for everyone)
        limits = NO_LIMITS
        
        if file_size_mb > limits["max_file_size_mb"]:
            raise HTTPException(
                status_code=413, 
                detail=f"File size ({file_size_mb:.1f}MB) exceeds maximum limit of {limits['max_file_size_mb']}MB"
            )
        
        # Parse file based on type
        rows = []
        if file_ext == 'csv':
            text_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(text_content))
            rows = list(csv_reader)
        elif file_ext in ['xlsx', 'xls']:
            if not EXCEL_SUPPORT:
                raise HTTPException(status_code=400, detail="Excel support not available. Please convert to CSV.")
            
            # Use pandas to read Excel
            if PANDAS_AVAILABLE:
                try:
                    df = pd.read_excel(io.BytesIO(content))
                    rows = df.to_dict('records')
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail="Excel support requires pandas. Please convert to CSV.")
        
        if not rows:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Check row and column limits
        if len(rows) > limits["max_rows"]:
            raise HTTPException(
                status_code=413,
                detail=f"File has {len(rows)} rows, exceeds maximum limit of {limits['max_rows']} rows"
            )
        
        columns = list(rows[0].keys())
        if len(columns) > limits["max_columns"]:
            raise HTTPException(
                status_code=413,
                detail=f"File has {len(columns)} columns, exceeds maximum limit of {limits['max_columns']} columns"
            )
        
        # Classify columns based on available classifier
        classifications = {}
        
        if classifier and classifier_type in ["ai_enhanced", "enhanced", "basic"]:
            try:
                if classifier_type == "ai_enhanced" and PANDAS_AVAILABLE:
                    # Use AI enhanced classifier with pandas
                    df = pd.DataFrame(rows)
                    classification_results = classifier.classify_columns(df)
                    
                    for col_name, result in classification_results.items():
                        classifications[col_name] = {
                            "type": result['suggested_category'],
                            "confidence": result['confidence'],
                            "ai_enhanced": result.get('ai_enhanced', False),
                            "ai_reasoning": result.get('ai_reasoning', None)
                        }
                elif classifier_type == "enhanced" and PANDAS_AVAILABLE:
                    # Use enhanced classifier with pandas
                    df = pd.DataFrame(rows)
                    classification_results = classifier.classify_columns(df)
                    
                    for col_name, result in classification_results.items():
                        classifications[col_name] = {
                            "type": result['suggested_category'],
                            "confidence": result['confidence']
                        }
                else:
                    # Use basic classifier (if available)
                    for col in columns:
                        col_data = [row.get(col, '') for row in rows]
                        result = classifier._classify_business_name(col_data) if hasattr(classifier, '_classify_business_name') else 0.5
                        classifications[col] = {"type": "Business Name", "confidence": result}
            except Exception as e:
                print(f"Classifier error: {e}, falling back to simple classification")
                # Fallback to simple classification
                for col in columns:
                    col_data = [row.get(col, '') for row in rows]
                    classifications[col] = classify_column_simple(col_data, col)
        else:
            # Use simple built-in classification
            for col in columns:
                col_data = [row.get(col, '') for row in rows]
                classifications[col] = classify_column_simple(col_data, col)
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'filename': file.filename,
            'columns': columns,
            'data': rows,
            'classifications': classifications,
            'row_count': len(rows),
            'file_size_mb': file_size_mb
        }
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "columns": columns,
            "classifications": classifications,
            "row_count": len(rows),
            "file_size_mb": round(file_size_mb, 2),
            "classifier_used": classifier_type,
            "message": f"File analyzed successfully using {classifier_type} classifier",
            "sample_data": rows[:10] if len(rows) > 0 else [],  # First 10 rows for preview
            "total_columns": len(columns),
            "total_rows": len(rows)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/process-columns")
async def process_columns(request: dict):
    """Process selected columns and clean data"""
    try:
        session_id = request.get("session_id")
        selected_columns = request.get("selected_columns", {})
        
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = sessions[session_id]
        
        # Filter data to only include selected columns
        selected_col_names = [col for col, selected in selected_columns.items() if selected]
        
        if not selected_col_names:
            raise HTTPException(status_code=400, detail="No columns selected")
        
        # Create proper column headers based on classification
        column_headers = {}
        classifications = session_data.get('classifications', {})
        
        for col_name in selected_col_names:
            classification = classifications.get(col_name, {})
            detected_type = classification.get('type', 'Unknown')
            
            # Map detected types to proper headers
            header_mapping = {
                'Business Name': 'Business Name',
                'Phone Number': 'Phone Number', 
                'Email': 'Email Address',
                'Category': 'Business Category',
                'Location': 'Address/Location',
                'Social Links': 'Website/Social Media',
                'Review': 'Customer Review',
                'Hours': 'Operating Hours',
                'Price': 'Price/Cost',
                'Unknown / Junk': col_name  # Keep original name for unknown
            }
            
            column_headers[col_name] = header_mapping.get(detected_type, col_name)
        
        # Create cleaned data with proper headers
        cleaned_data = []
        for row in session_data['data']:
            cleaned_row = {}
            for original_col, new_header in column_headers.items():
                cleaned_row[new_header] = row.get(original_col, '')
            cleaned_data.append(cleaned_row)
        
        # Update session with processed data
        sessions[session_id]['processed_data'] = cleaned_data
        sessions[session_id]['selected_columns'] = selected_col_names
        sessions[session_id]['column_headers'] = column_headers
        
        # Return preview of first 10 rows
        preview_data = cleaned_data[:10] if len(cleaned_data) > 0 else []
        
        return {
            "message": f"Successfully processed {len(cleaned_data)} rows with {len(selected_col_names)} columns",
            "processed_rows": len(cleaned_data),
            "selected_columns": selected_col_names,
            "column_headers": column_headers,
            "preview_data": preview_data,  # First 10 rows of processed data
            "total_rows": len(cleaned_data),
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing columns: {str(e)}")

@app.get("/download/{session_id}")
async def download_processed_file(session_id: str):
    """Download processed CSV file"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = sessions[session_id]
        
        # Get processed data or fallback to original data
        data_to_export = session_data.get('processed_data', session_data['data'])
        
        if not data_to_export:
            raise HTTPException(status_code=400, detail="No data to download")
        
        # Create CSV content
        output = io.StringIO()
        if data_to_export:
            writer = csv.DictWriter(output, fieldnames=data_to_export[0].keys())
            writer.writeheader()
            writer.writerows(data_to_export)
        
        csv_content = output.getvalue()
        
        # Generate filename
        original_filename = session_data['filename']
        base_name = original_filename.rsplit('.', 1)[0]
        cleaned_filename = f"cleaned_{base_name}.csv"
        
        return {
            "csv_data": csv_content,
            "filename": cleaned_filename,
            "row_count": len(data_to_export),
            "message": "File ready for download"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating download: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
