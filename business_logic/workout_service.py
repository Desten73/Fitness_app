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

    def update_workout(self, workout: Workout) -> None:
        if workout.doc_id is None:
            raise ValueError("Cannot update workout without doc_id")
        data = workout.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        self.db.update_workout(workout.doc_id, data)

    def delete_workout(self, doc_id: int) -> None:
        self.db.delete_workout(doc_id)

    def get_workout(self, doc_id: int) -> Workout | None:
        # Note: we might need to add get_workout to DB interface if we want efficiency,
        # but for now we can filter get_all_workouts or just trust get_all if it's small.
        # However, it's better to add it to DB interface.
        # Let's assume we can use get_all_workouts for now or add it later.
        workouts = self.get_all_workouts()
        for w in workouts:
            if w.doc_id == doc_id:
                return w
        return None

    def get_sorted_workouts_v2(self, query: str = None, clients_map: dict = None) -> dict:
        """
        Возвращает отсортированные группы тренировок.
        Если задан query, возвращает плоский список всех совпадений.
        """
        all_workouts = self.get_all_workouts()
        today = datetime.now().date()

        if query:
            query = query.lower()
            filtered = []
            for w in all_workouts:
                client_names = [clients_map.get(cid, "").lower() for cid in w.client_ids] if clients_map else []
                client_match = any(query in name for name in client_names)
                status_match = query in w.status.lower()
                date_match = query in w.date.strftime("%d.%m.%Y")
                payment_match = False
                if query in "оплачено":
                    payment_match = w.is_paid
                elif query in "не оплачено":
                    payment_match = not w.is_paid

                if client_match or status_match or date_match or payment_match:
                    filtered.append(w)

            # Сортировка для поиска: от новых к старым
            filtered.sort(key=lambda w: (w.date, w.time), reverse=True)
            return {"search_results": filtered}

        today_workouts = [w for w in all_workouts if w.date == today
                          and w.status != "Проведена" and w.status != "Отменена"]
        future_workouts = [w for w in all_workouts if w.date > today]
        past_workouts = [w for w in all_workouts if w.date < today or
                         (w.date == today and (w.status == "Проведена" or w.status == "Отменена"))]

        # Сегодняшние: от меньшего времени к большему
        today_workouts.sort(key=lambda w: w.time)

        # Будущие: от меньшей даты и времени к большей
        future_workouts.sort(key=lambda w: (w.date, w.time))

        # Прошедшие:
        # Сначала неоплаченные (красные), от большей даты к меньшей
        # Затем оплаченные (серые), от большей даты к меньшей (лимит 10)
        past_unpaid = [w for w in past_workouts if not w.is_paid and w.status == "Проведена"]
        past_paid = [w for w in past_workouts if w.is_paid or w.status != "Проведена"]

        past_unpaid.sort(key=lambda w: (w.date, w.time), reverse=True)
        past_paid.sort(key=lambda w: (w.date, w.time), reverse=True)

        return {
            "today": today_workouts,
            "future": future_workouts,
            "past_unpaid": past_unpaid,
            "past_paid": past_paid[:10]
        }

    def get_client_workouts(self, client_id: int) -> List[Workout]:
        """Возвращает все тренировки конкретного клиента"""
        all_workouts = self.get_all_workouts()
        return [w for w in all_workouts if client_id in w.client_ids]

    def get_last_workout_with_program(self, client_id: int, program_id: int) -> Workout | None:
        """Возвращает последнюю проведенную тренировку клиента с данной программой"""
        client_workouts = self.get_client_workouts(client_id)
        # Фильтруем по программе и статусу "Проведена" (или просто по программе, если нужно из любой последней)
        # По требованию: "из последней тренировки клиента с такой тренировочной программой"
        program_workouts = [w for w in client_workouts if w.program_id == program_id]
        if not program_workouts:
            return None

        # Сортируем по дате и времени в порядке убывания
        program_workouts.sort(key=lambda w: (w.date, w.time), reverse=True)
        return program_workouts[0]
