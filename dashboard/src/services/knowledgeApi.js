import apiClient from './api';

/**
 * Knowledge-base admin API client (upload/list/delete/reindex documents for
 * the RAG pipeline). Every call requires an admin key, sent as the
 * X-Admin-Key header - see backend/app/api/routes/knowledge.py.
 */
export const knowledgeApi = {
  listDocuments: async (adminKey) => {
    return apiClient.get('/api/knowledge/documents', {
      headers: { 'X-Admin-Key': adminKey },
    });
  },

  uploadDocument: async (file, adminKey) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/knowledge/upload', formData, {
      headers: { 'X-Admin-Key': adminKey },
    });
  },

  deleteDocument: async (sourceFile, adminKey) => {
    return apiClient.delete(`/api/knowledge/documents/${encodeURIComponent(sourceFile)}`, {
      headers: { 'X-Admin-Key': adminKey },
    });
  },

  reindexCorpus: async (adminKey) => {
    return apiClient.post(
      '/api/knowledge/reindex-corpus',
      {},
      { headers: { 'X-Admin-Key': adminKey } }
    );
  },
};
