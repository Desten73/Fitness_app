import flet as ft

class StatisticsView:
    def __init__(self, page: ft.Page, client_service, workout_service):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service

    def build(self) -> ft.View:
        return ft.View(
            "/statistics",
            [
                ft.AppBar(title=ft.Text("Статистика"), bgcolor=ft.colors.SURFACE_VARIANT),
                ft.Text("Статистика о количестве заработанных денег, количестве тренировок, клиентах и посещаемости.", size=20),
                ft.Text("Скоро в приложении!", size=14, color=ft.colors.GREY_600),
                ft.ElevatedButton("Назад", on_click=lambda _: self.page.views.pop() or self.page.update())
            ],
            padding=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
