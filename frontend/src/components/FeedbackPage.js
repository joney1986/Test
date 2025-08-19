import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

function FeedbackPage() {
  const location = useLocation();
  const { interviewData } = location.state || { interviewData: [] };
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (interviewData.length > 0) {
      const analyze = async () => {
        try {
          const formData = new FormData();
          interviewData.forEach(item => {
            formData.append('transcriptions', item.transcription);
            // The blob is already in the correct format (webm)
            formData.append('audio_files', item.blob, `audio_${Date.now()}.webm`);
          });

          const response = await fetch('http://127.0.0.1:5000/analyze-feedback', {
            method: 'POST',
            body: formData,
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze feedback');
          }
          setFeedback(data);
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };
      analyze();
    } else {
      setLoading(false);
    }
  }, [interviewData]);

  const getPacingFeedback = (wpm) => {
    if (wpm < 140) {
      return "Your pace is a bit slow. Try to speak more fluidly, but don't rush.";
    }
    if (wpm > 160) {
      return "Your pace is a bit fast. Take a breath and try to slow down to ensure the interviewer can follow you.";
    }
    return "Your pacing is great! You are speaking at a conversational and easy-to-follow pace (140-160 WPM).";
  };

  const getFillerWordFeedback = (count) => {
    if (count > 5) {
      return `You used ${count} filler words. Try to be more mindful of them. Pausing to think is better than using a filler word.`;
    }
    if (count > 0) {
      return `You used ${count} filler words, which is very common. Keep practicing to reduce them further.`;
    }
    return "Excellent! You didn't use any common filler words.";
  };

  if (loading) {
    return <div className="container"><h1>Analyzing your interview...</h1></div>;
  }

  if (error) {
    return <div className="container error-message"><h1>Error: {error}</h1></div>;
  }

  return (
    <div className="container">
      <h1>Post-Interview Feedback</h1>
      {feedback ? (
        <div className="feedback-results">
          <h3>Overall Analysis</h3>
          <p><strong>Total Words Spoken:</strong> {feedback.total_words}</p>
          <p><strong>Total Speaking Time:</strong> {feedback.total_duration_seconds} seconds</p>

          <div className="feedback-card">
            <h4>Pacing</h4>
            <p><strong>Words Per Minute:</strong> {feedback.wpm}</p>
            <p><em>{getPacingFeedback(feedback.wpm)}</em></p>
          </div>

          <div className="feedback-card">
            <h4>Clarity (Filler Words)</h4>
            <p><strong>Filler Words Counted:</strong> {feedback.filler_word_count}</p>
            <p><em>{getFillerWordFeedback(feedback.filler_word_count)}</em></p>
          </div>
        </div>
      ) : (
        <p>No interview data was provided or an error occurred.</p>
      )}
    </div>
  );
}

export default FeedbackPage;
