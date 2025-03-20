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

    def analyze_code_with_ai(self, code_combined: str):
        try:
            # Kirim kode yang sudah digabungkan ke AI untuk dianalisis
            response = self.model.generate_content(f"Pahami Code Java Berikut, Jelaskan, dan berikan response dalam format markdown :\n{code_combined}")

            if response and hasattr(response, 'candidates') and response.candidates:
                ai_response = response.candidates[0].content.parts[0].text
                return ai_response
            else:
                return "No response from Gemini AI."

        except Exception as e:
            return e

    def grade_code_with_ai(self, code_combined: str, questions: list):
        try:
            grading_results = []

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

                    grading_results.append({
                        "question": question,
                        "review": ai_response,  # AI response dalam format markdown                        
                    })                    
                else:
                    grading_results.append({
                        "question": question,
                        "review": "⚠️ **No response from AI.**",                        
                    })            

            return grading_results
        
        except Exception as e:
            return e

