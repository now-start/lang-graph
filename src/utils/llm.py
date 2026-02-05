"""LLM initialization utilities."""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFacePipeline

from src.config.config import Config


def get_local_llm() -> HuggingFacePipeline:
    """Initialize local HuggingFace model.

    Returns:
        HuggingFacePipeline: Initialized language model
    """
    model_id = Config.HUGGINGFACE_MODEL

    print(f"🔄 Loading model: {model_id}")
    print("   This may take a few minutes on first run...")

    # Check for GPU availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"   Using device: {device}")

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
        low_cpu_mem_usage=True
    )

    # Create pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.1,
        top_p=0.95,
        repetition_penalty=1.15
    )

    # Wrap with LangChain
    llm = HuggingFacePipeline(pipeline=pipe)
    print("✅ Model loaded successfully!\n")

    return llm
