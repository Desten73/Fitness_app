import flet as ft
import calendar
from datetime import datetime, date
from business_logic.workout_service import WorkoutService
from business_logic.client_service import ClientService

class CalendarView:
    def __init__(self, page: ft.Page, client_service: ClientService, workout_service: WorkoutService):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.calendar_grid = ft.Column(expand=True)
        self.month_label = ft.Text(size=20, weight=ft.FontWeight.BOLD)

    def build(self) -> ft.View:
        self.refresh_calendar()

        return ft.View(
            route="/calendar",
            controls=[
                ft.AppBar(
                    title=ft.Text("Календарь тренировок"),
                    bgcolor=ft.Colors.OUTLINE_VARIANT,
                ),
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=self.prev_month),
                        self.month_label,
                        ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=self.next_month),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=self.calendar_grid,
                    padding=10,
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def refresh_calendar(self):
        self.calendar_grid.controls.clear()

        # Названия месяцев на русском
        months_ru = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        self.month_label.value = f"{months_ru[self.current_month - 1]} {self.current_year}"

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

        # Календарная сетка
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        for week in month_days:
            week_row = ft.Row(spacing=5, vertical_alignment=ft.CrossAxisAlignment.START)
            for day in week:
                if day == 0:
                    # Пустая ячейка
                    week_row.controls.append(ft.Container(expand=True))
                else:
                    # Ячейка дня
                    day_date = date(self.current_year, self.current_month, day)
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
                                on_click=lambda e, cid=w.client_ids[0] if w.client_ids else None: self.go_to_client(cid),
                            )
                        )

                    is_today = day_date == date.today()

                    week_row.controls.append(
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        str(day),
                                        weight=ft.FontWeight.BOLD if is_today else None,
                                        color=ft.Colors.BLUE if is_today else None
                                    ),
                                    ft.Column(workout_controls, spacing=2),
                                ],
                                spacing=5,
                            ),
                            padding=5,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=8,
                            expand=True,
                            # min_height=100,
                        )
                    )
            self.calendar_grid.controls.append(week_row)

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

    def go_to_client(self, client_id):
        if client_id:
            self.page.go(f"/client_details/{client_id}")
