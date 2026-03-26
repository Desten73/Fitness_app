from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TrainingProgram:
    """Модель тренировочной программы"""
    client_id: int
    name: str
    exercise_ids: List[int]
    doc_id: Optional[int] = None

    def to_dict(self) -> dict:
        data = {
            "client_id": self.client_id,
            "name": self.name,
            "exercise_ids": self.exercise_ids
        }
        if self.doc_id is not None:
            data["doc_id"] = self.doc_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "TrainingProgram":
        return cls(
            client_id=data["client_id"],
            name=data["name"],
            exercise_ids=data.get("exercise_ids", []),
            doc_id=data.get("doc_id")
        )
