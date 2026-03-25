from typing import List, Dict
from models.client import Client, WorkoutPackage
from models.workout import Workout
from database.db_interface import ClientDatabaseInterface

class ClientService:
    def __init__(self, db: ClientDatabaseInterface):
        self.db = db

    def get_all_clients(self) -> List[Client]:
        """Получить всех клиентов в виде объектов Client (отсортированы по алфавиту)"""
        clients_data = self.db.get_all_clients()
        clients = [Client.from_dict(c) for c in clients_data]
        clients.sort(key=lambda c: c.name.lower())
        return clients

    def get_client(self, doc_id: int) -> Client | None:
        data = self.db.get_client(doc_id)
        if data:
            return Client.from_dict(data)
        return None

    def add_client(self, client: Client) -> int:
        """Добавляет клиента, возвращает его ID"""
        data = client.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        return self.db.add_client(data)

    def update_client(self, client: Client) -> None:
        """Обновляет существующего клиента"""
        if client.doc_id is None:
            raise ValueError("Cannot update client without doc_id")
        data = client.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        self.db.update_client(client.doc_id, data)

    def delete_client(self, doc_id: int) -> None:
        self.db.delete_client(doc_id)

    def search_clients(self, query: str) -> List[Client]:
        """Простой поиск по имени или телефону"""
        all_clients = self.get_all_clients()
        query_lower = query.lower()
        return [
            c for c in all_clients
            if query_lower in c.name.lower() or query_lower in c.phone
        ]

    def archive_client(self, doc_id: int) -> None:
        client = self.get_client(doc_id)
        if client:
            client.is_archived = True
            self.update_client(client)

    def unarchive_client(self, doc_id: int) -> None:
        client = self.get_client(doc_id)
        if client:
            client.is_archived = False
            self.update_client(client)

    def calculate_remaining_workouts(self, client: Client, client_workouts: List[Workout]) -> Dict[int, int]:
        """
        Рассчитывает количество оставшихся тренировок для каждого пакета клиента.
        Возвращает словарь {индекс_пакета: остаток}.
        """
        # Сортируем пакеты по дате покупки (старые первыми)
        packages_with_indices = sorted(
            enumerate(client.packages),
            key=lambda x: x[1].purchase_date
        )

        # Берем только завершенные тренировки клиента
        completed_workouts = [w for w in client_workouts if w.is_paid]
        # completed_workouts = [w for w in client_workouts if w.is_paid and w.status in ["завершено", "Проведена"]]
        # Сортируем тренировки по дате и времени (старые первыми)
        completed_workouts.sort(key=lambda w: (w.date, w.time))

        remaining = {i: p.total_workouts for i, p in enumerate(client.packages)}

        for workout in completed_workouts:
            # Находим самый старый пакет, купленный до или в день тренировки, в котором еще есть тренировки
            for idx, package in packages_with_indices:
                if package.purchase_date <= workout.date and remaining[idx] > 0:
                    remaining[idx] -= 1
                    break

        return remaining

    def get_total_remaining_workouts(self, client: Client, client_workouts: List[Workout]) -> int:
        """Возвращает общее количество оставшихся тренировок по всем пакетам"""
        remaining = self.calculate_remaining_workouts(client, client_workouts)
        return sum(remaining.values())
