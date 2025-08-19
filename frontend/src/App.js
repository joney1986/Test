import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import './App.css';
import AnalyzerPage from './components/AnalyzerPage';
import BuilderPage from './components/BuilderPage';
import CopilotPage from './components/CopilotPage';
import FeedbackPage from './components/FeedbackPage';

function App() {
  return (
    <div>
      <nav className="navbar">
        <div className="container">
          <Link to="/" className="nav-logo">Final Round AI</Link>
          <ul className="nav-menu">
            <li className="nav-item">
              <Link to="/" className="nav-link">Resume Analyzer</Link>
            </li>
            <li className="nav-item">
              <Link to="/builder" className="nav-link">Resume Builder</Link>
            </li>
            <li className="nav-item">
              <Link to="/copilot" className="nav-link">Interview Copilot</Link>
            </li>
          </ul>
        </div>
      </nav>
      <div className="main-content">
        <Routes>
          <Route path="/" element={<AnalyzerPage />} />
          <Route path="/builder" element={<BuilderPage />} />
          <Route path="/copilot" element={<CopilotPage />} />
          <Route path="/feedback" element={<FeedbackPage />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
