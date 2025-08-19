import { useState } from 'react';
import '../App.css';

function AnalyzerPage() {
  const [resume, setResume] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setResults(null);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume,
          job_description: jobDescription,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Network response was not ok');
      }
      setResults(data);
    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const renderSkillsList = (skills, title) => {
    if (!skills || skills.length === 0) {
      return <p>None</p>;
    }
    return (
      <div className="skills-category">
        <h4>{title}</h4>
        <ul>
          {skills.map((skill, index) => (
            <li key={index}>{skill}</li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="container">
      <h1>Final Round AI - Resume Analyzer</h1>
      <p>Paste your resume and the job description below to get a match score.</p>
      <div className="text-areas">
        <div className="textarea-container">
          <h2>Your Resume</h2>
          <textarea
            id="resume"
            placeholder="Paste your resume here..."
            value={resume}
            onChange={(e) => setResume(e.target.value)}
          />
        </div>
        <div className="textarea-container">
          <h2>Job Description</h2>
          <textarea
            id="job-description"
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>
      </div>
      <button id="analyze-button" onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
      {error && <div className="error-message">{error}</div>}
      {results && (
        <div id="results-container" className="results">
          <h2>Analysis Results</h2>
          <h3>Overall Match Score: {results.score}%</h3>
          <div className="skills-grid">
            <div className="skills-column">
              <h3>Matched Skills</h3>
              {renderSkillsList(results.matched_skills.required, 'Required')}
              {renderSkillsList(results.matched_skills.nice_to_have, 'Nice-to-Have')}
            </div>
            <div className="skills-column">
              <h3>Missing Skills</h3>
              {renderSkillsList(results.missing_skills.required, 'Required')}
              {renderSkillsList(results.missing_skills.nice_to_have, 'Nice-to-Have')}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyzerPage;
