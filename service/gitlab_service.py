import gitlab
import os
from dotenv import load_dotenv
from utils.utils import extract_gitlab_namespace
from utils.exception import GitLabRepositoryException
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
                raise GitLabRepositoryException("Folder 'src' tidak ditemukan di dalam repository.")

            # Masuk ke dalam `src`
            src_items = project.repository_tree(path="src", ref=branch)

            # Cari folder `com` di dalam `src`
            com_folder = next((item for item in src_items if item["type"] == "tree" and item["path"] == "src/com"), None)
            if not com_folder:                
                raise GitLabRepositoryException("Folder 'com' tidak ditemukan di dalam 'src'.")

            # Masuk ke dalam `src/com`
            com_items = project.repository_tree(path="src/com", ref=branch)

            # Cari folder `enigmacamp` di dalam `src/com`
            enigmacamp_folder = next((item for item in com_items if item["type"] == "tree" and item["path"].startswith("src/com/enigmacamp")), None)
            if not enigmacamp_folder:                
                raise GitLabRepositoryException("Folder 'enigmacamp' tidak ditemukan di dalam 'src/com'.")

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
                                return e.error_message

                except gitlab.exceptions.GitlabGetError as e:
                    return e.error_message

                return code_text

            # Ambil seluruh kode dari folder `src/com/enigmacamp`
            code_combined = extract_code_from_tree(enigmacamp_folder["path"])

            if not code_combined.strip():
                raise GitLabRepositoryException("Tidak ada file .java yang ditemukan dalam 'src/com/enigmacamp'.")

            return code_combined

        except gitlab.exceptions.GitlabGetError as e:                      
            print(f"Gitlab Error : {e.error_message}")  
            raise GitLabRepositoryException(f"GitLab Error: {e.error_message}")
        except Exception as e:
            print(str(e))  
            raise GitLabRepositoryException(f"Unexpected Error: {str(e)}")


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
        
    def get_java_repository_from_main(self, repository_url: str, branch: str):
        """
        Mendapatkan seluruh kode Java yang berada di dalam folder yang sama dengan Main.java,
        tanpa bergantung pada prefix folder dan menelusuri subfolder ke tingkat lebih dalam.
        """
        try:
            # Ambil namespace dan project
            namespace = extract_gitlab_namespace(repository_url)
            project = self.gl.projects.get(namespace)

            # Fungsi rekursif untuk mencari file Main.java
            def find_main_file(path=""):
                """Mencari file Main.java dalam seluruh struktur repository"""
                folder_items = project.repository_tree(path=path, ref=branch)
                
                for item in folder_items:
                    # Jika item adalah folder, telusuri lagi secara rekursif
                    if item["type"] == "tree":
                        found_file = find_main_file(item["path"])  # Cari dalam subfolder
                        if found_file:  # Jika ditemukan, kembalikan path file Main.java
                            return found_file
                    elif item["type"] == "blob" and item["path"].endswith("Main.java"):
                        return item["path"]  # Temukan Main.java, kembalikan pathnya
                
                return None  # Jika tidak ditemukan

            # Cari file Main.java di seluruh repository
            main_file_path = find_main_file()

            # Jika Main.java tidak ditemukan, lempar exception
            if not main_file_path:
                raise GitLabRepositoryException("File 'Main.java' tidak ditemukan di dalam repository.")

            # Fungsi untuk menelusuri dan mengambil semua file `.java` dari folder yang sama dengan Main.java
            def extract_code_from_tree(path):
                """Masuk ke dalam folder dan ambil semua file `.java` yang ada di dalam folder ini dan subfoldernya"""
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
                                return e.error_message

                except gitlab.exceptions.GitlabGetError as e:
                    return e.error_message

                return code_text

            # Ambil folder tempat Main.java berada
            main_file_folder = "/".join(main_file_path.split("/")[:-1])  # Mengambil path tanpa nama file

            # Ambil seluruh kode dari folder yang sama dengan Main.java
            code_combined = extract_code_from_tree(main_file_folder)

            if not code_combined.strip():
                raise GitLabRepositoryException("Tidak ada file .java yang ditemukan dalam folder yang sama dengan 'Main.java'.")
            print(f"TEST!!! : {code_combined}")
            return code_combined

        except gitlab.exceptions.GitlabGetError as e:
            print(f"Gitlab Error : {e.error_message}")
            raise GitLabRepositoryException(f"GitLab Error: {e.error_message}")
        except Exception as e:
            print(str(e))
            raise GitLabRepositoryException(f"Unexpected Error: {str(e)}")

    def get_java_repository_from_src(self, repository_url: str, branch: str):
        """
        Mendapatkan seluruh kode Java yang ada di dalam folder /src dan semua subfoldernya.
        Semua file .java yang ditemukan akan digabungkan.
        """
        try:
            # Ambil namespace dan project
            namespace = extract_gitlab_namespace(repository_url)
            project = self.gl.projects.get(namespace)

            # Fungsi untuk menelusuri dan mengambil semua file `.java` dalam folder /src dan subfoldernya
            def extract_code_from_tree(path="src"):
                """Masuk ke dalam folder src dan ambil semua file `.java` yang ada di dalam folder ini dan subfoldernya"""
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
                                return e.error_message

                except gitlab.exceptions.GitlabGetError as e:
                    return e.error_message

                return code_text

            # Ambil seluruh kode dari folder src dan subfoldernya
            code_combined = extract_code_from_tree("src")

            if not code_combined.strip():
                raise GitLabRepositoryException("Tidak ada file .java yang ditemukan dalam folder /src atau subfoldernya.")

            return code_combined

        except gitlab.exceptions.GitlabGetError as e:
            print(f"Gitlab Error : {e.error_message}")
            raise GitLabRepositoryException(f"GitLab Error: {e.error_message}")
        except Exception as e:
            print(str(e))
            raise GitLabRepositoryException(f"Unexpected Error: {str(e)}")

