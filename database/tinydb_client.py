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
        result = []
        for client in clients:
            client_dict = dict(client)
            client_dict["doc_id"] = client.doc_id
            result.append(client_dict)
        return result

    def get_client(self, doc_id: int) -> Optional[dict]:
        client = self.clients_table.get(doc_id=doc_id)
        if client:
            client_dict = dict(client)
            client_dict["doc_id"] = client.doc_id
            return client_dict
        return None

    def add_client(self, client_data: dict) -> int:
        return self.clients_table.insert(client_data)

    def update_client(self, doc_id: int, client_data: dict) -> None:
        self.clients_table.update(client_data, doc_ids=[doc_id])

    def delete_client(self, doc_id: int) -> None:
        self.clients_table.remove(doc_ids=[doc_id])

    def get_all_workouts(self) -> List[dict]:
        workouts = self.workouts_table.all()
        result = []
        for workout in workouts:
            w_dict = dict(workout)
            w_dict["doc_id"] = workout.doc_id
            result.append(w_dict)
        return result

    def add_workout(self, workout_data: dict) -> int:
        return self.workouts_table.insert(workout_data)

    def update_workout(self, doc_id: int, workout_data: dict) -> None:
        self.workouts_table.update(workout_data, doc_ids=[doc_id])

    def delete_workout(self, doc_id: int) -> None:
        self.workouts_table.remove(doc_ids=[doc_id])
