import React from 'react';

// --- SVG Icon Components ---
const WorkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
);
const EducationIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"></path></svg>
);
const SkillsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
);
// --- End SVG Icon Components ---

const Preview = ({ data, templateName }) => {
  const templateClass = templateName || 'Original';

  const renderSkills = () => {
    if (templateName === 'Swiss') {
      return (
        <div className="progress-skills">
          {(data.detailedSkills || []).map((skill, index) => (
            <div key={index} className="progress-skill-item">
              <p>{skill.name}</p>
              <div className="progress-bar">
                <div className="progress-bar-inner" style={{ width: `${skill.level}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      );
    }
    if (templateName === 'Pillbox') {
      return (
        <div className="skill-pills">
          {(data.skills || 'Client-Side, Server-side, Development & Operations')
            .split(',')
            .map((skill, index) => (
              <span key={index} className="skill-pill">{skill.trim()}</span>
          ))}
        </div>
      );
    }
    return <p>{data.skills || 'Skill 1, Skill 2, Skill 3'}</p>;
  };

  return (
    <div className={`resume-preview ${templateClass}`}>
      <div className="main-content">
        <header className="resume-header">
          <h1>{data.name || 'Your Name'}</h1>
          <p>{data.email || 'your.email@example.com'} | {data.phone || '123-456-7890'} | {data.linkedin || 'linkedin.com/in/yourprofile'}</p>
        </header>
        <section className="summary-section">
          <h2>Professional Summary</h2>
          <p>{data.summary || 'A brief professional summary about your career, skills, and goals.'}</p>
        </section>
        <section className="experience-section">
          <h2 className="section-title">{templateName === 'Swiss' && <WorkIcon />} Work Experience</h2>
          {data.experience.map((exp, index) => (
            <div key={index} className="job">
              <h3>{exp.jobTitle || 'Job Title'} at {exp.company || 'Company'}</h3>
              <p className="dates">{exp.dates || 'Month Year - Month Year'}</p>
              <p>{exp.responsibilities || 'Key responsibilities and achievements.'}</p>
            </div>
          ))}
        </section>
      </div>
      <div className="sidebar">
        <section className="education-section">
          <h2 className="section-title">{templateName === 'Swiss' && <EducationIcon />} Education</h2>
          {data.education.map((edu, index) => (
            <div key={index} className="education-entry">
              <h3>{edu.degree || 'Degree'}</h3>
              <p>{edu.school || 'School/University'} - {edu.dates || 'Year'}</p>
            </div>
          ))}
        </section>
        <section className="skills-section">
          <h2 className="section-title">{templateName === 'Swiss' && <SkillsIcon />} Skills</h2>
          {renderSkills()}
        </section>
      </div>
    </div>
  );
};

export default Preview;
