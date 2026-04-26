
# Create Python functions to interact with NVIDIA's OpenAI-compatible API for financial analysis.
# Include functions to find relevant document sections based on questions and generate answers with reasoning.
import os
import re
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)
api_key = os.getenv("NVIDIA_API_KEY")  # Use NVIDIA API key instead of Google

if not api_key:
    raise ValueError("NVIDIA_API_KEY missing from .env file")

# Initialize NVIDIA client (OpenAI-compatible)
client = OpenAI(
    api_key=api_key,
    base_url="https://integrate.api.nvidia.com/v1"
)


def _tokenize(text):
    return re.findall(r"\w+", text.lower())


def _section_title_match(query, title):
    query_words = set(_tokenize(query))
    title_words = set(_tokenize(title))
    return bool(query_words and len(query_words.intersection(title_words)) >= max(1, len(query_words) // 2))


# 🔁 Safe API call (fail fast on quota limit)
def safe_generate(prompt, retries=1):
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="meta/llama-3.1-8b-instruct",  # NVIDIA-hosted Llama model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=512,   # Limit output length
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "429" in error_msg or "rate" in error_msg:
                print("❌ API quota/rate limit reached. Using fallback...")
                return None
            if i < retries - 1:
                print(f"⚠️ Attempt {i+1} failed. Retrying in 3 seconds...")
                time.sleep(3)

    print("❌ API call failed. Using fallback.")
    return None


# 🔍 Find relevant sections (1 API call only)
def get_relevant_sections(sections, question, max_sections=3):
    relevant = {}
    limited_sections = list(sections.items())[:16]

    section_text = "\n".join([
        f"- {title}: {content[:250]}"
        for title, content in limited_sections
    ])

    # Prompt sent to the NVIDIA OpenAI-compatible API to choose the most relevant sections.
    # The model should read the question, review the listed document sections, and return
    # the titles of the sections that are most useful for answering the question.
    # Example prompt text:
    # """
    # You are a financial analyst.
    #
    # Question: [the user question]
    #
    # Sections:
    # - Section title 1: first 250 chars of content
    # - Section title 2: first 250 chars of content
    #
    # Task:
    # Select the most relevant section titles to answer the question. If none are relevant, say NONE.
    #
    # Output format:
    # Title1
    # Title2
    # Title3
    # """
    prompt = f"""
You are a financial analyst.

Question: {question}

Sections:
{section_text}

Task:
Select the most relevant section titles to answer the question. If none are relevant, say NONE.

Output format:
Title1
Title2
Title3
"""

    response = safe_generate(prompt)

    if response:
        lines = [line.strip() for line in response.splitlines() if line.strip()]
        for line in lines:
            line = re.sub(r"^[0-9\)\.\-\s]+", "", line.lower())
            if line == "none":
                break
            for title in sections:
                title_lower = title.lower()
                if line in title_lower or _section_title_match(line, title):
                    relevant[title] = sections[title][:1200]
                    break

    if not relevant:
        return fallback_sections(sections, question, max_sections=max_sections)

    return relevant


# 🔁 Fallback (no API)
def fallback_sections(sections, question, max_sections=3):
    print("⚠️ Using fallback mode")
    question_terms = set(_tokenize(question))
    scored = []

    for title, content in sections.items():
        title_score = len(question_terms.intersection(_tokenize(title)))
        content_score = len(question_terms.intersection(_tokenize(content[:400])))
        score = title_score * 2 + content_score
        if score > 0:
            scored.append((score, title))

    scored.sort(key=lambda item: (-item[0], item[1]))

    if not scored:
        scored = [(0, title) for title in list(sections)[:max_sections]]

    top_sections = [title for _, title in scored[:max_sections]]
    return {title: sections[title][:1200] for title in top_sections}


# 🧠 Final answer generation
def generate_final_answer(relevant_sections, question):
    combined = ""

    for title, content in relevant_sections.items():
        combined += f"{title}:\n{content}\n\n"

    # Prompt sent to the NVIDIA OpenAI-compatible API to generate the final answer.
    # It instructs the model to use only the selected relevant sections and to format
    # the output with a clear ANSWER and REASONING block.
    # Example prompt text:
    # """
    # Answer the question using ONLY the information below:
    #
    # [Section title 1]: [section content]
    # [Section title 2]: [section content]
    #
    # Question: [the user question]
    #
    # Format your response as:
    # ANSWER: [Your answer here]
    #
    # REASONING: [Explain which sections you used and how you arrived at the answer]
    # """
    prompt = f"""
Answer the question using ONLY the information below:

{combined}

Question: {question}

Format your response as:
ANSWER: [Your answer here]

REASONING: [Explain which sections you used and how you arrived at the answer]
"""

    response = safe_generate(prompt)

    if not response:
        return "Fallback: Unable to generate answer due to API limit.", "API limit reached - using fallback mode"

    lines = response.split('\n')
    answer = ""
    reasoning = ""
    in_answer = False
    in_reasoning = False

    for line in lines:
        line_lower = line.lower().strip()
        if line_lower.startswith('answer:'):
            in_answer = True
            in_reasoning = False
            answer += line.split(':', 1)[1].strip() + ' '
        elif line_lower.startswith('reasoning:'):
            in_reasoning = True
            in_answer = False
            reasoning += line.split(':', 1)[1].strip() + ' '
        elif in_answer:
            answer += line.strip() + ' '
        elif in_reasoning:
            reasoning += line.strip() + ' '

    answer = answer.strip()
    reasoning = reasoning.strip()

    if not answer:
        answer = response.split('\n')[0] if response else "Unable to parse answer"
    if not reasoning:
        reasoning = "Based on the provided document sections"

    return answer, reasoning