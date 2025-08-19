from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import spacy
from spacy.matcher import Matcher
from fpdf import FPDF

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

def create_resume_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    name = data.get('name', '')
    if name:
        pdf.set_font('Helvetica', 'B', 20)
        pdf.cell(0, 10, name.upper(), 0, 1, 'C')

    contact_info = []
    if data.get('email'): contact_info.append(data.get('email'))
    if data.get('phone'): contact_info.append(data.get('phone'))
    if data.get('linkedin'): contact_info.append(data.get('linkedin'))
    if contact_info:
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 10, " | ".join(contact_info), 0, 1, 'C')

    pdf.ln(5)

    # Summary
    summary = data.get('summary', '')
    if summary:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'PROFESSIONAL SUMMARY', 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, summary)
        pdf.ln(5)

    # Work Experience
    experience = data.get('experience', [])
    if experience and any(exp.get('jobTitle') for exp in experience):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'WORK EXPERIENCE', 0, 1)
        for exp in experience:
            if exp.get('jobTitle'):
                pdf.set_font('Helvetica', 'B', 10)
                pdf.cell(0, 5, f"{exp.get('jobTitle', '').upper()} | {exp.get('company', '')} | {exp.get('dates', '')}", 0, 1)
                pdf.set_font('Helvetica', '', 10)
                responsibilities = exp.get('responsibilities', '').split('\n')
                for resp in responsibilities:
                    if resp:
                        pdf.multi_cell(0, 5, f'  - {resp.strip()}')
                pdf.ln(3)

    # Education
    education = data.get('education', [])
    if education and any(edu.get('degree') for edu in education):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'EDUCATION', 0, 1)
        pdf.set_font('Helvetica', '', 10)
        for edu in education:
            if edu.get('degree'):
                pdf.cell(0, 5, f"{edu.get('degree', '')}", 0, 1)
                pdf.cell(0, 5, f"{edu.get('school', '')} | {edu.get('dates', '')}", 0, 1)
                pdf.ln(3)

    # Skills
    skills = data.get('skills', '')
    if skills:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'SKILLS', 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, skills)

    return pdf.output(dest='S').encode('latin-1')

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

    jd_required_skills = set(SKILLS_DB['required'])
    jd_nice_to_have_skills = set(SKILLS_DB['nice_to_have'])

    matched_required = list(resume_skills & jd_required_skills)
    matched_nice_to_have = list(resume_skills & jd_nice_to_have_skills)

    missing_required = list(jd_required_skills - resume_skills)
    missing_nice_to_have = list(jd_nice_to_have_skills - resume_skills)

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

    try:
        pdf_bytes = create_resume_pdf(data)

        response = make_response(pdf_bytes)
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename='resume.pdf')
        return response
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({"error": "An error occurred while generating the PDF."}), 500

if __name__ == '__main__':
    app.run(debug=True)
