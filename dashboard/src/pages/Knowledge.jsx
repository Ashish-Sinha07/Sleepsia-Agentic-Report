import { useState, useEffect, useCallback } from 'react';
import { Upload, Trash2, RefreshCw, Loader, AlertCircle, KeyRound, FileText } from 'lucide-react';
import { knowledgeApi } from '../services/knowledgeApi';

const ADMIN_KEY_STORAGE_KEY = 'sleepsia_knowledge_admin_key';

export default function Knowledge() {
  const [adminKey, setAdminKey] = useState(() => sessionStorage.getItem(ADMIN_KEY_STORAGE_KEY) || '');
  const [keyInput, setKeyInput] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSummary, setUploadSummary] = useState(null);
  const [reindexing, setReindexing] = useState(false);

  const errorText = (err) => {
    if (!err) return 'Something went wrong';
    if (typeof err === 'string') return err;
    return err.detail || JSON.stringify(err);
  };

  const loadDocuments = useCallback(async (key) => {
    if (!key) return;
    setLoading(true);
    setError(null);
    try {
      const docs = await knowledgeApi.listDocuments(key);
      setDocuments(Array.isArray(docs) ? docs : []);
    } catch (err) {
      setError(errorText(err));
      if (err?.detail?.toLowerCase?.().includes('invalid')) {
        // Bad key - don't keep retrying silently with it.
        sessionStorage.removeItem(ADMIN_KEY_STORAGE_KEY);
        setAdminKey('');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (adminKey) loadDocuments(adminKey);
  }, [adminKey, loadDocuments]);

  const handleSaveKey = () => {
    const trimmed = keyInput.trim();
    if (!trimmed) return;
    sessionStorage.setItem(ADMIN_KEY_STORAGE_KEY, trimmed);
    setAdminKey(trimmed);
    setKeyInput('');
  };

  const handleForgetKey = () => {
    sessionStorage.removeItem(ADMIN_KEY_STORAGE_KEY);
    setAdminKey('');
    setDocuments([]);
  };

  const handleUpload = async () => {
    if (!uploadFile || !adminKey) return;
    setUploading(true);
    setError(null);
    setUploadSummary(null);
    try {
      const summary = await knowledgeApi.uploadDocument(uploadFile, adminKey);
      setUploadSummary(summary);
      setUploadFile(null);
      await loadDocuments(adminKey);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (sourceFile) => {
    if (!window.confirm(`Remove all indexed chunks for "${sourceFile}"? This cannot be undone.`)) return;
    setError(null);
    try {
      await knowledgeApi.deleteDocument(sourceFile, adminKey);
      await loadDocuments(adminKey);
    } catch (err) {
      setError(errorText(err));
    }
  };

  const handleReindexCorpus = async () => {
    setReindexing(true);
    setError(null);
    try {
      await knowledgeApi.reindexCorpus(adminKey);
      await loadDocuments(adminKey);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setReindexing(false);
    }
  };

  if (!adminKey) {
    return (
      <div className="max-w-lg mx-auto mt-12 space-y-4">
        <div className="text-center">
          <KeyRound className="w-10 h-10 text-sleepsia-600 mx-auto mb-2" />
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Base Admin</h1>
          <p className="text-gray-600 mt-1 text-sm">
            Enter the admin key to manage the AI Assistant's business-knowledge documents.
          </p>
        </div>
        <div className="card p-4 space-y-3">
          <input
            type="password"
            value={keyInput}
            onChange={(e) => setKeyInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSaveKey()}
            placeholder="Admin key (X-Admin-Key)"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sleepsia-500"
          />
          <button onClick={handleSaveKey} className="btn-primary w-full" disabled={!keyInput.trim()}>
            Continue
          </button>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <p className="text-xs text-gray-500">
            This key is only kept in this browser tab's session storage, never saved permanently or sent
            anywhere except this backend.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen p-0 -m-8 p-8">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-teal-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 left-10 w-80 h-80 bg-cyan-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10 space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-1 h-8 bg-gradient-to-b from-teal-600 to-cyan-600 rounded-full"></div>
              <h1 className="text-3xl font-black bg-gradient-to-r from-teal-700 via-cyan-600 to-teal-800 bg-clip-text text-transparent">
                Knowledge Base Admin
              </h1>
            </div>
            <p className="text-sm text-gray-700 font-medium ml-4">📚 Manage the business policy/guideline documents for AI Assistant</p>
          </div>
          <button
            onClick={handleForgetKey}
            className="text-sm text-gray-500 hover:text-gray-700 underline"
          >
            Forget admin key
          </button>
        </div>

        {error && (
          <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-900">{error}</p>
          </div>
        )}

        <div className="card p-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Upload a document</h2>
          <p className="text-sm text-gray-600">
            Excel (.xlsx/.xls), CSV, or Markdown (.md) files only. Only static business knowledge belongs here
            (policies, guidelines, thresholds) - not transactional data, which flows through the regular ETL
            pipeline.
          </p>
          <div className="flex gap-3 items-center">
            <input
              type="file"
              accept=".xlsx,.xls,.csv,.md"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              className="text-sm"
            />
            <button
              onClick={handleUpload}
              disabled={!uploadFile || uploading}
              className="btn-primary flex items-center gap-2 disabled:opacity-50"
            >
              {uploading ? <Loader className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
          {uploadSummary && (
            <div className="text-sm bg-green-50 border border-green-200 rounded-lg p-3 text-green-900">
              Indexed <strong>{uploadSummary.filename}</strong>: {uploadSummary.sheets_processed} sheet(s),{' '}
              {uploadSummary.documents_created} document(s), {uploadSummary.chunks_created} chunk(s) created.
            </div>
          )}
        </div>

        <div className="card p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="font-semibold text-gray-900">Indexed documents</h2>
            <div className="flex gap-2">
              <button
                onClick={handleReindexCorpus}
                disabled={reindexing}
                className="text-sm flex items-center gap-1 px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                title="Re-run ingestion of the bundled business-rules.md + config sheets"
              >
                {reindexing ? (
                  <Loader className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <RefreshCw className="w-3.5 h-3.5" />
                )}
                Reindex bundled corpus
              </button>
              <button
                onClick={() => loadDocuments(adminKey)}
                disabled={loading}
                className="text-sm px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Refresh
              </button>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center gap-2 text-gray-600 py-6 justify-center">
              <Loader className="w-4 h-4 animate-spin" /> Loading...
            </div>
          ) : documents.length === 0 ? (
            <p className="text-sm text-gray-500 py-6 text-center">No documents indexed yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-200">
                  <th className="py-2">Source file</th>
                  <th className="py-2">Type</th>
                  <th className="py-2">Chunks</th>
                  <th className="py-2"></th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.source_file} className="border-b border-gray-100">
                    <td className="py-2 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-gray-400" />
                      {doc.source_file}
                    </td>
                    <td className="py-2 text-gray-600">{doc.document_type}</td>
                    <td className="py-2 text-gray-600">{doc.chunk_count}</td>
                    <td className="py-2 text-right">
                      <button
                        onClick={() => handleDelete(doc.source_file)}
                        className="text-red-600 hover:text-red-700 p-1.5 hover:bg-red-50 rounded"
                        title="Delete this document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
