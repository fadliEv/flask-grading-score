class GradingResult:
    def __init__(self, question: str, result: str, reason: str):
        """
        - question: Soal yang diajukan.
        - result: Hasil grading (lulus/gagal).
        - reason: Penjelasan kenapa lulus/gagal (error atau logika).
        """
        self.question = question
        self.result = result
        self.reason = reason


class GradingResponse:
    def __init__(self, grade: float, details: list):
        """
        - grade: Nilai akhir dari analisis (0-100).
        - details: List GradingResult untuk setiap soal.
        """
        self.grade = grade
        self.details = details
