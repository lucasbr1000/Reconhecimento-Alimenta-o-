import os
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from src.models.student import Student, db
import base64
from PIL import Image
import io

facial_recognition_bp = Blueprint('facial_recognition', __name__)

# Configurações para upload de arquivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path

def preprocess_face(face_roi):
    """Pré-processamento avançado da face para melhorar a precisão"""
    try:
        # 1. Redimensionar para tamanho padrão
        face_resized = cv2.resize(face_roi, (150, 150))
        
        # 2. Equalização de histograma para normalizar iluminação
        face_equalized = cv2.equalizeHist(face_resized)
        
        # 3. Aplicar filtro Gaussiano para suavizar ruídos
        face_smoothed = cv2.GaussianBlur(face_equalized, (3, 3), 0)
        
        # 4. Normalização de contraste usando CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        face_normalized = clahe.apply(face_smoothed)
        
        return face_normalized
    except Exception as e:
        print(f"Erro no pré-processamento: {e}")
        return cv2.resize(face_roi, (150, 150))

def calculate_lbp_histogram(image):
    """Calcular histograma LBP (Local Binary Patterns) para características mais robustas"""
    try:
        # Parâmetros LBP
        radius = 3
        n_points = 8 * radius
        
        # Calcular LBP
        lbp = np.zeros_like(image)
        for i in range(radius, image.shape[0] - radius):
            for j in range(radius, image.shape[1] - radius):
                center = image[i, j]
                binary_string = ''
                
                # Calcular valores dos pontos vizinhos
                for k in range(n_points):
                    angle = 2 * np.pi * k / n_points
                    x = int(i + radius * np.cos(angle))
                    y = int(j + radius * np.sin(angle))
                    
                    if 0 <= x < image.shape[0] and 0 <= y < image.shape[1]:
                        if image[x, y] >= center:
                            binary_string += '1'
                        else:
                            binary_string += '0'
                    else:
                        binary_string += '0'
                
                # Converter para decimal
                lbp[i, j] = int(binary_string, 2)
        
        # Calcular histograma
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        
        # Normalizar histograma
        hist = hist.astype(float)
        hist /= (hist.sum() + 1e-7)
        
        return hist
    except Exception as e:
        print(f"Erro no cálculo LBP: {e}")
        # Fallback para histograma simples
        hist, _ = np.histogram(image.ravel(), bins=256, range=(0, 256))
        hist = hist.astype(float)
        hist /= (hist.sum() + 1e-7)
        return hist

def compare_faces_advanced(face1, face2):
    """Comparação avançada usando múltiplas métricas"""
    try:
        # 1. Pré-processar ambas as faces
        face1_processed = preprocess_face(face1)
        face2_processed = preprocess_face(face2)
        
        # 2. Calcular histogramas LBP
        hist1 = calculate_lbp_histogram(face1_processed)
        hist2 = calculate_lbp_histogram(face2_processed)
        
        # 3. Calcular correlação entre histogramas
        correlation = cv2.compareHist(hist1.astype(np.float32), hist2.astype(np.float32), cv2.HISTCMP_CORREL)
        
        # 4. Calcular distância Chi-quadrado (invertida para similaridade)
        chi_square = cv2.compareHist(hist1.astype(np.float32), hist2.astype(np.float32), cv2.HISTCMP_CHISQR)
        chi_square_similarity = 1.0 / (1.0 + chi_square)
        
        # 5. Template matching como métrica adicional
        template_result = cv2.matchTemplate(face1_processed, face2_processed, cv2.TM_CCOEFF_NORMED)
        template_score = template_result[0][0]
        
        # 6. Combinar métricas com pesos
        final_score = (0.4 * correlation + 0.3 * chi_square_similarity + 0.3 * template_score)
        
        return final_score
    except Exception as e:
        print(f"Erro na comparação avançada: {e}")
        # Fallback para template matching simples
        face1_resized = cv2.resize(face1, (150, 150))
        face2_resized = cv2.resize(face2, (150, 150))
        result = cv2.matchTemplate(face1_resized, face2_resized, cv2.TM_CCOEFF_NORMED)
        return result[0][0]

