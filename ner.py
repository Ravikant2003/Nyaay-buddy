from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import os
from pathlib import Path
import numpy as np

# === Setup Absolute Paths ===
BASE_DIR = Path(__file__).resolve().parent
PREAMBLE_MODEL_PATH = str((BASE_DIR / "preamble_ner_model").resolve())
JUDGEMENT_MODEL_PATH = str((BASE_DIR / "judgement_ner_model").resolve())

# === Load Preamble NER Model ===
preamble_tokenizer = AutoTokenizer.from_pretrained(
    PREAMBLE_MODEL_PATH,
    local_files_only=True
)
preamble_model = AutoModelForTokenClassification.from_pretrained(
    PREAMBLE_MODEL_PATH,
    local_files_only=True
)
preamble_pipeline = pipeline(
    "ner",
    model=preamble_model,
    tokenizer=preamble_tokenizer,
    aggregation_strategy="simple"
)

# === Load Judgement NER Model ===
judgement_tokenizer = AutoTokenizer.from_pretrained(
    JUDGEMENT_MODEL_PATH,
    local_files_only=True
)
judgement_model = AutoModelForTokenClassification.from_pretrained(
    JUDGEMENT_MODEL_PATH,
    local_files_only=True
)
judgement_pipeline = pipeline(
    "ner",
    model=judgement_model,
    tokenizer=judgement_tokenizer,
    aggregation_strategy="simple"
)

# === Utility: Convert NumPy types to native Python types ===
def convert_numpy_types(obj):
    """Recursively convert numpy types to native Python types."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    return obj

# === Preamble NER Runner ===
def process_preamble_text(preamble: str):
    return preamble_pipeline(preamble)

# === Judgement NER Runner ===
def process_judgement_text(judgement: str):
    return judgement_pipeline(judgement)

# === General Entry Point for Uploaded Files ===
def run_ner_on_uploaded_file(filename: str):
    filepath = f"./uploads/{filename}"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filename}")
    
    with open(filepath, "r") as f:
        text = f.read()
    
    if "preamble" in filename.lower():
        result = process_preamble_text(text)
    elif "judgement" in filename.lower():
        result = process_judgement_text(text)
    else:
        raise ValueError("Unknown file type for NER processing")

    # Convert NumPy types to native Python types
    result = convert_numpy_types(result)

    # === Display Results ===
    for ent in result:
        print(f"{ent['entity_group']}: {ent['word']} (score: {ent['score']:.2f})")

    return result
