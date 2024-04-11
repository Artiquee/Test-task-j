import time
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium import webdriver
from logger import get_logger
from fake_useragent import UserAgent

TARGET_URL = 'https://realtylink.org/en/properties~for-rent'
logger = get_logger(__name__)

ua = UserAgent()
random_user_agent = ua.random

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument(f"user-agent={random_user_agent}")
driver = webdriver.Chrome(options=options)


def single_page_data():
    driver.implicitly_wait(2)
    title = driver.find_element(By.XPATH, '//*[@data-id="PageTitle"]').text
    price = driver.find_elements(By.CLASS_NAME, 'text-nowrap')[1].text
    price = price.split('/')[0]
    price = int(price[1:].replace(',', ''))
    full_address = driver.find_element(By.CLASS_NAME, 'pt-1').text
    address = ','.join(full_address.split(',')[:2])
    region = ','.join(full_address.split(',')[1:])
    try:
        description = driver.find_element(By.XPATH, '//*[@itemprop="description"]').text
    except:
        description = ''
    image_urls = driver.execute_script("""
        return window.MosaicPhotoUrls;
    """)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        bedrooms = driver.find_element(By.CSS_SELECTOR, 'div.col-lg-3.col-sm-6.cac').text[0]
    except:
        logger.error(f'NO BEDROOMS {driver.current_url}')
        bedrooms = 0

    try:
        bathrooms = driver.find_element(By.CSS_SELECTOR, 'div.col-lg-3.col-sm-6.sdb').text[0]
    except:
        logger.error(f'NO BATHROOMS {driver.current_url}')
        bathrooms = 0
    rooms = int(bedrooms) + int(bathrooms)
    area = driver.find_element(By.CLASS_NAME, 'carac-value').text
    return {
        "link": driver.current_url,
        "title": title,
        "region": region,
        "address": address,
        "description": description,
        "images": image_urls,
        "date": date,
        "price": price,
        "rooms": rooms,
        "area": area
    }


def get_first_page():
    first_items = driver.find_elements(By.CSS_SELECTOR, 'a.property-thumbnail-summary-link')
    driver.get(first_items[0].get_attribute("href"))
    time.sleep(1)
    current_page = driver.find_element(By.CSS_SELECTOR, 'li.pager-current').text
    if current_page[0] == 1:
        return
    else:
        driver.find_element(By.CLASS_NAME, 'goFirst').click()


def main() -> list:
    items = []
    driver.get(TARGET_URL)
    get_first_page()
    current_page = 1
    while current_page != 60:
        current_page = driver.find_element(By.CLASS_NAME, 'pager-current').text
        current_page = int(current_page.split(' ')[0])
        data = single_page_data()
        logger.info(f"{current_page} {data}")
        items.append(data)
        driver.find_element(By.CSS_SELECTOR, 'li.next').click()
        time.sleep(1)
    return items


if __name__ == '__main__':
    result = main()
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)
