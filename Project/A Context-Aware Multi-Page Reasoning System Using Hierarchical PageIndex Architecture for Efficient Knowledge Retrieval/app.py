# Create a Flask web app that allows users to upload PDF documents and ask questions.
# The app should extract text from PDFs, split it into sections, find relevant sections using AI,
# and generate answers with reasoning. Include file upload, question input, and result display.
from flask import Flask, request, render_template, flash, redirect, url_for
import os
import time
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from parser import (
    extract_and_store_text,
    get_stored_text_path,
    load_text_from_file,
    cleanup_stored_text_storage,
)
from tree import split_text_into_sections
from reasoner import get_relevant_sections, generate_final_answer

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['TEXT_STORAGE_FOLDER'] = os.path.join(os.path.dirname(__file__), 'stored_texts')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        question_text = request.form.get('questions', '').strip()
        questions = [q.strip() for q in question_text.splitlines() if q.strip()]

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if not questions:
            flash('Please enter at least one question')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            start_time = time.time()

            try:
                # Process the PDF
                print("Processing PDF...")
                text_path = get_stored_text_path(filepath, app.config['TEXT_STORAGE_FOLDER'])

                if os.path.exists(text_path):
                    print(f"Loading stored text from {text_path}")
                    text = load_text_from_file(text_path)
                else:
                    print(f"Extracting text and storing to {text_path}")
                    text, _ = extract_and_store_text(filepath, text_path=text_path)

                sections = split_text_into_sections(text)

                print(f"Found {len(sections)} sections")

                qa_results = []
                for question in questions:
                    print(f"Finding relevant sections for: {question}")
                    relevant_sections = get_relevant_sections(sections, question)
                    print(f"Generating answer for: {question}")
                    answer, reasoning = generate_final_answer(relevant_sections, question)
                    relevant_sections_list = [
                        {"title": title, "content": content}
                        for title, content in relevant_sections.items()
                    ]
                    qa_results.append({
                        "question": question,
                        "answer": answer,
                        "reasoning": reasoning,
                        "relevant_sections": relevant_sections_list,
                        "sections_analyzed": len(relevant_sections),
                    })

                processing_time = round(time.time() - start_time, 2)

                return render_template('result.html',
                                     results=qa_results,
                                     total_sections=len(sections),
                                     processing_time=processing_time,
                                     error=None)

            except Exception as e:
                return render_template('result.html',
                                     results=[],
                                     total_sections=0,
                                     processing_time=0,
                                     error=str(e))
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
                cleanup_stored_text_storage(app.config['TEXT_STORAGE_FOLDER'])
    return render_template('index.html')


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)