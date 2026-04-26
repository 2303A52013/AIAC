# A Context-Aware Multi-Page Reasoning System Using Hierarchical PageIndex Architecture for Efficient Knowledge Retrieval

This project is a web application that allows users to upload PDF documents and ask questions about them. Instead of manually reading long documents, the system finds relevant sections and generates answers using an AI model.

The main idea is to break the document into smaller sections, organize them in a hierarchical structure (PageIndex), and use only the important parts for answering queries.

--------------------------------------------------

What it does

- Upload a PDF file
- Ask questions related to the document
- Extract text from the PDF
- Split content into structured sections
- Identify relevant parts of the document
- Generate answers using an AI model

--------------------------------------------------

Features

- Works with PDF files (up to 16MB)
- Context-aware question answering
- Uses NVIDIA LLM (meta/llama-3.1-8b-instruct)
- Simple and clean web interface
- Stores extracted text locally for reuse

--------------------------------------------------

Tech Stack

- Python (Flask)
- pdfplumber (PDF parsing)
- NVIDIA API (OpenAI-compatible)
- HTML, CSS (frontend)

--------------------------------------------------

Project Structure

A Context-Aware Multi-Page Reasoning System Using Hierarchical PageIndex Architecture for Efficient Knowledge Retrieval/
│
├── app.py              # Flask web app (handles routing and UI)
├── main.py             # CLI version for testing
├── parser.py           # Extracts text from PDFs
├── tree.py             # Builds hierarchical PageIndex structure
├── reasoner.py         # Handles query processing and AI responses
│
├── templates/
│   ├── index.html      # Upload page
│   └── result.html     # Results display page
│
├── stored_texts/       # Cached extracted text
│
└── README.md

--------------------------------------------------

Setup

1. Clone the repository

git clone https://github.com/2303A52013/AIAC.git
cd AIAC/Project/"A Context-Aware Multi-Page Reasoning System Using Hierarchical PageIndex Architecture for Efficient Knowledge Retrieval"

2. Create virtual environment

python -m venv .venv

3. Activate environment

Windows:
.venv\Scripts\activate

Mac/Linux:
source .venv/bin/activate

4. Install dependencies

pip install flask python-dotenv openai pdfplumber

--------------------------------------------------

Environment Variables

Create a .env file:

NVIDIA_API_KEY=your_api_key_here

--------------------------------------------------

Run the Application

python app.py

Open in browser:
http://localhost:5000

--------------------------------------------------

How to Use

1. Upload a PDF
2. Enter a question
3. Click "Analyze Document"
4. View:
   - Answer
   - Reasoning
   - Relevant sections

--------------------------------------------------

How it works (simple explanation)

1. PDF is converted into text  
2. Text is split into logical sections  
3. Sections are organized into a tree (PageIndex)  
4. System selects relevant sections based on query  
5. AI model generates answer from selected content  

Instead of searching everything blindly, the system iteratively selects useful sections and builds the answer step by step, similar to reasoning-based retrieval. :contentReference[oaicite:1]{index=1}

--------------------------------------------------

Limitations

- Works best with text-based PDFs
- Not suitable for scanned/image PDFs
- Retrieval logic is basic (can be improved)
- Runs locally (no deployment yet)

--------------------------------------------------

Future Improvements

- Add semantic search (embeddings)
- Support multiple PDFs
- Improve UI/UX
- Deploy using cloud services
- Optimize retrieval speed
- Better cross-page reasoning

--------------------------------------------------

Author

Thrishank Porandla  
B.Tech CSE (AI & ML)

--------------------------------------------------
