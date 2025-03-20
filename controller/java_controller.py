from flask import jsonify, request
from service.java_service import JavaService
from entity.dto.common_response_dto import CommonResponseDTO 
from utils.exception import GitLabRepositoryException 
import logging

# Inisialisasi service
java_service = JavaService()

logging.basicConfig(level=logging.DEBUG)

class JavaController:
    @staticmethod
    def get_java_code():
        """
        Endpoint untuk mendapatkan seluruh kode Java dari repository GitLab
        """
        try:
            # Ambil data request JSON
            data = request.get_json()
            if not data:                
                return jsonify(CommonResponseDTO(message="Request body tidak boleh kosong", data={}).dict()), 400

            repository_url = data.get("repository_url")
            branch = data.get("branch", "master")  # Default branch is master

            if not repository_url:            
                return jsonify(CommonResponseDTO(message="repository_url harus disertakan juga", data={}).dict()), 400

            # Panggil method untuk mendapatkan seluruh kode Java dari folder src/com/enigmacamp
            code_combined = java_service.get_java_repository(repository_url, branch)

            # if isinstance(code_combined, str) and code_combined.startswith("Tidak ada file .java"):                
            #     return jsonify(CommonResponseDTO(message=code_combined, data={}).dict()), 404
            # print(f"DEBUG: Code Combined -> {code_combined}")

            # Cek jika hasilnya adalah error message
            if isinstance(code_combined, str) and code_combined.startswith("GitLab Error"):
                # Jika ada error dari GitLab, lempar exception untuk ditangani
                raise GitLabRepositoryException(code_combined)
            return jsonify(CommonResponseDTO(message="Success get Java code", data=code_combined).dict()), 200

        except GitLabRepositoryException as e:
            logging.error(f"Error di JavaController: {str(e)}")            
            return jsonify(CommonResponseDTO(message=str(e), data={}).dict()), 500
        
        except Exception as e:
            logging.error(f"Error di JavaController: {str(e)}")            
            return jsonify(CommonResponseDTO(message=str(e), data={}).dict()), 500
        
    @staticmethod
    def analyze_code():
        """
        Endpoint untuk menganalisis kode Java dari repository GitLab
        """
        try:
            # Ambil data request JSON
            data = request.get_json()
            if not data:
                return jsonify(CommonResponseDTO(message="Request body tidak boleh kosong", data={}).dict()), 400

            repository_url = data.get("repository_url")
            branch = data.get("branch", "master")  # Default branch is master

            if not repository_url:
                return jsonify(CommonResponseDTO(message="repository_url harus disertakan juga", data={}).dict()), 400

            # Panggil service untuk menganalisis kode Java
            result = java_service.analyze_java_code(repository_url, branch)
            
            return jsonify(CommonResponseDTO(message="Success analyze code with AI", data=result).dict()), 200

        except Exception as e:
            logging.error(f"Error di JavaController: {str(e)}")
            return jsonify(CommonResponseDTO(message=str(e), data={}).dict()), 500

    @staticmethod
    def grade_code():
        try:
            data = request.get_json()
            if not data:
                return jsonify(CommonResponseDTO(message="Request body tidak boleh kosong", data={}).dict()), 400
            
            repository_url = data.get("repository_url")
            branch = data.get("branch", "master")
            questions = data.get("questions", [])

            if not repository_url:
                return jsonify(CommonResponseDTO(message="repository_url harus disertakan juga", data={}).dict()), 400
            
            if not questions or not isinstance(questions, list):                
                return jsonify(CommonResponseDTO(message="Pertanyaan harus diberikan dalam bentuk list", data={}).dict()), 400
            
            # logging.debug(f"📝 Menilai kode dari repository: {repository_url}, branch: {branch}")
            response = java_service.grade(repository_url, branch, questions)            
            return jsonify(CommonResponseDTO(message="Success analyze grading code with AI", data=response).dict()), 200
        
        except Exception as e:
            logging.error(f"❌ Error di grade_code: {str(e)}")
            return jsonify(CommonResponseDTO(message=str(e), data={}).dict()), 500