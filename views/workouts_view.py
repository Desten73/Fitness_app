import flet as ft
from business_logic.workout_service import WorkoutService
from models.workout import Workout
from datetime import datetime, date, time, timedelta

class WorkoutsView:
    def __init__(self, page: ft.Page, workout_service: WorkoutService, client_service):
        self.page = page
        self.workout_service = workout_service
        self.client_service = client_service
        self.workouts_list = ft.ListView(expand=1, spacing=10, padding=10)
        self.search_field = ft.TextField(
            label="Поиск (Клиент, статус, оплата, дата)",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search_change
        )
        self.current_edit_workout_id = None

    def build(self) -> ft.View:
        add_button = ft.ElevatedButton(
            "Добавить тренировку",
            icon=ft.Icons.ADD,
            on_click=self.add_workout_click
        )

        view = ft.View(
            route="/workouts",
            controls=[
                ft.AppBar(title=ft.Text("Тренировки"), bgcolor=ft.Colors.OUTLINE_VARIANT),
                ft.Row([add_button], alignment=ft.MainAxisAlignment.CENTER),
                self.search_field,
                self.workouts_list,
            ],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.START
        )
        self.refresh_list()
        return view

    def on_search_change(self, e):
        self.refresh_list(self.search_field.value)

    def refresh_list(self, query=None):
        self.workouts_list.controls.clear()
        try:
            clients = self.client_service.get_all_clients()
            client_map = {c.doc_id: c.name for c in clients if c.doc_id is not None}

            groups = self.workout_service.get_sorted_workouts_v2(query, client_map)
        except Exception as e:
            print(f"Error refreshing workouts list: {e}")
            self.workouts_list.controls.append(ft.Text(f"Ошибка загрузки данных: {e}", color=ft.Colors.RED))
            self.page.update()
            return

        if "search_results" in groups:
            for w in groups["search_results"]:
                self.workouts_list.controls.append(self.create_workout_card(w, client_map))
        else:
            # Today
            if groups["today"]:
                # self.workouts_list.controls.append(ft.Text("Сегодня", weight=ft.FontWeight.BOLD))
                for w in groups["today"]:
                    self.workouts_list.controls.append(self.create_workout_card(w, client_map))

            # Future
            if groups["future"]:
                # self.workouts_list.controls.append(ft.Text("Будущие", weight=ft.FontWeight.BOLD))
                for w in groups["future"]:
                    self.workouts_list.controls.append(self.create_workout_card(w, client_map))

            # Past
            if groups["past_unpaid"] or groups["past_paid"]:
                self.workouts_list.controls.append(ft.Divider())
                for w in groups["past_unpaid"]:
                    self.workouts_list.controls.append(self.create_workout_card(w, client_map, is_past=True))
                for w in groups["past_paid"]:
                    self.workouts_list.controls.append(self.create_workout_card(w, client_map, is_past=True))

        self.page.update()

    def create_workout_card(self, w: Workout, client_map, is_past=False):
        client_names = [client_map.get(cid, "Неизвестный") for cid in w.client_ids]
        client_names_str = ", ".join(client_names)

        bgcolor = None
        if is_past:
            if not w.is_paid:
                bgcolor = ft.Colors.RED_100
            else:
                bgcolor = ft.Colors.GREY_200

        status_icon = ft.Icons.TIMER
        if w.status == "Проведена":
            status_icon = ft.Icons.CHECK_CIRCLE
        elif w.status == "Отменена":
            status_icon = ft.Icons.CANCEL

        payment_icon = ft.Icons.MONEY_OFF if not w.is_paid else ft.Icons.ATTACH_MONEY
        payment_color = ft.Colors.RED if not w.is_paid else ft.Colors.GREEN

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(status_icon),
                            title=ft.Text(f"{w.date.strftime('%d.%m.%Y')} {w.time.strftime('%H:%M')}"),
                            # subtitle=ft.Text(f"Клиент: {client_names_str}\nЦена: {w.price} руб.\nСтатус: {w.status}"),
                            subtitle=ft.Text(f"{client_names_str}\n{w.price} руб.\n{w.status}"),
                            trailing=ft.Row(
                                [
                                    ft.Icon(payment_icon, color=payment_color),
                                    # ft.IconButton(ft.Icons.EDIT, on_click=lambda e: self.edit_workout(w)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED,
                                                  on_click=lambda e: self.delete_workout(w)),
                                ],
                                tight=True,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            on_click=lambda e: self.edit_workout(w),
                        ),
                    ],
                    spacing=0,
                ),
                padding=5,
                bgcolor=bgcolor
            )
        )

    def add_workout_click(self, e):
        self.show_workout_dialog()

    def edit_workout(self, workout: Workout):
        self.show_workout_dialog(workout)

    def delete_workout(self, workout: Workout):
        def confirm_delete(e):
            self.workout_service.delete_workout(workout.doc_id)
            self.page.pop_dialog()
            self.refresh_list(self.search_field.value)

        dialog = ft.AlertDialog(
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text(f"Вы уверены, что хотите удалить тренировку "
                            f"{workout.date.strftime('%d.%m.%Y')} "
                            f"{workout.time.strftime('%H:%M')}?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.pop_dialog()),
                ft.TextButton("Удалить", on_click=confirm_delete),
            ],
        )
        self.page.show_dialog(dialog)

    def show_workout_dialog(self, workout: Workout = None):
        clients = self.client_service.get_all_clients()
        active_clients = [c for c in clients if not c.is_archived]

        client_options = [ft.dropdown.Option(key=str(c.doc_id), text=c.name) for c in active_clients]

        status_dropdown = ft.Dropdown(
            label="Статус",
            options=[
                ft.dropdown.Option("Планируется"),
                ft.dropdown.Option("Подтверждена"),
                ft.dropdown.Option("Проведена"),
                ft.dropdown.Option("Отменена"),
            ],
            value=workout.status if workout else "Планируется"
        )

        client_dropdown = ft.Dropdown(
            label="Клиент",
            options=client_options,
            value=str(workout.client_ids[0]) if workout and workout.client_ids else None,
            on_select=lambda e: self.on_client_select(e, price_field, active_clients, paid_checkbox)
        )

        date_val = workout.date if workout else date.today()
        date_button = ft.ElevatedButton(
            date_val.strftime("%d.%m.%Y"),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.page.show_dialog(date_picker)
        )

        def on_date_change(e):
            if e.control.value:
                date_button.text = e.control.value.strftime("%d.%m.%Y")
                date_button.update()

        date_picker = ft.DatePicker(
            value=date_val,
            on_change=on_date_change
        )

        time_val = workout.time if workout else time(12, 0)
        time_field = ft.TextField(label="Время (ЧЧ:ММ)", value=time_val.strftime("%H:%M"))

        price_field = ft.TextField(
            label="Стоимость",
            value=str(workout.price) if workout else "",
            input_filter=ft.NumbersOnlyInputFilter()
        )

        paid_checkbox = ft.Checkbox(label="Оплачено", value=workout.is_paid if workout else False)

        program_field = ft.TextField(label="Тренировочная программа (скоро)", disabled=True)

        def save_click(e):
            if not client_dropdown.value:
                self.page.snack_bar = ft.SnackBar(ft.Text("Выберите клиента"))
                self.page.overlay.append(self.page.snack_bar)
                self.page.snack_bar.open = True
                self.page.update()
                return

            try:
                t_parts = time_field.value.split(":")
                workout_time = time(int(t_parts[0]), int(t_parts[1]))
            except:
                self.page.snack_bar = ft.SnackBar(ft.Text("Неверный формат времени"))
                self.page.overlay.append(self.page.snack_bar)
                self.page.snack_bar.open = True
                self.page.update()
                return

            selected_date = date_picker.value if date_picker.value else date_val
            if isinstance(selected_date, datetime):
                selected_date = selected_date.date() + timedelta(days=1)

            new_workout = Workout(
                client_ids=[int(client_dropdown.value)],
                date=selected_date,
                time=workout_time,
                price=int(price_field.value or 0),
                status=status_dropdown.value,
                is_paid=paid_checkbox.value,
                doc_id=workout.doc_id if workout else None
            )

            if workout:
                self.workout_service.update_workout(new_workout)
            else:
                self.workout_service.add_workout(new_workout)

            self.page.pop_dialog()
            self.refresh_list(self.search_field.value)

        dialog = ft.AlertDialog(
            title=ft.Text("Тренировка"),
            content=ft.Column(
                [
                    status_dropdown,
                    client_dropdown,
                    ft.Row([ft.Text("Дата:"), date_button]),
                    time_field,
                    price_field,
                    paid_checkbox,
                    program_field
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.pop_dialog()),
                ft.TextButton("Сохранить", on_click=save_click),
            ],
        )
        self.page.show_dialog(dialog)

    def on_client_select(self, e, price_field, clients, paid_checkbox):
        client_id = int(e.control.value)
        for c in clients:
            if c.doc_id == client_id:
                price_field.value = str(c.workout_price)
                price_field.update()

                client_workouts = self.workout_service.get_client_workouts(client_id)
                remaining = self.client_service.get_total_remaining_workouts(c, client_workouts)
                if remaining > 0:
                    paid_checkbox.value = True
                    paid_checkbox.update()
                break
