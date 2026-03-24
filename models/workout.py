from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional

@dataclass
class Workout:
    """Модель тренировки"""
    client_ids: List[int]
    date: date
    time: time
    price: int
    status: str  # Планируется, Подтверждена, Проведена, Отменена
    is_paid: bool = False
    doc_id: Optional[int] = None

    def to_dict(self) -> dict:
        data = {
            "client_ids": self.client_ids,
            "date": self.date.isoformat(),
            "time": self.time.isoformat(),
            "price": self.price,
            "status": self.status,
            "is_paid": self.is_paid
        }
        if self.doc_id is not None:
            data["doc_id"] = self.doc_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Workout":
        return cls(
            client_ids=data["client_ids"],
            date=date.fromisoformat(data["date"]),
            time=time.fromisoformat(data["time"]),
            price=data["price"],
            status=data["status"],
            is_paid=data.get("is_paid", False),
            doc_id=data.get("doc_id")
        )
