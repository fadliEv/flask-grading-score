import gitlab
import base64  # Untuk decode isi file dari GitLab

# Masukkan URL GitLab dan token pribadi
private_token = "tjJ6xfkqVs8cePESzf-Q"
gitlab_url = "https://git.enigmacamp.com"

# Inisialisasi koneksi ke GitLab
gl = gitlab.Gitlab(gitlab_url, private_token=private_token)

# Akses repository
project_namespace = "enigma-camp/oflline-class-lovelace/lovelace-turing-19/muhammad-billy-hasman/be/challenge/crud-nasabah"
project = gl.projects.get(project_namespace)

# Tentukan branch
branch = "03-with-arrayList"

# 🔹 Ambil daftar file & folder di root repository
items = project.repository_tree(ref=branch)

# 🔹 Tampilkan daftar file & folder di root
print(f"Daftar file dan folder di branch '{branch}':")
for item in items:
    print(f"{item['type']}: {item['path']}")

# 🔹 Fungsi Rekursif untuk Menampilkan Isi Folder dan Membaca File `.java`
def list_folder_contents(path):
    """Masuk ke dalam folder dan tampilkan isi di dalamnya"""
    folder_items = project.repository_tree(path=path, ref=branch)
    
    print(f"\nMasuk ke dalam folder: {path}")
    for item in folder_items:
        print(f"{item['type']}: {item['path']}")
        
        # 🔥 Jika ada subfolder, masuk lagi ke dalamnya (rekursif)
        if item["type"] == "tree":
            list_folder_contents(item["path"])

        # 🔥 Jika file `.java`, ambil isi filenya
        elif item["type"] == "blob" and item["path"].endswith(".java"):
            file_content = project.files.get(file_path=item["path"], ref=branch)
            
            # 🔹 Decode isi file dari Base64
            decoded_content = base64.b64decode(file_content.content).decode("utf-8")

            print(f"\n📄 Isi File: {item['path']} 📄\n")
            print(decoded_content)
            print("\n" + "="*50 + "\n")  # Pemisah antar file

# 🔹 Mulai dari folder `src`
src_folder = next((item for item in items if item["type"] == "tree" and item["path"] == "src"), None)

if src_folder:
    list_folder_contents("src")  # 🔥 Panggil fungsi rekursif untuk masuk ke dalam src
else:
    print("\nFolder 'src' tidak ditemukan di dalam repository ini.")