import cohere
import json
import os
import re
import datetime

def generate_quiz(description_file_path, num_questions=3):
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    if not COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY environment variable not set.")
    output_dir = 'quizzes'
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(description_file_path))[0]
    OUTPUT_TXT_FILE = os.path.join(output_dir, f"{base_name}_quiz_{timestamp}.txt")
    OUTPUT_JSON_FILE = os.path.join(output_dir, f"{base_name}_quiz_{timestamp}.json")
    co = cohere.Client(COHERE_API_KEY)
    with open(description_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    prompt = f"""
Generate exactly {num_questions} multiple-choice questions from the following text:\n\n\"\"\"{text}\"\"\"\n\nFormat each question EXACTLY like this:\n\nQ1. [Question text here]\na) [Option A]\nb) [Option B]\nc) [Option C]\nd) [Option D]\nAnswer: [letter]\n\nQ2. [Question text here]\na) [Option A]\nb) [Option B]\nc) [Option C]\nd) [Option D]\nAnswer: [letter]\n\nMake sure each question is clearly separated and follows this exact format.\n"""
    response = co.generate(
        model='command-r-plus',
        prompt=prompt,
        max_tokens=800,
        temperature=0.7
    )
    quiz_text = response.generations[0].text.strip()
    with open(OUTPUT_TXT_FILE, 'w', encoding='utf-8') as txt_file:
        txt_file.write(quiz_text)
    quiz_json = []
    question_blocks = re.split(r'\n(?=Q\d+\.)', quiz_text)
    for block in question_blocks:
        if not block.strip():
            continue
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue
        question_line = next((line for line in lines if re.match(r'Q\d+\.', line)), None)
        if not question_line:
            continue
        options = {}
        answer = ""
        for line in lines:
            option_match = re.match(r'^([a-d])\)\s*(.+)', line)
            if option_match:
                key = option_match.group(1)
                options[key] = option_match.group(2)
            answer_match = re.match(r'^Answer:\s*([a-dA-D])', line)
            if answer_match:
                answer = answer_match.group(1).lower()
        if question_line and options and answer:
            quiz_json.append({
                'question': question_line,
                'options': options,
                'answer': answer
            })
    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(quiz_json, json_file, indent=2)
    return OUTPUT_JSON_FILE.replace("\\", "/")
