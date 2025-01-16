import os
import google.generativeai as genai
from service.gitlab_service import GitLabService
from dotenv import load_dotenv

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

    def analyze_code_with_ai(self, branch: str):
        try:
            # Dapatkan kode dari GitLab
            repository_tree = self.gitlab_service.get_repository_tree_with_content(branch)

            # Gabungkan semua kode menjadi satu string
            code_combined = ""
            for item in repository_tree:
                if item['type'] == 'blob':  # Jika file, tambahkan isi file
                    code_combined += f"\n\nFile: {item['path']}\n{item['content']}"
                elif item['type'] == 'tree':  # Jika folder, tambahkan isi folder
                    for sub_item in item.get('listFile', []):
                        if sub_item['type'] == 'blob':
                            code_combined += f"\n\nFile: {sub_item['path']}\n{sub_item['content']}"

            # Kirim prompt ke Gemini AI
            
            response = self.model.generate_content(f"Pahami Code Berikut, Jelaskan :\n{code_combined}")

            # Ekstrak teks dari respons
            if response and hasattr(response, 'candidates') and response.candidates:
                # Ambil teks dari kandidat pertama
                ai_response = response.candidates[0].content.parts[0].text
                return {"response": ai_response}
            else:
                return {"error": "No response from Gemini AI."}
        except Exception as e:
            return {"error": f"Error: {e}"}

    def grade_code_with_ai(self, branch: str, questions: list):
        try:
            # Dapatkan kode dari GitLab
            repository_tree = self.gitlab_service.get_repository_tree_with_content(branch)

            # Gabungkan semua kode menjadi satu string
            code_combined = ""
            for item in repository_tree:
                if item['type'] == 'blob':  # Jika file, tambahkan isi file
                    code_combined += f"\n\nFile: {item['path']}\n{item['content']}"
                elif item['type'] == 'tree':  # Jika folder, tambahkan isi folder
                    for sub_item in item.get('listFile', []):
                        if sub_item['type'] == 'blob':
                            code_combined += f"\n\nFile: {sub_item['path']}\n{sub_item['content']}"

            # Proses setiap soal
            grading_results = []
            total_score = 0

            for question in questions:
                prompt = f"Pahamilah code berikut:\n{code_combined}\n\nSoal: {question}\n\nJelaskan apakah kode tersebut memenuhi requirement soal dan jika terdapat error program atau tidak sesuai intruksi soal jelaskan alasannya."                
                response = self.model.generate_content(prompt)

                if response and hasattr(response, 'candidates') and response.candidates:
                    ai_response = response.candidates[0].content.parts[0].text
                    if "error" in ai_response.lower() or "tidak memenuhi" in ai_response.lower():
                        grading_results.append({"question": question, "result": "Gagal", "reason": ai_response})
                        total_score += 0
                    else:
                        grading_results.append({"question": question, "result": "Lulus", "reason": ai_response})
                        total_score += 100
                else:
                    grading_results.append({"question": question, "result": "Gagal", "reason": "No response from AI."})

            # Hitung nilai rata-rata
            final_grade = total_score / len(questions)
            return {"grade": final_grade, "details": grading_results}
        except Exception as e:
            return {"errors": f"Error: {e}"}