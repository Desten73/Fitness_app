import flet as ft
from business_logic.client_service import ClientService
from business_logic.workout_service import WorkoutService

class ClientsView:
    def __init__(self, page: ft.Page, client_service: ClientService, workout_service: WorkoutService):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service
        self.clients_list = ft.ListView(expand=1, spacing=10, padding=10)

    def build(self) -> ft.View:
        # Кнопка добавления клиента
        add_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=self.add_client_click
        )

        # Заголовок
        title = ft.Row(
            [ft.Text("Мои клиенты", size=30, weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.CENTER
        )

        # Поле поиска
        search_field = ft.TextField(
            hint_text="Поиск по имени или телефону",
            on_change=self.search_clients,
            expand=True
        )

        # Собираем экран
        view = ft.View(
            route="/clients",
            controls=[
                ft.AppBar(title=ft.Text("Клиенты"), bgcolor=ft.Colors.OUTLINE_VARIANT),
                title,
                ft.Row([search_field]),
                self.clients_list,
            ],
            floating_action_button=add_button,
            vertical_alignment=ft.MainAxisAlignment.START
        )
        self.refresh_list()
        return view

    def refresh_list(self, search_query: str = ""):
        """Обновляет список клиентов на экране"""
        self.clients_list.controls.clear()
        if search_query:
            clients = self.client_service.search_clients(search_query)
        else:
            clients = self.client_service.get_all_clients()

        # Разделяем на активных и архивных
        active_clients = [c for c in clients if not c.is_archived]
        archived_clients = [c for c in clients if c.is_archived]

        for client in active_clients:
            client_workouts = self.workout_service.get_client_workouts(client.doc_id)
            remaining = self.client_service.get_total_remaining_workouts(client, client_workouts)
            self.clients_list.controls.append(
                ft.ListTile(
                    title=ft.Text(client.name),
                    subtitle=ft.Text(f"{client.phone}\nОсталось тренировок - {remaining}"),
                    is_three_line=True,
                    on_click=lambda e, c=client: self.open_client_details(c),
                    trailing=ft.IconButton(
                        icon=ft.Icons.DELETE,
                        on_click=lambda e, c=client: self.delete_client_click(c)
                    ),
                )
            )

        if archived_clients:
            self.clients_list.controls.append(ft.Divider())
            for client in archived_clients:
                client_workouts = self.workout_service.get_client_workouts(client.doc_id)
                remaining = self.client_service.get_total_remaining_workouts(client, client_workouts)
                self.clients_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(client.name, color=ft.Colors.GREY_500),
                        subtitle=ft.Text(f"{client.phone}\nОсталось тренировок - {remaining}", color=ft.Colors.GREY_500),
                        is_three_line=True,
                        on_click=lambda e, c=client: self.open_client_details(c),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE,
                            on_click=lambda e, c=client: self.delete_client_click(c),
                            icon_color=ft.Colors.GREY_500
                        ),
                    )
                )
        self.page.update()

    def add_client_click(self, e):
        # Переход на экран добавления клиента
        self.page.go("/add_client")

    def open_client_details(self, client):
        self.page.go(f"/client_details/{client.doc_id}")

    def delete_client_click(self, client):
        def confirm_delete(e):
            self.client_service.delete_client(client.doc_id)
            dlg.open = False
            self.page.update()
            self.refresh_list()
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Клиент {client.name} удалён"))
            self.page.snack_bar.open = True
            self.page.update()

        # Диалог подтверждения
        dlg = ft.AlertDialog(
            title=ft.Text("Удалить клиента?"),
            content=ft.Text(f"Вы уверены, что хотите удалить {client.name}?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(e, dlg)),
                ft.TextButton("Удалить", on_click=confirm_delete)
            ]
        )
        self.page.show_dialog(dlg)

    def close_dialog(self, e, dlg):
        dlg.open = False
        self.page.update()

    def search_clients(self, e):
        self.refresh_list(e.control.value)
