from flask import Blueprint
from controller.gitlab_controller import GitLabController

# Buat blueprint
gitlab_routes = Blueprint("gitlab_routes", __name__)

gitlab_routes.add_url_rule(
    "/gitlab/repository-check",
    view_func=GitLabController.check_repository_tree,
    methods=["POST"]
)

gitlab_routes.add_url_rule(
    "/gitlab/scan-branches",
    view_func=GitLabController.scan_branches,
    methods=["POST"]
)