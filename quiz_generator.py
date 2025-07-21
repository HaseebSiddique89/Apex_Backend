import cohere
import json
import os
import re
import datetime

# ====== CONFIG ======
COHERE_API_KEY = os.getenv("COHERE_API_KEY")  # Or replace with actual key: "your_api_key_here"
INPUT_FILE = 'D:\\Work\\GitHub\\Trellis_ImageTo3D_Setup\\Descriptions\\heart_description_20250721_202800.txt'
NUM_QUESTIONS = 3

# Create 'Quizzes' directory if it doesn't exist
output_dir = 'Quizzes'
os.makedirs(output_dir, exist_ok=True)

# Generate timestamped filenames to avoid overwriting
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
base_name = os.path.splitext(os.path.basename(INPUT_FILE))[0]
OUTPUT_TXT_FILE = os.path.join(output_dir, f"{base_name}_quiz_{timestamp}.txt")
OUTPUT_JSON_FILE = os.path.join(output_dir, f"{base_name}_quiz_{timestamp}.json")
# ====================

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

# Read input text
with open(INPUT_FILE, 'r', encoding='utf-8') as file:
    text = file.read()

# Prepare prompt for quiz generation
prompt = f"""
Generate exactly {NUM_QUESTIONS} multiple-choice questions from the following text:

\"\"\"{text}\"\"\"

Format each question EXACTLY like this:

Q1. [Question text here]
a) [Option A]
b) [Option B] 
c) [Option C]
d) [Option D]
Answer: [letter]

Q2. [Question text here]
a) [Option A]
b) [Option B]
c) [Option C] 
d) [Option D]
Answer: [letter]

Make sure each question is clearly separated and follows this exact format.
"""

# Send to Cohere (remove stop_sequences to allow full generation)
response = co.generate(
    model='command-r-plus',
    prompt=prompt,
    max_tokens=800,
    temperature=0.7
)

# Get generated quiz
quiz_text = response.generations[0].text.strip()

# DEBUG: Print the raw response
print("=== RAW GENERATED TEXT ===")
print(quiz_text)
print("=== END RAW TEXT ===\n")

# Save as .txt
with open(OUTPUT_TXT_FILE, 'w', encoding='utf-8') as txt_file:
    txt_file.write(quiz_text)

# Improved parsing logic using regex
quiz_json = []

# Split into question blocks
question_blocks = re.split(r'\n(?=Q\d+\.)', quiz_text)

for block in question_blocks:
    if not block.strip():
        continue

    lines = [line.strip() for line in block.split('\n') if line.strip()]
    if not lines:
        continue

    # Find question line
    question_line = next((line for line in lines if re.match(r'Q\d+\.', line)), None)
    if not question_line:
        continue

    # Extract options and answer
    options = {}
    answer = ""
    for line in lines:
        option_match = re.match(r'^([a-d])\)\s*(.+)', line)
        if option_match:
            key = option_match.group(1)
            value = option_match.group(2).strip()
            options[key] = value

        answer_match = re.match(r'(?:Answer|Correct Answer):\s*([a-d])', line, re.IGNORECASE)
        if answer_match:
            answer = answer_match.group(1).lower()

    # Only add if valid question, options, and answer exist
    if question_line and len(options) == 4 and answer:
        quiz_json.append({
            "question": question_line,
            "options": options,
            "answer": answer
        })

# DEBUG: Print parsed JSON
print("=== PARSED JSON ===")
print(json.dumps(quiz_json, indent=2))
print("=== END PARSED JSON ===\n")

# Save as JSON
with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as json_file:
    json.dump(quiz_json, json_file, indent=2)

# Final message
print(f"✅ Quiz saved to:")
print(f"- {OUTPUT_TXT_FILE}")
print(f"- {OUTPUT_JSON_FILE}")
print(f"📊 Generated {len(quiz_json)} questions")

# Additional debug message
if len(quiz_json) == 0:
    print("\n❌ No questions were parsed successfully! Check the raw output format.")
elif len(quiz_json) < NUM_QUESTIONS:
    print(f"\n⚠️ Only {len(quiz_json)} out of {NUM_QUESTIONS} questions were parsed.")
else:
    print(f"\n✅ All {NUM_QUESTIONS} questions parsed successfully!")
