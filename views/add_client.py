import flet as ft
from models.client import Client
from business_logic.client_service import ClientService


class AddClientView:
    def __init__(self, page: ft.Page, client_service: ClientService):
        self.page = page
        self.client_service = client_service
        self.name_field = ft.TextField(label="Имя", autofocus=True)
        self._last_phone_val = ""
        self.phone_field = ft.TextField(
            label="Телефон",
            on_focus=self.on_phone_focus,
            on_change=self.on_phone_change,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9+() \-]", replacement_string="")
        )
        self.price_field = ft.TextField(label="Стоимость тренировки", value="1000",
                                        input_filter=ft.NumbersOnlyInputFilter())
        self.goals_field = ft.TextField(label="Цели (через запятую)")
        self.notes_field = ft.TextField(label="Заметки", multiline=True)

    def on_phone_focus(self, e):
        if not e.control.value:
            e.control.value = "+7 ("
            self._last_phone_val = "+7 ("
            e.control.update()

    def on_phone_change(self, e):
        v = e.control.value
        last_v = self._last_phone_val
        is_deletion = len(v) < len(last_v)

        if is_deletion:
            if v in ["+7 (", "+7 ", "+7", "+", ""]:
                e.control.value = ""
            else:
                e.control.value = v
            self._last_phone_val = e.control.value
            e.control.update()
            return

        digits = "".join([c for c in v if c.isdigit()])
        if digits.startswith("7") or digits.startswith("8"):
            digits = digits[1:]

        digits = digits[:10]

        res = "+7 ("
        if len(digits) >= 1:
            res += digits[:min(len(digits), 3)]
        if len(digits) >= 4:
            res += ") " + digits[3:min(len(digits), 6)]
        if len(digits) >= 7:
            res += "-" + digits[6:min(len(digits), 8)]
        if len(digits) >= 9:
            res += "-" + digits[8:min(len(digits), 10)]

        if len(digits) == 3:
            res += ") "
        elif len(digits) == 6:
            res += "-"
        elif len(digits) == 8:
            res += "-"

        e.control.value = res
        self._last_phone_val = res
        e.control.update()

    def build(self) -> ft.View:
        return ft.View(
            route="/add_client",
            controls=[
                ft.AppBar(title=ft.Text("Добавить клиента"), bgcolor=ft.Colors.OUTLINE_VARIANT),
                self.name_field,
                self.phone_field,
                self.price_field,
                self.goals_field,
                self.notes_field,
                ft.Row(
                    [
                        ft.ElevatedButton("Сохранить", on_click=self.save_client),
                        ft.TextButton("Отмена", on_click=self.cancel)
                    ],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.START
        )

    def save_client(self, e):
        # Валидация
        if not self.name_field.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("Имя обязательно"))
            self.page.overlay.append(self.page.snack_bar)
            self.page.snack_bar.open = True
            self.page.update()
            return

        goals = [g.strip() for g in self.goals_field.value.split(",")] if self.goals_field.value else []

        phone = self.phone_field.value
        if phone == "+7 (":
            phone = ""

        client = Client(
            name=self.name_field.value,
            phone=phone,
            workout_price=int(self.price_field.value or 1000),
            goals=goals,
            notes=self.notes_field.value or ""
        )
        self.client_service.add_client(client)
        self.page.go("/clients")
        self.page.snack_bar = ft.SnackBar(ft.Text("Клиент добавлен"))
        self.page.overlay.append(self.page.snack_bar)
        self.page.snack_bar.open = True
        self.page.update()

    def cancel(self, e):
        self.page.go("/clients")
        self.page.update()
