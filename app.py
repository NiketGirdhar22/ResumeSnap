from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import os
from dotenv import load_dotenv
from groq import Groq
import json
import re

nltk.download('punkt')
nltk.download('stopwords')

nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)
CORS(app)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return str(e)

def clean_text(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    return " ".join(filtered_text)

def extract_relevant_sections(text):
    sections = {
        "skills": [],
        "projects": [],
        "experience": [],
        "education": []
    }
    sentences = sent_tokenize(text)
    current_section = None

    for sentence in sentences:
        lower_sentence = sentence.lower()
        if "skills" in lower_sentence:
            current_section = "skills"
        elif "projects" in lower_sentence or "project" in lower_sentence:
            current_section = "projects"
        elif "experience" in lower_sentence or "work experience" in lower_sentence:
            current_section = "experience"
        elif "education" in lower_sentence:
            current_section = "education"
        elif current_section:
            sections[current_section].append(sentence)

    return sections

def summarize_sections(sections, job_role):
    all_content = []
    for section, content in sections.items():
        if content:
            all_content.extend(content)
    
    prompt = f"Summarize the following resume content for a job role of '{job_role}':\n\n" + " ".join(all_content)+ ". Also tell if the resume is fit for the given job profile or not with the sentence: Yes the resume is fit for the entered Job Profile."
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    summary = chat_completion.choices[0].message.content.strip()
    return summary

def rate_readability(text):
    common_resume_keywords = ["experience", "skills", "projects", "education", "work", "professional", "summary"]
    sentences = sent_tokenize(text)
    word_tokens = word_tokenize(text)

    keyword_presence = sum(1 for word in word_tokens if word.lower() in common_resume_keywords)
    keyword_score = min(keyword_presence / len(common_resume_keywords), 1.0) * 4

    coherent_sentences = sum(1 for sentence in sentences if len(word_tokenize(sentence)) > 5)
    coherence_score = min(coherent_sentences / len(sentences), 1.0) * 6

    readability_score = int(keyword_score + coherence_score)

    if len(sentences) < 10 or len(word_tokens) < 100:
        readability_score -= 2 
    if keyword_presence < 2:
        readability_score -= 1

    readability_score = max(min(readability_score, 10), 1)
    print(f"Readability rating: {readability_score}")
    return readability_score

def validate_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(regex, email):
        return True
    else:
        return False

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    job_role = request.form.get('jobRole', '')
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and job_role:
        file_path = os.path.join('uploads', file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        text = read_pdf(file_path)
        if not text:
            return jsonify({'error': 'Unable to read the PDF file'}), 500
        cleaned_text = clean_text(text)
        sections = extract_relevant_sections(cleaned_text)
        summary = summarize_sections(sections, job_role)
        readability_rating = rate_readability(cleaned_text)
        os.remove(file_path)
        return jsonify({'summary': summary, 'readability_rating': readability_rating})
    else:
        return jsonify({'error': 'Please provide a job role'}), 400

@app.route('/review', methods=['POST'])
def submit_review():
    review_data = request.get_json()
    review = review_data.get('review')
    name = review_data.get('name')
    email = review_data.get('email')
    if review and name and email:
        if validate_email(email):
            try:
                with open('reviews.json', 'a') as f:
                    f.write(json.dumps(review_data) + '\n')
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid email address'}), 400
    else:
        return jsonify({'error': 'Name, email, and review text are required'}), 400

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)