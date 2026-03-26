from typing import List, Optional
from models.training_program import TrainingProgram
from database.db_interface import ClientDatabaseInterface

class ProgramService:
    def __init__(self, db: ClientDatabaseInterface):
        self.db = db

    def get_all_programs(self) -> List[TrainingProgram]:
        data = self.db.get_all_programs()
        return [TrainingProgram.from_dict(d) for d in data]

    def get_client_programs(self, client_id: int) -> List[TrainingProgram]:
        all_programs = self.get_all_programs()
        return [p for p in all_programs if p.client_id == client_id]

    def add_program(self, program: TrainingProgram) -> int:
        data = program.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        return self.db.add_program(data)

    def update_program(self, program: TrainingProgram) -> None:
        if program.doc_id is None:
            raise ValueError("Cannot update program without doc_id")
        data = program.to_dict()
        if "doc_id" in data:
            del data["doc_id"]
        self.db.update_program(program.doc_id, data)

    def delete_program(self, doc_id: int) -> None:
        self.db.delete_program(doc_id)

    def get_program(self, doc_id: int) -> Optional[TrainingProgram]:
        all_programs = self.get_all_programs()
        for p in all_programs:
            if p.doc_id == doc_id:
                return p
        return None
