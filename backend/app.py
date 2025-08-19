from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import spacy
from spacy.matcher import Matcher
from fpdf import FPDF
import speech_recognition as sr
from pydub import AudioSegment
import io

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# A predefined list of skills, now structured with importance.
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

QUESTION_CATEGORIES = {
    "behavioral": [
        "tell me about a time", "what would you do if", "give me an example",
        "describe a situation", "how do you handle", "teamwork", "conflict",
        "challenge", "failure", "success", "leadership"
    ],
    "technical": [
        "what is", "explain", "how does", "compare", "contrast", "code",
        "algorithm", "data structure", "database", "python", "javascript", "react"
    ],
    "personal": [
        "tell me about yourself", "walk me through your resume",
        "why are you interested in this role", "what are your strengths",
        "what are your weaknesses"
    ]
}

SUGGESTIONS_DB = {
    "behavioral": "Structure your answer using the STAR method:\n- **S (Situation):** Describe the context. What was the situation and where did it take place?\n- **T (Task):** What was your role or responsibility in the situation?\n- **A (Action):** What specific actions did you take to handle the situation?\n- **R (Result):** What was the outcome of your actions? Quantify your success if possible.",
    "technical": {
        "what is python": "Python is a high-level, interpreted programming language known for its clear syntax and readability.",
        "explain javascript": "JavaScript is a programming language that enables interactive web pages. It's a core technology of the web, alongside HTML and CSS.",
        "what is a data structure": "A data structure is a way of organizing and storing data in a computer so that it can be accessed and modified efficiently."
    },
    "personal": "When answering personal questions, be authentic and connect your story to the company's values and the role's requirements. Highlight your passion and what makes you a great fit.",
    "general": "Listen carefully to the question. If you need clarification, it's okay to ask. Take a moment to structure your thoughts before answering."
}

# This is a simulated database of answers that a model like Gemini might provide.
GEMINI_ANSWERS_DB = {
    "behavioral": {
        "default": "Of course. One time at my previous job, we were facing a tight deadline for a critical project deliverable. The situation was that a key team member left unexpectedly, leaving us short-staffed. My task was to reorganize the remaining workload to ensure we still met the deadline. The action I took was to first hold a team meeting to assess our current progress and morale. I then redistributed the tasks, taking on some of the critical path items myself. I also set up a daily check-in to monitor progress and address any roadblocks immediately. The result was that not only did we meet the deadline, but the project was also praised for its quality. This experience taught me the importance of proactive leadership and clear communication in a crisis."
    },
    "technical": {
        "what is python": "Python is a high-level, dynamically-typed programming language that is widely used for web development, data science, artificial intelligence, and scripting. It's known for its simple, clean syntax which emphasizes readability. Key features include a large standard library, automatic memory management, and support for multiple programming paradigms like object-oriented, imperative, functional, and procedural.",
        "default": "That's a great technical question. While the specifics can vary depending on the context, the general principle is that [concept] is a method for [main purpose]. It works by [brief explanation of mechanism]. A common use case is in [example], where it helps to achieve [benefit]."
    },
    "personal": {
        "default": "I'm a passionate and driven software engineer with a background in [Your Field]. Over the past [Number] years, I've honed my skills in [Key Skill 1], [Key Skill 2], and [Key Skill 3]. I'm particularly proud of my work on [Project or Accomplishment], where I was able to [Specific Achievement]. I'm drawn to this role at [Company Name] because of your commitment to [Company Value or Mission], and I'm confident that my skills and experience align perfectly with the requirements of this position."
    },
    "general": {
        "default": "That's an interesting question. Based on my understanding, I would say that the most important aspect to consider is [Key Point]. This is because [Reasoning]. Additionally, one should also take into account [Secondary Point]. Ultimately, it's a balance between these factors."
    }
}

def generate_gemini_answer(category, text):
    """
    Simulates a call to the Google Gemini API to generate a sample answer.
    In a real application, this function would contain the API call.
    """
    text = text.lower()
    if category in GEMINI_ANSWERS_DB:
        # Check for a specific keyword match first (for technical questions)
        if category == "technical":
            for keyword, answer in GEMINI_ANSWERS_DB[category].items():
                if keyword in text:
                    return answer
        # Return the default answer for the category
        return GEMINI_ANSWERS_DB[category].get("default", "I would need a moment to think about that.")
    return GEMINI_ANSWERS_DB["general"]["default"]

