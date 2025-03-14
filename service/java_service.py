import gitlab
import os
from dotenv import load_dotenv
import logging
from utils.utils import extract_gitlab_namespace

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

        self.gl = gitlab.Gitlab(self.gitlab_url, private_token=os.getenv("PRIVATE_TOKEN"))

    def get_java_repository_tree(self, repository_url: str, branch: str):
        try:
            logging.debug(f"Request ke repository Java: {repository_url} di branch: {branch}")

            repository = extract_gitlab_namespace(repository_url)
            print(f"Name Space !!!! :  {repository}")   

            # Ambil repository berdasarkan namespace
            project = self.gl.projects.get(repository)
            logging.debug(f"Proyek ditemukan: {project.id}")

            # Ambil daftar file & folder dari repository
            items = project.repository_tree(ref=branch)
            logging.debug(f"Repository tree: {items}")

            return {"status": "success", "data": items}
        
        except gitlab.exceptions.GitlabGetError as e:
            logging.error(f"GitLab error: {e.error_message}")
            return {"status": "error", "error": f"GitLab error: {e.error_message}"}
        
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"status": "error", "error": f"Unexpected error: {str(e)}"}
