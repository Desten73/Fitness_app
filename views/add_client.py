import flet as ft
from models.client import Client
from business_logic.client_service import ClientService

class AddClientView:
    def __init__(self, page: ft.Page, client_service: ClientService):
        self.page = page
        self.client_service = client_service
        self.name_field = ft.TextField(label="Имя", autofocus=True)
        self.phone_field = ft.TextField(label="Телефон")
        self.email_field = ft.TextField(label="Email")
        self.goals_field = ft.TextField(label="Цели (через запятую)")
        self.notes_field = ft.TextField(label="Заметки", multiline=True)

    def build(self) -> ft.View:
        return ft.View(
            "/add_client",
            [
                ft.AppBar(title=ft.Text("Добавить клиента"), bgcolor=ft.colors.SURFACE_VARIANT),
                self.name_field,
                self.phone_field,
                self.email_field,
                self.goals_field,
                self.notes_field,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=self.save_client),
                        ft.TextButton("Отмена", on_click=self.cancel)
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.START
        )

    def save_client(self, e):
        # Валидация
        if not self.name_field.value or not self.phone_field.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Имя и телефон обязательны"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        goals = [g.strip() for g in self.goals_field.value.split(",")] if self.goals_field.value else []

        client = Client(
            name=self.name_field.value,
            phone=self.phone_field.value,
            email=self.email_field.value or "",
            goals=goals,
            notes=self.notes_field.value or ""
        )
        self.client_service.add_client(client)
        self.page.views.pop()  # возвращаемся на главный экран
        self.page.snack_bar = ft.SnackBar(ft.Text("Клиент добавлен"))
        self.page.snack_bar.open = True
        self.page.update()

    def cancel(self, e):
        self.page.views.pop()
        self.page.update()