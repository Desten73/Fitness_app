import flet as ft
from datetime import date
from models.client import Client, WorkoutPackage
from business_logic.client_service import ClientService
from business_logic.workout_service import WorkoutService

class ClientDetailsView:
    def __init__(self, page: ft.Page, client_service: ClientService, workout_service: WorkoutService, client_id: int):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service
        self.client_id = client_id
        self.client = self.client_service.get_client(client_id)
        self.edit_mode = False

        # Контейнеры для динамического обновления
        self.info_container = ft.Column()
        self.packages_container = ft.Column()
        self.history_container = ft.Column()

        # Поля редактирования
        self.name_field = ft.TextField(label="Имя")
        self.phone_field = ft.TextField(label="Телефон")
        self.price_field = ft.TextField(label="Стоимость тренировки", input_filter=ft.NumbersOnlyInputFilter())
        self.status_checkbox = ft.Checkbox(label="В архиве")
        self.goals_field = ft.TextField(label="Цели")
        self.notes_field = ft.TextField(label="Заметки", multiline=True)

        # Поля для нового пакета
        self.new_pkg_count = ft.TextField(label="Кол-во тренировок", expand=True, input_filter=ft.NumbersOnlyInputFilter())
        self.new_pkg_price = ft.TextField(label="Стоимость пакета", expand=True, input_filter=ft.NumbersOnlyInputFilter())

    def build(self) -> ft.View:
        if not self.client:
            return ft.View(route=f"/client_details/{self.client_id}", controls=[ft.AppBar(title=ft.Text("Клиент не найден")), ft.Text("Клиент не найден")])

        self.refresh_data_and_ui()

        return ft.View(
            route=f"/client_details/{self.client_id}",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.AppBar(
                    title=ft.Text(f"Инфо: {self.client.name}"),
                    bgcolor=ft.Colors.OUTLINE_VARIANT,
                    actions=[
                        ft.IconButton(ft.Icons.DELETE, on_click=self.delete_client_click, icon_color=ft.Colors.RED_400),
                    ]
                ),
                self.info_container,
                ft.Divider(),
                self.packages_container,
                ft.Divider(),
                self.history_container,
            ]
        )

    def refresh_data_and_ui(self):
        self.client = self.client_service.get_client(self.client_id)
        if not self.client: return

        self.client_workouts = self.workout_service.get_client_workouts(self.client_id)
        self.remaining_map = self.client_service.calculate_remaining_workouts(self.client, self.client_workouts)

        self.update_info_ui()
        self.update_packages_ui()
        self.update_history_ui()

    def update_info_ui(self):
        self.info_container.controls.clear()
        if self.edit_mode:
            self.name_field.value = self.client.name
            self.phone_field.value = self.client.phone
            self.price_field.value = str(self.client.workout_price)
            self.status_checkbox.value = self.client.is_archived
            self.goals_field.value = ", ".join(self.client.goals)
            self.notes_field.value = self.client.notes

            self.info_container.controls.extend([
                self.name_field,
                self.phone_field,
                self.price_field,
                self.status_checkbox,
                self.goals_field,
                self.notes_field,
                ft.Row([
                    ft.ElevatedButton("Сохранить", on_click=self.save_changes, icon=ft.Icons.SAVE),
                    ft.TextButton("Отмена", on_click=self.toggle_edit)
                ])
            ])
        else:
            self.info_container.controls.extend([
                ft.Row([
                    ft.Text(f"Имя: {self.client.name}", size=20, weight=ft.FontWeight.BOLD, expand=True),
                    ft.IconButton(ft.Icons.EDIT, on_click=self.toggle_edit)
                ]),
                ft.Text(f"Телефон: {self.client.phone}"),
                ft.Text(f"Стоимость тренировки: {self.client.workout_price} руб."),
                ft.Text(f"Цели: {', '.join(self.client.goals)}"),
                ft.Text(f"Заметки: {self.client.notes}"),
                ft.Text(f"Статус: {'Архивный' if self.client.is_archived else 'Активный'}",
                        color=ft.Colors.GREY_500 if self.client.is_archived else ft.Colors.GREEN),
            ])
        if self.info_container.page:
            self.info_container.update()

    def update_packages_ui(self):
        self.packages_container.controls.clear()
        self.packages_container.controls.append(ft.Text("Пакеты тренировок", size=18, weight=ft.FontWeight.BOLD))

        for i, pkg in enumerate(self.client.packages):
            rem = self.remaining_map.get(i, 0)
            self.packages_container.controls.append(
                ft.ListTile(
                    title=ft.Text(f"Пакет от {pkg.purchase_date}"),
                    subtitle=ft.Text(f"Тренировок: {pkg.total_workouts}, Цена: {pkg.price} руб.\nОсталось: {rem}"),
                    trailing=ft.IconButton(ft.Icons.DELETE, on_click=lambda e, idx=i: self.delete_package(idx))
                )
            )

        self.packages_container.controls.append(
            ft.Column([
                ft.Text("Добавить пакет", weight=ft.FontWeight.W_500),
                ft.Row([self.new_pkg_count, self.new_pkg_price]),
                ft.ElevatedButton("Добавить пакет", on_click=self.add_package, icon=ft.Icons.ADD)
            ])
        )
        if self.packages_container.page:
            self.packages_container.update()

    def update_history_ui(self):
        self.history_container.controls.clear()
        self.history_container.controls.append(ft.Text("История тренировок", size=18, weight=ft.FontWeight.BOLD))

        sorted_workouts = sorted(self.client_workouts, key=lambda w: (w.date, w.time), reverse=True)

        for w in sorted_workouts:
            is_dimmed = w.status != "завершено"
            color = ft.Colors.GREY_500 if is_dimmed else ft.Colors.BLACK
            self.history_container.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{w.date} {w.time}", color=color),
                    subtitle=ft.Text(f"Статус: {w.status}, Цена: {w.price}", color=color),
                )
            )

        if not sorted_workouts:
            self.history_container.controls.append(ft.Text("Тренировок пока не было", italic=True))

        if self.history_container.page:
            self.history_container.update()

    def toggle_edit(self, e):
        self.edit_mode = not self.edit_mode
        self.update_info_ui()

    def save_changes(self, e):
        self.client.name = self.name_field.value
        self.client.phone = self.phone_field.value
        self.client.workout_price = int(self.price_field.value or 1000)
        self.client.is_archived = self.status_checkbox.value
        self.client.goals = [g.strip() for g in self.goals_field.value.split(",")] if self.goals_field.value else []
        self.client.notes = self.notes_field.value

        self.client_service.update_client(self.client)
        self.edit_mode = False
        self.refresh_data_and_ui()
        self.page.snack_bar = ft.SnackBar(ft.Text("Данные обновлены"))
        self.page.snack_bar.open = True
        self.page.update()

    def add_package(self, e):
        if not self.new_pkg_count.value or not self.new_pkg_price.value:
            return

        new_pkg = WorkoutPackage(
            purchase_date=date.today(),
            total_workouts=int(self.new_pkg_count.value),
            price=int(self.new_pkg_price.value)
        )
        self.client.packages.append(new_pkg)
        self.client_service.update_client(self.client)
        self.new_pkg_count.value = ""
        self.new_pkg_price.value = ""
        self.refresh_data_and_ui()

    def delete_package(self, index):
        self.client.packages.pop(index)
        self.client_service.update_client(self.client)
        self.refresh_data_and_ui()

    def delete_client_click(self, e):
        def confirm_delete(ev):
            self.client_service.delete_client(self.client_id)
            dlg.open = False
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Клиент {self.client.name} удалён"))
            self.page.snack_bar.open = True
            # Навигация назад к списку клиентов
            self.page.go("/clients")

        dlg = ft.AlertDialog(
            title=ft.Text("Удалить клиента?"),
            content=ft.Text(f"Вы уверены, что хотите полностью удалить {self.client.name}?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda ev: self.close_dialog(ev, dlg)),
                ft.TextButton("Удалить", on_click=confirm_delete)
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dialog(self, e, dlg):
        dlg.open = False
        self.page.update()
