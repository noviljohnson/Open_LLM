

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
import re

# Initialize FastAPI app
app = FastAPI()


# Load model directly :Qwen2.5-VL-3B-Instruct-AWQ
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct-AWQ")
# model = AutoModelForImageTextToText.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct-AWQ")

model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    # load_in_8bit=True,  # Use 8-bit quantization for efficiency
    # device_map="auto"   # Automatically map layers to GPU/CPU
)

# Set pad_token_id to eos_token_id if it's not already set
if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Define request body schema
class TextInput(BaseModel):
    message: str

@app.post("/chat")
async def chat(input_data: TextInput):
    try:
        # Extract user input
        user_input = input_data.message

        # Prepend system instructions to discourage intermediate reasoning
        system_message = "You are a helpful assistant that provides concise and direct answers without intermediate reasoning steps."
        full_input = f"{system_message} {user_input}"

        # Tokenize the input and generate attention mask
        input_ids = tokenizer.encode(full_input, return_tensors="pt", padding=True, truncation=True).to(device)
        attention_mask = (input_ids != tokenizer.pad_token_id).to(device)

        # Generate response with optimized parameters
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=2000,                # Allow up to 200 new tokens
            min_length=50,                      # Ensure at least 50 tokens are generated
            temperature=0.7,                    # Moderate creativity
            do_sample=True,                     # Enable sampling for diverse responses
            top_k=50,                           # Consider only the top 50 most likely tokens
            top_p=0.95,                         # Use nucleus sampling with cumulative probability 0.95
            repetition_penalty=1.2,             # Penalize repeated tokens
            early_stopping=False         # Disable early stopping
        )

        # Decode only the newly generated tokens
        response = tokenizer.decode(output[0][len(input_ids[0]):], skip_special_tokens=True)

        # Remove <think> tags using regex
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

        # Return the response
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Hugging Face Model Server!"}
