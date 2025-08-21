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
    """Reconhecer face a partir de uma imagem base64"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'Imagem é obrigatória'}), 400
        
        # Decodificar imagem base64
        image_data = data['image'].split(',')[1]  # Remove o prefixo data:image/...;base64,
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Converter para OpenCV
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detectar faces na imagem
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return jsonify({'error': 'Nenhuma face detectada'}), 400
        
        # Pegar a primeira face detectada
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # Comparar com todas as faces de referência
        students = Student.query.all()
        best_match = None
        best_score = float('inf')
        
        for student in students:
            ref_path = os.path.join(current_app.static_folder, student.reference_image_path)
            if os.path.exists(ref_path):
                ref_image = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
                ref_faces = face_cascade.detectMultiScale(ref_image, 1.1, 4)
                
                if len(ref_faces) > 0:
                    (rx, ry, rw, rh) = ref_faces[0]
                    ref_face_roi = ref_image[ry:ry+rh, rx:rx+rw]
                    
                    # Redimensionar para o mesmo tamanho
                    face_resized = cv2.resize(face_roi, (100, 100))
                    ref_resized = cv2.resize(ref_face_roi, (100, 100))
                    
                    # Calcular diferença usando template matching
                    result = cv2.matchTemplate(face_resized, ref_resized, cv2.TM_SQDIFF_NORMED)
                    score = result[0][0]
                    
                    if score < best_score:
                        best_score = score
                        best_match = student
        
        # Definir threshold para reconhecimento (ajustar conforme necessário)
        threshold = 0.6
        
        if best_match and best_score < threshold:
            return jsonify({
                'recognized': True,
                'student': best_match.to_dict(),
                'confidence': 1 - best_score
            })
        else:
            return jsonify({
                'recognized': False,
                'message': 'Face não reconhecida'
            })
            
    except Exception as e:
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

