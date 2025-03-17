import gitlab
import os
from dotenv import load_dotenv
from utils.utils import extract_gitlab_namespace
import base64
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Pastikan level debug aktif
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Kirim log ke console
    ]
)
class GitLabService:
    def __init__(self):
        load_dotenv()
        self.gitlab_url = os.getenv("GITLAB_URL")
        self.private_token = os.getenv("PRIVATE_TOKEN")

        if not self.gitlab_url or not self.private_token:
            raise ValueError("GITLAB_URL dan PRIVATE_TOKEN harus disetel di .env")

        self.gl = gitlab.Gitlab(self.gitlab_url, private_token=self.private_token)

    def get_repository_tree_with_content(self, repository_url: str, branch: str, path: str = ""):
        try:
            namespace = extract_gitlab_namespace(repository_url)
            project = self.gl.projects.get(namespace)

            # 🔹 Ambil daftar file & folder dengan path tertentu
            items = project.repository_tree(ref=branch, path=path)
            result = []

            for item in items:
                if item["type"] == "blob":
                    # 🔹 Jika file, ambil isi file
                    content = self.get_file_content(repository_url, item["path"], branch)
                    result.append({
                        **item,
                        "content": content
                    })
                else:
                    # 🔹 Jika folder, tambahkan tanpa mengambil ulang
                    result.append(item)

            return {"status": "success", "data": result}

        except gitlab.exceptions.GitlabGetError as e:
            return {"status": "error", "error": f"GitLab error: {e.error_message}"}


    def get_file_content(self, project, file_path: str, branch: str):
        try:
            # 🔹 Pastikan `project` adalah objek GitLab
            if not isinstance(project, gitlab.v4.objects.Project):
                raise ValueError(f"Expected Project object, but got {type(project)}")

            file = project.files.get(file_path=file_path, ref=branch)

            # 🔹 Decode base64 content dari GitLab
            content_bytes = base64.b64decode(file.content)  
            content_str = content_bytes.decode("utf-8")  
            
            return content_str
        except gitlab.exceptions.GitlabGetError as e:
            return f"Error fetching file content: {e.error_message}"


    def get_branches_in_repository(self, repository_url: str):
        """
        Mengambil daftar branch yang ada dalam repository GitLab
        """
        try:
            namespace = extract_gitlab_namespace(repository_url)
            project = self.gl.projects.get(namespace)

            branches = project.branches.list(all=True) 
            branch_names = [branch.name for branch in branches]

            return {"status": "success", "branches": branch_names}

        except gitlab.exceptions.GitlabGetError as e:
            return {"status": "error", "error": f"GitLab error: {e.error_message}"}

        except Exception as e:
            return {"status": "error", "error": f"Unexpected error: {str(e)}"}