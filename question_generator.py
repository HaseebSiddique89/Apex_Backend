from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the question generation model
tokenizer = AutoTokenizer.from_pretrained("iarfmoose/t5-base-question-generator")
model = AutoModelForSeq2SeqLM.from_pretrained("iarfmoose/t5-base-question-generator")

# Provide a context and an answer to base the question on
context = "The mitochondria is the powerhouse of the cell. It generates ATP through respiration."
answer = "mitochondria"

# Format the input correctly
input_text = f"context: {context} answer: {answer}"

# Tokenize and generate
input_ids = tokenizer.encode(input_text, return_tensors="pt")
output = model.generate(input_ids, max_length=64, num_beams=4, early_stopping=True)

# Decode the output
question = tokenizer.decode(output[0], skip_special_tokens=True)

print("Generated Question:", question)
