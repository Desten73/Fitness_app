from typing import List
from models.exercise import Exercise
from database.db_interface import ClientDatabaseInterface

class ExerciseService:
    def __init__(self, db: ClientDatabaseInterface):
        self.db = db

    def get_all_exercises(self) -> List[Exercise]:
        data = self.db.get_all_exercises()
        exercises = [Exercise.from_dict(d) for d in data]
        return sorted(exercises, key=lambda x: x.name.lower())

    def add_exercise(self, exercise: Exercise) -> int:
        data = exercise.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        return self.db.add_exercise(data)

    def update_exercise(self, exercise: Exercise) -> None:
        if exercise.doc_id is None:
            raise ValueError("Cannot update exercise without doc_id")
        data = exercise.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        self.db.update_exercise(exercise.doc_id, data)

    def delete_exercise(self, doc_id: int) -> None:
        # First, we might want to remove this exercise from all programs
        # But per requirements: "Оно просто исчезнет" (It will just disappear)
        # We'll handle this in ProgramService or just let it be missing.
        # To be safe, we should probably update programs that use it.
        self.db.delete_exercise(doc_id)
