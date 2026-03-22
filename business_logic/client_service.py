from typing import List
from models.client import Client
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
