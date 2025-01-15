from flask import Blueprint
from controller.customer_controller import CustomerController

# Buat blueprint untuk customer routes
customer_routes = Blueprint("customer_routes", __name__)

# Tambahkan endpoint untuk GET /customer
customer_routes.add_url_rule("/customer", view_func=CustomerController.get_customer, methods=["GET"])
