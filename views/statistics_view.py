import flet as ft
from datetime import datetime, date, timedelta
from collections import Counter, defaultdict

class StatisticsView:
    def __init__(self, page: ft.Page, client_service, workout_service):
        self.page = page
        self.client_service = client_service
        self.workout_service = workout_service

        self.start_date = None
        self.end_date = None

        self.client_dropdown = ft.Dropdown(
            label="Выберите клиента",
            options=[ft.dropdown.Option(key="all", text="Все клиенты")],
            value="all",
            on_select=self.on_filter_change
        )

        self.start_date_btn = ft.ElevatedButton(
            "Начальная дата",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self.page.show_dialog(self.start_date_picker)
        )
        self.end_date_btn = ft.ElevatedButton(
            "Конечная дата",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self.page.show_dialog(self.end_date_picker)
        )

        self.start_date_picker = ft.DatePicker(
            on_change=self.on_start_date_change
        )
        self.end_date_picker = ft.DatePicker(
            on_change=self.on_end_date_change
        )

        self.reset_dates_btn = ft.TextButton("Сбросить даты", on_click=self.reset_dates, visible=False)

        self.weeks_stats_column = ft.Column(spacing=5)

        self.stats_column = ft.Column(spacing=10)
        self.extra_stats_column = ft.Column(spacing=10)

    def build(self) -> ft.View:
        clients = self.client_service.get_all_clients()
        self.client_dropdown.options = [ft.dropdown.Option(key="all", text="Все клиенты")]
        for c in clients:
            self.client_dropdown.options.append(ft.dropdown.Option(key=str(c.doc_id), text=c.name))

        self.update_statistics()

        return ft.View(
            route="/statistics",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.AppBar(title=ft.Text("Статистика"), bgcolor=ft.Colors.OUTLINE_VARIANT),
                ft.Container(
                    content=ft.Column([
                        self.client_dropdown,
                        ft.Row([
                            self.start_date_btn,
                            self.end_date_btn,
                        ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                        ft.Row([self.reset_dates_btn], alignment=ft.MainAxisAlignment.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10
                ),
                ft.Text("Количество тренировок в неделю", size=16, weight=ft.FontWeight.BOLD),
                self.weeks_stats_column,
                ft.Divider(),
                self.stats_column,
                self.extra_stats_column,
                ft.Container(height=20)
            ],
            padding=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def on_filter_change(self, e):
        self.update_statistics()
        self.page.update()

    def on_start_date_change(self, e):
        if e.control.value:
            self.start_date = e.control.value.date() if isinstance(e.control.value, datetime) else e.control.value
            self.start_date_btn.text = self.start_date.strftime("%d.%m.%Y")
            self.reset_dates_btn.visible = True
            self.update_statistics()
            self.page.update()

    def on_end_date_change(self, e):
        if e.control.value:
            self.end_date = e.control.value.date() if isinstance(e.control.value, datetime) else e.control.value
            self.end_date_btn.text = self.end_date.strftime("%d.%m.%Y")
            self.reset_dates_btn.visible = True
            self.update_statistics()
            self.page.update()

    def reset_dates(self, e):
        self.start_date = None
        self.end_date = None
        self.start_date_btn.text = "Начальная дата"
        self.end_date_btn.text = "Конечная дата"
        self.reset_dates_btn.visible = False
        self.update_statistics()
        self.page.update()

    def update_statistics(self):
        all_workouts = self.workout_service.get_all_workouts()

        # Filter by client
        selected_client_id = None
        if self.client_dropdown.value != "all":
            selected_client_id = int(self.client_dropdown.value)
            all_workouts = [w for w in all_workouts if selected_client_id in w.client_ids]

        # Filter by date
        if self.start_date:
            all_workouts = [w for w in all_workouts if w.date >= self.start_date]
        if self.end_date:
            all_workouts = [w for w in all_workouts if w.date <= self.end_date]

        conducted_workouts = [w for w in all_workouts if w.status == "Проведена"]
        paid_conducted_workouts = [w for w in conducted_workouts if w.is_paid]
        total_money = sum(w.price for w in paid_conducted_workouts)
        cancelled_workouts = [w for w in all_workouts if w.status == "Отменена"]

        self.stats_column.controls = [
            ft.Text(f"Количество тренировок: {len(conducted_workouts)}", size=18),
            ft.Text(f"Количество денег: {total_money} руб.", size=18),
            ft.Text(f"Количество отмен: {len(cancelled_workouts)}", size=18),
        ]

        # Extra stats for "All Clients"
        if self.client_dropdown.value == "all" and conducted_workouts:
            self.extra_stats_column.controls = [ft.Divider()]

            # 1. Average workouts per week
            if not self.start_date or not self.end_date:
                workout_dates = [w.date for w in conducted_workouts]
                actual_start = self.start_date or min(workout_dates)
                actual_end = self.end_date or max(workout_dates)
            else:
                actual_start = self.start_date
                actual_end = self.end_date

            num_days = (actual_end - actual_start).days + 1
            num_weeks = max(1, num_days / 7)
            avg_workouts_week = len(conducted_workouts) / num_weeks

            # 2. Average busiest day
            days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            day_counts = Counter(w.date.weekday() for w in conducted_workouts)
            busiest_day_idx = day_counts.most_common(1)[0][0] if day_counts else 0
            busiest_day = days_of_week[busiest_day_idx]

            # 3. Average workout price
            avg_price = total_money / len(paid_conducted_workouts) if paid_conducted_workouts else 0

            # 4. Most active client
            # 5. Least active client
            client_counts = Counter()
            for w in conducted_workouts:
                for cid in w.client_ids:
                    client_counts[cid] += 1

            clients_dict = {c.doc_id: c.name for c in self.client_service.get_all_clients()}

            most_active_client = "Нет данных"
            least_active_client = "Нет данных"

            if client_counts:
                most_active_id = client_counts.most_common(1)[0][0]
                most_active_client = f"{clients_dict.get(most_active_id, 'Неизвестный')} ({client_counts[most_active_id]})"

                least_active_id = client_counts.most_common()[-1][0]
                least_active_client = f"{clients_dict.get(least_active_id, 'Неизвестный')} ({client_counts[least_active_id]})"

            self.extra_stats_column.controls.extend([
                ft.Text(f"Среднее число тренировок в неделю: {avg_workouts_week:.1f}", size=16),
                ft.Text(f"В среднем самый нагруженный день: {busiest_day}", size=16),
                ft.Text(f"Средняя цена тренировки: {int(avg_price)} руб.", size=16),
                ft.Text(f"Самый активный клиент: {most_active_client}", size=16),
                ft.Text(f"Самый неактивный клиент: {least_active_client}", size=16),
            ])
            self.extra_stats_column.visible = True
        else:
            self.extra_stats_column.visible = False

        # Weekly Stats Logic
        self.update_weekly_stats(conducted_workouts)

    def update_weekly_stats(self, conducted_workouts):
        self.weeks_stats_column.controls.clear()
        if not conducted_workouts:
            self.weeks_stats_column.controls.append(ft.Text("Нет данных за выбранный период", size=14, italic=True))
            return

        workout_dates = [w.date for w in conducted_workouts]
        range_start = self.start_date or min(workout_dates)
        range_end = self.end_date or max(workout_dates)

        # Group by week (Monday)
        def get_monday(d):
            return d - timedelta(days=d.weekday())

        start_monday = get_monday(range_start)
        end_monday = get_monday(range_end)

        mondays = []
        curr = start_monday
        while curr <= end_monday:
            mondays.append(curr)
            curr += timedelta(weeks=1)

        # Count workouts per week
        counts = Counter()
        for w in conducted_workouts:
            m = get_monday(w.date)
            counts[m] += 1

        for i, m in enumerate(mondays):
            sunday = m + timedelta(days=6)
            count = counts[m]
            self.weeks_stats_column.controls.append(
                ft.Text(f"Неделя {i + 1} ({m.strftime('%d.%m')} - {sunday.strftime('%d.%m')}): {count}", size=16)
            )
