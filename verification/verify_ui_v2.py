from playwright.sync_api import sync_playwright, expect
import time
import os

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # We need to use a port that's likely to be open or check the logs.
            # Assuming main.py is running on default port if we could start it.
            # Since I can't easily start the server and connect to it reliably in this environment's playwright,
            # I will focus on making sure the code is correct.
            # However, I can try one more time with a longer sleep.

            page.goto("http://localhost:8550")
            page.wait_for_timeout(5000)

            # Take screenshot of home page
            page.screenshot(path="verification/home_page_v2.png")

            # Check for buttons
            if page.get_by_text("Упражнения").is_visible():
                 page.get_by_text("Упражнения").click()
                 page.wait_for_timeout(2000)
                 page.screenshot(path="verification/exercises_page_v2.png")
            else:
                 print("Упражнения button not found")

        except Exception as e:
            print(f"Error during verification: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
