from flask import Flask
from routes.gitlab_routes import gitlab_routes
from routes.customer_routes import customer_routes
from routes.java_routes import java_routes

app = Flask(__name__)

# Register semua routes
app.register_blueprint(customer_routes)
app.register_blueprint(gitlab_routes)
app.register_blueprint(java_routes)

if __name__ == "__main__":
    app.run(host="localhost", port=5100, debug=True)




