import json
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

option = Options()
option.binary_location = r"Тут путь до вашего Firefox"
option.set_preference('dom.webdriver.enabled', False)
browser = webdriver.Firefox(options=option)


def get_catalog_hrefs():
    """Каталог Электроники"""
    d = {}
    browser.get("https://www.wildberries.ru/catalog/elektronika")
    time.sleep(2)
    all_hrefs = browser.find_elements(By.CLASS_NAME, "j-menu-item")

    for href in all_hrefs:
        name = href.text
        href = href.get_attribute("href")
        d[name] = href

    with open("goods/WB_links.json", "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)


def from_catalog_hrefs_cards():
    """Ссылки на карточки с Ссылок Каталога"""
    d_cards_hrefs = {}
    with open("goods/WB_links.json", "r", encoding="utf-8") as file:
        wb_links = json.load(file)
        with open("WB_Goods.json", "w", encoding="utf-8") as file_goods:
            for key in wb_links:
                link = wb_links[key]
                browser.get(link)
                time.sleep(5)
                all_hrefs = browser.find_elements(By.CLASS_NAME, "product-card__wrapper")
                d_cards_hrefs[link] = {"links":
                                           [href.find_element(By.TAG_NAME, "a").get_attribute("href") for href in
                                            all_hrefs],
                                       "name": key}
            json.dump(d_cards_hrefs, file_goods, indent=4, ensure_ascii=False)


def parser_cards():
    """Парсинг Карточки с товаром"""
    d_cards = {}
    with open("WB_Goods.json", "r", encoding="utf-8") as file:
        wb_goods = json.load(file)
        for key in wb_goods.keys():
            links = wb_goods[key]["links"]
            for link in links[:20]:  # Здесь выбирайте какое кол-во товаров надо спарсить
                browser.get(link)
                time.sleep(2)
                try:
                    btn = browser.find_element(By.XPATH,
                                               "/html/body/div[1]/main/div[2]/div/div[3]/div/div[3]/section/div[3]/div[1]/div/div[2]/div[2]/button")
                    # кнопка для открытия полного описания
                except Exception:
                    btn = ""

                if btn:
                    ActionChains(browser) \
                        .scroll_by_amount(0, 1200) \
                        .perform()
                    time.sleep(2)

                    btn.click()

                description = browser.find_element(By.CLASS_NAME, "collapsable__text").text

                more_info = browser.find_elements(By.CLASS_NAME, 'product-params__table')
                name = browser.find_element(By.CLASS_NAME, "product-page__header-wrap").find_element(By.TAG_NAME,
                                                                                                     "h1").text
                img = browser.find_element(By.CLASS_NAME, "zoom-image-container").find_element(By.TAG_NAME,
                                                                                               "img").get_attribute(
                    "src")
                try:
                    price = browser.find_element(By.CLASS_NAME, "price-block__final-price").text
                except:
                    price = "Нет в наличии"

                list_1 = []
                time.sleep(2)

                for row in more_info:

                    more_info_two = row.find_elements(By.CLASS_NAME, "product-params__row")

                    for s in more_info_two:

                        name_inf = s.find_element(By.TAG_NAME, "th").find_element(By.TAG_NAME, "span").text
                        val_inf = s.find_element(By.TAG_NAME, "td").find_element(By.TAG_NAME, "span").text

                        if val_inf and name_inf:
                            list_1.append((name_inf, val_inf))

                    d_cards[link] = {
                        'description': description,
                        'price': price,
                        'name': name,
                        'img': img,
                        'more_info': {
                            "information": list_1

                        }
                    }
            with open(f"goods/{wb_goods[key]['name']}.json", "w", encoding="utf-8") as file_Wb:
                json.dump(d_cards, file_Wb, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    get_catalog_hrefs()
    from_catalog_hrefs_cards()
    parser_cards()
    browser.quit()
