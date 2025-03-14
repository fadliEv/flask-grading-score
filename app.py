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


# import gitlab

# # Masukkan URL GitLab dan token pribadi
# # Ganti "your_gitlab_personal_access_token" dengan token pribadi Anda
# private_token = "tjJ6xfkqVs8cePESzf-Q"
# gitlab_url = "https://git.enigmacamp.com"  # Base URL GitLab Anda

# # Inisialisasi koneksi ke GitLab
# gl = gitlab.Gitlab(gitlab_url, private_token=private_token)

# # Akses repository
# # Ganti dengan ID proyek atau namespace proyek GitLab Anda
# project_namespace = "enigma-camp/oflline-class-lovelace/lovelace-turing-19/muhammad-billy-hasman/be/challenge/crud-nasabah"
# project = gl.projects.get(project_namespace)

# # Ambil daftar file dan folder di cabang tertentu
# branch = "master"  # Ganti dengan cabang yang sesuai
# items = project.repository_tree(ref=branch)

# # Tampilkan file dan folder
# print(f"Daftar file dan folder di branch '{branch}':")
# for item in items:
#     print(f"{item['type']}: {item['path']}")
