import gitlab
import os
from dotenv import load_dotenv
from utils.utils import extract_gitlab_namespace
import logging
import base64

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
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

    def get_repository_tree(self, repository_url: str, branch: str):
        try:            
            repository = extract_gitlab_namespace(repository_url)                        
            project = self.gl.projects.get(repository)             
            items = project.repository_tree(ref=branch)
            return items
        
        except gitlab.exceptions.GitlabGetError as e:
            return e.error_message

        except Exception as e:            
            return str(e)
        
    def get_java_repository(self, repository_url: str, branch: str):
        """
        Mendapatkan seluruh kode Java dari folder src/com/enigmacamp
        """
        try:
            # Ambil namespace dan project
            namespace = extract_gitlab_namespace(repository_url)
            project = self.gl.projects.get(namespace)

            # Ambil daftar file & folder di root repository
            items = project.repository_tree(ref=branch)

            # Cari folder `src`
            src_folder = next((item for item in items if item["type"] == "tree" and item["path"] == "src"), None)
            if not src_folder:
                return {"error": "Folder 'src' tidak ditemukan di dalam repository."}

            # Masuk ke dalam `src`
            src_items = project.repository_tree(path="src", ref=branch)

            # Cari folder `com` di dalam `src`
            com_folder = next((item for item in src_items if item["type"] == "tree" and item["path"] == "src/com"), None)
            if not com_folder:
                return {"error": "Folder 'com' tidak ditemukan di dalam 'src'."}

            # Masuk ke dalam `src/com`
            com_items = project.repository_tree(path="src/com", ref=branch)

            # Cari folder `enigmacamp` di dalam `src/com`
            enigmacamp_folder = next((item for item in com_items if item["type"] == "tree" and item["path"].startswith("src/com/enigmacamp")), None)
            if not enigmacamp_folder:
                return {"error": "Folder 'enigmacamp' tidak ditemukan di dalam 'src/com'."}

            # Fungsi Rekursif untuk Mengambil Kode dari Semua File `.java`
            def extract_code_from_tree(path):
                """Masuk ke dalam folder dan ambil semua file `.java`"""
                code_text = ""
                try:
                    folder_items = project.repository_tree(path=path, ref=branch)

                    for item in folder_items:
                        # Jika ada subfolder, masuk lagi ke dalamnya (rekursif)
                        if item["type"] == "tree":
                            code_text += extract_code_from_tree(item["path"])

                        # Jika file `.java`, ambil isi filenya
                        elif item["type"] == "blob" and item["path"].endswith(".java"):
                            try:
                                file_content = project.files.get(file_path=item["path"], ref=branch)

                                # Decode isi file dari Base64
                                decoded_content = base64.b64decode(file_content.content).decode("utf-8")

                                code_text += f"\n\nFile: {item['path']}\n{decoded_content}\n"
                            except gitlab.exceptions.GitlabGetError as e:
                                print(f"⚠️ Error: Tidak dapat membaca file '{item['path']}' ({e.error_message})")

                except gitlab.exceptions.GitlabGetError as e:
                    print(f"⚠️ Error: {e.error_message}")

                return code_text

            # Ambil seluruh kode dari folder `src/com/enigmacamp`
            code_combined = extract_code_from_tree(enigmacamp_folder["path"])

            if not code_combined.strip():
                return "Tidak ada file .java yang ditemukan dalam 'src/com/enigmacamp'."

            return code_combined

        except gitlab.exceptions.GitlabGetError as e:            
            return e.error_message

        except Exception as e:
            return str(e)


    def get_branches_in_repository(self, repository_url: str):
        """
        Mengambil daftar branch yang ada dalam repository GitLab
        """
        try:
            namespace = extract_gitlab_namespace(repository_url)
            project = self.gl.projects.get(namespace)

            branches = project.branches.list(all=True) 
            branch_names = [branch.name for branch in branches]

            return branch_names
        except gitlab.exceptions.GitlabGetError as e:            
            return e.error_message
        except Exception as e:            
            return str(e)