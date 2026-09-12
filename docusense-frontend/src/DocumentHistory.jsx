import { useState, useEffect } from 'react';
import axios from 'axios';

function DocumentHistory() {
  const [documents, setDocuments] = useState([]);

  // useEffect — ye component load hote hi ek baar chalta hai
  useEffect(() => {
    axios.get('http://localhost:8000/api/documents')
      .then(res => setDocuments(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h2>Document History</h2>
      {documents.length === 0 ? (
        <p>Abhi tak koi document process nahi hua.</p>
      ) : (
        documents.map(doc => (
          <div className="card" key={doc.id} style={{ marginBottom: '10px' }}>
            <strong>{doc.filename}</strong> — {doc.document_type}
            <p>{doc.summary}</p>
          </div>
        ))
      )}
    </div>
  );
}

export default DocumentHistory;