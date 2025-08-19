import React, { useState } from 'react';
import '../App.css';

function BuilderPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    linkedin: '',
    summary: '',
    experience: [{ jobTitle: '', company: '', dates: '', responsibilities: '' }],
    education: [{ degree: '', school: '', dates: '' }],
    skills: '',
  });
  const [generatedResume, setGeneratedResume] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e, section, index) => {
    if (section) {
      const newSection = [...formData[section]];
      newSection[index][e.target.name] = e.target.value;
      setFormData({ ...formData, [section]: newSection });
    } else {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    }
  };

  const addSection = (section) => {
    if (section === 'experience') {
      setFormData({
        ...formData,
        experience: [...formData.experience, { jobTitle: '', company: '', dates: '', responsibilities: '' }],
      });
    } else if (section === 'education') {
      setFormData({
        ...formData,
        education: [...formData.education, { degree: '', school: '', dates: '' }],
      });
    }
  };

  const removeSection = (section, index) => {
    const newSection = [...formData[section]];
    newSection.splice(index, 1);
    setFormData({ ...formData, [section]: newSection });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneratedResume('');
    setError(null);
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/generate-resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate resume');
      }
      setGeneratedResume(data.resume_text);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="builder-columns">
        <div className="form-column">
          <h1>AI Resume Builder</h1>
          <p>Fill out the form below to generate your resume.</p>
          <form onSubmit={handleSubmit} className="resume-form">
            <h2>Personal Information</h2>
            <input type="text" name="name" placeholder="Full Name" onChange={handleChange} required />
            <input type="email" name="email" placeholder="Email" onChange={handleChange} required />
            <input type="tel" name="phone" placeholder="Phone" onChange={handleChange} />
            <input type="url" name="linkedin" placeholder="LinkedIn Profile URL" onChange={handleChange} />

            <h2>Professional Summary</h2>
            <textarea name="summary" placeholder="A brief summary of your career" onChange={handleChange}></textarea>

            <h2>Work Experience</h2>
            {formData.experience.map((exp, index) => (
              <div key={index} className="form-section">
                <input type="text" name="jobTitle" placeholder="Job Title" value={exp.jobTitle} onChange={(e) => handleChange(e, 'experience', index)} />
                <input type="text" name="company" placeholder="Company" value={exp.company} onChange={(e) => handleChange(e, 'experience', index)} />
                <input type="text" name="dates" placeholder="Dates (e.g., Jan 2020 - Present)" value={exp.dates} onChange={(e) => handleChange(e, 'experience', index)} />
                <textarea name="responsibilities" placeholder="Key Responsibilities (one per line)" value={exp.responsibilities} onChange={(e) => handleChange(e, 'experience', index)}></textarea>
                {formData.experience.length > 1 && <button type="button" className="remove-btn" onClick={() => removeSection('experience', index)}>Remove</button>}
              </div>
            ))}
            <button type="button" className="add-btn" onClick={() => addSection('experience')}>Add Experience</button>

            <h2>Education</h2>
            {formData.education.map((edu, index) => (
              <div key={index} className="form-section">
                <input type="text" name="degree" placeholder="Degree (e.g., B.S. in Computer Science)" value={edu.degree} onChange={(e) => handleChange(e, 'education', index)} />
                <input type="text" name="school" placeholder="School/University" value={edu.school} onChange={(e) => handleChange(e, 'education', index)} />
                <input type="text" name="dates" placeholder="Dates (e.g., Aug 2016 - May 2020)" value={edu.dates} onChange={(e) => handleChange(e, 'education', index)} />
                {formData.education.length > 1 && <button type="button" className="remove-btn" onClick={() => removeSection('education', index)}>Remove</button>}
              </div>
            ))}
            <button type="button" className="add-btn" onClick={() => addSection('education')}>Add Education</button>

            <h2>Skills</h2>
            <textarea name="skills" placeholder="List your skills, separated by commas" onChange={handleChange}></textarea>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Generating...' : 'Generate Resume'}
            </button>
          </form>
        </div>
        <div className="preview-column">
          <h2>Generated Resume</h2>
          {error && <div className="error-message">{error}</div>}
          <pre className="resume-preview">
            {generatedResume || "Your generated resume will appear here..."}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default BuilderPage;
