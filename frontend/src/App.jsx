import React, { useState, useRef } from 'react';
import { parseMarkdown, renderContent } from './markdownUtils';
import './App.css';

function App() {
  const [task, setTask] = useState('');
  const [description, setDescription] = useState('');
  const [constraints, setConstraints] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const resultsRef = useRef(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:8000/search-datasets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ml_task: task,
          problem_description: description,
          constraints: constraints,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data);
      
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      setError(err.message || 'Failed to fetch datasets');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const quickTasks = [
    'Image Classification',
    'Customer Churn Prediction',
    'Sentiment Analysis',
    'Time Series Forecasting',
    'Object Detection',
    'Recommendation Systems',
  ];

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <span>DataFinder</span>
          </div>
          <p className="tagline">Smart dataset discovery</p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          
          {!results && (
            <section className="hero">
              <h1>Find your dataset faster</h1>
              <p>Search across Kaggle, HuggingFace, GitHub & ArXiv with smart domain detection</p>
            </section>
          )}

          {!results && (
            <section className="search-section">
              <form onSubmit={handleSearch} className="search-form">
                <div className="form-field">
                  <label>Task</label>
                  <input
                    type="text"
                    placeholder="e.g., Customer Churn Prediction, Image Classification"
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    required
                  />
                </div>

                <div className="form-field">
                  <label>Use case (optional)</label>
                  <textarea
                    placeholder="e.g., Predict whether a telecom customer will leave the service"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows="2"
                  />
                </div>

                <div className="form-field">
                  <label>Constraints (optional)</label>
                  <input
                    type="text"
                    placeholder="e.g., Tabular CSV data, customer-level rows, monthly charges"
                    value={constraints}
                    onChange={(e) => setConstraints(e.target.value)}
                  />
                </div>

                <button type="submit" disabled={loading || !task} className="btn-search">
                  {loading ? (
                    <>
                      <span className="spinner-small"></span>
                      Searching...
                    </>
                  ) : (
                    <>Search</>
                  )}
                </button>
              </form>

              {!loading && (
                <div className="quick-start">
                  <p className="quick-label">Try:</p>
                  <div className="quick-buttons">
                    {quickTasks.map((t) => (
                      <button
                        key={t}
                        type="button"
                        onClick={() => {
                          setTask(t);
                          setDescription('');
                          setConstraints('');
                        }}
                        className="quick-btn"
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </section>
          )}

          {error && (
            <div className="error-box">
              <p><strong>Error:</strong> {error}</p>
            </div>
          )}

          {results && (
            <section className="results-section" ref={resultsRef}>
              <div className="results-header">
                <div>
                  <h2>Results for <em>{results.task}</em></h2>
                  <div className="result-meta">
                    <span className="badge">Domain: {results.domain || 'General'}</span>
                    <span className="badge">Data Type: {results.data_type}</span>
                  </div>
                  <p className="search-query">Query: {results.query}</p>
                </div>
                <button
                  onClick={() => {
                    setTask('');
                    setDescription('');
                    setConstraints('');
                    setResults(null);
                  }}
                  className="btn-new"
                >
                  New Search
                </button>
              </div>

              <div className="results-content">
                {parseMarkdown(results.recommendations).map(element => renderContent(element))}
              </div>
            </section>
          )}

          {!results && !loading && !error && (
            <section className="empty-state">
              <h3>No search yet</h3>
              <p>Enter your ML task to find the best datasets</p>
            </section>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>DataFinder • Smart dataset discovery</p>
      </footer>
    </div>
  );
}

export default App;
