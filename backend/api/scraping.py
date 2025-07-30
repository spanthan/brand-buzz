import pandas as pd
import re
import ollama
import nltk
from typing import List, Dict
import os
import json
import argostranslate.package
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from sentiment_analysis import *

# Load once at the top
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

def get_comments_data(json_path="tiktok_apify_comments.json"):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    comments = []

    for item in raw_data:
        comment_text = item.get("text")
        
        if not comment_text:
            continue
        else:
            comment_text = comment_text.encode("ascii", "ignore").decode()
            comment_text = comment_text.lower()
            comment_text = comment_text.strip('“”‘’"\'')

        comments.append({
            "text": comment_text,
        })

    return comments

def fix_grammar(comment):
    prompt = f'fix the grammar, punctuation, and spelling in this sentence. Only give me back the corrected sentence, no justification or notes: {comment}'
    response = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": prompt}]
            )
    output = response["message"]["content"].strip()
    if "\n" in output:
        fixed_text = output.split("\n")[-1].strip()
    else:
        fixed_text = output
    fixed_text = fixed_text.strip('“”‘’"\'')
    print(fixed_text)
    return fixed_text

# === Helper: Check if comment is only a mention ===
def is_only_mention(text: str) -> bool:
    """Check if the entire comment is just mentions and whitespace."""
    if text == "@":
        return True
    text = text.strip()
    return re.fullmatch(r"(?:@\S+\s*)+", text) is not None

def strip_mentions(text: str) -> str:
    """Remove all @mentions from the text, only if there's more than just mentions."""
    
    return re.sub(r"@\S+", "", text).strip()

# === Helper: Check if a comment is a question (POS + regex) ===
def is_question(text: str) -> bool:
    text = text.strip().lower()

    # === Rule 1: ends in question mark ===
    if text.endswith("?"):
        return True

    # === Rule 2: starts with common question words ===
    question_starters = (
        "how", "has", "where", "when", "why", "who", "what", "which", "can", "could", "do", "does", "did", "is", "are", "should", "would"
    )
    first_word = text.split()[0] if text.split() else ""
    if first_word in question_starters:
        return True

    # === Rule 3: POS pattern check ONLY on first few tokens ===
    try:
        tokens = word_tokenize(text)
        tags = [tag for _, tag in pos_tag(tokens)]

        # Check first 10 tokens only
        short_seq = tags[:10]
        for i in range(len(short_seq) - 2):
            if short_seq[i:i+3] == ["MD", "PRP", "VB"]:
                return True
    except Exception:
        pass

    return False

# === MAIN FUNCTION ===
def filter_comments(all_comments: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(all_comments)

    print(f"Initial comments: {len(df)}")
    df["text"] = df["text"].str.lower()

    # === Step 1: Remove @mention-only comments ===
    
    mention_only_mask = df["text"].apply(is_only_mention)
    mention_only_comments = df[mention_only_mask]
    df = df[~mention_only_mask]
    print(f"Removed @mention-only: {len(mention_only_comments)}")


    # STEP 3: Optionally, drop rows that became empty after mention stripping
    df["text"] = df["text"].apply(strip_mentions)
    print(df["text"])

    non_english_mask = df["text"].apply(is_non_english)
    non_english_comments = df[non_english_mask]
    df = df[~non_english_mask]
    print(f"Removed non-English: {len(non_english_comments)}")

    # TODO: REMOVE THIS IF NOT NEEDED!
    df["text"] = df["text"].apply(fix_grammar)

    # === Step 2: Remove question-style comments ===
    question_mask = df["text"].apply(is_question)
    question_comments = df[question_mask]
    df = df[~question_mask]
    print(f"Removed questions: {len(question_comments)}")

    # === Step 3: Use LLM for relevance filtering ===
    # texts = df["text"].tolist()
    # relevance_labels = classify_comments_with_ollama(texts)
    # df["relevance"] = relevance_labels

    # irrelevant_mask = df["relevance"] != "relevant"
    # irrelevant_comments = df[irrelevant_mask]
    # df = df[~irrelevant_mask].reset_index(drop=True)
    # print(f"Removed irrelevant via LLM: {len(irrelevant_comments)}")

    
    # print(f"Translating Comments")
    # df["translated_text"] = df["text"].apply(translate_comment)

    # df.to_csv("translated_comments.csv", index=False)

    df["sentiment"] = df["text"].apply(get_sentiment)

    # === Optionally save removed comments for inspection ===
    mention_only_comments.to_csv("filtered_mentions.csv", index=False)
    question_comments.to_csv("filtered_questions.csv", index=False)
    non_english_comments.to_csv("non_english_comments.csv", index=False)
    df.to_csv("final_comments.csv", index=False)
    # irrelevant_comments.to_csv("filtered_irrelevant.csv", index=False)

    print(f"Final kept comments: {len(df)}")
    return df

def install_language_pair_if_needed(source_lang, target_lang="en"):
    installed_languages = argostranslate.translate.get_installed_languages()

    for lang in installed_languages:
        if lang.code == source_lang:
            for translation in lang.translations:
                if translation.to_lang.code == target_lang:
                    return  # Already installed

    # Download and install if not found
    available_packages = argostranslate.package.get_available_packages()
    for pkg in available_packages:
        if pkg.from_code == source_lang and pkg.to_code == target_lang:
            download_path = pkg.download()
            argostranslate.package.install_from_path(download_path)
            print(f"✅ Installed translation model: {source_lang} → {target_lang}")
            return

    print(f"⚠️ No translation model available for: {source_lang} → {target_lang}")

def is_non_english(text):
    if not isinstance(text, str) or not text.strip():
            return text

    try:
        lang_code = detect(text)
        return lang_code != "en"
    except Exception as e:
        return True

def translate_comment(text):
    try:
        if not isinstance(text, str) or not text.strip():
            return text

        lang_code = detect(text)
        if lang_code == "en":
            return text  # Already English

        install_language_pair_if_needed(lang_code, "en")

        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = next((lang for lang in installed_languages if lang.code == lang_code), None)
        to_lang = next((lang for lang in installed_languages if lang.code == "en"), None)

        if from_lang and to_lang:
            translation = from_lang.get_translation(to_lang)
            return translation.translate(text)

    except Exception as e:
        print(f"⚠️ Translation failed for: {text} ({e})")

    return text  # Fallback


if __name__ == "__main__":
    # # Ensure NLTK resources are downloaded
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    comments = get_comments_data()
    filter_comments(comments)
