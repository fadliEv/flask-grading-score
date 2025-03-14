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

    def get_repository_tree_with_content(self, repository_url: str, branch: str):
        try:
            print(f"GitLab URL: {self.gitlab_url}")
            print(f"Private Token: {self.private_token}") 
            namespace = extract_gitlab_namespace(repository_url)
            print(f"Name Space !!!! :  {namespace}")   
            print(f"Branch !!!! :  {branch}")   
            project = self.gl.projects.get(namespace)

            items = project.repository_tree(ref=branch)            
            print(f"Items !!!! :  {items}")   
            result = []

            for item in items:
                if item['type'] == 'tree':
                    sub_items = project.repository_tree(path=item['path'], ref=branch)
                    sub_items_with_content = []

                    for sub_item in sub_items:
                        if sub_item['type'] == 'blob':
                            content = self.get_file_content(project, sub_item['path'], branch)
                            sub_items_with_content.append({
                                **sub_item,
                                "content": content
                            })

                    result.append({
                        **item,
                        "listFile": sub_items_with_content
                    })
                elif item['type'] == 'blob':
                    content = self.get_file_content(project, item['path'], branch)
                    result.append({
                        **item,
                        "content": content
                    })

            return {"status": "success", "data": result}
        except gitlab.exceptions.GitlabGetError as e:
            return {"status": "error", "error": f"GitLab error: {e.error_message}"}

    def get_file_content(self, project, file_path: str, branch: str):
        try:
            file = project.files.get(file_path=file_path, ref=branch)
            
            # Decode base64 content dari file GitLab
            content_bytes = base64.b64decode(file.content)  # Gunakan base64 decoding
            content_str = content_bytes.decode("utf-8")  # Ubah bytes ke string
            
            return content_str
        except gitlab.exceptions.GitlabGetError as e:
            return f"Error fetching file content: {e.error_message}"

