from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import json
import os
import tempfile
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid
from column_classifier import ColumnClassifier

app = FastAPI(title="Data Cleaner API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store session data
sessions = {}
classifier = ColumnClassifier()

class ColumnSelection(BaseModel):
    session_id: str
    selected_columns: List[str]
    output_format: str = "csv"  # csv or xlsx

class AnalysisResult(BaseModel):
    session_id: str
    filename: str
    columns: Dict[str, Dict[str, Any]]
    total_rows: int
    preview_data: List[Dict[str, Any]]

@app.get("/")
async def root():
    return {"message": "Data Cleaner API is running!"}

@app.post("/upload-file", response_model=AnalysisResult)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and analyze a CSV or Excel file.
    Returns column classifications and data preview.
    """
    
    # Validate file type
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="Only CSV and Excel files are supported"
        )
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    try:
        # Read file content
        content = await file.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Read data based on file type
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(tmp_file_path, encoding='utf-8')
        else:
            df = pd.read_excel(tmp_file_path)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        # Validate dataframe
        if df.empty:
            raise HTTPException(status_code=400, detail="File is empty")
        
        if len(df.columns) == 0:
            raise HTTPException(status_code=400, detail="No columns found in file")
        
        # Classify columns
        column_analysis = classifier.classify_columns(df)
        
        # Create preview data (first 10 rows)
        preview_df = df.head(10)
        preview_data = []
        
        for _, row in preview_df.iterrows():
            row_dict = {}
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    row_dict[col] = None
                else:
                    row_dict[col] = str(value)
            preview_data.append(row_dict)
        
        # Store session data
        sessions[session_id] = {
            'dataframe': df,
            'filename': file.filename,
            'column_analysis': column_analysis
        }
        
        return AnalysisResult(
            session_id=session_id,
            filename=file.filename,
            columns=column_analysis,
            total_rows=len(df),
            preview_data=preview_data
        )
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="File is empty or corrupted")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Unable to parse file. Please check file format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/process-columns")
async def process_columns(selection: ColumnSelection):
    """
    Process selected columns and return cleaned data with download file.
    """
    
    if selection.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[selection.session_id]
    df = session_data['dataframe']
    original_filename = session_data['filename']
    
    if not selection.selected_columns:
        raise HTTPException(status_code=400, detail="No columns selected")
    
    # Validate selected columns exist
    invalid_columns = [col for col in selection.selected_columns if col not in df.columns]
    if invalid_columns:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid columns: {invalid_columns}"
        )
    
    try:
        # Filter dataframe to selected columns
        filtered_df = df[selection.selected_columns].copy()
        
        # Create preview data (first 10 rows of filtered data)
        preview_df = filtered_df.head(10)
        preview_data = []
        
        for _, row in preview_df.iterrows():
            row_dict = {}
            for col in selection.selected_columns:
                value = row[col]
                if pd.isna(value):
                    row_dict[col] = None
                else:
                    row_dict[col] = str(value)
            preview_data.append(row_dict)
        
        # Generate output filename
        base_name = os.path.splitext(original_filename)[0]
        output_filename = f"{base_name}_cleaned.{selection.output_format}"
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{selection.output_format}") as tmp_file:
            if selection.output_format == "csv":
                filtered_df.to_csv(tmp_file.name, index=False)
            else:  # xlsx
                filtered_df.to_excel(tmp_file.name, index=False)
            
            output_file_path = tmp_file.name
        
        # Store output file path in session for download
        sessions[selection.session_id]['output_file'] = output_file_path
        sessions[selection.session_id]['output_filename'] = output_filename
        
        return {
            "session_id": selection.session_id,
            "message": "Data processed successfully",
            "preview_data": preview_data,
            "filtered_columns": selection.selected_columns,
            "total_rows": len(filtered_df),
            "download_ready": True,
            "output_filename": output_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.get("/download/{session_id}")
async def download_file(session_id: str):
    """
    Download the processed file.
    """
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    if 'output_file' not in session_data:
        raise HTTPException(status_code=404, detail="No processed file available")
    
    output_file_path = session_data['output_file']
    output_filename = session_data['output_filename']
    
    if not os.path.exists(output_file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=output_file_path,
        filename=output_filename,
        media_type='application/octet-stream'
    )

@app.delete("/session/{session_id}")
async def cleanup_session(session_id: str):
    """
    Clean up session data and temporary files.
    """
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    # Clean up temporary output file if it exists
    if 'output_file' in session_data and os.path.exists(session_data['output_file']):
        os.unlink(session_data['output_file'])
    
    # Remove session data
    del sessions[session_id]
    
    return {"message": "Session cleaned up successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "sessions": len(sessions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
