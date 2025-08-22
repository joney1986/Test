import React from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import './App.css';
import AnalyzerPage from './components/AnalyzerPage';
import BuilderPage from './components/BuilderPage';
import Register from './components/Register';
import Login from './components/Login';
import { useAuth } from './context/AuthContext';

function App() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/'); // Redirect to home page after logout
  };

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
            {isAuthenticated ? (
              <li className="nav-item">
                <button onClick={handleLogout} className="nav-link-button">Logout</button>
              </li>
            ) : (
              <>
                <li className="nav-item">
                  <Link to="/register" className="nav-link">Register</Link>
                </li>
                <li className="nav-item">
                  <Link to="/login" className="nav-link">Login</Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </nav>
      <div className="main-content">
        <Routes>
          <Route path="/" element={<AnalyzerPage />} />
          <Route path="/builder" element={<BuilderPage />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
