<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a full-stack data cleaning and column classification tool with the following architecture:

## Backend (FastAPI)
- Python FastAPI backend located in `/backend/`
- Main API file: `main.py`
- Column classification logic: `column_classifier.py`
- Uses pandas for data processing, openpyxl for Excel files
- Endpoints: `/upload-file`, `/process-columns`, `/download/{session_id}`

## Frontend (Next.js)
- TypeScript Next.js application located in `/frontend/`
- Uses Tailwind CSS for styling
- Components: FileUpload, ColumnAnalysis, ProcessingResult
- Uses react-dropzone for file uploads, lucide-react for icons

## Key Features
- Intelligent column classification using regex patterns and data analysis
- Categories: Business Name, Phone Number, Email, Category, Location, Social Links, Review, Unknown/Junk
- File upload with drag & drop support
- Interactive column selection with confidence scores
- Data preview and download functionality
- Session-based file processing

## Development
- Backend runs on port 8000
- Frontend runs on port 3000
- CORS enabled for local development
- Uses temporary files for processing uploads
