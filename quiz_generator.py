import cohere
import json

# ====== CONFIG ======
COHERE_API_KEY = 'YOUR_API_KEY'  # Replace with your actual API key
INPUT_FILE = 'input_text.txt'
OUTPUT_TXT_FILE = 'generated_quiz.txt'
OUTPUT_JSON_FILE = 'generated_quiz.json'
NUM_QUESTIONS = 3  # You can increase this
# ====================

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

# Read input text
with open(INPUT_FILE, 'r', encoding='utf-8') as file:
    text = file.read()

# Prepare prompt for quiz generation
prompt = f"""
Generate {NUM_QUESTIONS} multiple-choice questions from the following text:
\"\"\"{text}\"\"\"

Each question should have 4 options (a, b, c, d) and indicate the correct answer.

Format:
Q1. ...
a) ...
b) ...
c) ...
d) ...
Answer: ...
"""

# Send to Cohere
response = co.generate(
    model='command-r-plus',
    prompt=prompt,
    max_tokens=500,
    temperature=0.7,
    stop_sequences=["\n\n"]
)

# Get generated quiz
quiz_text = response.generations[0].text.strip()

# Save as .txt
with open(OUTPUT_TXT_FILE, 'w', encoding='utf-8') as txt_file:
    txt_file.write(quiz_text)

# Parse and save as .json
quiz_lines = quiz_text.split('\n')
quiz_json = []

current_question = {}
for line in quiz_lines:
    line = line.strip()
    if line.startswith("Q"):
        if current_question:
            quiz_json.append(current_question)
        current_question = {"question": line, "options": {}, "answer": ""}
    elif line.startswith(("a)", "b)", "c)", "d)")):
        key = line[0]
        current_question["options"][key] = line[3:].strip()
    elif line.lower().startswith("answer"):
        current_question["answer"] = line.split(":")[-1].strip().lower()

if current_question:
    quiz_json.append(current_question)

with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as json_file:
    json.dump(quiz_json, json_file, indent=2)

print(f"\n✅ Quiz saved to:\n- {OUTPUT_TXT_FILE}\n- {OUTPUT_JSON_FILE}")
