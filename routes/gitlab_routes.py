from flask import Blueprint
from controller.gitlab_controller import GitLabController

# Buat blueprint
gitlab_routes = Blueprint("gitlab_routes", __name__)

# Tambahkan endpoint untuk repository-check
gitlab_routes.add_url_rule(
    "/gitlab/repository-check",
    view_func=GitLabController.repository_check,
    methods=["GET"]
)


# Tambahkan endpoint untuk analisis kode
gitlab_routes.add_url_rule(
    "/gitlab/analyze-code",
    view_func=GitLabController.analyze_code,
    methods=["GET"]
)


gitlab_routes.add_url_rule(
    "/grading",
    view_func=GitLabController.grade_project,
    methods=["POST"]
)