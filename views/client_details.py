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

        # Поля редактирования
        self.name_field = ft.TextField(label="Имя", value=self.client.name)
        self.phone_field = ft.TextField(label="Телефон", value=self.client.phone)
        self.price_field = ft.TextField(label="Стоимость тренировки", value=str(self.client.workout_price), input_filter=ft.NumbersOnlyInputFilter())
        self.goals_field = ft.TextField(label="Цели", value=", ".join(self.client.goals))
        self.notes_field = ft.TextField(label="Заметки", value=self.client.notes, multiline=True)

        # Поля для нового пакета
        self.new_pkg_count = ft.TextField(label="Кол-во тренировок", expand=True, input_filter=ft.NumbersOnlyInputFilter())
        self.new_pkg_price = ft.TextField(label="Стоимость пакета", expand=True, input_filter=ft.NumbersOnlyInputFilter())

    def build(self) -> ft.View:
        if not self.client:
            return ft.View(route=f"/client_details/{self.client_id}", controls=[ft.Text("Клиент не найден")])

        self.client_workouts = self.workout_service.get_client_workouts(self.client_id)
        self.remaining_map = self.client_service.calculate_remaining_workouts(self.client, self.client_workouts)

        return ft.View(
            route=f"/client_details/{self.client_id}",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.AppBar(
                    title=ft.Text(f"Инфо: {self.client.name}"),
                    bgcolor=ft.Colors.OUTLINE_VARIANT,
                    actions=[
                        ft.IconButton(ft.Icons.EDIT, on_click=self.toggle_edit) if not self.edit_mode else ft.IconButton(ft.Icons.SAVE, on_click=self.save_changes),
                        ft.IconButton(ft.Icons.ARCHIVE if not self.client.is_archived else ft.Icons.UNARCHIVE, on_click=self.toggle_archive),
                    ]
                ),
                self.build_client_info(),
                ft.Divider(),
                self.build_packages_section(),
                ft.Divider(),
                self.build_workouts_history(),
            ]
        )

    def build_client_info(self):
        if self.edit_mode:
            return ft.Column([
                self.name_field,
                self.phone_field,
                self.price_field,
                self.goals_field,
                self.notes_field,
                ft.ElevatedButton("Сохранить", on_click=self.save_changes)
            ])
        else:
            return ft.Column([
                ft.Text(f"Имя: {self.client.name}", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Телефон: {self.client.phone}"),
                ft.Text(f"Стоимость тренировки: {self.client.workout_price} руб."),
                ft.Text(f"Цели: {', '.join(self.client.goals)}"),
                ft.Text(f"Заметки: {self.client.notes}"),
                ft.Text(f"Статус: {'Архивный' if self.client.is_archived else 'Активный'}", color=ft.Colors.GREY_500 if self.client.is_archived else ft.Colors.GREEN),
            ])

    def build_packages_section(self):
        package_controls = [ft.Text("Пакеты тренировок", size=18, weight=ft.FontWeight.BOLD)]

        for i, pkg in enumerate(self.client.packages):
            rem = self.remaining_map.get(i, 0)
            package_controls.append(
                ft.ListTile(
                    title=ft.Text(f"Пакет от {pkg.purchase_date}"),
                    subtitle=ft.Text(f"Тренировок: {pkg.total_workouts}, Цена: {pkg.price} руб.\nОсталось: {rem}"),
                    trailing=ft.IconButton(ft.Icons.DELETE, on_click=lambda e, idx=i: self.delete_package(idx))
                )
            )

        # Форма добавления пакета
        package_controls.append(
            ft.Column([
                ft.Text("Добавить пакет", weight=ft.FontWeight.W_500),
                ft.Row([self.new_pkg_count, self.new_pkg_price]),
                ft.ElevatedButton("Добавить пакет", on_click=self.add_package)
            ])
        )
        return ft.Column(package_controls)

    def build_workouts_history(self):
        history_controls = [ft.Text("История тренировок", size=18, weight=ft.FontWeight.BOLD)]

        # Сортировка от новых к старым
        sorted_workouts = sorted(self.client_workouts, key=lambda w: (w.date, w.time), reverse=True)

        for w in sorted_workouts:
            is_dimmed = w.status != "завершено"
            color = ft.Colors.GREY_500 if is_dimmed else ft.Colors.BLACK
            history_controls.append(
                ft.ListTile(
                    title=ft.Text(f"{w.date} {w.time}", color=color),
                    subtitle=ft.Text(f"Статус: {w.status}, Цена: {w.price}", color=color),
                )
            )

        if not sorted_workouts:
            history_controls.append(ft.Text("Тренировок пока не было", italic=True))

        return ft.Column(history_controls)

    def toggle_edit(self, e):
        self.edit_mode = True
        self.update_view()

    def save_changes(self, e):
        self.client.name = self.name_field.value
        self.client.phone = self.phone_field.value
        self.client.workout_price = int(self.price_field.value or 1000)
        self.client.goals = [g.strip() for g in self.goals_field.value.split(",")] if self.goals_field.value else []
        self.client.notes = self.notes_field.value
        self.client_service.update_client(self.client)
        self.edit_mode = False
        self.update_view()

    def toggle_archive(self, e):
        if self.client.is_archived:
            self.client_service.unarchive_client(self.client.doc_id)
        else:
            self.client_service.archive_client(self.client.doc_id)
        self.client = self.client_service.get_client(self.client_id)
        self.update_view()

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
        self.update_view()

    def delete_package(self, index):
        self.client.packages.pop(index)
        self.client_service.update_client(self.client)
        self.update_view()

    def update_view(self):
        # Перерисовываем всю вьюху
        new_view = self.build()
        # Находим индекс текущей вьюхи в стеке и заменяем её
        for i, view in enumerate(self.page.views):
            if view.route == f"/client_details/{self.client_id}":
                self.page.views[i] = new_view
                break
        self.page.update()