def detect_face_quality(face_roi):
    """Avaliar a qualidade da face detectada"""
    try:
        # Calcular variância (indicador de nitidez)
        variance = cv2.Laplacian(face_roi, cv2.CV_64F).var()
        
        # Calcular brilho médio
        brightness = np.mean(face_roi)
        
        # Calcular contraste
        contrast = np.std(face_roi)
        
        # Critérios de qualidade
        quality_score = 0
        
        # Nitidez (variância > 100 é considerada boa)
        if variance > 100:
            quality_score += 0.4
        elif variance > 50:
            quality_score += 0.2
        
        # Brilho (entre 50 e 200 é ideal)
        if 50 <= brightness <= 200:
            quality_score += 0.3
        elif 30 <= brightness <= 220:
            quality_score += 0.15
        
        # Contraste (> 30 é bom)
        if contrast > 30:
            quality_score += 0.3
        elif contrast > 15:
            quality_score += 0.15
        
        return quality_score, variance, brightness, contrast
    except Exception as e:
        print(f"Erro na avaliação de qualidade: {e}")
        return 0.5, 0, 0, 0

@facial_recognition_bp.route('/students', methods=['POST'])
def add_student():
    """Adicionar um novo estudante com imagens de referência e exibição"""
    try:
        name = request.form.get('name')
        if not name:
            return jsonify({'error': 'Nome é obrigatório'}), 400
        
        # Verificar se os arquivos foram enviados
        if 'reference_image' not in request.files or 'display_image' not in request.files:
            return jsonify({'error': 'Imagens de referência e exibição são obrigatórias'}), 400
        
        reference_file = request.files['reference_image']
        display_file = request.files['display_image']
        
        if reference_file.filename == '' or display_file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not (allowed_file(reference_file.filename) and allowed_file(display_file.filename)):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        upload_path = ensure_upload_folder()
        
        # Salvar imagem de referência
        reference_filename = secure_filename(f"ref_{name}_{reference_file.filename}")
        reference_path = os.path.join(upload_path, reference_filename)
        reference_file.save(reference_path)
        
        # Salvar imagem de exibição
        display_filename = secure_filename(f"display_{name}_{display_file.filename}")
        display_path = os.path.join(upload_path, display_filename)
        display_file.save(display_path)
        
        # Validar qualidade da imagem de referência
        try:
            ref_image = cv2.imread(reference_path, cv2.IMREAD_GRAYSCALE)
            if ref_image is not None:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(ref_image, 1.1, 4)
                
                if len(faces) > 0:
                    (x, y, w, h) = faces[0]
                    face_roi = ref_image[y:y+h, x:x+w]
                    quality_score, variance, brightness, contrast = detect_face_quality(face_roi)
                    
                    if quality_score < 0.3:
                        return jsonify({
                            'error': 'Qualidade da imagem de referência muito baixa. Tente uma imagem com melhor iluminação e nitidez.',
                            'quality_details': {
                                'score': quality_score,
                                'variance': variance,
                                'brightness': brightness,
                                'contrast': contrast
                            }
                        }), 400
        except Exception as e:
            print(f"Erro na validação de qualidade: {e}")
        
        # Criar novo estudante no banco de dados
        student = Student(
            name=name,
            reference_image_path=f"{UPLOAD_FOLDER}/{reference_filename}",
            display_image_path=f"{UPLOAD_FOLDER}/{display_filename}"
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Estudante adicionado com sucesso',
            'student': student.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@facial_recognition_bp.route('/students', methods=['GET'])
def get_students():
    """Listar todos os estudantes"""
    try:
        students = Student.query.all()
        return jsonify([student.to_dict() for student in students])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@facial_recognition_bp.route('/recognize', methods=['POST'])
def recognize_face():
    """Reconhecer face a partir de uma imagem base64 com algoritmo melhorado"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'Imagem é obrigatória'}), 400
        
        # Decodificar imagem base64
        try:
            image_data = data['image'].split(',')[1]  # Remove o prefixo data:image/...;base64,
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            print(f"Erro ao decodificar imagem: {e}")
            return jsonify({'error': 'Erro ao processar imagem'}), 400
        
        # Converter para OpenCV
        try:
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Erro ao converter imagem para OpenCV: {e}")
            return jsonify({'error': 'Erro ao processar imagem'}), 400
        
        # Detectar faces na imagem
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        except Exception as e:
            print(f"Erro na detecção de faces: {e}")
            return jsonify({'error': 'Erro na detecção de faces'}), 500
        
        if len(faces) == 0:
            return jsonify({'error': 'Nenhuma face detectada'}), 400
        
        # Pegar a maior face detectada (mais provável de ser a face principal)
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        (x, y, w, h) = largest_face
        face_roi = gray[y:y+h, x:x+w]
        
        # Avaliar qualidade da face capturada
        quality_score, variance, brightness, contrast = detect_face_quality(face_roi)
        
        if quality_score < 0.2:
            return jsonify({
                'error': 'Qualidade da imagem muito baixa. Melhore a iluminação e mantenha o rosto bem posicionado.',
                'quality_score': quality_score
            }), 400
        
        # Comparar com todas as faces de referência usando algoritmo melhorado
        try:
            students = Student.query.all()
            best_match = None
            best_score = 0.0
            all_scores = []
            
            for student in students:
                ref_path = os.path.join(current_app.static_folder, student.reference_image_path)
                if os.path.exists(ref_path):
                    try:
                        ref_image = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
                        if ref_image is None:
                            print(f"Erro ao carregar imagem de referência: {ref_path}")
                            continue
                            
                        ref_faces = face_cascade.detectMultiScale(ref_image, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
                        
                        if len(ref_faces) > 0:
                            # Pegar a maior face da imagem de referência
                            largest_ref_face = max(ref_faces, key=lambda face: face[2] * face[3])
                            (rx, ry, rw, rh) = largest_ref_face
                            ref_face_roi = ref_image[ry:ry+rh, rx:rx+rw]
                            
                            # Usar algoritmo de comparação melhorado
                            score = compare_faces_advanced(face_roi, ref_face_roi)
                            all_scores.append(score)
                            
                            print(f"Score para {student.name}: {score}")
                            
                            if score > best_score:
                                best_score = score
                                best_match = student
                    except Exception as e:
                        print(f"Erro ao processar estudante {student.name}: {e}")
                        continue
        except Exception as e:
            print(f"Erro na comparação de faces: {e}")
            return jsonify({'error': 'Erro na comparação de faces'}), 500
        
        # Threshold adaptativo baseado na distribuição de scores
        if len(all_scores) > 1:
            mean_score = np.mean(all_scores)
            std_score = np.std(all_scores)
            # Threshold dinâmico: média + 1 desvio padrão, mas no mínimo 0.4
            dynamic_threshold = max(0.4, mean_score + std_score)
        else:
            dynamic_threshold = 0.4
        
        print(f"Melhor score: {best_score}, Threshold: {dynamic_threshold}")
        
        if best_match and best_score > dynamic_threshold:
            return jsonify({
                'recognized': True,
                'student': best_match.to_dict(),
                'confidence': float(best_score),
                'quality_score': float(quality_score),
                'threshold_used': float(dynamic_threshold)
            })
        else:
            return jsonify({
                'recognized': False,
                'message': 'Face não reconhecida',
                'best_score': float(best_score) if best_score > 0 else 0.0,
                'threshold_used': float(dynamic_threshold),
                'quality_score': float(quality_score)
            })
            
    except Exception as e:
        print(f"Erro geral no reconhecimento: {e}")
        return jsonify({'error': str(e)}), 500

@facial_recognition_bp.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Deletar um estudante"""
    try:
        student = Student.query.get_or_404(student_id)
        
        # Deletar arquivos de imagem
        ref_path = os.path.join(current_app.static_folder, student.reference_image_path)
        display_path = os.path.join(current_app.static_folder, student.display_image_path)
        
        if os.path.exists(ref_path):
            os.remove(ref_path)
        if os.path.exists(display_path):
            os.remove(display_path)
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'message': 'Estudante deletado com sucesso'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

