import flet as ft
from business_logic.workout_service import WorkoutService

class WorkoutsView:
    def __init__(self, page: ft.Page, workout_service: WorkoutService, client_service):
        self.page = page
        self.workout_service = workout_service
        self.client_service = client_service
        self.workouts_list = ft.ListView(expand=1, spacing=10, padding=10)

    def build(self) -> ft.View:
        add_button = ft.ElevatedButton(
            "Добавить тренировку",
            icon=ft.icons.ADD,
            on_click=self.add_workout_click
        )

        view = ft.View(
            "/workouts",
            [
                ft.AppBar(title=ft.Text("Тренировки"), bgcolor=ft.colors.SURFACE_VARIANT),
                ft.Row([add_button], alignment=ft.MainAxisAlignment.CENTER),
                self.workouts_list,
            ],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.START
        )
        self.refresh_list()
        return view

    def refresh_list(self):
        self.workouts_list.controls.clear()
        workouts = self.workout_service.get_sorted_workouts()
        clients = self.client_service.get_all_clients()
        client_map = {c.doc_id: c.name for c in clients}

        for w in workouts:
            client_names = [client_map.get(cid, "Неизвестный") for cid in w.client_ids]
            client_names_str = ", ".join(client_names)

            # Color coding
            color = None
            if w.status == "завершено":
                color = ft.colors.GREEN_100
            elif w.status == "отменено":
                color = ft.colors.GREY_300

            self.workouts_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.FITNESS_CENTER),
                                    title=ft.Text(f"{w.date.strftime('%d.%m.%Y')} {w.time.strftime('%H:%M')}"),
                                    subtitle=ft.Text(f"Клиенты: {client_names_str}\nЦена: {w.price} руб.\nСтатус: {w.status}"),
                                ),
                            ],
                            spacing=0,
                        ),
                        padding=5,
                        bgcolor=color
                    )
                )
            )
        self.page.update()

    def add_workout_click(self, e):
        from views.add_workout import AddWorkoutView
        self.page.views.append(AddWorkoutView(self.page, self.client_service, self.workout_service).build())
        self.page.update()
