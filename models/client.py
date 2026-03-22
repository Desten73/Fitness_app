from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Client:
    """Модель клиента фитнес-тренера"""
    name: str
    phone: str
    email: str = ""
    birth_date: Optional[date] = None
    goals: list[str] = None  # цели: похудение, набор массы и т.п.
    notes: str = ""
    doc_id: Optional[int] = None  # ID в TinyDB, будет назначаться при сохранении

    def __post_init__(self):
        if self.goals is None:
            self.goals = []

    def to_dict(self) -> dict:
        """Преобразование в словарь для сохранения в БД"""
        data = {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "goals": self.goals,
            "notes": self.notes
        }
        if self.doc_id is not None:
            data["doc_id"] = self.doc_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Client":
        """Создание объекта из данных БД"""
        birth = date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None
        return cls(
            name=data["name"],
            phone=data["phone"],
            email=data.get("email", ""),
            birth_date=birth,
            goals=data.get("goals", []),
            notes=data.get("notes", ""),
            doc_id=data.get("doc_id")
        )