from typing import Generator, Iterable, Optional
from threading import Thread
from backend.config.settings import get_settings

settings = get_settings()

# Lazy-loaded singletons
tokenizer = None
model = None
TextStreamer = None


def _resolve_dtype(torch_module):
    precision = (settings.chat_precision or "float16").lower()
    if settings.chat_device.lower() == "cpu":
        return torch_module.float32
    if precision == "float32":
        return torch_module.float32
    if precision == "bfloat16":
        return torch_module.bfloat16
    return torch_module.float16


def _load_model():
    global tokenizer, model, TextStreamer
    if tokenizer is not None and model is not None and TextStreamer is not None:
        return

    from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
    import torch

    model_name = settings.chat_model
    if not model_name:
        raise RuntimeError("CHAT_MODEL must be configured before using the chat endpoint.")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    device_target = (settings.chat_device or "auto").lower()
    torch_dtype = _resolve_dtype(torch)

    if device_target == "cpu":
        model_instance = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
        )
        model_instance.to("cpu")
    elif device_target == "auto":
        model_instance = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch_dtype,
        )
    else:
        model_instance = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
        )
        model_instance.to(device_target)

    model_instance.eval()
    model = model_instance
    TextStreamer = TextIteratorStreamer


def _format_prompt(prompt: str, history: Optional[Iterable[dict]] = None) -> str:
    formatted = "You are a helpful assistant who answers in the same language as the user.\n"
    if history:
        last = list(history)[-4:]
        for turn in last:
            role = turn.get("role") if isinstance(turn, dict) else getattr(turn, "role", "")
            content = turn.get("content") if isinstance(turn, dict) else getattr(turn, "content", "")
            if role == "user":
                formatted += f"User: {content}\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n"
    formatted += f"User: {prompt}\nAssistant:"
    return formatted


def generate_reply(prompt: str, history=None, max_new_tokens: int = 300, temperature: float = 0.7) -> str:
    _load_model()
    input_text = _format_prompt(prompt, history)
    try:
        import torch

        inputs = tokenizer([input_text], return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                do_sample=True,
                temperature=temperature,
                max_new_tokens=max_new_tokens,
                eos_token_id=tokenizer.eos_token_id,
            )
        text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
        return text.split("Assistant:")[-1].strip()
    except Exception as e:
        raise RuntimeError(f"LLM inference failed: {e}")


def stream_reply(prompt: str, history=None, max_new_tokens: int = 300, temperature: float = 0.7) -> Generator[str, None, None]:
    _load_model()
    input_text = _format_prompt(prompt, history)
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    inputs = tokenizer([input_text], return_tensors="pt").to(model.device)

    def _generate():
        try:
            model.generate(
                **inputs,
                do_sample=True,
                temperature=temperature,
                max_new_tokens=max_new_tokens,
                eos_token_id=tokenizer.eos_token_id,
                streamer=streamer,
            )
        except Exception:
            streamer.put(None)

    thread = Thread(target=_generate)
    thread.start()

    for text in streamer:
        # Filter out the prefix upto "Assistant:" in case it appears
        yield text

    thread.join()
