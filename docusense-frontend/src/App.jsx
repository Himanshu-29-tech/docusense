import { useState } from 'react';
import axios from 'axios';
import './App.css';
import DocumentHistory from './DocumentHistory';

const API_URL = 'https://docusense-backend-ifnw.onrender.com';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Jab user file select kare
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
    setSaveSuccess(false);
  };

  // Jab user "Process" button dabaye
  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setSaveSuccess(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${API_URL}/api/process-document`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResult(response.data);
    } catch (err) {
      setError('Processing failed. Backend chal raha hai check karo.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Jab user "Confirm & Save" dabaye
  const handleSave = async () => {
    setSaving(true);
    setSaveSuccess(false);
    try {
      await axios.post(`${API_URL}/api/save-document`, {
        filename: result.filename,
        document_type: result.analysis.document_type,
        raw_text: result.raw_text,
        entities: result.entities,
        summary: result.analysis.summary,
        anomalies: result.analysis.anomalies,
      });
      setSaveSuccess(true);
    } catch (err) {
      setError('Save failed.');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="app">
      <h1>📄 DocuSense</h1>
      <p>AI Document Intelligence for SMEs</p>

      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setActiveTab('upload')}>Upload</button>
        <button onClick={() => setActiveTab('history')}>History</button>
      </div>

      {activeTab === 'upload' ? (
        <div>
          <div className="upload-box">
            <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileChange} />
            <button onClick={handleUpload} disabled={!file || loading}>
              {loading ? 'Processing...' : 'Process Document'}
            </button>
          </div>

          {error && <div className="error">{error}</div>}

          {result && (
            <div className="results">
              <h2>Results</h2>

              {result.is_duplicate && (
                <div className="alert-warning">
                  ⚠️ Duplicate Alert: This invoice number already exists!
                </div>
              )}

              <div className="result-grid">
                <div className="card">
                  <h3>Extracted Entities</h3>
                  <p><strong>Invoice Number:</strong> {result.entities.invoice_number || 'N/A'}</p>
                  <p><strong>Organizations:</strong> {result.entities.organizations.join(', ') || 'N/A'}</p>
                  <p><strong>Dates:</strong> {result.entities.dates.join(', ') || 'N/A'}</p>
                  <p><strong>Amounts:</strong> {result.entities.amounts_found.join(', ') || 'N/A'}</p>
                </div>

                <div className="card">
                  <h3>AI Summary</h3>
                  <p>{result.analysis.summary}</p>
                  <p><strong>Type:</strong> {result.analysis.document_type}</p>

                  {result.analysis.anomalies.length > 0 ? (
                    <div>
                      <strong>Anomalies:</strong>
                      <ul>
                        {result.analysis.anomalies.map((a, i) => <li key={i}>{a}</li>)}
                      </ul>
                    </div>
                  ) : (
                    <p>✅ No anomalies detected</p>
                  )}
                </div>
              </div>

              <button
                onClick={handleSave}
                style={{ marginTop: '16px' }}
                disabled={saving}
              >
                {saving ? 'Saving...' : '✅ Confirm & Save'}
              </button>
              {saveSuccess && <p style={{ color: '#90ee90' }}>Saved successfully!</p>}
            </div>
          )}
        </div>
      ) : (
        <DocumentHistory />
      )}
    </div>
  );
}

export default App;