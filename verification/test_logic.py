import flet as ft
from database.tinydb_client import TinyDBClient
from business_logic.client_service import ClientService
from business_logic.workout_service import WorkoutService
from business_logic.exercise_service import ExerciseService
from business_logic.program_service import ProgramService
from models.exercise import Exercise
from models.training_program import TrainingProgram
from models.client import Client
import os

def test_logic():
    db_path = "test_fitness.json"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = TinyDBClient(db_path)
    client_service = ClientService(db)
    workout_service = WorkoutService(db)
    exercise_service = ExerciseService(db)
    program_service = ProgramService(db)

    # 1. Test Exercise
    ex = Exercise(name="Test Exercise")
    ex_id = exercise_service.add_exercise(ex)
    exercises = exercise_service.get_all_exercises()
    assert len(exercises) == 1
    assert exercises[0].name == "Test Exercise"
    assert exercises[0].doc_id == ex_id

    # 2. Test Client
    client = Client(name="Test Client", phone="123")
    client_id = client_service.add_client(client)

    # 3. Test Program
    prog = TrainingProgram(client_id=client_id, name="Test Program", exercise_ids=[ex_id])
    prog_id = program_service.add_program(prog)
    programs = program_service.get_client_programs(client_id)
    assert len(programs) == 1
    assert programs[0].name == "Test Program"
    assert programs[0].exercise_ids == [ex_id]

    print("Logic tests passed!")
    os.remove(db_path)

if __name__ == "__main__":
    test_logic()
