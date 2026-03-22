import flet as ft
from database.tinydb_client import TinyDBClient
from business_logic.client_service import ClientService
from business_logic.workout_service import WorkoutService
from views.home_view import HomeView


def main(page: ft.Page):
    # Настройки страницы
    page.title = "Fitness Trainer"
    # page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Инициализация базы данных и сервисов
    db = TinyDBClient("fitness_trainer.json")
    client_service = ClientService(db)
    workout_service = WorkoutService(db)

    def on_route_change(route):
        pass

    def on_view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop

    # Создаём начальный экран
    home_view = HomeView(page, client_service, workout_service)
    page.views.append(home_view.build())
    page.update()


if __name__ == "__main__":
    ft.run(main)
