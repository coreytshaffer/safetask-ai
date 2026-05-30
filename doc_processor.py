import os
import json
import PyPDF2
import re
from collections import Counter

REGULATIONS_FILE = "regulations.json"

# Basic list of English stop words for deterministic keyword generation
STOP_WORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
])

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def generate_keywords(text, num_keywords=15):
    # Deterministic keyword generation using Term Frequency
    # 1. Lowercase and remove punctuation
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    # 2. Remove stop words
    filtered_words = [w for w in words if w not in STOP_WORDS]
    # 3. Count frequencies
    word_counts = Counter(filtered_words)
    # 4. Get top N keywords
    top_keywords = [item[0] for item in word_counts.most_common(num_keywords)]
    return top_keywords

def append_to_database(code, title, raw_text, keywords):
    # Load existing
    if os.path.exists(REGULATIONS_FILE):
        with open(REGULATIONS_FILE, 'r') as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = []
    else:
        db = []
        
    # Check if code already exists to avoid duplicates
    existing_index = next((index for (index, d) in enumerate(db) if d["code"] == code), None)
    
    new_entry = {
        "code": code,
        "title": title,
        "summary": raw_text,
        "keywords": keywords
    }
    
    if existing_index is not None:
        db[existing_index] = new_entry
    else:
        db.append(new_entry)
        
    with open(REGULATIONS_FILE, 'w') as f:
        json.dump(db, f, indent=2)
        
    return new_entry

def process_upload(file_path, code, title):
    try:
        raw_text = extract_text_from_pdf(file_path)
        if not raw_text:
            raise ValueError("No text could be extracted from the PDF.")
            
        keywords = generate_keywords(raw_text)
        new_policy = append_to_database(code, title, raw_text, keywords)
        return new_policy
    except Exception as e:
        raise Exception(f"Failed to process document: {str(e)}")
