import gitlab
import os
from dotenv import load_dotenv
import logging
from service.gitlab_service import GitLabService
from service.ai_integration_service import AIIntegrationService
from utils.exception import GitLabRepositoryException

# Konfigurasi logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

class JavaService:
    def __init__(self):
        load_dotenv(override=True)
        self.gitlab_url = os.getenv("GITLAB_URL")
        self.private_token = os.getenv("PRIVATE_TOKEN")
        if not self.gitlab_url or not self.private_token:
            raise ValueError("GITLAB_URL dan PRIVATE_TOKEN harus disetel di .env")
        self.gl = gitlab.Gitlab(self.gitlab_url, private_token=self.private_token)
        self.gitlab_service = GitLabService() 
        self.ai_service = AIIntegrationService()

    def get_java_repository(self, repository_url: str, branch: str):
        """
        Mendapatkan seluruh kode Java dari folder src/com/enigmacamp
        """
        try:
            # Ambil kode Java dari GitLab
            code_combined = self.gitlab_service.get_java_repository(repository_url, branch)

            # Jika ada error yang dilemparkan (misalnya, folder tidak ditemukan)
            if isinstance(code_combined, str) and code_combined.startswith("Tidak ada file .java"):
                raise GitLabRepositoryException(code_combined)  # Lempar exception jika ada error

            return code_combined  # Mengembalikan kode yang digabungkan jika tidak ada error

        except GitLabRepositoryException as e:
            # Menangkap dan menangani error dari GitLabRepositoryException
            return str(e)  # Mengembalikan pesan error sebagai string
        except Exception as e:
            # Menangani error lainnya jika ada
            return f"Unexpected error occurred: {str(e)}"
        
    def analyze_java_code(self, repository_url: str, branch: str):
        """
        Mengambil kode Java dari GitLab dan mengirimnya untuk dianalisis dengan AI
        """
        # Ambil kode Java dari GitLab
        code_combined = self.get_java_repository(repository_url, branch)

        # Jika ada error atau tidak ada kode Java ditemukan
        if isinstance(code_combined, str) and code_combined.startswith("Tidak ada file .java"):
            return code_combined
        
        # Kirim kode yang telah digabungkan ke AI untuk dianalisis
        analysis_result = self.ai_service.analyze_code_with_ai(code_combined)

        return analysis_result
        # return "Test"

    def grade(self,repository_url: str, branch: str, questions: list):
        """
        Mengambil kode Java dari GitLab dan mengirimnya untuk dianalisis dengan AI
        """
        # Ambil kode Java dari GitLab
        code_combined = self.get_java_repository(repository_url, branch)

        # Jika ada error atau tidak ada kode Java ditemukan
        if isinstance(code_combined, str) and code_combined.startswith("Tidak ada file .java"):
            return code_combined
        
        # Kirim kode yang telah digabungkan ke AI untuk dianalisis
        analysis_result = self.ai_service.grade_code_with_ai(code_combined,questions)

        return analysis_result
        # return "Test"
