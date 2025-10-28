import React, { useState, useEffect } from 'react';
import Preview from './Preview';
import TemplateGallery from './TemplateGallery';
import { useAuth } from '../context/AuthContext';
import '../App.css';
import '../styles/templates/Original.css';
import '../styles/templates/Harvard.css';
import '../styles/templates/Pillbox.css';
import '../styles/templates/Swiss.css';

const templates = [
  { id: 'Original', name: 'Original', thumbnail: 'https://cdn.enhancv.com/predefined-examples/J3V4PtHeJHYSg1beoq1kVI2hUjELaVRbVPGxNjsR/image.png' },
  { id: 'Harvard', name: 'Harvard', thumbnail: 'https://cdn.enhancv.com/predefined-examples/J3V4PtHeJHYSg1beoq1kVI2hUjELaVRbVPGxNjsR/image.png' },
  { id: 'Pillbox', name: 'Pillbox', thumbnail: 'https://cdn.enhancv.com/predefined-examples/cB6IJmJsn0HkbrvBgqegn3MUTOdbH5lk48fbLgfg/image.png' },
  { id: 'Swiss', name: 'Swiss', thumbnail: 'https://cdn.enhancv.com/predefined-examples/wKSNOJgrxVvWIKOehnx8dk5F1vJD667kyFcdSsmF/image.png' },
];

