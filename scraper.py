# scraper.py
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def init_driver(headless: bool = True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(), options=options)
    return driver

def hybrid_wait(driver, timeout: int = 30, check_interval: int = 3) -> bool:
    """Espera hasta timeout; cada check_interval seg compara longitud del HTML."""
    end = time.time() + timeout
    prev_len = len(driver.page_source)
    while time.time() < end:
        time.sleep(check_interval)
        curr_len = len(driver.page_source)
        if curr_len == prev_len:
            return True
        prev_len = curr_len
    return False

def scrape_page(page_num: int) -> list[dict]:
    """
    Abre la página indicada, selecciona 'SENTENCIAS ESCRITAS',
    espera carga híbrida y devuelve lista de dicts con los datos.
    """
    url = "https://tesauro.supersociedades.gov.co/results?restart=true#/"
    driver = init_driver()
    try:
        driver.get(url)
        # Hacer clic en 'SENTENCIAS ESCRITAS'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(.,'SENTENCIAS ESCRITAS')]")
            )
        ).click()
        # Navegar a la página específica, si la URL soporta paginación vía hash
        driver.get(f"{url}page/{page_num}")
        # Hybrid wait
        hybrid_wait(driver, timeout=30, check_interval=3)
        # Esperar al menos a un resultado
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.result_card"))
        )

        cards = driver.find_elements(By.CSS_SELECTOR, "div.result_card")
        data = []
        for idx, card in enumerate(cards, start=1):
            title = card.find_element(By.CSS_SELECTOR, "span.card__title").text.strip()
            date = card.find_element(
                By.XPATH,
                ".//div[@class='card__info-title' and normalize-space()='Fecha:']"
                "/following-sibling::div[@class='card__info-value']"
            ).text.strip()
            theme = card.find_element(
                By.XPATH,
                ".//div[@class='card__info-title' and normalize-space()='Tema:']"
                "/following-sibling::div[@class='card__info-value']"
            ).text.strip()
            data.append({
                "page": page_num,
                "card": idx,
                "title": title,
                "date": date,
                "theme": theme
            })
        return data

    finally:
        driver.quit()
