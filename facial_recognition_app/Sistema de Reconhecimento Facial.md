# Sistema de Reconhecimento Facial

Um aplicativo web completo para reconhecimento facial de estudantes, desenvolvido com Flask (backend) e HTML/CSS/JavaScript (frontend).

## Funcionalidades

✅ **Gerenciamento de Estudantes**
- Cadastro de estudantes com nome, imagem de referência e imagem de exibição
- Lista de estudantes cadastrados
- Exclusão de estudantes

✅ **Reconhecimento Facial**
- Acesso à câmera do dispositivo
- Captura de imagens em tempo real
- Reconhecimento facial usando OpenCV
- Comparação com banco de dados de referências
- Exibição da imagem do estudante reconhecido por 3 segundos

✅ **Interface Moderna**
- Design responsivo e profissional
- Interface intuitiva com dois painéis principais
- Feedback visual para todas as operações
- Suporte a dispositivos móveis

## Tecnologias Utilizadas

### Backend
- **Flask** - Framework web Python
- **SQLite** - Banco de dados
- **OpenCV** - Processamento de imagens e reconhecimento facial
- **Pillow** - Manipulação de imagens
- **Flask-CORS** - Suporte a requisições cross-origin

### Frontend
- **HTML5** - Estrutura da página
- **CSS3** - Estilização moderna com gradientes e animações
- **JavaScript** - Lógica do frontend e integração com câmera
- **WebRTC** - Acesso à câmera do dispositivo

## Estrutura do Projeto

```
facial_recognition_app/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── user.py          # Modelo base do banco
│   │   │   └── student.py       # Modelo de estudantes
│   │   ├── routes/
│   │   │   ├── user.py          # Rotas de usuários
│   │   │   └── facial_recognition.py  # Rotas de reconhecimento
│   │   ├── static/
│   │   │   ├── index.html       # Interface principal
│   │   │   └── app.js          # Lógica JavaScript
│   │   ├── database/
│   │   │   └── app.db          # Banco SQLite
│   │   └── main.py             # Aplicação principal
│   ├── venv/                   # Ambiente virtual
│   └── requirements.txt        # Dependências
└── README.md                   # Esta documentação
```

## Como Usar

### 1. Instalação

```bash
# Clonar o projeto
cd facial_recognition_app/backend

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar o Aplicativo

```bash
# Iniciar o servidor
python src/main.py
```

O aplicativo estará disponível em `http://localhost:5002`

### 3. Cadastrar Estudantes

1. No painel "Gerenciar Estudantes":
   - Digite o nome do estudante
   - Selecione uma imagem de referência (para reconhecimento)
   - Selecione uma imagem de exibição (mostrada quando reconhecido)
   - Clique em "Adicionar Estudante"

### 4. Reconhecimento Facial

1. No painel "Reconhecimento Facial":
   - Clique em "Iniciar Câmera"
   - Posicione o rosto na frente da câmera
   - Clique em "Capturar e Reconhecer"
   - Se reconhecido, a imagem do estudante será exibida por 3 segundos

## API Endpoints

### Estudantes
- `GET /api/students` - Listar todos os estudantes
- `POST /api/students` - Adicionar novo estudante
- `DELETE /api/students/<id>` - Excluir estudante

### Reconhecimento
- `POST /api/recognize` - Reconhecer face a partir de imagem base64

## Algoritmo de Reconhecimento

O sistema utiliza:
1. **Detecção de Faces**: Haar Cascades do OpenCV
2. **Comparação**: Template matching para comparar faces
3. **Threshold**: Configurável para ajustar sensibilidade
4. **Preprocessing**: Redimensionamento e conversão para escala de cinza

## Limitações e Melhorias Futuras

### Limitações Atuais
- Reconhecimento básico usando template matching
- Funciona melhor com imagens frontais e bem iluminadas
- Requer permissão de câmera do navegador

### Melhorias Possíveis
- Implementar reconhecimento facial mais avançado (face_recognition library)
- Adicionar múltiplas imagens de referência por estudante
- Implementar treinamento de modelo personalizado
- Adicionar autenticação e controle de acesso
- Melhorar a precisão do reconhecimento
- Adicionar logs de reconhecimento
- Implementar backup automático do banco de dados

## Requisitos do Sistema

- Python 3.11+
- Câmera web (para reconhecimento)
- Navegador moderno com suporte a WebRTC
- Permissões de câmera habilitadas

## Solução de Problemas

### Erro de Câmera
- Verifique se a câmera está conectada
- Conceda permissões de câmera ao navegador
- Teste em HTTPS (algumas funcionalidades requerem conexão segura)

### Problemas de Reconhecimento
- Use imagens bem iluminadas e frontais
- Ajuste o threshold no código se necessário
- Verifique se as imagens de referência têm faces detectáveis

### Problemas de Performance
- Redimensione imagens grandes antes do upload
- Limite o número de estudantes cadastrados para testes
- Use imagens em formato JPG para melhor compatibilidade

## Contribuição

Este é um projeto educacional demonstrando conceitos de:
- Desenvolvimento web full-stack
- Reconhecimento facial básico
- Integração frontend-backend
- Manipulação de imagens
- Interface de usuário moderna

## Licença

Projeto desenvolvido para fins educacionais e demonstrativos.

