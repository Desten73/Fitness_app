import flet as ft
import shutil
import os
from datetime import datetime

class HomeView:
    def __init__(self, page: ft.Page, client_service, workout_service):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service

    def build(self) -> ft.View:
        # Ищем существующий FilePicker или создаем новый
        file_picker = next((c for c in self.page.overlay if isinstance(c, ft.FilePicker)), None)
        if not file_picker:
            file_picker = ft.FilePicker()
            self.page.overlay.append(file_picker)

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
            suggested_name = f"fitness_trainer_{now.strftime('%Y-%m-%d')}.json"
            try:
                # В данной версии flet save_file возвращает путь или None
                save_path = await file_picker.save_file(
                    file_name=suggested_name,
                    allowed_extensions=["json"]
                )
                if save_path:
                    shutil.copy("fitness_trainer.json", save_path)
                    self.page.open(ft.SnackBar(ft.Text(f"Файл сохранен: {os.path.basename(save_path)}")))
            except Exception as ex:
                self.page.open(ft.SnackBar(ft.Text(f"Ошибка при сохранении: {str(ex)}")))

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
