from abc import ABC, abstractmethod
from typing import List, Optional

class ClientDatabaseInterface(ABC):
    """Интерфейс для работы с хранилищем клиентов"""

    @abstractmethod
    def get_all_clients(self) -> List[dict]:
        """Возвращает список всех клиентов (словари)"""
        pass

    @abstractmethod
    def get_client(self, doc_id: int) -> Optional[dict]:
        """Возвращает одного клиента по ID"""
        pass

    @abstractmethod
    def add_client(self, client_data: dict) -> int:
        """Добавляет клиента, возвращает ID"""
        pass

    @abstractmethod
    def update_client(self, doc_id: int, client_data: dict) -> None:
        """Обновляет данные клиента"""
        pass

    @abstractmethod
    def delete_client(self, doc_id: int) -> None:
        """Удаляет клиента"""
        pass

    @abstractmethod
    def get_all_workouts(self) -> List[dict]:
        """Возвращает список всех тренировок"""
        pass

    @abstractmethod
    def add_workout(self, workout_data: dict) -> int:
        """Добавляет тренировку"""
        pass
