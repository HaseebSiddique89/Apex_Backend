from transformers import pipeline

# Load T5-based question generation pipeline
generator = pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")

# Load the content from the text file
with open("Descriptions\\heart_description_20250721_202800.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split text into manageable chunks
chunks = text.split("\n\n")  # or use a sentence tokenizer if needed

# Generate questions
for i, chunk in enumerate(chunks):
    if chunk.strip():
        print(f"--- Chunk {i+1} ---")
        result = generator(f"generate questions: {chunk}", max_length=128, do_sample=False)
        print(result[0]['generated_text'])
