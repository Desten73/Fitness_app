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
                ft.Text("Фитнес-тренер", size=30, weight=ft.FontWeight.BOLD),
                ft.Text(current_date, size=20)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Разделяющая линия
        divider = ft.Divider(height=1, color=ft.Colors.GREY_400)

        # Список кнопок с иконками
        menu_buttons = [
            ("Тренировки", ft.Icons.FITNESS_CENTER, "/workouts"),
            ("Клиенты", ft.Icons.PEOPLE, "/clients"),
            ("Календарь тренировок", ft.Icons.CALENDAR_MONTH, "/calendar"),
            ("Статистика", ft.Icons.QUERY_STATS, "/statistics"),
            ("Упражнения", ft.Icons.LIST, "/exercises"),
            ("Тренировочная программа", ft.Icons.DASHBOARD, "/programs"),
        ]

        buttons_column = ft.Column(
            [
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Icon(icon),
                            ft.Text(text, size=18)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    on_click=lambda _, r=route: self.page.go(r),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    width=400,
                    height=60
                )
                for text, icon, route in menu_buttons
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        view = ft.View(
            route="/",
            controls=[
                header,
                divider,
                ft.Container(height=40),
                buttons_column,
            ],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.START
        )
        return view
