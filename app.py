from flask import Flask
from routes.gitlab_routes import gitlab_routes
from routes.customer_routes import customer_routes

app = Flask(__name__)

# Register semua routes
app.register_blueprint(customer_routes)
app.register_blueprint(gitlab_routes)

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
# import google.generativeai as genai

# # Konfigurasikan API key
# genai.configure(api_key="AIzaSyCKnwkTKeaUW6xBy9YcRd2aocl6dm1NrXU")

# # Kirim permintaan ke AI
# try:
#     # Inisialisasi model
#     model = genai.GenerativeModel('gemini-pro')

#     # Menghasilkan konten dengan prompt
#     response = model.generate_content("Hallo, selamat siang?")

#     # Ekstrak teks dari respons
#     if response and hasattr(response, 'candidates') and response.candidates:
#         # Ambil teks dari kandidat pertama
#         text = response.candidates[0].content.parts[0].text
#         print(f"AI Response: {text}")
#     else:
#         print("No response received.")
# except Exception as e:
#     print(f"Error: {e}")
