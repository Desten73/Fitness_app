from playwright.sync_api import sync_playwright, expect
import time

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # We need to find the port. Flet by default might use a random one if not specified or 8550 if set.
        # But wait, usually flet starts a web server.
        try:
            page.goto("http://localhost:8550")
            page.wait_for_timeout(3000)

            # Take screenshot of home page
            page.screenshot(path="verification/home_page.png")
            print("Home page screenshot taken")

            # Navigate to Exercises
            page.get_by_text("Упражнения").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="verification/exercises_page.png")
            print("Exercises page screenshot taken")

            # Click Add Exercise
            page.get_by_text("Добавить упражнение").click()
            page.wait_for_timeout(1000)
            page.get_by_label("Наименование упражнения").fill("Приседания")
            page.get_by_text("Сохранить").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="verification/exercises_list.png")
            print("Exercises list screenshot taken")

            # Go back home
            page.get_by_role("button").first.click() # Back arrow
            page.wait_for_timeout(1000)

            # Go to Programs
            page.get_by_text("Тренировочная программа").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="verification/programs_page.png")
            print("Programs page screenshot taken")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
