from flask import jsonify, request
from service.gitlab_service import GitLabService

gitlab_service = GitLabService()

class GitLabController:
    @staticmethod
    def repository_check():
        branch = request.args.get("branch", default="master", type=str)
        result = gitlab_service.get_repository_tree_with_content(branch)
        return jsonify(result), 200
