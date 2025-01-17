"""
Purpose:
This file handles the interaction with the LLaMA, loading the pre-trained model and running inference 
(text generation) tasks based on input text. It will take the preprocessed text, pass it to the model, and return the 
generated text.

Concept:

This file abstracts away the complexity of interacting directly with the AI model.
The model is typically loaded from a pre-trained checkpoint using Hugging Face's Transformers library.
The generate_text() function takes the cleaned input text, tokenizes it (through the tokenizer), and runs inference 
with the model to generate a relevant output.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

def load_model():
    model_name = "meta-llama/Llama-3.2-3B-Instruct-SpinQuant_INT4_EO8"

    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Apply PEFT (LoRA)
    lora_config = LoraConfig(
        task_type="CAUSAL_LM",
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"]
    )
    model = get_peft_model(model, lora_config)

    return model, tokenizer
