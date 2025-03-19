# File: dto/common_response_dto.py
from pydantic import BaseModel
from typing import Any, List

class CommonResponseDTO(BaseModel):
    message: str
    data: Any  # Bisa berupa list, dict, atau tipe data lain sesuai kebutuhan

    class Config:
        # Mengatur agar model ini dapat dikonversi menjadi dictionary dengan lebih mudah
        orm_mode = True
