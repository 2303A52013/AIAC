# Create a Python script that processes a PDF file, extracts text, splits into sections,
# allows interactive question asking, finds relevant sections using AI, and generates answers with reasoning.
from parser import (
    extract_and_store_text,
    get_stored_text_path,
    load_text_from_file,
    delete_stored_text,
)
from tree import split_text_into_sections
from reasoner import get_relevant_sections, generate_final_answer
import os


def main():
    pdf_path = r"D:\ClgDocs\3-2\AIAC\Project\PageIndex\deepreason\e61754b8-e28c-4a21-8d51-7d412b383f46.pdf"

    print("\nProcessing your questions...\n")

    # Step 1
    text_path = get_stored_text_path(pdf_path)
    if os.path.exists(text_path):
        print(f"[1/4] Loading stored text from {text_path}...")
        text = load_text_from_file(text_path)
    else:
        print(f"[1/4] Extracting text from PDF and storing to {text_path}...")
        text, _ = extract_and_store_text(pdf_path, text_path=text_path)

    try:
        # Step 2
        print("[2/4] Splitting text into sections...")
        sections = split_text_into_sections(text)

        print("\nEnter your questions one by one. Press Enter on a blank line to finish.")
        while True:
            question = input("\nQuestion: ").strip()
            if not question:
                print("\nNo more questions. Exiting.")
                break

            print("\n[3/4] Finding relevant sections...")
            relevant_sections = get_relevant_sections(sections, question)

        # Step 4
            print("[4/4] Generating final answer...\n")
            answer, reasoning = generate_final_answer(relevant_sections, question)

            print("========== FINAL ANSWER ==========")
            print(answer)

            print("\n========== REASONING PATH ==========")
            for title in relevant_sections:
                print("→", title)
            print("\n" + "=" * 60)
    finally:
        delete_stored_text(text_path)


if __name__ == "__main__":
    main()