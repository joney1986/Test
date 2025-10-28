import React from 'react';
import '../styles/TemplateGallery.css';

const TemplateGallery = ({ templates, selectedTemplate, onSelect }) => {
  return (
    <div className="template-gallery">
      <h2>Template</h2>
      <div className="gallery-grid">
        {templates.map((template) => (
          <div
            key={template.id}
            className={`gallery-item ${selectedTemplate === template.id ? 'selected' : ''}`}
            onClick={() => onSelect(template.id)}
            title={`Select ${template.name} template`}
          >
            <img src={template.thumbnail} alt={`${template.name} Template Thumbnail`} />
            <p className="template-name">{template.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemplateGallery;
