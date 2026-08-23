import apiClient from './api';

export const aiAssistantApi = {
  /**
   * Ask the AI assistant a business question
   * @param {string} question - The business question
   * @param {object} context - Optional context data
   * @returns {Promise} Response with answer, confidence, data sources, and recommendations
   */
  askQuestion: async (question, context = null) => {
    try {
      const response = await apiClient.post('/api/ai/ask', {
        question,
        context,
      });
      return response;
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  },

  /**
   * Get suggested questions for the AI assistant
   * @returns {Promise} Array of suggested questions
   */
  getSuggestions: async () => {
    try {
      const response = await apiClient.get('/api/ai/suggestions');
      return response;
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      throw error;
    }
  },

  /**
   * Get explanation for a business metric
   * @param {string} metric - The metric name
   * @returns {Promise} Metric explanation with definition, formula, and interpretation
   */
  explainMetric: async (metric) => {
    try {
      const response = await apiClient.post('/api/ai/explain-metric', {
        metric,
      });
      return response;
    } catch (error) {
      console.error('Error explaining metric:', error);
      throw error;
    }
  },
};
