from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from typing import List, Optional, Union, Dict, Any
from backend.config.settings import MODEL_NAME, LLM_TIMEOUT
import logging

logger = logging.getLogger(__name__)

# Lazy loading of models
_tokenizer = None
_model = None
_generator = None

def get_generator():
    """Lazy load the text generation pipeline"""
    global _tokenizer, _model, _generator
    
    if _generator is None:
        logger.info(f"Loading model: {MODEL_NAME}")
        
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.float16
        )

        _generator = pipeline(
            "text-generation",
            model=_model,
            tokenizer=_tokenizer,
            max_new_tokens=300,
            do_sample=True,
            temperature=0.7,
        )
        logger.info("Model loaded successfully")
    
    return _generator

def generate_reply(prompt: str, history: Optional[List[Any]] = None) -> str:
    """
    Generate a reply using the LLM model.
    
    Args:
        prompt: User input text
        history: Optional conversation history
        
    Returns:
        Generated response text
        
    Raises:
        RuntimeError: If LLM inference fails
        ValueError: If input is invalid
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    formatted_prompt = "You are a helpful assistant who answers in the same language as the user.\n"

    if history:
        # Keep only the last 4 conversation turns for context
        history = history[-4:]
        for turn in history:
            try:
                role = turn.role if hasattr(turn, "role") else turn.get("role")
                content = turn.content if hasattr(turn, "content") else turn.get("content")
                
                if role == "user":
                    formatted_prompt += f"User: {content}\n"
                elif role == "assistant":
                    formatted_prompt += f"Assistant: {content}\n"
            except (AttributeError, TypeError) as e:
                logger.warning(f"Skipping invalid history item: {e}")
                continue

    formatted_prompt += f"User: {prompt}\nAssistant:"

    try:
        logger.debug("Generating response...")
        generator = get_generator()
        
        output = generator(formatted_prompt, return_full_text=False)
        logger.debug("Response generated successfully")
        
        if not output or len(output) == 0:
            raise RuntimeError("Model returned empty output")
            
        response = output[0]["generated_text"].strip()
        
        # Extract only the assistant's response
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()
        
        if not response:
            raise RuntimeError("Model generated empty response")
            
        return response
        
    except Exception as e:
        logger.error(f"LLM inference failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"LLM inference failed: {str(e)}")
