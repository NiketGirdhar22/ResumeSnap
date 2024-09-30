from PyPDF2 import PdfReader
import docx
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = [p.text for p in doc.paragraphs]
    return "\n".join(text)

def preprocess_text_spacy(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return tokens

def extract_keywords_spacy(job_description):
    return preprocess_text_spacy(job_description)

def keyword_matching_score_spacy(resume_text, job_keywords):
    resume_tokens = preprocess_text_spacy(resume_text)
    score = sum([1 for token in resume_tokens if token in job_keywords])
    return score

def calculate_similarity_score(resume_text, job_description):
    documents = [resume_text, job_description]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return cosine_sim[0][0]

def generate_ats_score(resume_text, job_description):
    job_keywords = extract_keywords_spacy(job_description)
    keyword_score = keyword_matching_score_spacy(resume_text, job_keywords)
    similarity_score = calculate_similarity_score(resume_text, job_description)
    
    # Combine the scores and normalize
    combined_score = (keyword_score + similarity_score * 100) / 2
    return combined_score, job_keywords, keyword_score, similarity_score

# Example usage
resume_text = extract_text_from_pdf('resume.pdf')
job_description = extract_text_from_docx('Job Description.docx')

ats_score, job_keywords, keyword_score, similarity_score = generate_ats_score(resume_text, job_description)
print(f"Score: {ats_score:.2f} out of 100")
print(f"Job Keywords: {job_keywords}")
print(f"Keyword Matching Score: {keyword_score}")
print(f"Similarity Score: {similarity_score:.2f} out of 1")