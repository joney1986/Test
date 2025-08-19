from flask import Flask, jsonify, request, send_from_directory
import os

# The static folder is now the 'dist' directory of the built React app.
# The path is relative to the location of this script.
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))

app = Flask(__name__, static_folder=static_dir, static_url_path='')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    resume = data.get('resume', '')
    job_description = data.get('job_description', '')

    # Simple keyword extraction and scoring logic
    jd_keywords = set(job_description.lower().split())
    resume_keywords = set(resume.lower().split())

    # Find common keywords
    common_keywords = jd_keywords.intersection(resume_keywords)

    # Ignore common English words (stop words)
    stop_words = set(['a', 'an', 'the', 'in', 'on', 'of', 'for', 'to', 'and', 'is', 'are', 'with', 'it', 'as', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'but', 'if', 'or', 'so', 'about', 'i', 'me', 'my', 'we', 'our', 'you', 'your'])
    meaningful_keywords = [word for word in common_keywords if word not in stop_words and len(word) > 2]

    score = 0
    if len(jd_keywords) > 0:
        # Calculate score based on the number of matching meaningful keywords
        score = (len(meaningful_keywords) / len(jd_keywords - stop_words)) * 100 if len(jd_keywords - stop_words) > 0 else 0

    return jsonify({
        'score': round(score, 2),
        'keywords': list(meaningful_keywords)
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
