/**
 * API Client - Funciones para comunicarse con el backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

class ApiClient {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    }

    async checkHealth() {
        try {
            return await this.request('/health');
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', ollama_available: false };
        }
    }

    async processAudio(text, useAi = false) {
        return await this.request('/process-audio', {
            method: 'POST',
            body: JSON.stringify({
                text: text,
                use_ai: useAi
            })
        });
    }

    async getTransactions() {
        return await this.request('/transactions');
    }

    async getTransactionsByCategory(category) {
        return await this.request(`/transactions/category/${encodeURIComponent(category)}`);
    }

    async getAnalysis(period) {
        return await this.request(`/analysis/${period}`);
    }

    async getSuggestions(period = 'mensual') {
        return await this.request(`/suggestions?period=${period}`);
    }

    async getAnalysisWithSuggestions(period) {
        return await this.request(`/analysis-with-suggestions/${period}`);
    }

    async getKeywordsInfo() {
        return await this.request('/keywords');
    }

    async testClassify(text) {
        return await this.request('/test/classify', {
            method: 'POST',
            body: JSON.stringify({ text: text })
        });
    }

    async clearAllTransactions() {
        return await this.request('/transactions', {
            method: 'DELETE'
        });
    }
}

// Instancia global
const apiClient = new ApiClient();
