from tinydb import TinyDB, Query
from .db_interface import ClientDatabaseInterface
from typing import List, Optional

class TinyDBClient(ClientDatabaseInterface):
    def __init__(self, db_path: str = "clients_db.json"):
        self.db = TinyDB(db_path)
        self.clients_table = self.db.table("clients")
        self.query = Query()

    def get_all_clients(self) -> List[dict]:
        return self.clients_table.all()

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