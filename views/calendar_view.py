import flet as ft
import calendar
from datetime import datetime, date, timedelta
from business_logic.workout_service import WorkoutService
from business_logic.client_service import ClientService
from views.workout_edit_dialog import show_workout_dialog

class CalendarView:
    def __init__(self, page: ft.Page, client_service: ClientService, workout_service: WorkoutService, exercise_service, program_service):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service
        self.exercise_service = exercise_service
        self.program_service = program_service
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.view_mode = "MONTH"  # "MONTH" или "WEEK"
        self.selected_date = date.today()
        # Начало недели для недельного вида (понедельник)
        self.current_week_start = self.selected_date - timedelta(days=self.selected_date.weekday())

        self.calendar_grid = ft.Column()
        self.detailed_workouts_list = ft.ListView(expand=True, spacing=10)
        self.month_label = ft.Text(size=20, weight=ft.FontWeight.BOLD)

    def build(self) -> ft.View:
        self.refresh_calendar()

        add_button = ft.ElevatedButton(
            "Добавить тренировку",
            icon=ft.Icons.ADD,
            on_click=self.add_workout_click
        )

        app_bar = ft.AppBar(
            title=ft.Text("Календарь тренировок"),
            bgcolor=ft.Colors.OUTLINE_VARIANT,
        )

        if self.view_mode == "WEEK":
            app_bar.leading = ft.IconButton(
                ft.Icons.ARROW_BACK,
                on_click=self.go_to_month_mode
            )
        else:
            app_bar.leading = ft.IconButton(
                ft.Icons.ARROW_BACK,
                on_click=lambda: self.page.go("/")
            )

        calendar_content = ft.Column(
            [
                ft.Row([add_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=self.prev_click),
                        self.month_label,
                        ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=self.next_click),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=self.calendar_grid,
                    padding=10,
                ),
            ]
        )

        # Детектор жестов только для верхней части (сетка календаря),
        # чтобы не мешать скроллу списка тренировок снизу.
        gesture_detector = ft.GestureDetector(
            content=calendar_content,
            on_vertical_drag_update=self.on_swipe_down,
        )

        content = ft.Column(
            [
                gesture_detector,
                ft.Divider() if self.view_mode == "WEEK" else ft.Container(),
                self.detailed_workouts_list if self.view_mode == "WEEK" else ft.Container(),
            ],
            expand=True,
        )

        return ft.View(
            route="/calendar",
            controls=[
                app_bar,
                content
            ],
            scroll=ft.ScrollMode.HIDDEN if self.view_mode == "WEEK" else ft.ScrollMode.AUTO,
        )

    def on_swipe_down(self, e: ft.DragUpdateEvent):
        # Только если это явный свайп вниз (положительная дельта по Y)
        if self.view_mode == "WEEK" and e.primary_delta is not None and e.primary_delta > 5:
            self.go_to_month_mode(None)
            self.refresh_calendar()
            self.detailed_workouts_list.controls.clear()

    def go_to_month_mode(self, e):
        self.view_mode = "MONTH"
        self.page.go("/calendar")
        self.update_view()

    def prev_click(self, e):
        if self.view_mode == "MONTH":
            self.prev_month(e)
        else:
            self.prev_week(e)

    def next_click(self, e):
        if self.view_mode == "MONTH":
            self.next_month(e)
        else:
            self.next_week(e)

    def refresh_calendar(self):
        self.calendar_grid.controls.clear()

        # Названия месяцев на русском
        months_ru = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        if self.view_mode == "MONTH":
            self.month_label.value = f"{months_ru[self.current_month - 1]} {self.current_year}"
        else:
            self.month_label.value = f"{months_ru[self.current_week_start.month - 1]} {self.current_week_start.year}"

        # Заголовки дней недели
        days_header = ft.Row(
            [
                ft.Container(
                    content=ft.Text(day, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    expand=True,
                )
                for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            ],
            spacing=5,
        )
        self.calendar_grid.controls.append(days_header)

        # Получаем все тренировки
        all_workouts = self.workout_service.get_all_workouts()
        clients = self.client_service.get_all_clients()
        client_map = {c.doc_id: c.name for c in clients}

        if self.view_mode == "MONTH":
            cal = calendar.Calendar(firstweekday=0)
            month_days = cal.monthdayscalendar(self.current_year, self.current_month)

            for week in month_days:
                week_row = ft.Row(spacing=5, vertical_alignment=ft.CrossAxisAlignment.START)
                for day in week:
                    if day == 0:
                        week_row.controls.append(ft.Container(expand=True))
                    else:
                        day_date = date(self.current_year, self.current_month, day)
                        week_row.controls.append(self.create_day_container(day_date, all_workouts, client_map))
                self.calendar_grid.controls.append(week_row)
        else:
            week_row = ft.Row(spacing=5, vertical_alignment=ft.CrossAxisAlignment.START)
            for i in range(7):
                day_date = self.current_week_start + timedelta(days=i)
                week_row.controls.append(self.create_day_container(day_date, all_workouts, client_map))
            self.calendar_grid.controls.append(week_row)
            self.refresh_detailed_workouts(all_workouts, client_map)

    def create_day_container(self, day_date, all_workouts, client_map):
        day_workouts = [w for w in all_workouts if w.date == day_date]
        day_workouts.sort(key=lambda w: w.time)

        workout_controls = []
        for w in day_workouts:
            client_name = client_map.get(w.client_ids[0], "Неизвестный") if w.client_ids else "Без клиента"
            workout_controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"{w.time.strftime('%H:%M')}", size=10, weight=ft.FontWeight.BOLD),
                            ft.Text(client_name, size=10, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=0,
                    ),
                    padding=2,
                    border_radius=4,
                    bgcolor=ft.Colors.BLUE_50,
                    on_click=lambda e, workout=w: self.edit_workout(workout),
                )
            )

        is_today = day_date == date.today()
        is_selected = self.view_mode == "WEEK" and day_date == self.selected_date

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        str(day_date.day),
                        weight=ft.FontWeight.BOLD if (is_today or is_selected) else None,
                        color=ft.Colors.BLUE if is_today else (ft.Colors.ORANGE if is_selected else None)
                    ),
                    ft.Column(workout_controls, spacing=2),
                ],
                spacing=5,
            ),
            padding=5,
            border=ft.border.all(2 if is_selected else 1, ft.Colors.ORANGE if is_selected else ft.Colors.GREY_300),
            border_radius=8,
            expand=True,
            on_click=lambda e: self.show_week_view(day_date),
        )

    def refresh_detailed_workouts(self, all_workouts, client_map):
        self.detailed_workouts_list.controls.clear()
        day_workouts = [w for w in all_workouts if w.date == self.selected_date]
        day_workouts.sort(key=lambda w: w.time)

        if not day_workouts:
            self.detailed_workouts_list.controls.append(
                ft.Container(
                    content=ft.Text("Нет тренировок на этот день", italic=True, text_align=ft.TextAlign.CENTER),
                    padding=20
                )
            )
        else:
            for w in day_workouts:
                self.detailed_workouts_list.controls.append(self.create_detailed_workout_card(w, client_map))

    def create_detailed_workout_card(self, w, client_map):
        client_names = [client_map.get(cid, "Неизвестный") for cid in w.client_ids]
        client_names_str = ", ".join(client_names)

        status_icon = ft.Icons.TIMER
        if w.status == "Проведена":
            status_icon = ft.Icons.CHECK_CIRCLE
        elif w.status == "Отменена":
            status_icon = ft.Icons.CANCEL

        payment_icon = ft.Icons.MONEY_OFF if not w.is_paid else ft.Icons.ATTACH_MONEY
        payment_color = ft.Colors.RED if not w.is_paid else ft.Colors.GREEN

        return ft.Card(
            content=ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(status_icon),
                    title=ft.Text(f"{w.time.strftime('%H:%M')}"),
                    subtitle=ft.Text(f"{client_names_str}\n{w.price} руб.\n{w.status}"),
                    trailing=ft.Icon(payment_icon, color=payment_color),
                    on_click=lambda e, workout=w: self.edit_workout(workout),
                ),
                padding=5,
            )
        )

    def show_week_view(self, day_date):
        self.view_mode = "WEEK"
        self.selected_date = day_date
        self.current_week_start = day_date - timedelta(days=day_date.weekday())
        self.update_view()

    def update_view(self):
        new_view = self.build()
        current_view = self.page.views[-1]
        current_view.controls = new_view.controls
        current_view.app_bar = new_view.appbar
        current_view.scroll = new_view.scroll
        self.page.update()

    def prev_week(self, e):
        self.current_week_start -= timedelta(days=7)
        self.selected_date -= timedelta(days=7)
        self.current_year = self.current_week_start.year
        self.current_month = self.current_week_start.month
        self.refresh_calendar()
        self.page.update()

    def next_week(self, e):
        self.current_week_start += timedelta(days=7)
        self.selected_date += timedelta(days=7)
        self.current_year = self.current_week_start.year
        self.current_month = self.current_week_start.month
        self.refresh_calendar()
        self.page.update()

    def prev_month(self, e):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_calendar()
        self.page.update()

    def next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_calendar()
        self.page.update()

    def add_workout_click(self, e):
        show_workout_dialog(self.page, self.workout_service, self.client_service, self.exercise_service, self.program_service, on_save=self.on_dialog_save)

    def edit_workout(self, workout):
        show_workout_dialog(self.page, self.workout_service, self.client_service, self.exercise_service, self.program_service,
                            workout=workout, on_save=self.on_dialog_save)

    def on_dialog_save(self):
        self.refresh_calendar()
        self.page.update()
