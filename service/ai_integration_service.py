import os
import google.generativeai as genai
from service.gitlab_service import GitLabService
from dotenv import load_dotenv
from utils.utils import extract_gitlab_namespace
import gitlab
import base64

class AIIntegrationService:
    def __init__(self):
        # Muat file .env
        load_dotenv()

        # Konfigurasi Gemini AI
        api_key = os.getenv("KEY_AI")
        if not api_key:
            raise ValueError("KEY_AI harus disetel di .env")
        genai.configure(api_key=api_key)

        model_ai = os.getenv("MODEL_AI")
        if not model_ai:
            raise ValueError("MODEL_AI harus disetel di .env")        

        # Inisialisasi GitLabService
        self.gitlab_service = GitLabService()
        # setup model 
        self.model = genai.GenerativeModel(model_ai)

    def analyze_code_with_ai(self, repository_url: str, branch: str):
        try:
            # 🔹 Ambil namespace dari URL
            namespace = extract_gitlab_namespace(repository_url)
            print(f"DEBUG: Extracted namespace -> {namespace}")  # 🔥 Debugging namespace

            try:
                # 🔹 Ambil objek `project` dari GitLab
                project = self.gitlab_service.gl.projects.get(namespace)
                
                if not hasattr(project, "id"):  
                    raise ValueError(f"Project retrieval issue: {project}")

            except gitlab.exceptions.GitlabGetError:
                # 🔹 Jika gagal, coba cari project berdasarkan nama
                project_list = self.gitlab_service.gl.projects.list(search=namespace)
                if not project_list:
                    return {"error": f"Project {namespace} not found in GitLab."}
                project = project_list[0]  # Ambil project pertama yang cocok

            print(f"DEBUG: Project ID -> {project.id}")  

            # 🔹 Ambil daftar file & folder di root repository
            items = project.repository_tree(ref=branch)

            # 🔹 Cari folder `src`
            src_folder = next((item for item in items if item["type"] == "tree" and item["path"] == "src"), None)

            if not src_folder:
                return {"error": "Folder 'src' tidak ditemukan di dalam repository."}
        
            src_items = project.repository_tree(path="src", ref=branch)

            # 🔹 Cari folder `com` di dalam `src`
            com_folder = next((item for item in src_items if item["type"] == "tree" and item["path"] == "src/com"), None)

            if not com_folder:
                return {"error": "Folder 'com' tidak ditemukan di dalam 'src'."}

            # Masuk ke dalam `src/com`
            com_items = project.repository_tree(path="src/com", ref=branch)

            # 🔹 Cari folder `enigmacamp` di dalam `src/com`
            enigmacamp_folder = next((item for item in com_items if item["type"] == "tree" and item["path"].startswith("src/com/enigmacamp")), None)

            if not enigmacamp_folder:
                return {"error": "Folder 'enigmacamp' tidak ditemukan di dalam 'src/com'."}

            # 🔹 Fungsi Rekursif untuk Mengambil Kode dari Semua File `.java`
            def extract_code_from_tree(path):
                """Masuk ke dalam folder dan ambil semua file `.java`"""
                code_text = ""
                try:
                    folder_items = project.repository_tree(path=path, ref=branch)

                    print(f"\nMasuk ke dalam folder: {path}")
                    for item in folder_items:
                        print(f"{item['type']}: {item['path']}")

                        # Jika ada subfolder, masuk lagi ke dalamnya (rekursif)
                        if item["type"] == "tree":
                            code_text += extract_code_from_tree(item["path"])

                        # Jika file `.java`, ambil isi filenya
                        elif item["type"] == "blob" and item["path"].endswith(".java"):
                            try:
                                file_content = project.files.get(file_path=item["path"], ref=branch)

                                # 🔹 Decode isi file dari Base64
                                decoded_content = base64.b64decode(file_content.content).decode("utf-8")

                                code_text += f"\n\nFile: {item['path']}\n{decoded_content}\n"
                            except gitlab.exceptions.GitlabGetError as e:
                                print(f"⚠️ Error: Tidak dapat membaca file '{item['path']}' ({e.error_message})")

                except gitlab.exceptions.GitlabGetError as e:
                    print(f"⚠️ Error: {e.error_message}")

                return code_text

            # 🔹 Mulai mengambil semua kode dari `src/com/enigmacamp`
            code_combined = extract_code_from_tree(enigmacamp_folder["path"])

            # 🔥 Jika tidak ada kode ditemukan
            if not code_combined.strip():
                return {"error": "Tidak ada file .java yang ditemukan dalam 'src/com/enigmacamp'."}

            print(f"DEBUG: Code Combined -> {code_combined}")

            # 🔥 Kirim kode ke AI
            response = self.model.generate_content(f"Pahami Code Java Berikut, dan Jelaskan :\n{code_combined}")

            if response and hasattr(response, 'candidates') and response.candidates:
                ai_response = response.candidates[0].content.parts[0].text
                return {"response": ai_response}
            else:
                return {"error": "No response from Gemini AI."}

        except Exception as e:
            return {"error": f"Error: {e}"}



    def grade_code_with_ai(self, repository_url: str, branch: str, questions: list):
        try:
            # 🔹 Ambil namespace dari URL
            namespace = extract_gitlab_namespace(repository_url)
            print(f"DEBUG: Extracted namespace -> {namespace}")  # 🔥 Debugging namespace

            try:
                # 🔹 Ambil objek `project` dari GitLab
                project = self.gitlab_service.gl.projects.get(namespace)

                # ✅ Pastikan `project` adalah objek yang benar
                if not hasattr(project, "id"):  
                    raise ValueError(f"Project retrieval issue: {project}")

            except gitlab.exceptions.GitlabGetError:
                # 🔹 Jika gagal, coba cari project berdasarkan nama
                project_list = self.gitlab_service.gl.projects.list(search=namespace)
                if not project_list:
                    return {"error": f"Project {namespace} not found in GitLab."}
                project = project_list[0]  # Ambil project pertama yang cocok

            print(f"DEBUG: Project ID -> {project.id}")  # 🔥 Pastikan project valid

            # 🔹 Ambil daftar file & folder di root repository
            items = project.repository_tree(ref=branch)

            # 🔹 Cari folder `src`
            src_folder = next((item for item in items if item["type"] == "tree" and item["path"] == "src"), None)

            if not src_folder:
                return {"error": "Folder 'src' tidak ditemukan di dalam repository."}

            # 🔥 Masuk ke dalam `src`
            src_items = project.repository_tree(path="src", ref=branch)

            # 🔹 Cari folder `com` di dalam `src`
            com_folder = next((item for item in src_items if item["type"] == "tree" and item["path"] == "src/com"), None)

            if not com_folder:
                return {"error": "Folder 'com' tidak ditemukan di dalam 'src'."}

            # 🔥 Masuk ke dalam `src/com`
            com_items = project.repository_tree(path="src/com", ref=branch)

            # 🔹 Cari folder `enigmacamp` di dalam `src/com`
            enigmacamp_folder = next((item for item in com_items if item["type"] == "tree" and item["path"].startswith("src/com/enigmacamp")), None)

            if not enigmacamp_folder:
                return {"error": "Folder 'enigmacamp' tidak ditemukan di dalam 'src/com'."}

            # 🔹 Fungsi Rekursif untuk Mengambil Kode dari Semua File `.java`
            def extract_code_from_tree(path):
                """Masuk ke dalam folder dan ambil semua file `.java`"""
                code_text = ""
                try:
                    folder_items = project.repository_tree(path=path, ref=branch)

                    print(f"\nMasuk ke dalam folder: {path}")
                    for item in folder_items:
                        print(f"{item['type']}: {item['path']}")

                        # 🔥 Jika ada subfolder, masuk lagi ke dalamnya (rekursif)
                        if item["type"] == "tree":
                            code_text += extract_code_from_tree(item["path"])

                        # 🔥 Jika file `.java`, ambil isi filenya
                        elif item["type"] == "blob" and item["path"].endswith(".java"):
                            try:
                                file_content = project.files.get(file_path=item["path"], ref=branch)

                                # 🔹 Decode isi file dari Base64
                                decoded_content = base64.b64decode(file_content.content).decode("utf-8")

                                code_text += f"\n\nFile: {item['path']}\n{decoded_content}\n"
                            except gitlab.exceptions.GitlabGetError as e:
                                print(f"⚠️ Error: Tidak dapat membaca file '{item['path']}' ({e.error_message})")

                except gitlab.exceptions.GitlabGetError as e:
                    print(f"⚠️ Error: {e.error_message}")

                return code_text

            # 🔹 Mulai mengambil semua kode dari `src/com/enigmacamp`
            code_combined = extract_code_from_tree(enigmacamp_folder["path"])

            # 🔥 Jika tidak ada kode ditemukan
            if not code_combined.strip():
                return {"error": "Tidak ada file .java yang ditemukan dalam 'src/com/enigmacamp'."}

            grading_results = []
            total_score = 0

            for question in questions:
                prompt = f"""
                ### 📌 **Analisis Kode Java:**
                {code_combined}

                ### ❓ **Soal:** 
                {question}

                💡 **Instruksi AI:**  
                - ⚠️ **Jangan berikan revisi atau improvement code.**  
                - ✅ Cukup beritahu apakah kode memenuhi requirement atau tidak.  
                - 🚨 Jika ada error atau kesalahan, **berikan cuplikan kode yang relevan saja**, jangan berikan seluruh kode.  
                - 📜 **Gunakan format Markdown** untuk respons agar mudah dibaca. Gunakan heading (`#`), bold (`**`), bullet points (`-`), dan code blocks (```java ... ``` jika diperlukan).  
                """

                response = self.model.generate_content(prompt)

                if response and hasattr(response, 'candidates') and response.candidates:
                    ai_response = response.candidates[0].content.parts[0].text

                    # Status Lulus atau Gagal berdasarkan apakah ada error atau tidak
                    result_status = "Lulus" if "error" not in ai_response.lower() and "tidak memenuhi" not in ai_response.lower() else "Gagal"

                    grading_results.append({
                        "question": question,
                        "review": ai_response,  # AI response dalam format markdown
                        "result": result_status
                    })

                    total_score += 100 if result_status == "Lulus" else 0
                else:
                    grading_results.append({
                        "question": question,
                        "review": "⚠️ **No response from AI.**",
                        "result": "Gagal"
                    })

            # 🔹 Hitung nilai rata-rata (Harus dilakukan di luar loop for)
            final_grade = total_score / len(questions) if questions else 0

            return {"grade": final_grade, "details": grading_results}

        except Exception as e:
            return {"errors": f"Error: {e}"}
