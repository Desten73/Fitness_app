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
    status: str  # завершено, отменено, планируется, подтверждено
    doc_id: Optional[int] = None

    def to_dict(self) -> dict:
        data = {
            "client_ids": self.client_ids,
            "date": self.date.isoformat(),
            "time": self.time.isoformat(),
            "price": self.price,
            "status": self.status
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
            doc_id=data.get("doc_id")
        )
