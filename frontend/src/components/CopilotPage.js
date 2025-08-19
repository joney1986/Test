import React, { useState } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import { useNavigate } from 'react-router-dom';

function CopilotPage() {
  const [transcribedText, setTranscribedText] = useState('');
  const [questionCategory, setQuestionCategory] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const [geminiAnswer, setGeminiAnswer] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState(null);
  const [interviewData, setInterviewData] = useState([]);
  const navigate = useNavigate();

  const handleStop = async (blobUrl, blob) => {
    const formData = new FormData();
    formData.append('audio', blob, 'audio.webm');

    try {
      const response = await fetch('http://127.0.0.1:5000/transcribe', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to transcribe audio');
      }
      setTranscribedText(data.transcription);
      setQuestionCategory(data.category);
      setSuggestion(data.suggestion);
      setGeminiAnswer(data.gemini_answer);

      // Add the new data to the interviewData array
      setInterviewData(prevData => [...prevData, {
        transcription: data.transcription,
        category: data.category,
        suggestion: data.suggestion,
        gemini_answer: data.gemini_answer,
        blobUrl: blobUrl,
        blob: blob,
      }]);

    } catch (err) {
      setError(err.message);
    }
  };

  const { status, startRecording, stopRecording, mediaBlobUrl } = useReactMediaRecorder({
    audio: true,
    onStop: handleStop,
  });

  const handleStartRecording = () => {
    setTranscribedText('');
    setQuestionCategory('');
    setSuggestion('');
    setGeminiAnswer('');
    setError(null);
    setIsRecording(true);
    startRecording();
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    stopRecording();
  };

  const handleFinishInterview = () => {
    navigate('/feedback', { state: { interviewData } });
  };

  return (
    <div className="container">
      <h1>Interview Copilot</h1>
      <p>Your smart assistant for interviews.</p>
      <div className="copilot-controls">
        <p>Status: {status}</p>
        <button onClick={handleStartRecording} disabled={isRecording}>
          Start Recording
        </button>
        <button onClick={handleStopRecording} disabled={!isRecording}>
          Stop Recording
        </button>
      </div>

      {mediaBlobUrl && !isRecording && (
        <div className="audio-player">
          <h3>Last Answer:</h3>
          <audio src={mediaBlobUrl} controls />
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {transcribedText && (
        <div className="transcription">
          <h3>Transcription:</h3>
          <p>{transcribedText}</p>
          {questionCategory && (
            <p><strong>Question Category:</strong> {questionCategory}</p>
          )}
        </div>
      )}

      {suggestion && (
        <div className="suggestion">
          <h3>Suggestion:</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{suggestion}</p>
        </div>
      )}

      {geminiAnswer && (
        <div className="gemini-answer">
          <h3>AI-Generated Sample Answer:</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{geminiAnswer}</p>
          <small>Note: This is an AI-generated sample. Use it as inspiration, but always be authentic.</small>
        </div>
      )}

      {interviewData.length > 0 && (
        <div className="finish-interview-section">
          <hr />
          <p>You have answered {interviewData.length} questions.</p>
          <button onClick={handleFinishInterview}>
            Finish Interview & Get Feedback
          </button>
        </div>
      )}
    </div>
  );
}

export default CopilotPage;
