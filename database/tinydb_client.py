from tinydb import TinyDB, Query
from .db_interface import ClientDatabaseInterface
from typing import List, Optional

class TinyDBClient(ClientDatabaseInterface):
    def __init__(self, db_path: str = "fitness_trainer.json"):
        self.db = TinyDB(db_path)
        self.clients_table = self.db.table("clients")
        self.workouts_table = self.db.table("workouts")
        self.query = Query()

    def get_all_clients(self) -> List[dict]:
        clients = self.clients_table.all()
        for client in clients:
            client["doc_id"] = client.doc_id
        return clients

    def get_client(self, doc_id: int) -> Optional[dict]:
        result = self.clients_table.get(doc_id=doc_id)
        if result:
            result["doc_id"] = doc_id
        return result

    def add_client(self, client_data: dict) -> int:
        return self.clients_table.insert(client_data)

    def update_client(self, doc_id: int, client_data: dict) -> None:
        self.clients_table.update(client_data, doc_id=doc_id)

    def delete_client(self, doc_id: int) -> None:
        self.clients_table.remove(doc_id=doc_id)

    def get_all_workouts(self) -> List[dict]:
        workouts = self.workouts_table.all()
        for workout in workouts:
            workout["doc_id"] = workout.doc_id
        return workouts

    def add_workout(self, workout_data: dict) -> int:
        return self.workouts_table.insert(workout_data)