# Initialize the Matcher with the shared vocabulary
matcher = Matcher(nlp.vocab)

# Create patterns for all skills
all_skills = SKILLS_DB['required'] + SKILLS_DB['nice_to_have']
for skill in all_skills:
    pattern = [{'LOWER': token} for token in skill.split()]
    matcher.add(skill, [pattern])

app = Flask(__name__)
CORS(app)

# --- PDF Template Functions ---

def create_classic_template(pdf, data):
    """Generates a resume with a classic, centered layout."""
    pdf.set_font('Helvetica', '', 10)
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

    # Sections
    sections = {
        'PROFESSIONAL SUMMARY': data.get('summary'),
        'SKILLS': data.get('skills')
    }
    for title, content in sections.items():
        if content:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, title, 0, 1)
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 5, content)
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

def create_modern_template(pdf, data):
    """Generates a resume with a modern, left-aligned layout and different fonts."""
    pdf.set_text_color(34, 49, 63)
    pdf.set_font('Times', '', 10)

    # Header
    name = data.get('name', '')
    if name:
        pdf.set_font('Times', 'B', 28)
        pdf.cell(0, 12, name, 0, 1, 'L')

    contact_info = []
    if data.get('email'): contact_info.append(data.get('email'))
    if data.get('phone'): contact_info.append(data.get('phone'))
    if data.get('linkedin'): contact_info.append(data.get('linkedin'))
    if contact_info:
        pdf.set_font('Times', '', 10)
        pdf.cell(0, 6, " | ".join(contact_info), 0, 1, 'L')

    pdf.ln(8)

    # Sections
    sections = {
        'PROFESSIONAL SUMMARY': data.get('summary'),
        'SKILLS': data.get('skills')
    }
    for title, content in sections.items():
        if content:
            pdf.set_font('Times', 'B', 14)
            pdf.cell(0, 8, title, 'B', 1)
            pdf.ln(4)
            pdf.set_font('Times', '', 10)
            pdf.multi_cell(0, 5, content)
            pdf.ln(5)

    # Work Experience
    experience = data.get('experience', [])
    if experience and any(exp.get('jobTitle') for exp in experience):
        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 8, 'WORK EXPERIENCE', 'B', 1)
        pdf.ln(4)
        for exp in experience:
            if exp.get('jobTitle'):
                pdf.set_font('Times', 'B', 11)
                pdf.cell(0, 5, f"{exp.get('jobTitle', '').upper()}", 0, 1)
                pdf.set_font('Times', 'I', 10)
                pdf.cell(0, 5, f"{exp.get('company', '')} | {exp.get('dates', '')}", 0, 1)
                pdf.set_font('Times', '', 10)
                responsibilities = exp.get('responsibilities', '').split('\n')
                for resp in responsibilities:
                    if resp:
                        pdf.multi_cell(0, 5, f'  - {resp.strip()}')
                pdf.ln(3)

    # Education
    education = data.get('education', [])
    if education and any(edu.get('degree') for edu in education):
        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 8, 'EDUCATION', 'B', 1)
        pdf.ln(4)
        pdf.set_font('Times', '', 10)
        for edu in education:
            if edu.get('degree'):
                pdf.set_font('Times', 'B', 11)
                pdf.cell(0, 5, f"{edu.get('degree', '')}", 0, 1)
                pdf.set_font('Times', 'I', 10)
                pdf.cell(0, 5, f"{edu.get('school', '')} | {edu.get('dates', '')}", 0, 1)
                pdf.ln(3)

def create_resume_pdf(data):
    """Main controller to generate the PDF."""
    template = data.get('template', 'classic')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    if template == 'modern':
        create_modern_template(pdf, data)
    else:
        create_classic_template(pdf, data)

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

def classify_question(text):
    """Classifies a question into a category based on keywords."""
    text = text.lower()
    for category, keywords in QUESTION_CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return "general" # Default category if no keywords are matched

