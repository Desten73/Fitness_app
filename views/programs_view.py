import flet as ft
from models.training_program import TrainingProgram

class ProgramsView:
    def __init__(self, page: ft.Page, program_service, client_service, exercise_service):
        self.page = page
        self.program_service = program_service
        self.client_service = client_service
        self.exercise_service = exercise_service
        self.programs_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def build(self) -> ft.View:
        add_btn = ft.ElevatedButton(
            "Добавить тренировочную программу",
            icon=ft.Icons.ADD,
            on_click=lambda _: self.show_program_dialog()
        )

        self.update_programs_list()

        return ft.View(
            route="/programs",
            controls=[
                ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                        ft.Text("Тренировочные программы", size=30, weight=ft.FontWeight.BOLD)]),
                add_btn,
                ft.Divider(height=1, color=ft.Colors.GREY_400),
                self.programs_list
            ],
            padding=20
        )

    def update_programs_list(self):
        programs = self.program_service.get_all_programs()
        clients = {c.doc_id: c for c in self.client_service.get_all_clients()}

        # Сортировка по клиентам, по алфавиту
        programs.sort(key=lambda p: (clients.get(p.client_id).name.lower() if p.client_id in clients else "", p.name.lower()))

        self.programs_list.controls = [
            ft.ListTile(
                title=ft.Text(f"{p.name}"),
                subtitle=ft.Text(f"Клиент: {clients.get(p.client_id).name if p.client_id in clients else 'Неизвестно'}"),
                trailing=ft.Row([
                    ft.IconButton(ft.Icons.EDIT, on_click=lambda _, prog=p: self.show_program_dialog(prog)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda _, prog=p: self.confirm_delete_program(prog))
                ], tight=True),
            ) for p in programs
        ]
        if self.page:
            self.page.update()

    def show_program_dialog(self, program: TrainingProgram = None):
        clients = [c for c in self.client_service.get_all_clients() if not c.is_archived]
        client_options = [ft.dropdown.Option(key=str(c.doc_id), text=c.name) for c in clients]
        client_dropdown = ft.Dropdown(label="Клиент", options=client_options, value=str(program.client_id) if program else None)
        name_field = ft.TextField(label="Название программы", value=program.name if program else "")

        exercises = self.exercise_service.get_all_exercises()
        ex_map = {ex.doc_id: ex.name for ex in exercises}

        selected_exercise_ids = program.exercise_ids.copy() if program else []
        exercises_col = ft.Column()

        def update_exercises_ui():
            exercises_col.controls = []
            for i, ex_id in enumerate(selected_exercise_ids):
                exercises_col.controls.append(
                    ft.Row([
                        ft.Text(ex_map.get(ex_id, "Удалено")),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda _, idx=i: remove_exercise(idx))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

            # Dropdown to select and add another exercise
            ex_options = [ft.dropdown.Option(key=str(ex.doc_id), text=ex.name) for ex in exercises]

            def on_ex_select(e):
                if e.control.value:
                    add_exercise(int(e.control.value))
                    e.control.value = None
                    e.control.update()

            add_ex_dropdown = ft.Dropdown(
                label="Добавить упражнение",
                options=ex_options,
                on_select=on_ex_select,
                width=300
            )
            exercises_col.controls.append(add_ex_dropdown)
            self.page.update()

        def add_exercise(ex_id):
            selected_exercise_ids.append(ex_id)
            update_exercises_ui()

        def remove_exercise(idx):
            selected_exercise_ids.pop(idx)
            update_exercises_ui()

        update_exercises_ui()

        def save_click(e):
            if not client_dropdown.value or not name_field.value:
                return

            if program:
                program.client_id = int(client_dropdown.value)
                program.name = name_field.value
                program.exercise_ids = selected_exercise_ids
                self.program_service.update_program(program)
            else:
                new_prog = TrainingProgram(
                    client_id=int(client_dropdown.value),
                    name=name_field.value,
                    exercise_ids=selected_exercise_ids
                )
                self.program_service.add_program(new_prog)

            self.page.pop_dialog()
            self.update_programs_list()

        dialog = ft.AlertDialog(
            title=ft.Text("Тренировочная программа"),
            content=ft.Column([
                client_dropdown,
                name_field,
                ft.Text("Упражнения:"),
                exercises_col
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton("Сохранить", on_click=save_click)
            ]
        )
        self.page.show_dialog(dialog)

    def confirm_delete_program(self, program: TrainingProgram):
        def delete_click(e):
            self.program_service.delete_program(program.doc_id)
            self.page.pop_dialog()
            self.update_programs_list()

        dialog = ft.AlertDialog(
            title=ft.Text("Удаление"),
            content=ft.Text(f"Вы уверены, что хотите удалить программу '{program.name}'?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton("Удалить", on_click=delete_click)
            ]
        )
        self.page.show_dialog(dialog)
