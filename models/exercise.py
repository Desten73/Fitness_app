from dataclasses import dataclass
from typing import Optional

@dataclass
class Exercise:
    """Модель упражнения"""
    name: str
    doc_id: Optional[int] = None

    def to_dict(self) -> dict:
        data = {"name": self.name}
        if self.doc_id is not None:
            data["doc_id"] = self.doc_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Exercise":
        return cls(
            name=data["name"],
            doc_id=data.get("doc_id")
        )
