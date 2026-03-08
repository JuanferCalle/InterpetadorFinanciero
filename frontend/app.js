/**
 * Aplicación Principal - Lógica del Frontend
 */

// Estado global
const appState = {
    transactions: [],
    lastResult: null,
    currentAnalysis: null,
    ollamaAvailable: false,
    speechRecognition: null,
    isRecording: false,
    speechSupported: false,
    speechTranscript: '',
    recordingTimeoutId: null,
};

const MAX_RECORDING_MS = 60000;

// ==================== UTILIDADES ====================

function showLoading(show = true) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.style.display = 'flex';
    } else {
        loading.style.display = 'none';
    }
}

function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, duration);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getStatusEmoji(type) {
    const emojis = {
        'gasto': '📉',
        'ingreso': '📈',
        'Comida': '🍽️',
        'Ocio': '🎮',
        'Gasolina/Transporte': '🚗',
        'Gastos del hogar': '🏠',
        'Ropa': '👕',
        'Viajes': '✈️',
        'Servicios': '🔧',
        'Salud': '🏥',
        'Educacion': '📚',
        'Salario': '💵',
        'Bonificacion': '🎁',
        'Freelance': '💻',
        'Otro': '📦'
    };
    return emojis[type] || '💰';
}

// ==================== VOZ / DICTADO ====================

function updateVoiceStatus(message) {
    const voiceStatus = document.getElementById('voiceStatus');
    if (voiceStatus) {
        voiceStatus.textContent = `Voz: ${message}`;
    }
}

function initializeSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recordBtn = document.getElementById('recordBtn');

    if (!SpeechRecognition) {
        appState.speechSupported = false;
        updateVoiceStatus('no soportada en este navegador');
        if (recordBtn) {
            recordBtn.disabled = true;
            recordBtn.textContent = '🎤 No disponible';
        }
        return;
    }

    appState.speechSupported = true;
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        appState.isRecording = true;
        appState.speechTranscript = '';
        if (recordBtn) {
            recordBtn.textContent = '⏹️ Detener';
        }
        updateVoiceStatus('grabando... tienes hasta 60 segundos');

        if (appState.recordingTimeoutId) {
            clearTimeout(appState.recordingTimeoutId);
        }

        appState.recordingTimeoutId = setTimeout(() => {
            if (appState.isRecording) {
                appState.speechRecognition.stop();
                updateVoiceStatus('grabación finalizada por tiempo (60s)');
            }
        }, MAX_RECORDING_MS);
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i += 1) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                appState.speechTranscript += `${transcript} `;
            } else {
                interimTranscript += transcript;
            }
        }

        const input = document.getElementById('inputText');
        if (input) {
            input.value = `${appState.speechTranscript}${interimTranscript}`.trim();
        }
        updateVoiceStatus('transcribiendo...');
    };

    recognition.onerror = (event) => {
        updateVoiceStatus(`error (${event.error})`);
        showToast(`✗ Error de voz: ${event.error}`, 'error');
    };

    recognition.onend = () => {
        appState.isRecording = false;
        if (appState.recordingTimeoutId) {
            clearTimeout(appState.recordingTimeoutId);
            appState.recordingTimeoutId = null;
        }

        if (recordBtn) {
            recordBtn.textContent = '🎤 Grabar';
        }

        const input = document.getElementById('inputText');
        if (input && input.value.trim()) {
            showToast('✓ Audio convertido a texto', 'success');
        }

        if (document.getElementById('voiceStatus')?.textContent?.includes('grabando')) {
            updateVoiceStatus('lista');
        }
    };

    appState.speechRecognition = recognition;
    updateVoiceStatus('lista');
}

function toggleRecording() {
    if (!appState.speechSupported || !appState.speechRecognition) {
        showToast('Voz no soportada en este navegador', 'warning');
        return;
    }

    if (appState.isRecording) {
        appState.speechRecognition.stop();
        return;
    }

    appState.speechRecognition.start();
}

