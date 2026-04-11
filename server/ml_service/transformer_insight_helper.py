"""
Transformer-based Dataset Insight Generator

This module loads a HuggingFace transformer model (google/flan-t5-base) once at startup
and provides functionality to generate natural-language explanations of dataset patterns
from statistical summaries produced by the GAN service.
"""

import logging
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

# Global model and tokenizer - loaded once at module import
_model = None
_tokenizer = None
_device = None


def initialize_model(model_name: str = "google/flan-t5-base") -> None:
    """
    Initialize the transformer model and tokenizer for insight generation.
    Called once at module startup to load model into memory.
    
    Args:
        model_name: HuggingFace model identifier (default: google/flan-t5-base)
    """
    global _model, _tokenizer, _device
    
    if _model is not None:
        logger.info("Model already initialized, skipping reinitialization")
        return
    
    try:
        logger.info(f"Loading transformer model: {model_name}")
        
        # Determine device
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {_device}")
        
        # Load tokenizer and model
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        _model.to(_device)
        _model.eval()
        
        logger.info(f"✓ Transformer model initialized successfully on {_device}")
    
    except Exception as e:
        logger.error(f"Failed to initialize transformer model: {str(e)}")
        raise


def _ensure_model_loaded() -> None:
    """Ensure the model is loaded before use."""
    global _model
    if _model is None:
        initialize_model()


def _format_stats_for_prompt(stats: Dict[str, Any]) -> str:
    """
    Format dataset statistics into a structured text for the transformer.
    
    Args:
        stats: Dictionary with keys like age_range, bmi_range, diabetes_distribution, etc.
    
    Returns:
        Formatted string describing the dataset statistics
    """
    lines = ["Dataset Statistical Summary:"]
    
    # Age range
    if "age_range" in stats:
        age_range = stats["age_range"]
        if isinstance(age_range, dict):
            lines.append(f"Patient ages: {age_range.get('min', 'N/A')} to {age_range.get('max', 'N/A')} years")
        else:
            lines.append(f"Patient ages: {age_range}")
    
    # BMI range
    if "bmi_range" in stats:
        bmi_range = stats["bmi_range"]
        if isinstance(bmi_range, dict):
            lines.append(f"BMI range: {bmi_range.get('min', 'N/A'):.1f} to {bmi_range.get('max', 'N/A'):.1f}")
        else:
            lines.append(f"BMI range: {bmi_range}")
    
    # Diabetes distribution
    if "diabetes_distribution" in stats:
        dist = stats["diabetes_distribution"]
        if isinstance(dist, dict):
            diabetic_pct = dist.get('diabetic_percentage', 0)
            lines.append(f"Diabetes prevalence: {diabetic_pct:.1f}% diabetic patients")
        else:
            lines.append(f"Diabetes distribution: {dist}")
    
    # RBS (Random Blood Sugar) statistics
    if "diabetic_rbs_mean" in stats or "non_diabetic_rbs_mean" in stats:
        diabetic_rbs = stats.get("diabetic_rbs_mean", "N/A")
        non_diabetic_rbs = stats.get("non_diabetic_rbs_mean", "N/A")
        lines.append(f"RBS mean - Diabetic patients: {diabetic_rbs} mg/dL, Non-diabetic: {non_diabetic_rbs} mg/dL")
    
    # HbA1c range
    if "hba1c_range" in stats:
        hba1c_range = stats["hba1c_range"]
        if isinstance(hba1c_range, dict):
            lines.append(f"HbA1c range: {hba1c_range.get('min', 'N/A'):.2f}% to {hba1c_range.get('max', 'N/A'):.2f}%")
        else:
            lines.append(f"HbA1c range: {hba1c_range}")
    
    # Add any additional statistics
    known_keys = {"age_range", "bmi_range", "diabetes_distribution", 
                  "diabetic_rbs_mean", "non_diabetic_rbs_mean", "hba1c_range"}
    for key, value in stats.items():
        if key not in known_keys and value is not None:
            # Format additional keys in snake_case to readable format
            readable_key = key.replace("_", " ").title()
            lines.append(f"{readable_key}: {value}")
    
    return "\n".join(lines)


def generate_dataset_insight(stats: Dict[str, Any]) -> str:
    """
    Generate a concise natural-language explanation of dataset patterns.
    
    Accepts dataset statistics as produced by the GAN service and returns
    a medical-style summary explaining trends, distributions, and key patterns
    in the dataset.
    
    Args:
        stats: Dictionary containing dataset statistics with keys such as:
               - age_range: dict with 'min' and 'max' age values
               - bmi_range: dict with 'min' and 'max' BMI values
               - diabetes_distribution: dict with 'diabetic_percentage'
               - diabetic_rbs_mean: float, mean RBS for diabetic patients
               - non_diabetic_rbs_mean: float, mean RBS for non-diabetic patients
               - hba1c_range: dict with 'min' and 'max' HbA1c values
    
    Returns:
        String: A concise medical-style summary of the dataset patterns
    
    Raises:
        RuntimeError: If the transformer model is not initialized
        ValueError: If stats is empty or invalid
    """
    _ensure_model_loaded()
    
    if not stats:
        logger.warning("Empty statistics provided to generate_dataset_insight")
        return "No dataset statistics provided for analysis."
    
    try:
        # Create prompt for the transformer
        prompt = f"""
You are an AI healthcare data analyst.

The following statistics are from a GAN-generated synthetic healthcare dataset:

Age range: {stats.get("age_range")}
BMI range: {stats.get("bmi_range")}
Diabetes distribution: {stats.get("diabetes_distribution")}
Mean glucose (diabetic patients): {stats.get("diabetic_rbs_mean")}
Mean glucose (non-diabetic patients): {stats.get("non_diabetic_rbs_mean")}
HbA1c range: {stats.get("hba1c_range")}

Task:

Write a detailed explanation describing:

1. glucose level differences between diabetic and non-diabetic groups
2. how BMI variation relates to metabolic risk
3. whether the dataset appears medically realistic
4. what patterns a researcher could observe from this dataset
5. how this dataset could help downstream ML training

Write a professional paragraph (5–7 sentences).
Do NOT repeat numbers directly unless necessary.
"""
        
        logger.debug(f"Generated prompt for insight generation")
        
        # Tokenize input
        inputs = _tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(_device)
        
        # Generate insight using the model
        with torch.no_grad():
            outputs = _model.generate(
                inputs["input_ids"],
                max_length=300,
                num_beams=3,
                early_stopping=True,
                temperature=0.8,
                do_sample=True
            )
        
        # Decode the generated text
        insight = _tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        logger.info(f"✓ Generated insight successfully ({len(insight)} characters)")
        
        return insight
    
    except Exception as e:
        logger.error(f"Error generating dataset insight: {str(e)}", exc_info=True)
        raise


def get_model_info() -> Dict[str, Any]:
    """
    Get information about the loaded transformer model.
    
    Returns:
        Dictionary with model name, device, and status information
    """
    _ensure_model_loaded()
    
    return {
        "model_name": "google/flan-t5-base",
        "device": str(_device),
        "model_loaded": _model is not None,
        "tokenizer_loaded": _tokenizer is not None,
        "model_type": "seq2seq (T5-based)"
    }


# Initialize model on module import
try:
    initialize_model()
except Exception as e:
    logger.warning(f"Model initialization deferred: {str(e)}")
