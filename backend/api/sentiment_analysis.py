from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


def get_sentiment(text: str) -> str:
    try:
        result = sentiment_pipeline(text[:512])[0]["label"].lower()
        if result in ("positive", "neutral", "negative"):
            return result
        return "neutral"
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return "neutral"