// ==================== STATUS ====================

async function updateStatus() {
    try {
        const health = await apiClient.checkHealth();
        const statusEl = document.getElementById('ollamaStatus');
        const statusText = document.getElementById('statusText');
        
        if (health.status === 'ok') {
            const aiAvailable = health.ai_available ?? health.ollama_available;
            const aiProvider = health.ai_provider || 'ollama';
            appState.ollamaAvailable = aiAvailable;
            statusEl.classList.toggle('offline', !aiAvailable);
            statusText.textContent = aiAvailable
                ? `✓ Sistema en línea - IA disponible (${aiProvider})`
                : `⚠ Sistema en línea - IA no disponible (${aiProvider})`;
        } else {
            statusEl.classList.add('offline');
            statusText.textContent = '✗ Error de conexión';
        }
    } catch (error) {
        console.error('Error checking status:', error);
        document.getElementById('ollamaStatus').classList.add('offline');
        document.getElementById('statusText').textContent = '✗ Sin conexión';
    }
}

// ==================== PROCESAMIENTO DE TRANSACCIONES ====================

async function processTransaction() {
    const inputText = document.getElementById('inputText').value.trim();
    const useAi = document.getElementById('useAiCheckbox').checked;
    
    if (!inputText) {
        showToast('Por favor ingresa un texto', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        console.log('Procesando:', inputText);
        const result = await apiClient.processAudio(inputText, useAi);
        console.log('Resultado:', result);
        
        appState.lastResult = result;
        displayResult(result);
        
        if (result.success) {
            document.getElementById('inputText').value = '';
            showToast('✓ Transacción registrada', 'success');
            loadTransactions();
            loadAnalysis();  // Actualizar análisis automáticamente
        } else {
            showToast(`⚠ ${result.error || 'Error al procesar'}`, 'warning');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast(`✗ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayResult(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultContent = document.getElementById('resultContent');
    
    if (!result.success) {
        resultContent.innerHTML = `
            <div style="color: var(--danger-color);">
                <strong>❌ Error:</strong> ${result.error || 'Error desconocido'}
                ${result.advertencias ? `
                    <p style="margin-top: 10px; font-size: 0.9rem;">
                        <strong>Advertencias:</strong> ${result.advertencias.join(', ')}
                    </p>
                ` : ''}
            </div>
        `;
        resultsSection.style.display = 'block';
        return;
    }
    
    const transaccion = result.transaccion;
    const emoji = getStatusEmoji(transaccion.tipo);
    
    resultContent.innerHTML = `
        <div>
            <div class="result-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 15px; align-items: center;">
                <div style="text-align: center;">
                    <strong>Tipo:</strong><br>${emoji} ${transaccion.tipo.toUpperCase()}
                </div>
                <div style="text-align: center;">
                    <strong>Cantidad:</strong><br><span style="color: var(--primary-color); font-weight: 700; font-size: 1.2rem;">
                        ${formatCurrency(transaccion.cantidad)}
                    </span>
                </div>
                <div style="text-align: center;">
                    <strong>Confianza:</strong><br><span style="color: var(--success-color); font-weight: 700; font-size: 1.2rem;">
                        ${(transaccion.confianza * 100).toFixed(0)}%
                    </span>
                </div>
            </div>
            <div class="result-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; align-items: center;">
                <div style="text-align: center;">
                    <strong>Categoría:</strong><br>${getStatusEmoji(transaccion.categoria)} ${transaccion.categoria}
                </div>
                <div style="text-align: center;">
                    <strong>Fecha:</strong><br>${formatDate(transaccion.fecha)}
                </div>
            </div>
            ${transaccion.notas ? `
                <div style="margin-top: 10px;">
                    <strong>Notas:</strong> ${transaccion.notas}
                </div>
            ` : ''}
            ${result.keywords && result.keywords.length > 0 ? `
                <div style="margin-top: 10px;">
                    <strong>Palabras clave detectadas:</strong><br>
                    <span style="display: flex; gap: 5px; flex-wrap: wrap; margin-top: 5px;">
                        ${result.keywords.map(kw => `<span style="background: var(--primary-light); color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.85rem;">${kw}</span>`).join('')}
                    </span>
                </div>
            ` : ''}
        </div>
    `;
    
    resultsSection.style.display = 'block';
}

// ==================== ANÁLISIS ====================

async function loadAnalysis() {
    const period = document.getElementById('periodSelect').value;
    showLoading(true);
    
    try {
        const data = await apiClient.getAnalysisWithSuggestions(period);
        
        if (!data.success) {
            showToast(`Error: ${data.error}`, 'error');
            return;
        }
        
        const analysis = data.analysis;
        appState.currentAnalysis = analysis;
        
        // Mostrar análisis
        displayAnalysis(analysis);
        
        // Mostrar sugerencias
        if (data.suggestions && data.suggestions.length > 0) {
            displaySuggestions(data.suggestions);
        }
        
    } catch (error) {
        console.error('Error loading analysis:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayAnalysis(analysis) {
    const analysisContent = document.getElementById('analysisContent');
    
    const statusCards = `
        <div class="stat-card income">
            <div class="stat-label">💰 Ingresos</div>
            <div class="stat-value">${formatCurrency(analysis.ingresos_totales)}</div>
        </div>
        <div class="stat-card expense">
            <div class="stat-label">💸 Gastos</div>
            <div class="stat-value">${formatCurrency(analysis.gastos_totales)}</div>
        </div>
        <div class="stat-card ${analysis.balance >= 0 ? 'income' : 'expense'}">
            <div class="stat-label">📊 Balance</div>
            <div class="stat-value">${formatCurrency(analysis.balance)}</div>
        </div>
    `;
    
    const categoryBreakdown = Object.entries(analysis.por_categoria).length > 0 ? `
        <div class="category-breakdown">
            <h3 style="margin-bottom: 15px; font-size: 1.1rem;">Desglose por Categoría</h3>
            ${Object.entries(analysis.por_categoria)
                .sort(([, a], [, b]) => b.total - a.total)
                .map(([category, data]) => `
                    <div class="category-item">
                        <span class="category-name">${getStatusEmoji(category)} ${category}</span>
                        <div class="category-bar">
                            <div class="category-fill" style="width: ${data.porcentaje}%"></div>
                        </div>
                        <div class="category-stats">
                            <div class="category-percentage">${data.porcentaje.toFixed(1)}%</div>
                            <div class="category-amount">${formatCurrency(data.total)}</div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">${data.transacciones} transacción${data.transacciones !== 1 ? 'es' : ''}</div>
                        </div>
                    </div>
                `).join('')}
        </div>
    ` : '<p style="color: var(--text-secondary);">No hay datos de gastos por categoría</p>';
    
    analysisContent.innerHTML = statusCards + categoryBreakdown;
}

function displaySuggestions(suggestions) {
    const suggestionsSection = document.getElementById('suggestionsSection');
    const suggestionsContent = document.getElementById('suggestionsContent');
    
    if (suggestions.length === 0) {
        suggestionsSection.style.display = 'none';
        return;
    }
    
    suggestionsContent.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-card ${suggestion.prioridad}">
            <div class="suggestion-title">${suggestion.titulo}</div>
            <div class="suggestion-description">${suggestion.descripcion}</div>
            <div class="suggestion-meta">
                <span class="badge">Prioridad: ${suggestion.prioridad.toUpperCase()}</span>
                ${suggestion.ahorro_estimado ? `<span class="badge">💰 ${formatCurrency(suggestion.ahorro_estimado)}</span>` : ''}
            </div>
        </div>
    `).join('');
    
    suggestionsSection.style.display = 'block';
}

// ==================== TRANSACCIONES ====================

async function loadTransactions(category = '') {
    try {
        const data = category 
            ? await apiClient.getTransactionsByCategory(category)
            : await apiClient.getTransactions();
        
        if (!data.success || !data.transactions) {
            showToast('Error cargando transacciones', 'error');
            return;
        }
        
        appState.transactions = data.transactions;
        displayTransactions(data.transactions);
        
    } catch (error) {
        console.error('Error loading transactions:', error);
        showToast(`Error: ${error.message}`, 'error');
    }
}

function displayTransactions(transactions) {
    const transactionsContent = document.getElementById('transactionsContent');
    
    if (transactions.length === 0) {
        transactionsContent.innerHTML = '<p class="empty-state">📭 No hay transacciones registradas</p>';
        return;
    }
    
    transactionsContent.innerHTML = transactions
        .sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
        .map(transaction => {
            const confidencePercent = (transaction.confianza * 100).toFixed(0);
            return `
                <div class="transaction-card ${transaction.tipo}">
                    <div class="transaction-header">
                        <div>
                            <span class="transaction-category">${getStatusEmoji(transaction.categoria)} ${transaction.categoria}</span>
                        </div>
                        <div class="confidence" style="--confidence: ${transaction.confianza}">
                            ${confidencePercent}%
                        </div>
                    </div>
                    <div class="transaction-amount ${transaction.tipo}">
                        ${getStatusEmoji(transaction.tipo)} ${formatCurrency(transaction.cantidad)}
                    </div>
                    <div class="transaction-type">${transaction.tipo.toUpperCase()}</div>
                    <div class="transaction-description">${transaction.descripcion}</div>
                    <div class="transaction-footer">
                        <span>${formatDate(transaction.fecha)}</span>
                        <span>ID: ${transaction.id.slice(0, 8)}...</span>
                    </div>
                </div>
            `;
        }).join('');
}

// ==================== EVENT LISTENERS ====================

async function clearAllData() {
    if (!confirm('¿Estás seguro de que quieres borrar TODAS las transacciones? Esta acción no se puede deshacer.')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const result = await apiClient.clearAllTransactions();
        
        if (result.success) {
            showToast(`✓ ${result.message}`, 'success');
            appState.transactions = [];
            displayTransactions([]);
            
            // Ocultar resultados y sugerencias
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('suggestionsSection').style.display = 'none';
            
            // Recargar análisis
            loadAnalysis();
        } else {
            showToast(`✗ Error: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error clearing data:', error);
        showToast(`✗ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Botones principales
    document.getElementById('recordBtn').addEventListener('click', toggleRecording);
    document.getElementById('processBtn').addEventListener('click', processTransaction);
    document.getElementById('clearBtn').addEventListener('click', () => {
        document.getElementById('inputText').value = '';
        document.getElementById('resultsSection').style.display = 'none';
        updateVoiceStatus('lista');
    });
    
    // Análisis
    document.getElementById('analyzeBtn').addEventListener('click', loadAnalysis);
    document.getElementById('periodSelect').addEventListener('change', loadAnalysis);
    
    // Filtro de transacciones
    document.getElementById('categoryFilter').addEventListener('change', (e) => {
        loadTransactions(e.target.value);
    });
    
    // Botón de borrar todo
    document.getElementById('clearDataBtn').addEventListener('click', clearAllData);
    
    // Enter para procesar
    document.getElementById('inputText').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            processTransaction();
        }
    });
    
    // Inicializar
    initializeSpeechRecognition();
    updateStatus();
    loadTransactions();
    loadAnalysis();
    
    // Actualizar estado cada 10 segundos
    setInterval(updateStatus, 10000);
    
    // Recargar transacciones cada 30 segundos si hay cambios
    setInterval(() => {
        if (appState.lastResult && appState.lastResult.success) {
            loadTransactions();
        }
    }, 30000);
});
