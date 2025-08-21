class FacialRecognitionApp {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.stream = null;
        this.isRecognizing = false;
        this.recognitionInterval = null;
        
        this.checkAuthAndInit();
    }

    async checkAuthAndInit() {
        try {
            const response = await fetch('/api/auth/check');
            const result = await response.json();
            
            if (!result.authenticated) {
                // Usuário não está logado, redirecionar para login
                window.location.href = '/login.html';
                return;
            }
            
            // Usuário está logado, inicializar a aplicação
            this.initializeEventListeners();
            this.loadStudents();
            this.showWelcomeMessage(result.user);
        } catch (error) {
            console.error('Erro ao verificar autenticação:', error);
            window.location.href = '/login.html';
        }
    }

    showWelcomeMessage(user) {
        // Adicionar mensagem de boas-vindas e botão de logout
        const header = document.querySelector('h1');
        if (header) {
            const welcomeDiv = document.createElement('div');
            welcomeDiv.style.cssText = 'text-align: right; margin-bottom: 1rem; font-size: 0.9rem;';
            welcomeDiv.innerHTML = `
                <span style="color: #666;">Bem-vindo, ${user.username}!</span>
                <button id="logoutBtn" style="margin-left: 1rem; padding: 0.25rem 0.5rem; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Sair</button>
            `;
            header.parentNode.insertBefore(welcomeDiv, header);
            
            document.getElementById('logoutBtn').addEventListener('click', () => this.logout());
        }
    }

    async logout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            window.location.href = '/login.html';
        } catch (error) {
            console.error('Erro no logout:', error);
            window.location.href = '/login.html';
        }
    }

    initializeEventListeners() {
        // Botões da câmera
        document.getElementById("startCamera").addEventListener("click", () => this.startCamera());
        document.getElementById("stopCamera").addEventListener("click", () => this.stopCamera());
        
        // Formulário de estudante
        document.getElementById("studentForm").addEventListener("submit", (e) => this.handleStudentForm(e));
        
        // Fechar modal de exibição
        document.getElementById("studentDisplay").addEventListener("click", () => this.hideStudentDisplay());
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                } 
            });
            
            this.video.srcObject = this.stream;
            
            // Atualizar interface
            document.getElementById('startCamera').style.display = 'none';
            document.getElementById('stopCamera').style.display = 'block';
            document.getElementById('videoOverlay').classList.remove('show');
            
            this.showStatus('Câmera iniciada com sucesso! Iniciando reconhecimento...', 'info', 'recognitionStatus');
            
            // Iniciar reconhecimento automático
            this.recognitionInterval = setInterval(() => this.captureAndRecognize(), 1000); // A cada 1 segundo
            
        } catch (error) {
            console.error('Erro ao acessar a câmera:', error);
            this.showStatus('Erro ao acessar a câmera. Verifique as permissões.', 'error', 'recognitionStatus');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        // Parar reconhecimento automático
        if (this.recognitionInterval) {
            clearInterval(this.recognitionInterval);
            this.recognitionInterval = null;
        }

        this.video.srcObject = null;
        
        // Atualizar interface
        document.getElementById('startCamera').style.display = 'block';
        document.getElementById('stopCamera').style.display = 'none';
        document.getElementById('videoOverlay').classList.add('show');
        
        this.showStatus('Câmera parada.', 'info', 'recognitionStatus');
    }

    async captureAndRecognize() {
        if (!this.stream || this.isRecognizing) return;
        
        this.isRecognizing = true;
        
        try {
            // Capturar frame do vídeo
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Converter para base64
            const imageData = this.canvas.toDataURL('image/jpeg', 0.8);
            
            // Enviar para o backend
            const response = await fetch('/api/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                if (result.recognized) {
                    this.showRecognitionSuccess(result.student);
                } else {
                    this.showRecognitionFailure();
                }
            } else {
                throw new Error(result.error || 'Erro no reconhecimento');
            }
            
        } catch (error) {
            console.error('Erro no reconhecimento:', error);
            // Não mostrar erro na tela para cada falha de reconhecimento, apenas no console
        } finally {
            this.isRecognizing = false;
        }
    }

    showRecognitionSuccess(student) {
        this.showStatus(`✅ Estudante reconhecido: ${student.name}`, 'success', 'recognitionStatus');
        
        // Exibir imagem do estudante por 3 segundos
        this.showStudentDisplay(student);
        
        // Parar o reconhecimento enquanto a imagem é exibida
        if (this.recognitionInterval) {
            clearInterval(this.recognitionInterval);
            this.recognitionInterval = null;
        }
        
        setTimeout(() => {
            this.hideStudentDisplay();
            this.showStatus('Pronto para próximo reconhecimento', 'info', 'recognitionStatus');
            
            // Retomar o reconhecimento após 3 segundos
            this.recognitionInterval = setInterval(() => this.captureAndRecognize(), 1000);
        }, 3000);
    }

    showRecognitionFailure() {
        this.showStatus('❌ Face não reconhecida', 'error', 'recognitionStatus');
        
        setTimeout(() => {
            this.showStatus('Pronto para próximo reconhecimento', 'info', 'recognitionStatus');
        }, 2000);
    }

    showStudentDisplay(student) {
        const modal = document.getElementById('studentDisplay');
        const image = document.getElementById('studentDisplayImage');
        const name = document.getElementById('studentDisplayName');
        
        image.src = student.display_image_path;
        name.textContent = student.name;
        modal.classList.add('show');
    }

    hideStudentDisplay() {
        document.getElementById('studentDisplay').classList.remove('show');
    }

    async handleStudentForm(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('name', document.getElementById('studentName').value);
        formData.append('reference_image', document.getElementById('referenceImage').files[0]);
        formData.append('display_image', document.getElementById('displayImage').files[0]);
        
        try {
            this.showStatus('Adicionando estudante...', 'info', 'adminStatus');
            
            const response = await fetch('/api/students', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showStatus('Estudante adicionado com sucesso!', 'success', 'adminStatus');
                document.getElementById('studentForm').reset();
                this.loadStudents();
            } else {
                throw new Error(result.error || 'Erro ao adicionar estudante');
            }
            
        } catch (error) {
            console.error('Erro ao adicionar estudante:', error);
            this.showStatus(`Erro: ${error.message}`, 'error', 'adminStatus');
        }
    }

    async loadStudents() {
        try {
            const response = await fetch('/api/students');
            const students = await response.json();
            
            const container = document.getElementById('studentsList');
            
            if (students.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">Nenhum estudante cadastrado</div>';
                return;
            }
            
            container.innerHTML = students.map(student => `
                <div class="student-item">
                    <span class="student-name">${student.name}</span>
                    <button class="delete-btn" onclick="app.deleteStudent(${student.id})">🗑️ Excluir</button>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Erro ao carregar estudantes:', error);
            document.getElementById('studentsList').innerHTML = '<div style="text-align: center; color: #ff6b6b; padding: 2rem;">Erro ao carregar estudantes</div>';
        }
    }

    async deleteStudent(studentId) {
        if (!confirm('Tem certeza que deseja excluir este estudante?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/students/${studentId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showStatus('Estudante excluído com sucesso!', 'success', 'adminStatus');
                this.loadStudents();
            } else {
                const result = await response.json();
                throw new Error(result.error || 'Erro ao excluir estudante');
            }
            
        } catch (error) {
            console.error('Erro ao excluir estudante:', error);
            this.showStatus(`Erro: ${error.message}`, 'error', 'adminStatus');
        }
    }

    showStatus(message, type, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = `<div class="status ${type}">${message}</div>`;
        
        // Remover status após 5 segundos (exceto para info)
        if (type !== 'info') {
            setTimeout(() => {
                container.innerHTML = '';
            }, 5000);
        }
    }
}

// Inicializar aplicação quando a página carregar
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new FacialRecognitionApp();
});

