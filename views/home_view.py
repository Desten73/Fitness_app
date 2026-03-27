import flet as ft
from datetime import datetime
import shutil
import os

class HomeView:
    def __init__(self, page: ft.Page, client_service, workout_service):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service
        self.file_picker = ft.FilePicker()

    def on_download_click(self, e):
        now = datetime.now()
        filename = f"fitness_trainer_{now.strftime('%d-%m-%Y')}.json"
        db_path = "fitness_trainer.json"

        if not os.path.exists(db_path):
            with open(db_path, "w") as f:
                f.write("{}")

        with open(db_path, "rb") as f:
            db_bytes = f.read()

        async def save_file_async():
            if self.page.web or (self.page.platform and self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]):
                await self.file_picker.save_file(file_name=filename, src_bytes=db_bytes)
            else:
                path = await self.file_picker.save_file(file_name=filename)
                if path:
                    shutil.copyfile(db_path, path)

        self.page.run_task(save_file_async)

    def build(self) -> ft.View:
        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)

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
            ("Тренировочная программа", ft.Icons.DASHBOARD, "/programs"),
            ("Упражнения", ft.Icons.LIST, "/exercises"),
        ]

        buttons_column = ft.Column(
            [
                *[
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
                ft.Button(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.DOWNLOAD),
                            ft.Text("Скачать базу данных", size=18)
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    on_click=self.on_download_click,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    width=400,
                    height=60
                )
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
