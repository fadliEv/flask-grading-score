from flask import jsonify, request
from service.gitlab_service import GitLabService
from service.ai_integration_service import AIIntegrationService
from entity.grading_request import GradingRequest
from entity.grading_response import GradingResponse
import logging

gitlab_service = GitLabService()
ai_service = AIIntegrationService()

logging.basicConfig(level=logging.DEBUG)

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

    @staticmethod
    def grade_project():
        try:
            # Parse request body
            data = request.get_json()
            grading_request = GradingRequest(questions=data.get("questions", []))

            # Jalankan proses grading
            branch = data.get("branch", "master")
            grading_response = ai_service.grade_code_with_ai(branch, grading_request.questions)

            logging.debug(f"Response Gradingss :  {grading_response}")

            # # Format respons
            # return jsonify({
            #     "grade": grading_response.grade,
            #     "details": [
            #         {
            #             "question": result.question,
            #             "result": result.result,
            #             "reason": result.reason
            #         } for result in grading_response.details
            #     ]
            # }), 200
              # Format respons
            return grading_response, 200

        except Exception as e:
            return jsonify({"error": f"Error: {e}"}), 500