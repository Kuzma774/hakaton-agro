from seleniumbase import SB
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import os
import time

class WhatsAppScraper:
    def __init__(self, chat_name, output_file="whatsapp_chat_log.txt", wait_qr=30, wait_chat=5):
        self.chat_name = chat_name
        self.output_file = output_file
        self.wait_qr = wait_qr
        self.wait_chat = wait_chat
        self.all_text = []

    def scroll_up_to_top(self, driver, max_empty_tries=10, delay=2):
        last_count = 0
        empty_tries = 0

        while empty_tries < max_empty_tries:
            messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-")]//span')
            current_count = len(messages)

            if current_count == last_count:
                empty_tries += 1
            else:
                empty_tries = 0
                last_count = current_count

            ActionChains(driver)\
                .scroll_to_element(messages[0])\
                .perform()
                
            time.sleep(delay)

        print("Достигнут верх чата (история больше не загружается)")

    def save_to_file(self):
        output_path = os.path.abspath(self.output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.all_text))
        print(f"Сообщения сохранены в: {output_path}")

    def run(self):
        with SB(test=True, uc=True) as sb:
            sb.open("https://web.whatsapp.com/")
            print("Ожидание сканирования QR-кода...")
            sb.sleep(self.wait_qr)

            sb.type('[aria-placeholder="Поиск"]', f"{self.chat_name}\n")
            sb.sleep(3)

            print("Открываем чат...")
            sb.click(f'span:contains("{self.chat_name}")')
            sb.sleep(self.wait_chat)

            print("Ожидаем загрузку чата...")
            sb.sleep(30)
            try:
                print("Ищем кнопку 'Показать сообщения'...")
                sb.click('[class="x14m1o6m x150wa6m x1b9z3ur x9f619 x1rg5ohu x1okw0bk x193iq5w x123j3cw xn6708d x10b6aqq x1ye3gou x13a8xbf xdod15v x2b8uid x1lq5wgf xgqcy7u x30kzoy x9jhf4c"]')
                print("Клик по кнопке выполнен.")
                sb.sleep(120)
            except:
                print("Кнопка 'показать сообщения' не найдена — возможно, всё уже загружено.")

            sb.sleep(10)

            print("Начинаем прокрутку вверх...")
            self.scroll_up_to_top(sb.driver, max_empty_tries=10, delay=2)

            messages = sb.driver.find_elements(By.XPATH, '//div[contains(@class, "message-")]//span')
            print("Найдено сообщений:", len(messages))
            
            texts = [msg.text.strip() for msg in messages if msg.text.strip()]
                    
            sb.sleep(10)

            self.all_text.extend(texts)

        self.save_to_file()

if __name__ == "__main__":
    scraper = WhatsAppScraper(chat_name="Учебный чат Прогресс Агро")
    scraper.run()