def get_suggestion(category, text):
    """Gets a suggestion based on the question category and text."""
    if category == "technical":
        text = text.lower()
        # Look for a specific technical keyword in the text
        for keyword, suggestion in SUGGESTIONS_DB["technical"].items():
            if keyword in text:
                return suggestion
        # Generic technical suggestion if no specific keyword is found
        return "For technical questions, be precise. Define the term, explain its purpose, and provide a brief example if possible."
    return SUGGESTIONS_DB.get(category, SUGGESTIONS_DB["general"])

FILLER_WORDS = [
    "um", "uh", "er", "ah", "like", "okay", "right", "so", "you know"
]

@app.route('/analyze-feedback', methods=['POST'])
def analyze_feedback():
    if 'transcriptions' not in request.form or 'audio_files' not in request.files:
        return jsonify({"error": "Missing transcriptions or audio files."}), 400

    transcriptions = request.form.getlist('transcriptions')
    audio_files = request.files.getlist('audio_files')

    total_filler_words = 0
    total_words = 0
    total_duration_s = 0

    for i, text in enumerate(transcriptions):
        # Filler word analysis
        words = text.lower().split()
        total_words += len(words)
        for word in words:
            if word in FILLER_WORDS:
                total_filler_words += 1

        # Pacing analysis
        audio_file = audio_files[i]
        try:
            audio_data = io.BytesIO(audio_file.read())
            audio_segment = AudioSegment.from_file(audio_data) # pydub can infer format
            total_duration_s += audio_segment.duration_seconds
        except Exception as e:
            print(f"Could not process audio file {i}: {e}")
            # Skip this file if it's corrupted or in a wrong format
            continue

    wpm = (total_words / total_duration_s) * 60 if total_duration_s > 0 else 0

    feedback = {
        "filler_word_count": total_filler_words,
        "wpm": round(wpm, 2),
        "total_words": total_words,
        "total_duration_seconds": round(total_duration_s, 2)
    }

    return jsonify(feedback)


@app.route('/analyze', methods=['POST'])
def analyze():
    # ... (analyze function is the same)
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
    # This endpoint is now updated in the next step
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

@app.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided."}), 400

    resume_data = data.get('formData', {})
    job_description = data.get('jobDescription', '')

    if not job_description:
        return jsonify({'suggestions': []}) # Return empty if no JD

    # --- Suggestions Logic ---
    suggestions = []

    # 1. Skill comparison suggestion
    jd_skills = set(extract_skills(job_description))
    resume_skills_text = resume_data.get('skills', '')
    resume_skills = set([s.strip().lower() for s in resume_skills_text.split(',')])

    missing_skills = jd_skills - resume_skills
    if missing_skills:
        suggestions.append(f"Consider adding these skills from the job description to your resume: {', '.join(missing_skills)}.")

    # 2. Keyword in summary suggestion
    summary = resume_data.get('summary', '').lower()
    jd_keywords = [skill for skill in SKILLS_DB['required'] if skill in job_description.lower()]
    missing_keywords_in_summary = [kw for kw in jd_keywords if kw not in summary]

    if missing_keywords_in_summary:
        suggestions.append(f"Your summary could be stronger. Try to include keywords like: {', '.join(missing_keywords_in_summary)}.")

    if not suggestions and jd_skills:
        suggestions.append("Your resume looks like a great match for this job description! No immediate suggestions.")

    return jsonify({
        'suggestions': suggestions
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files['audio']

    # The audio from the browser is in webm format, so we need to convert it
    try:
        # Read the audio file in memory
        audio_data = io.BytesIO(audio_file.read())

        # Convert webm to wav using pydub
        audio_segment = AudioSegment.from_file(audio_data, format="webm")

        # Export to wav format in memory
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)

        # Use SpeechRecognition to transcribe the audio
        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio = r.record(source)

        # Recognize speech using Google Web Speech API
        text = r.recognize_google(audio)

        # Classify the question
        category = classify_question(text)

        # Get a suggestion
        suggestion = get_suggestion(category, text)

        # Get a sample answer
        gemini_answer = generate_gemini_answer(category, text)

        return jsonify({
            'transcription': text,
            'category': category,
            'suggestion': suggestion,
            'gemini_answer': gemini_answer
        })

    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"error": "Failed to transcribe audio."}), 500

if __name__ == '__main__':
    app.run(debug=True)
