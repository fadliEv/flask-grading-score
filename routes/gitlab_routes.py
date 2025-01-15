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
