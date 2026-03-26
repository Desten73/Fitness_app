import flet as ft
from database.tinydb_client import TinyDBClient
from business_logic.client_service import ClientService
from business_logic.workout_service import WorkoutService
from views.home_view import HomeView


def main(page: ft.Page):
    # Настройки страницы
    page.title = "Фитнес-тренер"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Инициализация базы данных и сервисов
    db = TinyDBClient("fitness_trainer.json")
    client_service = ClientService(db)
    workout_service = WorkoutService(db)

    def on_route_change(e):
        page.views.clear()
        # Основной вид всегда внизу стека
        page.views.append(HomeView(page, client_service, workout_service).build())

        if page.route == "/workouts":
            from views.workouts_view import WorkoutsView
            page.views.append(WorkoutsView(page, workout_service, client_service).build())
        elif page.route == "/clients":
            from views.clients_view import ClientsView
            page.views.append(ClientsView(page, client_service, workout_service).build())
        elif page.route == "/calendar":
            from views.calendar_view import CalendarView
            page.views.append(CalendarView(page, client_service, workout_service).build())
        elif page.route == "/statistics":
            from views.statistics_view import StatisticsView
            page.views.append(StatisticsView(page, client_service, workout_service).build())
        elif page.route == "/add_client":
            from views.add_client import AddClientView
            page.views.append(AddClientView(page, client_service).build())
        elif page.route.startswith("/client_details/"):
            from views.client_details import ClientDetailsView
            client_id = int(page.route.split("/")[-1])
            page.views.append(ClientDetailsView(page, client_service, workout_service, client_id).build())

        page.update()

    def on_view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop

    # Инициализируем маршрут
    page.on_route_change(None)


if __name__ == "__main__":
    ft.app(target=main)
