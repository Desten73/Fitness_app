import flet as ft
from models.exercise import Exercise

class ExercisesView:
    def __init__(self, page: ft.Page, exercise_service):
        self.page = page
        self.exercise_service = exercise_service
        self.exercises_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def build(self) -> ft.View:
        add_btn = ft.ElevatedButton(
            "Добавить упражнение",
            icon=ft.Icons.ADD,
            on_click=lambda _: self.show_exercise_dialog()
        )

        self.update_exercises_list()

        return ft.View(
            route="/exercises",
            controls=[
                ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                        ft.Text("Упражнения", size=30, weight=ft.FontWeight.BOLD)]),
                add_btn,
                ft.Divider(height=1, color=ft.Colors.GREY_400),
                self.exercises_list
            ],
            padding=20
        )

    def update_exercises_list(self):
        exercises = self.exercise_service.get_all_exercises()
        self.exercises_list.controls = [
            ft.ListTile(
                title=ft.Text(ex.name),
                trailing=ft.Row([
                    ft.IconButton(ft.Icons.EDIT, on_click=lambda _, e=ex: self.show_exercise_dialog(e)),
                    ft.IconButton(ft.Icons.DELETE, on_click=lambda _, e=ex: self.confirm_delete_exercise(e))
                ], tight=True),
            ) for ex in exercises
        ]
        if self.page:
            self.page.update()

    def show_exercise_dialog(self, exercise: Exercise = None):
        name_field = ft.TextField(label="Наименование упражнения", value=exercise.name if exercise else "")

        def save_click(e):
            if not name_field.value:
                return
            if exercise:
                exercise.name = name_field.value
                self.exercise_service.update_exercise(exercise)
            else:
                self.exercise_service.add_exercise(Exercise(name=name_field.value))
            self.page.pop_dialog()
            self.update_exercises_list()

        dialog = ft.AlertDialog(
            title=ft.Text("Упражнение"),
            content=name_field,
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton("Сохранить", on_click=save_click)
            ]
        )
        self.page.show_dialog(dialog)

    def confirm_delete_exercise(self, exercise: Exercise):
        def delete_click(e):
            self.exercise_service.delete_exercise(exercise.doc_id)
            self.page.pop_dialog()
            self.update_exercises_list()

        dialog = ft.AlertDialog(
            title=ft.Text("Удаление"),
            content=ft.Text(f"Вы уверены, что хотите удалить '{exercise.name}'?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog()),
                ft.TextButton("Удалить", on_click=delete_click)
            ]
        )
        self.page.show_dialog(dialog)
