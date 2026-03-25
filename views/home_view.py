import flet as ft
from datetime import datetime

class HomeView:
    def __init__(self, page: ft.Page, client_service, workout_service):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service

    def build(self) -> ft.View:
        # Ищем существующий Share или создаем новый, чтобы избежать дублирования в overlay
        share = next((c for c in self.page.overlay if isinstance(c, ft.Share)), None)
        if not share:
            share = ft.Share()
            self.page.overlay.append(share)

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
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        async def export_db(e):
            try:
                await share.share_files([ft.ShareFile.from_path("fitness_trainer.json")])
                self.page.open(ft.SnackBar(ft.Text("База данных готова к отправке")))
            except Exception as ex:
                self.page.open(ft.SnackBar(ft.Text(f"Ошибка при выгрузке: {str(ex)}")))

        export_button = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FILE_DOWNLOAD),
                    ft.Text("Выгрузить БД", size=18)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            on_click=export_db,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            width=400,
            height=60
        )

        view = ft.View(
            route="/",
            controls=[
                header,
                divider,
                ft.Column(
                    [
                        ft.Container(height=20),
                        buttons_column,
                        ft.Container(expand=True),
                        export_button,
                    ],
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.START
        )
        return view
