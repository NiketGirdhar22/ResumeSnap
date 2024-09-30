from PyPDF2 import PdfReader
import docx
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Define specific keyword sets
experience_keywords = {'experience', 'years', 'worked', 'developed'}
education_keywords = {'bachelor', 'master', 'phd', 'degree'}
certification_keywords = {'certification', 'certified', 'credential'}
job_title_keywords = {'developer', 'engineer', 'programmer','intern'}
achievement_keywords = {'achievement', 'award', 'project', 'accomplished'}

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

def extract_experience(resume_text):
    # Extracting sentences containing experience-related keywords
    doc = nlp(resume_text)
    experience_sentences = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in experience_keywords)]
    return experience_sentences

def experience_score(resume_text, job_experience):
    resume_experience = extract_experience(resume_text)
    if job_experience == 0:
        return 0.0
    score = min(len(resume_experience) / job_experience * 100, 100)
    return score

def extract_education(resume_text):
    # Extracting sentences containing education-related keywords
    doc = nlp(resume_text)
    education_sentences = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in education_keywords)]
    return education_sentences

def education_score(resume_text, required_education):
    resume_education = extract_education(resume_text)
    if required_education == '':
        return 0.0
    if any(required_education.lower() in sentence.lower() for sentence in resume_education):
        score = 100
    else:
        score = 0
    return score

def extract_certifications(resume_text):
    # Extracting sentences containing certification-related keywords
    doc = nlp(resume_text)
    certifications_sentences = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in certification_keywords)]
    return certifications_sentences

def certifications_score(resume_text, job_certifications):
    resume_certifications = extract_certifications(resume_text)
    if len(job_certifications) == 0:
        return 0.0
    matched_certifications = set(resume_certifications) & set(job_certifications)
    score = len(matched_certifications) / len(job_certifications) * 100
    return score

def extract_job_titles(resume_text):
    # Extracting sentences containing job title-related keywords
    doc = nlp(resume_text)
    job_titles_sentences = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in job_title_keywords)]
    return job_titles_sentences

def job_titles_score(resume_text, job_titles):
    resume_job_titles = extract_job_titles(resume_text)
    if len(job_titles) == 0:
        return 0.0
    matched_job_titles = set(resume_job_titles) & set(job_titles)
    score = len(matched_job_titles) / len(job_titles) * 100
    return score

def extract_achievements_projects(resume_text):
    # Extracting sentences containing achievement-related keywords
    doc = nlp(resume_text)
    achievements_sentences = [sent.text for sent in doc.sents if any(keyword in sent.text.lower() for keyword in achievement_keywords)]
    return achievements_sentences

def achievements_projects_score(resume_text, job_achievements_projects):
    resume_achievements_projects = extract_achievements_projects(resume_text)
    if len(job_achievements_projects) == 0:
        return 0.0
    matched_achievements_projects = set(resume_achievements_projects) & set(job_achievements_projects)
    score = len(matched_achievements_projects) / len(job_achievements_projects) * 100
    return score

def extract_skills(resume_text):
    # Process the resume text with spaCy
    doc = nlp(resume_text)
    
    # Initialize an empty list to store skills
    skills = []
    
    # Iterate over each entity in the document
    for ent in doc.ents:
        # Check if the entity label is 'SKILL'
        if ent.label_ == 'SKILL':
            # Add the skill to the list, removing any leading/trailing whitespace and converting to lowercase
            skills.append(ent.text.strip().lower())
    
    # Return the list of skills
    return skills

def generate_ats_score(resume_text, job_description):
    job_keywords = extract_keywords_spacy(job_description)
    keyword_score = keyword_matching_score_spacy(resume_text, job_keywords)
    similarity_score = calculate_similarity_score(resume_text, job_description)
    skills_score = len(extract_skills(resume_text))  # Assuming skills count as a score
    experience = experience_score(resume_text, 5)  # Example: 5 years of required experience
    education = education_score(resume_text, 'Bachelor of Science')  # Example: Required education
    certifications = certifications_score(resume_text, extract_certifications(job_description))
    job_titles = job_titles_score(resume_text, extract_job_titles(job_description))
    achievements_projects = achievements_projects_score(resume_text, extract_achievements_projects(job_description))
    
    # Calculate combined score based on weights
    combined_score = (keyword_score * 0.3 +
                      skills_score * 0.25 +
                      similarity_score * 0.2 +
                      experience * 0.2 +
                      education * 0.1 +
                      certifications * 0.05 +
                      job_titles * 0.05 +
                      achievements_projects * 0.05)
    
    return combined_score, job_keywords, keyword_score, similarity_score, skills_score, experience, education, certifications, job_titles, achievements_projects

# Example usage
if __name__ == "__main__":
    resume_text = extract_text_from_pdf('resume.pdf')
    job_description = extract_text_from_docx('Job Description.docx')

    ats_score, job_keywords, keyword_score, similarity_score, skills_score, experience, education, certifications, job_titles, achievements_projects = generate_ats_score(resume_text, job_description)
    
    print(f"ATS Score: {ats_score:.2f} out of 100")
    print(f"Job Keywords: {job_keywords}")
    print(f"Keyword Matching Score: {keyword_score}")
    print(f"Similarity Score: {similarity_score:.2f} out of 1")
    print(f"Skills Count: {skills_score}")
    print(f"Experience Score: {experience:.2f} out of 100")
    print(f"Education Score: {education:.2f} out of 100")
    print(f"Certifications Score: {certifications:.2f} out of 100")
    print(f"Job Titles Score: {job_titles:.2f} out of 100")
    print(f"Achievements and Projects Score: {achievements_projects:.2f} out of 100")
