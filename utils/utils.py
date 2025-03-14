from urllib.parse import urlparse

def extract_gitlab_namespace(repository_url: str) -> str:
    """
    Mengambil namespace proyek GitLab dari full URL.
    
    Contoh:
    Input: "https://git.enigmacamp.com/enigma-camp/enigmacamp-2.0/batch-38-react-native/trainer/js-solve-problems"
    Output: "enigma-camp/enigmacamp-2.0/batch-38-react-native/trainer/js-solve-problems"
    """
    parsed_url = urlparse(str(repository_url))  # Pastikan repository_url adalah string

    # Pastikan domain benar (opsional, agar lebih ketat)
    if "git.enigmacamp.com" not in parsed_url.netloc:
        raise ValueError("URL bukan dari GitLab Enigmacamp")

    # Ambil path tanpa leading slash
    namespace = parsed_url.path.lstrip("/")
    
    return namespace
