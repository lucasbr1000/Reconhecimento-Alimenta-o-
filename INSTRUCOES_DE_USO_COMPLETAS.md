# 🔐 Sistema de Reconhecimento Facial com Autenticação

## Visão Geral

Este é um sistema completo de reconhecimento facial com autenticação de usuários, desenvolvido em Flask (backend) e HTML/CSS/JavaScript (frontend). O sistema agora inclui uma camada de segurança que requer login para acesso às funcionalidades.

## 🚀 Funcionalidades

### Sistema de Autenticação
- **Login seguro** com usuário e senha
- **Registro de novos usuários** 
- **Proteção de rotas** - acesso apenas para usuários autenticados
- **Sessões persistentes** - permanece logado durante a sessão
- **Logout seguro**

### Sistema de Reconhecimento Facial
- **Cadastro de estudantes** com imagens de referência e exibição
- **Reconhecimento facial em tempo real** via câmera web
- **Detecção automática de faces** usando OpenCV
- **Comparação inteligente** entre face capturada e banco de dados
- **Exibição temporária** da foto do estudante reconhecido (3 segundos)
- **Pausa automática** do reconhecimento durante exibição da foto
- **Interface responsiva** e moderna

## 📋 Pré-requisitos

- Python 3.11+
- Câmera web conectada
- Navegador moderno (Chrome, Firefox, Edge, Safari)
- Permissões de câmera concedidas pelo navegador

## 🔧 Como Usar

### 1. Primeiro Acesso

1. **Acesse o sistema:**
   - URL: `https://5000-izih2mn2caanflcxdw1fh-ef687b71.manusvm.computer/`
   - Você será automaticamente redirecionado para a página de login

2. **Criar uma conta:**
   - Na página de login, clique em "Criar conta"
   - Digite o nome de usuário desejado
   - Digite uma senha segura
   - Confirme a senha
   - Clique em "OK" para criar a conta

3. **Fazer login:**
   - Digite seu usuário e senha
   - Clique em "Entrar"
   - Você será redirecionado para o sistema principal

### 2. Cadastrando Estudantes

1. **Preencher informações:**
   - Digite o nome completo do estudante
   - Selecione a **Imagem de Referência** (usada para reconhecimento)
   - Selecione a **Imagem de Exibição** (mostrada quando reconhecido)

2. **Escolher imagens adequadas:**
   - **Imagem de Referência:** Foto clara do rosto, boa iluminação, olhando para frente
   - **Imagem de Exibição:** Pode ser a mesma ou uma foto diferente do estudante

3. **Salvar:**
   - Clique em "Adicionar Estudante"
   - O estudante aparecerá na lista abaixo

### 3. Reconhecimento Facial

1. **Iniciar câmera:**
   - Clique em "Iniciar Câmera"
   - Conceda permissão de acesso à câmera quando solicitado
   - A câmera começará a capturar e processar automaticamente

2. **Processo de reconhecimento:**
   - O sistema analisa a imagem da câmera a cada segundo
   - Quando uma face é detectada, compara com o banco de dados
   - Se reconhecida, exibe a foto do estudante por 3 segundos
   - Durante a exibição, o reconhecimento é pausado
   - Após 3 segundos, retoma o reconhecimento automático

3. **Parar câmera:**
   - Clique em "Câmera parada" para interromper o reconhecimento

### 4. Gerenciamento

- **Visualizar estudantes:** A lista mostra todos os estudantes cadastrados
- **Excluir estudantes:** Clique no botão "Excluir" ao lado do nome
- **Logout:** Clique em "Sair" no canto superior direito

## 🛡️ Segurança

- **Senhas criptografadas:** Todas as senhas são armazenadas com hash seguro
- **Sessões protegidas:** Sistema de sessões Flask para controle de acesso
- **Validação de entrada:** Todos os dados são validados no backend
- **Proteção CORS:** Configurado para permitir acesso apenas de origens autorizadas

## 🔧 Solução de Problemas

### Problemas de Login
- **"Credenciais inválidas":** Verifique se usuário e senha estão corretos
- **Não consegue criar conta:** Verifique se o usuário já existe
- **Redirecionamento contínuo:** Limpe cookies e cache do navegador

### Problemas de Câmera
- **Câmera não inicia:** Verifique se concedeu permissões no navegador
- **"Nenhuma face detectada":** Melhore a iluminação e posicionamento
- **Reconhecimento falha:** Verifique se há estudantes cadastrados

### Problemas de Upload
- **Imagens não carregam:** Verifique formato (JPG, PNG) e tamanho
- **Erro ao salvar:** Verifique conexão com servidor

## 📱 Compatibilidade

### Navegadores Suportados
- ✅ Google Chrome 80+
- ✅ Mozilla Firefox 75+
- ✅ Microsoft Edge 80+
- ✅ Safari 13+

### Dispositivos
- ✅ Desktop/Laptop com câmera web
- ✅ Tablets com câmera frontal
- ⚠️ Smartphones (funcionalidade limitada)

## 🚀 Deploy e Implantação

Para implantar permanentemente no Railway:

1. **Preparar repositório GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Sistema de Reconhecimento Facial com Autenticação"
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   git push -u origin master
   ```

2. **Implantar no Railway:**
   - Acesse [railway.app](https://railway.app)
   - Conecte sua conta GitHub
   - Selecione o repositório do projeto
   - O Railway detectará automaticamente o Flask
   - Aguarde a implantação

3. **Configurar domínio:**
   - O Railway fornecerá uma URL pública
   - Opcionalmente, configure um domínio personalizado

## 📞 Suporte

Para problemas técnicos ou dúvidas:
- Verifique os logs do navegador (F12 → Console)
- Teste em navegador diferente
- Verifique permissões de câmera
- Reinicie o navegador se necessário

---

**Desenvolvido por:** Manus AI  
**Versão:** 2.0 com Autenticação  
**Data:** Agosto 2025

