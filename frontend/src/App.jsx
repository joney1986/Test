import { useState } from 'react';
import './App.css';

function App() {
  const [resume, setResume] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setResults(null);
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
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
      // Optionally, set an error state here to display to the user
    } finally {
      setLoading(false);
    }
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
      {results && (
        <div id="results-container" className="results">
          <h2>Analysis Results</h2>
          <p><strong>Match Score:</strong> {results.score}%</p>
          {results.keywords && results.keywords.length > 0 ? (
            <>
              <h3>Matching Keywords:</h3>
              <ul>
                {results.keywords.map((keyword, index) => (
                  <li key={index}>{keyword}</li>
                ))}
              </ul>
            </>
          ) : (
            <p>No matching keywords found.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
