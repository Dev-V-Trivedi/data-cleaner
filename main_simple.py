from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import csv
import io
import re
import uuid
import os
import pandas as pd
from typing import List, Dict, Any
try:
    from enhanced_column_classifier import EnhancedColumnClassifier
    ENHANCED_CLASSIFIER_AVAILABLE = True
except ImportError:
    from column_classifier import ColumnClassifier
    ENHANCED_CLASSIFIER_AVAILABLE = False
    print("Enhanced classifier not available, using basic classifier")

app = FastAPI(title="Data Cleaner API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Simple in-memory storage for sessions
sessions = {}

# Initialize the column classifier
if ENHANCED_CLASSIFIER_AVAILABLE:
    column_classifier = EnhancedColumnClassifier()
    print("Using Enhanced Column Classifier with improved accuracy!")
else:
    column_classifier = ColumnClassifier()
    print("Using Basic Column Classifier")

# Freemium limits
FREE_TIER_LIMITS = {
    "max_file_size_mb": 5,  # 5MB for free users
    "max_rows": 1000,  # 1000 rows for free users
    "max_columns": 20,  # 20 columns for free users
    "daily_uploads": 10,  # 10 uploads per day for free users
}

PREMIUM_TIER_LIMITS = {
    "max_file_size_mb": 100,  # 100MB for premium users
    "max_rows": 50000,  # 50K rows for premium users
    "max_columns": 100,  # 100 columns for premium users
    "daily_uploads": 1000,  # 1000 uploads per day for premium users
}

# Track usage (in production, use a proper database)
user_usage = {}

def classify_column_simple(data: List[str], column_name: str) -> Dict[str, Any]:
    """Simple column classification without pandas"""
    if not data:
        return {"type": "Unknown", "confidence": 0.0}
    
    # Remove empty/null values
    clean_data = [str(item).strip() for item in data if item and str(item).strip()]
    if not clean_data:
        return {"type": "Unknown", "confidence": 0.0}
    
    # Phone number patterns
    phone_patterns = [
        r'\b\d{10}\b',  # 1234567890
        r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',  # 123-456-7890
        r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # (123) 456-7890
    ]
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Business categories
    business_keywords = [
        'restaurant', 'cafe', 'store', 'shop', 'market', 'hotel', 'motel',
        'hospital', 'clinic', 'pharmacy', 'bank', 'school', 'gym', 'spa',
        'salon', 'bar', 'pub', 'office', 'company', 'corp', 'inc', 'llc'
    ]
    
    # Count matches
    phone_matches = 0
    email_matches = 0
    business_matches = 0
    
    sample_size = min(100, len(clean_data))  # Check first 100 items
    sample_data = clean_data[:sample_size]
    
    for item in sample_data:
        item_lower = item.lower()
        
        # Check phone patterns
        for pattern in phone_patterns:
            if re.search(pattern, item):
                phone_matches += 1
                break
        
        # Check email
        if re.search(email_pattern, item):
            email_matches += 1
        
        # Check business keywords
        if any(keyword in item_lower for keyword in business_keywords):
            business_matches += 1
    
    # Calculate percentages
    phone_pct = phone_matches / sample_size
    email_pct = email_matches / sample_size
    business_pct = business_matches / sample_size
    
    # Determine type based on highest confidence
    if phone_pct > 0.7:
        return {"type": "Phone Number", "confidence": phone_pct}
    elif email_pct > 0.7:
        return {"type": "Email", "confidence": email_pct}
    elif business_pct > 0.5:
        return {"type": "Category", "confidence": business_pct}
    elif 'name' in column_name.lower() and business_pct > 0.2:
        return {"type": "Business Name", "confidence": 0.8}
    elif 'location' in column_name.lower() or 'address' in column_name.lower():
        return {"type": "Location", "confidence": 0.8}
    else:
        return {"type": "Unknown", "confidence": 0.3}

@app.get("/")
async def root():
    return {"message": "Data Cleaner API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/pricing")
async def get_pricing():
    """Get pricing tiers and features"""
    return {
        "tiers": {
            "free": {
                "name": "Free Tier",
                "price": "$0/month",
                "features": [
                    "Up to 1,000 rows per file",
                    "Up to 10 columns per file",
                    "5MB file size limit",
                    "10 uploads per day",
                    "Basic column classification",
                    "CSV export"
                ],
                "limits": FREE_TIER_LIMITS
            },
            "premium": {
                "name": "Premium Tier",
                "price": "$9.99/month",
                "features": [
                    "Up to 50,000 rows per file",
                    "Up to 100 columns per file", 
                    "100MB file size limit",
                    "1,000 uploads per day",
                    "Advanced column classification",
                    "CSV export",
                    "Priority support",
                    "No ads"
                ],
                "limits": PREMIUM_TIER_LIMITS
            }
        },
        "buymeacoffee": {
            "url": "https://buymeacoffee.com/datacleaner",
            "message": "Support this project! ☕"
        }
    }

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...), is_premium: bool = False):
    """Upload and analyze CSV file with freemium restrictions"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read file content
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        # Check freemium limits
        limits = PREMIUM_TIER_LIMITS if is_premium else FREE_TIER_LIMITS
        
        if file_size_mb > limits["max_file_size_mb"]:
            raise HTTPException(
                status_code=413, 
                detail=f"File size ({file_size_mb:.1f}MB) exceeds {'premium' if is_premium else 'free'} tier limit of {limits['max_file_size_mb']}MB"
            )
        
        text_content = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(text_content))
        rows = list(csv_reader)
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Check row and column limits
        if len(rows) > limits["max_rows"]:
            raise HTTPException(
                status_code=413,
                detail=f"File has {len(rows)} rows, exceeds {'premium' if is_premium else 'free'} tier limit of {limits['max_rows']} rows"
            )
        
        columns = list(rows[0].keys())
        if len(columns) > limits["max_columns"]:
            raise HTTPException(
                status_code=413,
                detail=f"File has {len(columns)} columns, exceeds {'premium' if is_premium else 'free'} tier limit of {limits['max_columns']} columns"
            )
        
        # Extract column data and create DataFrame for enhanced classification
        if ENHANCED_CLASSIFIER_AVAILABLE:
            # Use pandas DataFrame for enhanced classifier
            df = pd.DataFrame(rows)
            
            # Use enhanced classifier
            classification_results = column_classifier.classify_columns(df)
            
            # Convert to the expected format
            classifications = {}
            for col_name, result in classification_results.items():
                classifications[col_name] = {
                    "type": result['suggested_category'],
                    "confidence": result['confidence']
                }
        else:
            # Fallback to simple classification
            column_data = {}
            for col in columns:
                column_data[col] = [row.get(col, '') for row in rows]
            
            # Classify columns using simple method
            classifications = {}
            for col_name, col_data in column_data.items():
                classifications[col_name] = classify_column_simple(col_data, col_name)
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'filename': file.filename,
            'columns': columns,
            'data': rows,
            'classifications': classifications,
            'row_count': len(rows),
            'file_size_mb': file_size_mb,
            'is_premium': is_premium
        }
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "columns": columns,
            "classifications": classifications,
            "row_count": len(rows),
            "file_size_mb": round(file_size_mb, 2),
            "tier": "premium" if is_premium else "free",
            "limits_used": {
                "rows": f"{len(rows)}/{limits['max_rows']}",
                "columns": f"{len(columns)}/{limits['max_columns']}",
                "file_size": f"{file_size_mb:.1f}MB/{limits['max_file_size_mb']}MB"
            },
            "sample_data": rows[:10] if len(rows) > 0 else [],  # First 10 rows for preview
            "total_columns": len(columns),
            "total_rows": len(rows)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/process-columns")
async def process_columns(data: Dict[str, Any]):
    """Process columns based on user selections"""
    try:
        session_id = data.get('session_id')
        selected_columns = data.get('selected_columns', {})
        
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        
        # Filter data based on selected columns
        filtered_data = []
        for row in session['data']:
            filtered_row = {}
            for col_name, include in selected_columns.items():
                if include and col_name in row:
                    filtered_row[col_name] = row[col_name]
            if filtered_row:  # Only add non-empty rows
                filtered_data.append(filtered_row)
        
        # Update session with processed data
        session['processed_data'] = filtered_data
        session['selected_columns'] = selected_columns
        
        return {
            "message": "Columns processed successfully",
            "processed_rows": len(filtered_data),
            "selected_columns": list(selected_columns.keys())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing columns: {str(e)}")

@app.get("/download/{session_id}")
async def download_processed_file(session_id: str):
    """Download processed CSV file"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = sessions[session_id]
        processed_data = session.get('processed_data', [])
        
        if not processed_data:
            raise HTTPException(status_code=400, detail="No processed data available")
        
        # Create CSV content
        output = io.StringIO()
        if processed_data:
            fieldnames = processed_data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_data)
        
        csv_content = output.getvalue()
        
        return JSONResponse(
            content={"csv_data": csv_content, "filename": f"cleaned_{session['filename']}"},
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