function BuilderPage() {
  const { isAuthenticated, token } = useAuth();

  const initialData = {
    name: '',
    email: '',
    phone: '',
    linkedin: '',
    summary: '',
    experience: [{ jobTitle: '', company: '', dates: '', responsibilities: '' }],
    education: [{ degree: '', school: '', dates: '' }],
    skills: '',
    detailedSkills: [{ name: 'Project Management', level: 80 }, { name: 'Agile', level: 90 }, { name: 'Scrum', level: 75 }],
    template: 'Original', // Default template
  };

  const [formData, setFormData] = useState(() => {
    const savedData = localStorage.getItem('resumeData');
    return savedData ? JSON.parse(savedData) : initialData;
  });

  const [saveStatus, setSaveStatus] = useState('');


  // Effect for loading data from API if user is logged in
  useEffect(() => {
    const loadFromApi = async () => {
      if (isAuthenticated) {
        try {
          const response = await fetch('http://127.0.0.1:5000/api/resume', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          if (response.ok) {
            const data = await response.json();
            if (data) {
              setFormData(data);
            }
          }
        } catch (error) {
          console.error("Failed to load resume from API", error);
        }
      }
    };
    loadFromApi();
  }, [isAuthenticated, token]);


  // Effect for saving data to localStorage
  useEffect(() => {
    localStorage.setItem('resumeData', JSON.stringify(formData));
  }, [formData]);


  const handleSaveToCloud = async () => {
    if (!isAuthenticated) {
        setSaveStatus("Please log in to save your resume to the cloud.");
        return;
    }
    setSaveStatus("Saving...");
    try {
        const response = await fetch('http://127.0.0.1:5000/api/resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(formData),
        });
        if (response.ok) {
            setSaveStatus("Saved successfully!");
        } else {
            setSaveStatus("Failed to save.");
        }
    } catch (error) {
        console.error("Failed to save to cloud", error);
        setSaveStatus("Error saving.");
    }
  };


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

  const handleReorder = (section, index, direction) => {
    const list = [...formData[section]];
    const newIndex = direction === 'up' ? index - 1 : index + 1;

    if (newIndex >= 0 && newIndex < list.length) {
      const [movedItem] = list.splice(index, 1);
      list.splice(newIndex, 0, movedItem);
      setFormData({ ...formData, [section]: list });
    }
  };

  const handleDetailedSkillChange = (index, field, value) => {
    const newSkills = [...formData.detailedSkills];
    newSkills[index][field] = value;
    setFormData({ ...formData, detailedSkills: newSkills });
  };

  const addDetailedSkill = () => {
    setFormData({
      ...formData,
      detailedSkills: [...formData.detailedSkills, { name: '', level: 50 }],
    });
  };

  const removeDetailedSkill = (index) => {
    const newSkills = [...formData.detailedSkills];
    newSkills.splice(index, 1);
    setFormData({ ...formData, detailedSkills: newSkills });
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="container">
      <div className="builder-columns">
        <div className="form-column">
          <h1>Resume Builder</h1>
          <p>Fill out the form below to see your resume update in real-time.</p>
          <div className="resume-form">
            <TemplateGallery
              templates={templates}
              selectedTemplate={formData.template}
              onSelect={(templateId) => setFormData({ ...formData, template: templateId })}
            />

            <h2>Personal Information</h2>
            <input type="text" name="name" placeholder="Full Name" value={formData.name} onChange={handleChange} required />
            <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
            <input type="tel" name="phone" placeholder="Phone" value={formData.phone} onChange={handleChange} />
            <input type="url" name="linkedin" placeholder="LinkedIn Profile URL" value={formData.linkedin} onChange={handleChange} />

            <h2>Professional Summary</h2>
            <textarea name="summary" placeholder="A brief summary of your career" value={formData.summary} onChange={handleChange}></textarea>

            <h2>Work Experience</h2>
            {formData.experience.map((exp, index) => (
              <div key={index} className="form-section">
                <input type="text" name="jobTitle" placeholder="Job Title" value={exp.jobTitle} onChange={(e) => handleChange(e, 'experience', index)} />
                <input type="text" name="company" placeholder="Company" value={exp.company} onChange={(e) => handleChange(e, 'experience', index)} />
                <input type="text" name="dates" placeholder="Dates (e.g., Jan 2020 - Present)" value={exp.dates} onChange={(e) => handleChange(e, 'experience', index)} />
                <textarea name="responsibilities" placeholder="Key Responsibilities (one per line)" value={exp.responsibilities} onChange={(e) => handleChange(e, 'experience', index)}></textarea>
                <div className="section-buttons">
                  <button type="button" onClick={() => handleReorder('experience', index, 'up')} disabled={index === 0}>▲ Up</button>
                  <button type="button" onClick={() => handleReorder('experience', index, 'down')} disabled={index === formData.experience.length - 1}>▼ Down</button>
                  {formData.experience.length > 1 && <button type="button" className="remove-btn" onClick={() => removeSection('experience', index)}>Remove</button>}
                </div>
              </div>
            ))}
            <button type="button" className="add-btn" onClick={() => addSection('experience')}>Add Experience</button>

            <h2>Education</h2>
            {formData.education.map((edu, index) => (
              <div key={index} className="form-section">
                <input type="text" name="degree" placeholder="Degree (e.g., B.S. in Computer Science)" value={edu.degree} onChange={(e) => handleChange(e, 'education', index)} />
                <input type="text" name="school" placeholder="School/University" value={edu.school} onChange={(e) => handleChange(e, 'education', index)} />
                <input type="text" name="dates" placeholder="Dates (e.g., Aug 2016 - May 2020)" value={edu.dates} onChange={(e) => handleChange(e, 'education', index)} />
                <div className="section-buttons">
                  <button type="button" onClick={() => handleReorder('education', index, 'up')} disabled={index === 0}>▲ Up</button>
                  <button type="button" onClick={() => handleReorder('education', index, 'down')} disabled={index === formData.education.length - 1}>▼ Down</button>
                  {formData.education.length > 1 && <button type="button" className="remove-btn" onClick={() => removeSection('education', index)}>Remove</button>}
                </div>
              </div>
            ))}
            <button type="button" className="add-btn" onClick={() => addSection('education')}>Add Education</button>

            <h2>Skills</h2>
            <textarea name="skills" placeholder="List your skills, separated by commas" value={formData.skills} onChange={handleChange}></textarea>

            {formData.template === 'Swiss' && (
              <div className="detailed-skills-section">
                <h2>Detailed Skills (for Swiss Template)</h2>
                {formData.detailedSkills.map((skill, index) => (
                  <div key={index} className="form-section">
                    <input
                      type="text"
                      placeholder="Skill Name"
                      value={skill.name}
                      onChange={(e) => handleDetailedSkillChange(index, 'name', e.target.value)}
                    />
                    <div className="slider-container">
                      <label>Level: {skill.level}%</label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        step="5"
                        value={skill.level}
                        className="level-slider"
                        onChange={(e) => handleDetailedSkillChange(index, 'level', parseInt(e.target.value, 10))}
                      />
                    </div>
                    <button type="button" className="remove-btn" onClick={() => removeDetailedSkill(index)}>Remove</button>
                  </div>
                ))}
                <button type="button" className="add-btn" onClick={addDetailedSkill}>Add Detailed Skill</button>
              </div>
            )}
          </div>
          </div>
          <div className="action-buttons">
            <button type="button" className="submit-btn" onClick={handleSaveToCloud}>
              Save to Cloud
            </button>
            <button type="button" className="submit-btn" onClick={handlePrint}>
              Download as PDF
            </button>
          </div>
          {saveStatus && <p className="message">{saveStatus}</p>}
        </div>
        <div className="preview-column">
          <Preview data={formData} templateName={formData.template} />
        </div>
      </div>
    </div>
  );
}

export default BuilderPage;
