
# Create a function to split extracted PDF text into logical sections,
# detecting headers for SEC forms and financial documents, with fallback chunking if needed.
def split_text_into_sections(text):
    sections = {}
    current_section = "GENERAL"
    sections[current_section] = ""

    lines = text.split("\n")

    for i, line in enumerate(lines):
        line = line.strip()

        # Better section detection for SEC forms
        if (line.startswith("UNITED STATES SECURITIES") or
            line.startswith("STATEMENT OF CHANGES") or
            line.startswith("1. Name and Address") or
            line.startswith("2. Issuer Name") or
            line.startswith("Table I") or
            line.startswith("Table II") or
            (line.isupper() and len(line.split()) > 3 and len(line) > 20)):
            current_section = line[:50]  # Limit section name length
            sections[current_section] = ""
        else:
            sections[current_section] += line + " "

    # Clean up empty sections
    sections = {k: v.strip() for k, v in sections.items() if v.strip()}

    # If we have very few sections, create larger chunks
    if len(sections) < 3:
        # Split into roughly equal chunks of ~1000 characters
        chunk_size = 1000
        sections = {}
        words = text.split()
        for i in range(0, len(words), chunk_size // 10):  # Rough word-based chunking
            chunk = " ".join(words[i:i + chunk_size // 10])
            if chunk.strip():
                sections[f"SECTION_{len(sections) + 1}"] = chunk

    return sections