import flet as ft
from business_logic.client_service import ClientService

class MainView:
    def __init__(self, page: ft.Page, client_service: ClientService):
        self.page = page
        self.client_service = client_service
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
            "/",
            [
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

        for client in clients:
            self.clients_list.controls.append(
                ft.ListTile(
                    title=ft.Text(client.name),
                    subtitle=ft.Text(client.phone),
                    on_click=lambda e, c=client: self.open_client_details(c),
                    trailing=ft.IconButton(
                        icon=ft.icons.Icons.DELETE,
                        on_click=lambda e, c=client: self.delete_client_click(c)
                    ),
                )
            )
        self.page.update()

    def add_client_click(self, e):
        # Переход на экран добавления клиента
        from views.add_client import AddClientView
        self.page.views.append(AddClientView(self.page, self.client_service).build())
        self.page.update()

    def open_client_details(self, client):
        from views.client_details import ClientDetailsView
        self.page.views.append(ClientDetailsView(self.page, self.client_service, client).build())
        self.page.update()

    def delete_client_click(self, client):
        def confirm_delete(e):
            self.client_service.delete_client(client.doc_id)
            self.page.views.pop()  # закрываем диалог
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
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dialog(self, e, dlg):
        dlg.open = False
        self.page.update()

    def search_clients(self, e):
        self.refresh_list(e.control.value)