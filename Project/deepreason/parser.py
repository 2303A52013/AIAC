
# Create Python functions to extract text from PDF files using pdfplumber,
# store extracted text to files, load text from files, and manage text storage cleanup.
import os
import pdfplumber


def extract_text_from_pdf(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def get_stored_text_path(pdf_path, storage_dir=None):
    if storage_dir:
        os.makedirs(storage_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        return os.path.join(storage_dir, f"{base_name}.txt")

    return os.path.splitext(pdf_path)[0] + ".txt"


def save_text_to_file(text, text_path):
    os.makedirs(os.path.dirname(text_path), exist_ok=True)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    return text_path


def load_text_from_file(text_path):
    with open(text_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_and_store_text(pdf_path, text_path=None, storage_dir=None):
    text = extract_text_from_pdf(pdf_path)
    if text_path is None:
        text_path = get_stored_text_path(pdf_path, storage_dir)
    save_text_to_file(text, text_path)
    return text, text_path


def delete_stored_text(text_path):
    try:
        os.remove(text_path)
    except FileNotFoundError:
        pass


def cleanup_stored_text_storage(storage_dir):
    if not storage_dir or not os.path.isdir(storage_dir):
        return

    for filename in os.listdir(storage_dir):
        file_path = os.path.join(storage_dir, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
