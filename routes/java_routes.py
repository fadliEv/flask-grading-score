from flask import Blueprint
from controller.java_controller import JavaController

# Buat blueprint khusus untuk Java repository
java_routes = Blueprint("java_routes", __name__)

# Endpoint untuk cek repository Java
java_routes.add_url_rule(
    "/java/repository-check",
    view_func=JavaController.get_java_code,
    methods=["POST"]
)

java_routes.add_url_rule(
    "/java/analyze-code",
    view_func=JavaController.analyze_code,
    methods=["POST"]
)

java_routes.add_url_rule(
    "/java/grade-code",
    view_func=JavaController.grade_code,
    methods=["POST"]
)
