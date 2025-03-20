from flask import jsonify, request
from service.gitlab_service import GitLabService
from service.ai_integration_service import AIIntegrationService
from entity.dto.common_response_dto import CommonResponseDTO  
from entity.dto.repository_check_dto import RepositoryCheckRequest
import logging

gitlab_service = GitLabService()
ai_service = AIIntegrationService()

logging.basicConfig(level=logging.DEBUG)

class GitLabController:
    @staticmethod
    def check_repository_tree():
        try:
            data = request.get_json()
            if not data:
                return jsonify(CommonResponseDTO(message="Request body tidak boleh kosong", data={}).dict()), 400

            repository_url = data.get("repository_url")
            branch = data.get("branch", "master")

            if not repository_url:
                return jsonify(CommonResponseDTO(message="repository_url is required", data={}).dict()), 400
            
            result = gitlab_service.get_repository_tree(repository_url, branch)

            # Cek jika result adalah string (berarti error)
            if isinstance(result, str):
                return jsonify(CommonResponseDTO(message=result, data={}).dict()), 400

            # Cek jika result adalah list (berarti berhasil mendapatkan daftar repository tree)
            if isinstance(result, list):
                return jsonify(CommonResponseDTO(message="Success get repository tree", data=result).dict()), 200

            # Jika format result tidak sesuai
            return jsonify(CommonResponseDTO(message="Unexpected result format", data={}).dict()), 500

        except Exception as e:
            logging.error(f"Error di GitLabController: {str(e)}")
            return jsonify(CommonResponseDTO(message=str(e), data={}).dict()), 500            
        

    @staticmethod
    def scan_branches():
        """
        Endpoint untuk mendapatkan daftar branch dari repository GitLab
        """
        try:
            data = request.get_json()
            if not data or "repository_url" not in data:
                return jsonify(CommonResponseDTO(message="repository_url harus diberikan", data={}).dict()), 400

            repository_url = data["repository_url"]
            
            result = gitlab_service.get_branches_in_repository(repository_url)
            
            if isinstance(result, str):
                return jsonify(CommonResponseDTO(message=result, data={}).dict()), 200
            
            if isinstance(result, list):
                return jsonify(CommonResponseDTO(message="Success get branches", data=result).dict()), 200

            return jsonify(CommonResponseDTO(message="Unexpected result format", data={}).dict()), 500

        except Exception as e:
            return jsonify(CommonResponseDTO(message="Error occurred while fetching branches", data={"error": str(e)}).dict()), 500
