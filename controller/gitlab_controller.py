from flask import jsonify, request
from service.gitlab_service import GitLabService
from service.ai_integration_service import AIIntegrationService

gitlab_service = GitLabService()
ai_service = AIIntegrationService()

class GitLabController:
    @staticmethod
    def repository_check():
        branch = request.args.get("branch", default="master", type=str)
        result = gitlab_service.get_repository_tree_with_content(branch)
        return jsonify(result), 200

    @staticmethod
    def analyze_code():
        branch = request.args.get("branch", default="master", type=str)
        response = ai_service.analyze_code_with_ai(branch)
        return jsonify(response), 200
