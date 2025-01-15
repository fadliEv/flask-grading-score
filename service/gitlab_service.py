import gitlab
import os
from dotenv import load_dotenv

class GitLabService:
    def __init__(self):
        # Muat file .env
        load_dotenv()
        # Ambil variabel dari environment
        gitlab_url = os.getenv("GITLAB_URL")
        private_token = os.getenv("PRIVATE_TOKEN")
        project_namespace = os.getenv("PROJECT_NAMESPACE")

        # Validasi variabel lingkungan
        if not gitlab_url or not private_token or not project_namespace:
            raise ValueError("GITLAB_URL, PRIVATE_TOKEN, dan PROJECT_NAMESPACE harus disetel di .env")

        # Inisialisasi koneksi ke GitLab
        self.gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        self.project = self.gl.projects.get(project_namespace)

    def get_repository_tree_with_content(self, branch: str):
        try:
            # Ambil daftar tree di root
            items = self.project.repository_tree(ref=branch)
            result = []

            for item in items:
                if item['type'] == 'tree':
                    # Jika item adalah folder (tree), ambil isi folder
                    sub_items = self.project.repository_tree(path=item['path'], ref=branch)
                    sub_items_with_content = []

                    for sub_item in sub_items:
                        if sub_item['type'] == 'blob':
                            # Ambil isi file
                            content = self.get_file_content(sub_item['path'], branch)
                            sub_items_with_content.append({
                                **sub_item,
                                "content": content
                            })

                    result.append({
                        **item,
                        "listFile": sub_items_with_content
                    })
                elif item['type'] == 'blob':
                    # Jika item adalah file, ambil isi file
                    content = self.get_file_content(item['path'], branch)
                    result.append({
                        **item,
                        "content": content
                    })

            return result
        except gitlab.exceptions.GitlabGetError as e:
            return {"error": f"GitLab error: {e.error_message}"}

    def get_file_content(self, file_path: str, branch: str):
        try:
            file = self.project.files.get(file_path=file_path, ref=branch)
            # Decode isi file dari base64 dan konversi ke string
            return file.decode().decode('utf-8')
        except gitlab.exceptions.GitlabGetError as e:
            return f"Error fetching file content: {e.error_message}"
