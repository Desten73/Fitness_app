from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class WorkoutPackage:
    """Модель пакета тренировок"""
    purchase_date: date
    total_workouts: int
    price: int

    def to_dict(self) -> dict:
        return {
            "purchase_date": self.purchase_date.isoformat(),
            "total_workouts": self.total_workouts,
            "price": self.price
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkoutPackage":
        return cls(
            purchase_date=date.fromisoformat(data["purchase_date"]),
            total_workouts=data["total_workouts"],
            price=data["price"]
        )

@dataclass
class Client:
    """Модель клиента фитнес-тренера"""
    name: str
    phone: str
    birth_date: Optional[date] = None
    start_date: Optional[date] = None
    workout_price: int = 1000
    is_archived: bool = False
    goals: list[str] = None  # цели: похудение, набор массы и т.п.
    notes: str = ""
    packages: list[WorkoutPackage] = None
    doc_id: Optional[int] = None  # ID в TinyDB, будет назначаться при сохранении

    def __post_init__(self):
        if self.goals is None:
            self.goals = []
        if self.packages is None:
            self.packages = []
        if self.start_date is None:
            self.start_date = date.today()

    def to_dict(self) -> dict:
        """Преобразование в словарь для сохранения в БД"""
        data = {
            "name": self.name,
            "phone": self.phone,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "workout_price": self.workout_price,
            "is_archived": self.is_archived,
            "goals": self.goals,
            "notes": self.notes,
            "packages": [p.to_dict() for p in self.packages]
        }
        if self.doc_id is not None:
            data["doc_id"] = self.doc_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Client":
        """Создание объекта из данных БД"""
        birth = date.fromisoformat(data["birth_date"]) if data.get("birth_date") else None
        start = date.fromisoformat(data["start_date"]) if data.get("start_date") else None
        packages = [WorkoutPackage.from_dict(p) for p in data.get("packages", [])]
        return cls(
            name=data["name"],
            phone=data["phone"],
            birth_date=birth,
            start_date=start,
            workout_price=data.get("workout_price", 1000),
            is_archived=data.get("is_archived", False),
            goals=data.get("goals", []),
            notes=data.get("notes", ""),
            packages=packages,
            doc_id=data.get("doc_id")
        )
