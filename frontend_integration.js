// Código para integrar en DataSnap (agregar a main.js o crear chatbot.js)

class DataSnapChatbot {
    constructor(apiUrl = 'https://tu-app.onrender.com') {
        this.apiUrl = apiUrl;
        this.chatContainer = null;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.attachEventListeners();
    }

    createChatWidget() {
        const chatHTML = `
            <div id="chatbot-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
                <button id="chat-toggle" style="background: #007bff; color: white; border: none; border-radius: 50%; width: 60px; height: 60px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    💬
                </button>
                <div id="chat-panel" style="display: none; width: 350px; height: 400px; background: white; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); position: absolute; bottom: 70px; right: 0;">
                    <div style="background: #007bff; color: white; padding: 15px; border-radius: 10px 10px 0 0;">
                        <h4 style="margin: 0;">DataSnap Assistant</h4>
                    </div>
                    <div id="chat-messages" style="height: 280px; overflow-y: auto; padding: 10px;"></div>
                    <div style="padding: 10px; border-top: 1px solid #eee;">
                        <input type="text" id="chat-input" placeholder="Pregunta sobre tus datos..." style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatHTML);
        this.chatContainer = document.getElementById('chat-messages');
    }

    attachEventListeners() {
        const toggle = document.getElementById('chat-toggle');
        const panel = document.getElementById('chat-panel');
        const input = document.getElementById('chat-input');

        toggle.addEventListener('click', () => {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                this.sendMessage(input.value.trim());
                input.value = '';
            }
        });
    }

    async sendMessage(message) {
        this.addMessage(message, 'user');
        this.addMessage('Procesando...', 'bot', true);

        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({human_query: message})
            });

            const data = await response.json();
            this.removeLoadingMessage();
            
            if (data.answer) {
                this.addMessage(data.answer, 'bot');
            } else {
                this.addMessage('Error al procesar tu consulta', 'bot');
            }
        } catch (error) {
            this.removeLoadingMessage();
            this.addMessage('Error de conexión. Intenta más tarde.', 'bot');
        }
    }

    addMessage(text, sender, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            margin: 10px 0; 
            padding: 8px 12px; 
            border-radius: 10px; 
            max-width: 80%;
            ${sender === 'user' ? 'background: #007bff; color: white; margin-left: auto;' : 'background: #f1f1f1;'}
            ${isLoading ? 'id: loading-message' : ''}
        `;
        messageDiv.textContent = text;
        this.chatContainer.appendChild(messageDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    removeLoadingMessage() {
        const loading = document.getElementById('loading-message');
        if (loading) loading.remove();
    }
}

// Inicializar cuando cargue la página
document.addEventListener('DOMContentLoaded', () => {
    new DataSnapChatbot('https://tu-app.onrender.com');
});