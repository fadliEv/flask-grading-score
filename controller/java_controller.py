from flask import jsonify, request
from service.java_service import JavaService
from service.ai_integration_service import AIIntegrationService
import logging

# Inisialisasi service
java_service = JavaService()
ai_service = AIIntegrationService()

class JavaController:
    @staticmethod
    def check_java_repository():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Request body tidak boleh kosong"}), 400

            repository_url = data.get("repository_url")
            branch = data.get("branch", "master")

            if not repository_url:
                return jsonify({"error": "repository_url harus diberikan"}), 400

            logging.debug(f"Memeriksa repository Java: {repository_url} di branch: {branch}")

            # Panggil service untuk mengambil repository tree
            result = java_service.get_java_repository_tree(repository_url, branch)

            if result.get("status") == "error":
                return jsonify({"status": "error", "message": result["error"]}), 400

            return jsonify({"status": "success", "data": result["data"]}), 200

        except Exception as e:
            logging.error(f"Error di JavaController: {str(e)}")
            return jsonify({"error": f"Error: {str(e)}"}), 500
        
    @staticmethod
    def analyze_code():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body tidak boleh kosong"}), 400
        repository_url = data.get("repository_url")
        branch = data.get("branch", "master")
        if not repository_url:
            return jsonify({"error": "repository_url harus diberikan"}), 400
        response = ai_service.analyze_code_with_ai(repository_url,branch)
        return jsonify(response), 200
