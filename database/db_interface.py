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

    @abstractmethod
    def update_workout(self, doc_id: int, workout_data: dict) -> None:
        """Обновляет тренировку"""
        pass

    @abstractmethod
    def delete_workout(self, doc_id: int) -> None:
        """Удаляет тренировку"""
        pass

    @abstractmethod
    def get_all_exercises(self) -> List[dict]:
        """Возвращает список всех упражнений"""
        pass

    @abstractmethod
    def add_exercise(self, exercise_data: dict) -> int:
        """Добавляет упражнение"""
        pass

    @abstractmethod
    def update_exercise(self, doc_id: int, exercise_data: dict) -> None:
        """Обновляет упражнение"""
        pass

    @abstractmethod
    def delete_exercise(self, doc_id: int) -> None:
        """Удаляет упражнение"""
        pass

    @abstractmethod
    def get_all_programs(self) -> List[dict]:
        """Возвращает список всех тренировочных программ"""
        pass

    @abstractmethod
    def add_program(self, program_data: dict) -> int:
        """Добавляет тренировочную программу"""
        pass

    @abstractmethod
    def update_program(self, doc_id: int, program_data: dict) -> None:
        """Обновляет тренировочную программу"""
        pass

    @abstractmethod
    def delete_program(self, doc_id: int) -> None:
        """Удаляет тренировочную программу"""
        pass
