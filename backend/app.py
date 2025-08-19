from flask import Flask, jsonify, request
from flask_cors import CORS
import spacy
from spacy.matcher import Matcher

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# A predefined list of skills, now structured with importance.
# In a real-world app, this might be dynamically determined.
SKILLS_DB = {
    "required": [
        'python', 'javascript', 'sql', 'machine learning', 'project management'
    ],
    "nice_to_have": [
        'java', 'c++', 'react', 'angular', 'vue', 'nosql', 'mongodb',
        'postgresql', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
        'deep learning', 'nlp', 'data analysis', 'agile', 'scrum'
    ]
}

# Initialize the Matcher with the shared vocabulary
matcher = Matcher(nlp.vocab)

# Create patterns for all skills
all_skills = SKILLS_DB['required'] + SKILLS_DB['nice_to_have']
for skill in all_skills:
    pattern = [{'LOWER': token} for token in skill.split()]
    matcher.add(skill, [pattern])

app = Flask(__name__)
CORS(app)

def extract_skills(text):
    """Extracts skills from a text using spaCy's Matcher."""
    doc = nlp(text)
    matches = matcher(doc)
    found_skills = set()
    for match_id, start, end in matches:
        skill = nlp.vocab.strings[match_id]
        found_skills.add(skill)
    return list(found_skills)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    resume_text = data.get('resume', '')
    jd_text = data.get('job_description', '')

    if not resume_text or not jd_text:
        return jsonify({"error": "Resume or job description is missing."}), 400

    resume_skills = set(extract_skills(resume_text))

    # For this version, we assume the job description skills are our predefined lists
    # A more advanced version would extract these from the jd_text
    jd_required_skills = set(SKILLS_DB['required'])
    jd_nice_to_have_skills = set(SKILLS_DB['nice_to_have'])

    # Calculate matched skills
    matched_required = list(resume_skills & jd_required_skills)
    matched_nice_to_have = list(resume_skills & jd_nice_to_have_skills)

    # Calculate missing skills
    missing_required = list(jd_required_skills - resume_skills)
    missing_nice_to_have = list(jd_nice_to_have_skills - resume_skills)

    # Calculate weighted score
    score = 0
    if len(jd_required_skills) > 0:
        required_score = (len(matched_required) / len(jd_required_skills)) * 70
        score += required_score

    if len(jd_nice_to_have_skills) > 0:
        nice_to_have_score = (len(matched_nice_to_have) / len(jd_nice_to_have_skills)) * 30
        score += nice_to_have_score

    return jsonify({
        'score': round(score, 2),
        'matched_skills': {
            "required": matched_required,
            "nice_to_have": matched_nice_to_have
        },
        'missing_skills': {
            "required": missing_required,
            "nice_to_have": missing_nice_to_have
        }
    })

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided."}), 400

    # --- Resume Generation Logic ---

    resume_text = ""

    # Header
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    linkedin = data.get('linkedin', '')
    if name:
        resume_text += f"{name.upper()}\n"
    if email or phone or linkedin:
        resume_text += f"{email} | {phone} | {linkedin}\n"
    resume_text += "="*50 + "\n\n"

    # Summary
    summary = data.get('summary', '')
    if summary:
        resume_text += "PROFESSIONAL SUMMARY\n"
        resume_text += "-"*50 + "\n"
        resume_text += f"{summary}\n\n"

    # Work Experience
    experience = data.get('experience', [])
    if experience and any(exp.get('jobTitle') for exp in experience):
        resume_text += "WORK EXPERIENCE\n"
        resume_text += "-"*50 + "\n"
        for exp in experience:
            if exp.get('jobTitle'):
                resume_text += f"{exp.get('jobTitle', '').upper()} | {exp.get('company', '')} | {exp.get('dates', '')}\n"
                # Split responsibilities by newline and format as bullet points
                responsibilities = exp.get('responsibilities', '').split('\n')
                for resp in responsibilities:
                    if resp:
                        resume_text += f"  - {resp.strip()}\n"
                resume_text += "\n"

    # Education
    education = data.get('education', [])
    if education and any(edu.get('degree') for edu in education):
        resume_text += "EDUCATION\n"
        resume_text += "-"*50 + "\n"
        for edu in education:
            if edu.get('degree'):
                resume_text += f"{edu.get('degree', '')}\n"
                resume_text += f"{edu.get('school', '')} | {edu.get('dates', '')}\n\n"

    # Skills
    skills = data.get('skills', '')
    if skills:
        resume_text += "SKILLS\n"
        resume_text += "-"*50 + "\n"
        resume_text += f"{skills}\n"

    return jsonify({
        'resume_text': resume_text
    })

if __name__ == '__main__':
    app.run(debug=True)
