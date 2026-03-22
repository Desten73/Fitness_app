from typing import List
from datetime import datetime, timedelta
from models.workout import Workout
from database.db_interface import ClientDatabaseInterface

class WorkoutService:
    def __init__(self, db: ClientDatabaseInterface):
        self.db = db

    def get_all_workouts(self) -> List[Workout]:
        workouts_data = self.db.get_all_workouts()
        return [Workout.from_dict(w) for w in workouts_data]

    def add_workout(self, workout: Workout) -> int:
        data = workout.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        return self.db.add_workout(data)

    def get_sorted_workouts(self) -> List[Workout]:
        """
        Возвращает отсортированный список тренировок:
        1. Сначала Планируется/Подтверждена (сначала ближайшие)
        2. Затем остальные (Проведена/Отменена) за последние 30 дней (сначала новые)
        """
        all_workouts = self.get_all_workouts()
        now = datetime.now()
        thirty_days_ago = (now - timedelta(days=30)).date()

        upcoming = [w for w in all_workouts if w.status in ["планируется", "подтверждено"]]
        others = [w for w in all_workouts if w.status in ["завершено", "отменено"] and w.date >= thirty_days_ago]

        # Сортировка предстоящих: по дате и времени (по возрастанию)
        upcoming.sort(key=lambda w: (w.date, w.time))

        # Сортировка прошедших: по дате и времени (по убыванию)
        others.sort(key=lambda w: (w.date, w.time), reverse=True)

        return upcoming + others
