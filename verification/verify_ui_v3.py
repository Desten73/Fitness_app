from playwright.sync_api import sync_playwright, expect
import time
import os

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("http://localhost:8550")
            page.wait_for_timeout(5000)

            # Click Exercises
            page.get_by_text("Упражнения").click()
            page.wait_for_timeout(2000)
            page.screenshot(path="verification/exercises_page_v3.png")

            # Add an exercise
            page.get_by_text("Добавить упражнение").click()
            page.wait_for_timeout(1000)
            page.get_by_label("Наименование упражнения").fill("Приседания")
            page.get_by_text("Сохранить").click()
            page.wait_for_timeout(2000)
            page.screenshot(path="verification/exercises_list_v3.png")

            # Go back home
            page.get_by_role("button").first.click()
            page.wait_for_timeout(1000)

            # Go to Programs
            page.get_by_text("Тренировочная программа").click()
            page.wait_for_timeout(2000)
            page.screenshot(path="verification/programs_page_v3.png")

            # Add a program
            page.get_by_text("Добавить тренировочную программу").click()
            page.wait_for_timeout(1000)
            # Need a client. Let's assume there are none yet in a fresh DB.
            # But wait, I can add a client first if needed.
            page.screenshot(path="verification/add_program_dialog_v3.png")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="verification/error_v3.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
