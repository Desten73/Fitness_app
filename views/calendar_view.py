import flet as ft

class CalendarView:
    def __init__(self, page: ft.Page):
        self.page = page

    def build(self) -> ft.View:
        return ft.View(
            "/calendar",
            [
                ft.AppBar(title=ft.Text("Календарь тренировок"), bgcolor=ft.colors.SURFACE_VARIANT),
                ft.Text("Календарь тренировок за месяц в удобном виде.", size=20),
                ft.Text("Скоро в приложении!", size=14, color=ft.colors.GREY_600),
                ft.ElevatedButton("Назад", on_click=lambda _: self.page.views.pop() or self.page.update())
            ],
            padding=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
