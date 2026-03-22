"""
fitness_trainer_app/
├── main.py                 # Точка входа, запуск Flet-приложения
├── models/                 # Модели данных
│   └── client.py           # Класс Client (данные о клиенте)
├── database/               # Работа с базой данных
│   ├── db_interface.py     # Абстрактный интерфейс для БД
│   └── tinydb_client.py    # Реализация для TinyDB
├── business_logic/         # Бизнес-логика
│   └── client_service.py   # Операции с клиентами
├── views/                  # Экраны приложения (Flet)
│   ├── main_view.py        # Главный экран со списком клиентов
│   ├── client_details.py   # Карточка клиента
│   └── add_client.py       # Форма добавления клиента
├── utils/                  # Вспомогательные функции
│   └── helpers.py          # Форматирование дат, валидация и т.п.
└── assets/                 # Иконки, изображения (опционально)
    └── icon.png
"""

import flet as ft
from database.tinydb_client import TinyDBClient
from business_logic.client_service import ClientService
from views.main_view import MainView


def main(page: ft.Page):
    # Настройки страницы
    page.title = "Fitness Trainer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # Инициализация базы данных и сервисов
    db = TinyDBClient("fitness_trainer.json")
    client_service = ClientService(db)

    # Создаём главное окно
    main_view = MainView(page, client_service)
    page.views.append(main_view.build())
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
