from flask import jsonify, request
from service.customer_service import CustomerService

class CustomerController:
    @staticmethod
    def get_customer():
        # Panggil service untuk mendapatkan data customer
        customer = CustomerService.get_customer()
        # Kembalikan respons dalam format JSON
        return jsonify({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email
        }), 200
