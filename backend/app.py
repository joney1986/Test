from flask import Flask, jsonify, request
from flask_cors import CORS
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# A predefined list of skills. This can be expanded significantly.
SKILLS_DB = [
    'python', 'java', 'c++', 'javascript', 'react', 'angular', 'vue',
    'sql', 'nosql', 'mongodb', 'postgresql', 'docker', 'kubernetes',
    'aws', 'azure', 'gcp', 'machine learning', 'deep learning', 'nlp',
    'data analysis', 'project management', 'agile', 'scrum'
]

app = Flask(__name__)
CORS(app)

def extract_skills(text):
    """Extracts skills from a text using spaCy's noun chunks and a predefined skill list."""
    doc = nlp(text.lower())

    # Using noun chunks to find potential skills
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]

    # Combining with a search for our predefined skills
    found_skills = set()
    for skill in SKILLS_DB:
        if skill in text.lower():
            found_skills.add(skill)

    for chunk in noun_chunks:
        if chunk in SKILLS_DB:
            found_skills.add(chunk)

    return list(found_skills)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    resume_text = data.get('resume', '')
    jd_text = data.get('job_description', '')

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    # Calculate matched and missing skills
    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))

    # Calculate score
    score = 0
    if len(jd_skills) > 0:
        score = (len(matched_skills) / len(jd_skills)) * 100

    return jsonify({
        'score': round(score, 2),
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
    })

if __name__ == '__main__':
    app.run(debug=True)
