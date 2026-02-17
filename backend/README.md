# Backend API Documentation

FastAPI backend service that accepts earnings reports, extracts financial metrics using an LLM, and returns an Excel file with the extracted data.

## Tech Stack

- **FastAPI**
- **OpenAI API** - LLM for financial data extraction
- **spaCy** - Sentence segmentation
- **pdfplumber** - PDF text and table extraction
- **pandas** - Data organization and Excel generation

## Project Structure

```
backend/
├── __init__.py           # Package initialization
├── main.py               # FastAPI app entry point
├── utils.py              # Utility functions (data transformation, formatting)
├── routers/
│   ├── __init__.py       
│   └── reports.py        # Reports API endpoints
└── services/
    ├── __init__.py       
    └── extraction.py    # PDF extraction and LLM processing logic
```

## Setup

### Tested On

- Python 3.9+

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

3. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-openai-api-key
```

## Running the Server

### Development

```bash
cd backend
uvicorn main:app --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/reports/process`

Process one or more PDF files and return an Excel spreadsheet with extracted financial metrics.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** `files` (array of PDF files)

**Response:**
- **Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Body:** Excel file stream

**Constraints:**
- Only PDF files are accepted (`application/pdf`)
- Maximum file size: 20MB per file

## Extracted Metrics

The service extracts the following financial metrics from each PDF:

- **Company Name** - Name of the company
- **Quarter** - Quarter in format "Q(number) (year)" (e.g., "Q3 2024")
- **Total Revenue** - With YoY and QoQ percentages
- **Earnings Per Share** - With YoY and QoQ percentages
- **Net Income** - With YoY and QoQ percentages
- **Operating Income** - With YoY and QoQ percentages
- **Gross Margin** - Percentage with YoY and QoQ
- **Operating Expenses** - With YoY and QoQ percentages
- **Buybacks and Dividends** - Combined or separate values
- **Performance** - Score from -5 to 5 representing quarter performance

## Architecture

### Layers

1. **Routers** (`routers/reports.py`)
   - Handle HTTP requests/responses
   - Validate file uploads
   - Excel file generation and streaming

2. **Services** (`services/extraction.py`)
   - PDF parsing and text extraction
   - Sentence filtering using NLP
   - Table extraction and validation
   - LLM prompt construction and API calls
   - JSON parsing

3. **Utils** (`utils.py`)
   - Data transformation and formatting
   - Number magnitude conversion (K/M/B)
   - Table validation logic

### Processing Flow

1. Receive PDF files via form upload
2. Validate file type and size
3. For each PDF:
   - Extract text using pdfplumber
   - Segment sentences using spaCy
   - Filter relevant sentences (containing $, gross, million, billion, %)
   - Extract and validate tables
   - Combine metadata, text, and tables
   - Send to OpenAI API with structured prompt
   - Parse JSON response
   - Transform data to human-readable format
4. Combine all results into pandas DataFrame
5. Generate Excel file and stream response
