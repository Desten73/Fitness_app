import flet as ft
from datetime import date, time, datetime, timedelta
from models.workout import Workout

def show_workout_dialog(page: ft.Page, workout_service, client_service, exercise_service=None, program_service=None, workout: Workout = None, on_save=None):
    clients = client_service.get_all_clients()
    active_clients = [c for c in clients if not c.is_archived]

    # Если мы редактируем тренировку архивного клиента, он должен быть в списке
    if workout:
        workout_client_ids = set(workout.client_ids)
        current_clients_ids = {c.doc_id for c in active_clients}
        for cid in workout_client_ids:
            if cid not in current_clients_ids:
                c = client_service.get_client(cid)
                if c:
                    active_clients.append(c)

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

    def on_client_select(e):
        client_id = int(e.control.value)
        # Обновляем список программ для нового клиента
        if program_service:
            progs = program_service.get_client_programs(client_id)
            program_dropdown.options = [ft.dropdown.Option(key=str(p.doc_id), text=p.name) for p in progs]
            program_dropdown.value = None
            update_exercises_ui(None)
            program_dropdown.update()

        for c in active_clients:
            if c.doc_id == client_id:
                price_field.value = str(c.workout_price)
                price_field.update()

                client_workouts = workout_service.get_client_workouts(client_id)
                remaining = client_service.get_total_remaining_workouts(c, client_workouts)
                if remaining > 0:
                    paid_checkbox.value = True
                    paid_checkbox.update()
                break

    client_dropdown = ft.Dropdown(
        label="Клиент",
        options=client_options,
        value=str(workout.client_ids[0]) if workout and workout.client_ids else None,
        on_change=on_client_select
    )

    date_val = workout.date if workout else date.today()
    date_button = ft.ElevatedButton(
        date_val.strftime("%d.%m.%Y"),
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: page.show_dialog(date_picker)
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

    # Работа с программами
    exercises_data = workout.exercises_data.copy() if workout and workout.exercises_data else {}
    exercises_ui_col = ft.Column()

    def update_exercises_ui(program):
        exercises_ui_col.controls.clear()
        if not program:
            if page:
                page.update()
            return

        exercises = exercise_service.get_all_exercises()
        ex_map = {ex.doc_id: ex.name for ex in exercises}

        for ex_id in program.exercise_ids:
            ex_id_str = str(ex_id)
            if ex_id_str not in exercises_data:
                exercises_data[ex_id_str] = {"sets": "", "reps": "", "weight": ""}

            data = exercises_data[ex_id_str]

            exercises_ui_col.controls.append(ft.Text(ex_map.get(ex_id, "Упражнение удалено"), weight=ft.FontWeight.BOLD))

            sets_field = ft.TextField(label="Подходы", value=data["sets"], width=100, on_change=lambda e, eid=ex_id_str: update_data(eid, "sets", e.control.value))
            reps_field = ft.TextField(label="Повторы", value=data["reps"], width=100, on_change=lambda e, eid=ex_id_str: update_data(eid, "reps", e.control.value))
            weight_field = ft.TextField(label="Вес", value=data["weight"], width=100, on_change=lambda e, eid=ex_id_str: update_data(eid, "weight", e.control.value))

            exercises_ui_col.controls.append(ft.Row([sets_field, reps_field, weight_field]))

        if page:
            page.update()

    def update_data(ex_id, field, value):
        exercises_data[ex_id][field] = value

    def on_program_change(e):
        nonlocal exercises_data
        exercises_data = {} # Reset data
        if not e.control.value:
            update_exercises_ui(None)
            return

        prog_id = int(e.control.value)
        program = program_service.get_program(prog_id)

        # Автозаполнение из последней тренировки
        last_workout = workout_service.get_last_workout_with_program(int(client_dropdown.value), prog_id)
        if last_workout and last_workout.exercises_data:
            for ex_id in program.exercise_ids:
                ex_id_str = str(ex_id)
                if ex_id_str in last_workout.exercises_data:
                    exercises_data[ex_id_str] = last_workout.exercises_data[ex_id_str].copy()

        update_exercises_ui(program)

    program_options = []
    if workout and workout.client_ids and program_service:
        progs = program_service.get_client_programs(workout.client_ids[0])
        program_options = [ft.dropdown.Option(key=str(p.doc_id), text=p.name) for p in progs]

    program_dropdown = ft.Dropdown(
        label="Программа тренировки",
        options=program_options,
        value=str(workout.program_id) if workout and workout.program_id else None,
        on_change=on_program_change
    )

    if workout and workout.program_id:
        program = program_service.get_program(workout.program_id)
        update_exercises_ui(program)

    def save_click(e):
        if not client_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("Выберите клиента"))
            page.overlay.append(page.snack_bar)
            page.snack_bar.open = True
            page.update()
            return

        try:
            t_parts = time_field.value.split(":")
            workout_time = time(int(t_parts[0]), int(t_parts[1]))
        except:
            page.snack_bar = ft.SnackBar(ft.Text("Неверный формат времени"))
            page.overlay.append(page.snack_bar)
            page.snack_bar.open = True
            page.update()
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
            program_id=int(program_dropdown.value) if program_dropdown.value else None,
            exercises_data=exercises_data,
            doc_id=workout.doc_id if workout else None
        )

        if workout:
            workout_service.update_workout(new_workout)
        else:
            workout_service.add_workout(new_workout)

        page.pop_dialog()
        if on_save:
            on_save()

    def delete_click(e):
        def confirm_delete(e):
            workout_service.delete_workout(workout.doc_id)
            page.pop_dialog()
            page.pop_dialog()
            if on_save:
                on_save()

        confirm_dlg = ft.AlertDialog(
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text(f"Вы уверены, что хотите удалить тренировку "
                            f"{workout.date.strftime('%d.%m.%Y')} "
                            f"{workout.time.strftime('%H:%M')}?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: page.pop_dialog()),
                ft.TextButton("Удалить", on_click=confirm_delete),
            ],
        )
        page.show_dialog(confirm_dlg)

    actions = [
        ft.TextButton("Отмена", on_click=lambda e: page.pop_dialog()),
        ft.TextButton("Сохранить", on_click=save_click),
    ]

    if workout:
        actions.insert(0, ft.TextButton("Удалить", on_click=delete_click))

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
                program_dropdown,
                exercises_ui_col
            ],
            tight=True,
            scroll=ft.ScrollMode.AUTO
        ),
        actions=actions,
    )
    page.show_dialog(dialog)
    page.update()
