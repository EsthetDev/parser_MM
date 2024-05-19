import pickle
import random
import time
from bs4 import BeautifulSoup, element
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class SG:
    # example
    __proxy = ['123.45.678.901:2345']
    __user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.99 Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0 Unique/97.7.7239.70',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/118.0.2088.68 Version/17.0 Mobile/15E148 Safari/604.1'
    ]

    @classmethod
    def get_proxy(cls):
        return random.choice(cls.__proxy)

    @classmethod
    def get_user_agent(cls):
        return random.choice(cls.__user_agent)


class ParserMM:
    def __init__(
            self,
            target: str,
            count_item_cards: int,
            max_page: int,
            max_cycle_func_repeat: int,
            user_login: str = None,
            is_use_proxy = True,
            is_headless = True,
    ):
        self.__baseURL = 'https://megamarket.ru'
        self.__count_item_cards = int(count_item_cards)
        self.__max_cycle_func_repeat = int(max_cycle_func_repeat)
        self.__max_page = int(max_page)
        self.__user_login = user_login
        self.__is_use_proxy = is_use_proxy
        self.__is_headless = is_headless
        self.__target = target.replace(' ', '%20')
        self.__page = 1
        self.__delimiter_url = None
        self.__current_url = None
        self.__source_html_pages = []
        self.__out_items = []

    def __repr__(self):
        return ('ParserMM(user_login={0}, '
                'target={1}, '
                'count_item_cards={2}, '
                'max_page={3}, '
                'max_cycl_f_rep={4})').format(self.__user_login,
                                              self.__target,
                                              self.__count_item_cards,
                                              self.__max_page,
                                              self.__max_cycle_func_repeat)

    def __get_text_from_WebEl(self, By_what, value):
        try:
            text = self.__driver.find_element(By_what, value).text
        except Exception:
            text = None

        return text

    def __get_new_driver(self, url: str):
        self.__chrome_options = webdriver.ChromeOptions()
        self.__chrome_options.add_experimental_option(
            "prefs",
            {"profile.default_content_setting_values.notifications": 2}
        )
        self.__chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.__chrome_options.add_argument(f'user-agent={SG.get_user_agent()}')
        self.__chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.__chrome_options.add_argument('--no-sandbox')
        if self.__is_use_proxy:
            self.__chrome_options.add_argument(f'--proxy-server={SG.get_proxy()}')
        if self.__is_headless:
            self.__chrome_options.add_argument('--headless')

        self.__driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.__chrome_options
        )

        self.__add_cookies(url=url)

    def __check_driver(self, url):
        try:
            self.__driver.get_cookies()
            time.sleep(1)
            self.__driver.get(url=url)
            self.__check_captcha_holder()
        except Exception as ex:
            print(ex)
            self.__get_new_driver(url)

    def __add_cookies(self, url: str):
        self.__driver.get(url=url)
        WebDriverWait(self.__driver, 15).until(
            ec.presence_of_element_located((By.TAG_NAME, "html"))).is_displayed()

        self.__check_captcha_holder()
        is_disappeared = True
        if (self.__page == 1) and self.__user_login:
            self.__driver.delete_all_cookies()

            file_path = f'parserMM/cookies/{self.__user_login}-cookies'
            with open(file_path, 'rb') as file:
                for cookie in pickle.load(file):
                    self.__driver.add_cookie(cookie)

            self.__driver.refresh()

            is_disappeared = WebDriverWait(self.__driver, 15).until(
                ec.presence_of_element_located((By.TAG_NAME, "html"))).is_displayed()

            self.__check_captcha_holder()

            is_disappeared = WebDriverWait(self.__driver, 15).until(
                ec.presence_of_element_located((By.TAG_NAME, "html"))).is_displayed()
        return is_disappeared

    def save_cookies(self):
        old_is_headless, self.__is_headless = self.__is_headless, False
        self.__get_new_driver(url=self.__baseURL)
        self.__is_headless = old_is_headless

        WebDriverWait(self.__driver, 15).until(
            ec.presence_of_element_located((By.TAG_NAME, "html"))).is_displayed()

        input('Введи единицу, когда закончил')

        file_path = f'parserMM/cookies/{self.__user_login}-cookies'
        pickle.dump(self.__driver.get_cookies(), open(file_path, 'wb'))

        time.sleep(1)

        self.__driver.refresh()

    def __check_captcha_holder(self):
        try:
            self.__driver.find_element(By.ID, 'captcha-holder')
            # solver = TwoCaptcha(...)
            # Решение капчи через сервис TwoCaptcha
            #

        except Exception:
            pass

    def __save_source_html(self):
        def get_targetURL():
            if self.__page == 1:
                return self.__baseURL + f'/catalog/?q=' + self.__target
            elif self.__delimiter_url:
                first, second = self.__current_url.split(self.__delimiter_url)
                return first + f'page-{self.__page}' + self.__delimiter_url + second
            elif self.__current_url:
                return self.__current_url + f'page-{self.__page}'
            else:
                return self.__baseURL + f'/catalog/?q=' + self.__target

        def save_current_and_delimiter_url():
            if self.__page == 1:
                self.__current_url = self.__driver.current_url
                if '#?related_search' in self.__current_url:
                    self.__delimiter_url = '#?related_search'
                elif '?q' in self.__current_url:
                    self.__delimiter_url = '?q'

        targetURL = get_targetURL()

        self.__check_driver(url=targetURL)
        is_disappeared = WebDriverWait(self.__driver, 15).until(
            ec.presence_of_element_located((By.TAG_NAME, "html"))).is_displayed()

        self.__check_captcha_holder()

        if is_disappeared:
            self.__source_html_pages.append(self.__driver.page_source)
            save_current_and_delimiter_url()

        return is_disappeared

    def __save_item_cards(self):
        for src in self.__source_html_pages:
            soup = BeautifulSoup(src, 'lxml')
            items_divs = soup.find_all('div', class_='catalog-item-mobile')

            for item in items_divs:
                item_block = item.find('div', class_='item-block')
                item_link = item.find('div', class_='item-image')
                if isinstance(item_link, element.Tag):
                    link_block = item_link.find('a')
                    start = str(link_block).find('href="')
                    end = str(link_block).find('">', start)
                    link = self.__baseURL + str(link_block)[start + 6:end]
                    item_info = item_block.find('div', class_='item-info')
                    item_price_block = item_info.find(
                        'div', class_='inner catalog-item-mobile__prices-container')
                    item_money = item_price_block.find('div', class_='item-money')
                    item_price = item_money.find('div', class_='item-price')
                    item_price_result = item_price.find('span').get_text()
                    item_bonus = item_money.find('div', class_='item-bonus')
                    if isinstance(item_bonus, element.Tag):
                        item_bonus_loyalty = item_bonus.find(
                            'div', class_='money-bonus xs money-bonus_loyalty')
                        item_bonus_amount = item_bonus_loyalty.find(
                            'span', class_='bonus-amount').get_text()

                        name_item = item_info.find(
                            'div', class_='item-title'
                        ).get_text().replace('\t', '').replace('\n', '')

                        bonus = int(item_bonus_amount.replace(' ', ''))
                        price = int(item_price_result[0:-1].replace(' ', ''))
                        item_bonus_percent = round(bonus / price * 100)
                        final_price = round(price - bonus * 0.8)

                        self.__out_items.append({'price': item_price_result[0:-2],
                                                 'bonus amount': item_bonus_amount,
                                                 'bonus percent': item_bonus_percent,
                                                 'link': link,
                                                 'name item': name_item,
                                                 'final price': final_price,
                                                 'user login': self.__user_login,
                                                 'prime bonus': None,
                                                 'salesman': {'name': None,
                                                              'rating': None,
                                                              'rating item': None,
                                                              'no cancel': None,
                                                              'on market': None,
                                                              }
                                                 }
                                                )

    def __save_all_info(self):
        def get_info_about_salesman():
            is_clicked = False
            count = 0
            while not is_clicked and count < 6:
                count += 1
                self.__driver.execute_script(f"window.scrollTo(0, {200 * count})")
                try:
                    self.__driver.find_element(
                        By.CSS_SELECTOR,
                        '#app > main > div > div.page-catalog-details > div:nth-child(3) > article > div > div > div.pdp-first-screen-regular__wrapper > div.offers-info.pdp-first-screen-regular__offers-info > div > div.pdp-merchant-rating-block.pdp-sales-block__merchant-rating-block > div:nth-child(2) > div').click()
                    is_clicked = True
                except Exception:
                    pass
            rating_salesman, text_elements = None, [None, None, None]
            if is_clicked:
                rating_salesman = self.__get_text_from_WebEl(By.CLASS_NAME,
                    'pdp-merchant-logo-with-name-and-rating__rating-number')

                try:
                    elements = self.__driver.find_elements(
                        By.CLASS_NAME,
                        'pdp-merchant-rating-table__row-value')

                    for i in range(len(elements)):
                        text_elements[i] = elements[i].text

                except Exception:
                    pass

            return rating_salesman, text_elements

        action_chains = ActionChains(self.__driver)
        is_all_right = True
        for item in self.__out_items:
            if not (item["prime bonus"] and item["salesman"]["name"]):
                try:
                    time.sleep(5)
                    self.__check_driver(url=item['link'])

                    is_disappeared = WebDriverWait(self.__driver, 15).until(
                        ec.presence_of_element_located((By.TAG_NAME, "html"))).is_displayed()

                    if is_disappeared:
                        try:
                            self.__driver.find_element(By.CSS_SELECTOR,
                                                       '#app > div.my-modal-plugin-container > div > div > div')
                            #################################################################
                            self.__driver.set_window_size(700, 700)
                            action_chains.move_by_offset(350, 350).click().perform()

                        except Exception:
                            pass

                        prime_bonus = self.__get_text_from_WebEl(By.CSS_SELECTOR,
                            '#app > main > div > div.page-catalog-details > div:nth-child(3) > article > div > div > div.pdp-first-screen-regular__wrapper > div.offers-info.pdp-first-screen-regular__offers-info > div > div.pdp-cashback-table.pdp-sales-block__cashback-table > div.pdp-cashback-table__not-highlighted-groups > div > div.money-bonus.transparent.money-bonus_loyalty.money-bonus_with-plus.pdp-cashback-table__money-bonus > span')

                        name_com = self.__get_text_from_WebEl(By.CLASS_NAME,
                            'pdp-merchant-rating-block__merchant-name')

                        # Клик по имени продавца
                        rating_salesman, elements = get_info_about_salesman()

                        # Записать все данные
                        item.update(
                            {
                                'prime bonus': prime_bonus,
                                'salesman': {'name': name_com,
                                             'rating': rating_salesman,
                                             'rating item': elements[0],
                                             'no cancel': elements[1],
                                             'on market': elements[2]
                                             }
                            }
                        )

                        # Обновить фин ц
                        price = int(item['price'].replace(' ', ''))
                        bonus = int(item['bonus amount'].replace(' ', ''))
                        if item['prime bonus']:
                            bonus += int(item['prime bonus'].replace(' ', ''))

                        item['final price'] = round(price - bonus * 0.8)

                    else:
                        is_all_right = False

                except Exception:
                    time.sleep(15)

        return is_all_right

    def get_items(self):
        def cycle_for_func(func):
            def cycle(func, count):
                if count > self.__max_cycle_func_repeat:
                    return False
                try:
                    result = func()
                    return result
                except Exception:
                    return cycle(func, count+1)

            return cycle(func, 1)

        for self.__page in range(1, self.__max_page+1):
            result = cycle_for_func(self.__save_source_html)
            if (not result) and self.__page == 1:
                return None

        self.__save_item_cards()
        self.__out_items.sort(
            key=lambda item: item['bonus percent'],
            reverse=True)
        self.__out_items = self.__out_items[:self.__count_item_cards]

        cycle_for_func(self.__save_all_info)

        self.__driver.close()
        self.__driver.quit()

        return self.__out_items


def print_out_items(items):
    for item in items:
        print(item)


def main():
    parser = ParserMM(
        target='iphone 13',
        count_item_cards=1,
        max_page=1,
        max_cycle_func_repeat=3,
        user_login=None,
        is_use_proxy=False,
        is_headless=False
    )

    print_out_items(parser.get_items())


if __name__ == '__main__':
    main()
