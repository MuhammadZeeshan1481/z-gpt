from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16
)

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=300,
    do_sample=True,
    temperature=0.7,
)

def generate_reply(prompt: str, history=None):
    formatted_prompt = "You are a helpful assistant who answers in the same language as the user.\n"

    if history:
        history = history[-4:]
        for turn in history:
            role = turn.role if hasattr(turn, "role") else turn.get("role")
            content = turn.content if hasattr(turn, "content") else turn.get("content")
            if role == "user":
                formatted_prompt += f"User: {content}\n"
            elif role == "assistant":
                formatted_prompt += f"Assistant: {content}\n"

    formatted_prompt += f"User: {prompt}\nAssistant:"

    try:
        print(" Generating response...")
        output = generator(formatted_prompt, return_full_text=False)
        print(" Response generated.")
        response = output[0]["generated_text"].strip()
        return response.split("Assistant:")[-1].strip()
    except Exception as e:
        raise RuntimeError(f"LLM inference failed: {e}")
