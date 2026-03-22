import flet as ft
from datetime import datetime

class HomeView:
    def __init__(self, page: ft.Page, client_service, workout_service):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service

    def build(self) -> ft.View:
        now = datetime.now()
        current_date = now.strftime("%d.%m")

        # Название приложения и текущая дата
        header = ft.Row(
            [
                ft.Text("Fitness Trainer", size=30, weight=ft.FontWeight.BOLD),
                ft.Text(current_date, size=20)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Разделяющая линия
        divider = ft.Divider(height=1, color=ft.colors.GREY_400)

        # Список кнопок с иконками
        menu_buttons = [
            ("Тренировки", ft.icons.FITNESS_CENTER, self.open_workouts),
            ("Клиенты", ft.icons.PEOPLE, self.open_clients),
            ("Календарь тренировок", ft.icons.CALENDAR_MONTH, self.open_calendar),
            ("Статистика", ft.icons.QUERY_STATS, self.open_statistics),
        ]

        buttons_column = ft.Column(
            [
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(icon),
                            ft.Text(text, size=18)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    on_click=on_click,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    width=400,
                    height=60
                )
                for text, icon, on_click in menu_buttons
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        view = ft.View(
            "/",
            [
                header,
                divider,
                ft.Container(height=40),
                buttons_column,
            ],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.START
        )
        return view

    def open_workouts(self, e):
        from views.workouts_view import WorkoutsView
        self.page.views.append(WorkoutsView(self.page, self.workout_service, self.client_service).build())
        self.page.update()

    def open_clients(self, e):
        from views.clients_view import ClientsView
        self.page.views.append(ClientsView(self.page, self.client_service).build())
        self.page.update()

    def open_calendar(self, e):
        from views.calendar_view import CalendarView
        self.page.views.append(CalendarView(self.page).build())
        self.page.update()

    def open_statistics(self, e):
        from views.statistics_view import StatisticsView
        self.page.views.append(StatisticsView(self.page, self.client_service, self.workout_service).build())
        self.page.update()
