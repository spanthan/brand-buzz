from apify_client import ApifyClient
import json
import os
import re
from langchain_community.llms import Ollama
import ollama
import pandas as pd
import time


def save_to_json(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def get_actor_input():
     # Prepare the Actor input
    run_input = {
        "postURLs": ["https://www.tiktok.com/@sarahpalmyra/video/7086537682649697578?_r=1&_t=ZT-8yKbPxtxrLi"],
        "commentsPerPost": 1000,
        "maxRepliesPerComment": 0,
        "resultsPerPage": 1000,
    }
    return run_input

def scrape_to_json():
    api_token = os.environ.get("APIFY_API_TOKEN")

    if not api_token:
        raise EnvironmentError("⚠️ APIFY_API_TOKEN is not set in environment variables.")

    client = ApifyClient(api_token)
    run_input = get_actor_input()

    print("Running the Actor and waiting for it to finish...")
    run = client.actor("BDec00yAmCm1QbMEI").call(run_input=run_input)
    print("Actor finished.")

    results = []
    print("Fetching results...")
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)

    output_file = "tiktok_apify_comments.json"
    save_to_json(results, output_file)
    print(f"Saved {len(results)} items to {output_file}")

def get_comments_data(json_path="tiktok_apify_comments.json"):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    comments = []

    for item in raw_data:
        comment_text = item.get("text")
        username = item.get("uniqueId")

        if not comment_text or not username:
            continue
        
        comments.append({
            "username": username,
            "text": comment_text,
        })

    return comments

def run_llm(prompt):

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content'].strip()
def is_a_question(comment_text):
    with open(f"prompts/question_prompt.txt", "r", encoding="utf-8") as file:
        prompt = file.read()
    prompt += f"\n{comment_text}"

    response = run_llm(prompt)
    
    return response

def extract_json_from_response(response_text):
    # Match the first {...} block using a greedy match
    match = re.search(r'{[\s\S]*?}', response_text)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(response_text)
            print("⚠️ Failed to parse JSON.")
            return None
    else:
        print("⚠️ No JSON found in response.")
        return None

def process_comments(all_comments):
    # remove comments that are just @
    # translate comments not in english
    comments = []
    for comment in all_comments:
        comment_text = comment["text"]
        is_q_response = is_a_question(comment_text)

        json_part = extract_json_from_response(is_q_response)
        if json_part is not None:
            if not json_part.get("question"):
                json_part["type"] = "False"
                print("changing")
            print(comment_text, "\n\t", json_part)
            print()

            comments.append({
                "username": comment["username"],
                "text": comment["text"],
                "is_a_question": json_part["type"],
                "question_portion": json_part["question"]
            })

    return comments

OUTPUT_FILE = "labeled_comments.json"
BATCH_SIZE = 10  # adjust based on context length

# === STEP 2: Define LLM prompt logic ===
def classify_with_ollama(batch_comments):
    numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(batch_comments))
    with open(f"prompts/relevance_prompt.txt", "r", encoding="utf-8") as file:
        prompt = file.read()
    numbered = "\n".join(f"{i+1}. {c}" for i, c in enumerate(batch_comments))
    prompt += f"\n{numbered}"

    raw_output = run_llm(prompt)
    print(raw_output)
    lines = [line for line in raw_output.splitlines() if "." in line and line[0].isdigit()]

    labels = []
    for line in lines:
        try:
            _, label = line.split(".", 1)
            labels.append(label.strip().lower())
        except Exception:
            labels.append("unknown")

    return labels

def filter_irrelevant_comments(all_comments):
    # TODO: do a better job of getting rid of questions!
    df = pd.DataFrame(all_comments)

    all_labels = []
    for i in range(0, len(df), BATCH_SIZE):
        print(f'Running batch {i} with batch size {BATCH_SIZE}')
        batch_df = df.iloc[i:i + BATCH_SIZE]
        comments_batch = batch_df["text"].tolist()

        try:
            labels = classify_with_ollama(comments_batch)
        except Exception as e:
            print(f"Error during LLM classification: {e}")
            labels = ["unknown"] * len(comments_batch)

        # Pad if mismatch
        while len(labels) < len(comments_batch):
            labels.append("unknown")

        all_labels.extend(labels)
        time.sleep(1)  # rate-limit safety

    df["relevance"] = all_labels

    # === STEP 4: Filter based on relevance ===
    df_filtered = df[df["relevance"].isin(["relevant", "partial"])].reset_index(drop=True)

    print(f"Original comments: {len(df)}")
    print(f"Filtered comments: {len(df_filtered)}")

    # === STEP 5: Save to JSON ===
    df.to_json(OUTPUT_FILE, orient="records", indent=2, force_ascii=False)
    print(f"Filtered data saved to: {OUTPUT_FILE}")

def filter_comments(all_comments):
    df = pd.DataFrame(all_comments)

    # remove comments with only an @<username> and nothing else
    # remove comments that are a question by using the following method:
    '''
    import nltk
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    from nltk.tokenize import word_tokenize
    from nltk import pos_tag

    text = "could I please have a copy of file A."

    # Tokenization
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)

    tags_only = [tag[1] for tag in pos_tags]
    tags_only:

    ['MD', 'PRP', 'VB', 'VB', 'DT', 'NN', 'IN', 'NN', 'NNP', '.']
    The 'MD', 'PRP', 'VB' sequence can be always be associated to questions.

    This, together with regex on the presence of "how", "where", "when", "why", "wondering" or "?", might do the trick.

    '''
    # remove irrelevant comments by using an llm

    