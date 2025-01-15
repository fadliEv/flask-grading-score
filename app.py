from flask import Flask
from routes.gitlab_routes import gitlab_routes
from routes.customer_routes import customer_routes

app = Flask(__name__)

# Register semua routes
app.register_blueprint(customer_routes)
app.register_blueprint(gitlab_routes)

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
# import google.generativeai as gemini

# # Konfigurasikan API key
# gemini.configure(api_key="AIzaSyCKnwkTKeaUW6xBy9YcRd2aocl6dm1NrXU")

# model = genai.GenerativeModel('gemini-pro')