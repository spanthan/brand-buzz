import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

LABELS = ["negative", "neutral", "positive"]

def get_sentiment(text: str) -> str:
    try:
        inputs = tokenizer(text[:512], return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits
        scores = torch.nn.functional.softmax(logits, dim=1).squeeze().numpy()
        return LABELS[np.argmax(scores)]
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return "neutral"
