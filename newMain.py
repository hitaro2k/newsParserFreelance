#ПЕРЕД ЗАПУСКОМ ПРОПИШИТЕ pip install -r requirements.txt или же 
#pip install selenium pip install matplotlib pip install numpy
import re
import numpy as np
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import matplotlib.pyplot as plt
from selenium.webdriver.support.wait import WebDriverWait
import time


def get_browser():
    options = Options()
    options.headless = True
    browser = webdriver.Chrome(options=options)
    return browser


def get_quarter(month, year):
    #Функция которая считает квартлы, полгода = квартал.
    # Обычное условие которое в будущем поможет считать квартыл в виде quartals[то что возвращает эта функция]
    if year == 2024:
        if 1 <= month <= 6:
            return "Q1"
        elif 7 <= month <= 12:
            return "Q2"
    elif year == 2023:
        if 1 <= month <= 6:
            return "Q3"
        elif 7 <= month <= 12:
            return "Q4"
    elif year == 2022:
        if 1 <= month <= 6:
            return "Q5"
        elif 7 <= month <= 12:
            return "Q6"
    return None


def scrap_pl_country(browser):
    #Словарь месяцов в числовом формате
    polish_months = {
        "sty": 1, "lut": 2, "mar": 3, "kwi": 4, "maj": 5, "cze": 6,
        "lip": 7, "sie": 8, "wrz": 9, "paź": 10, "lis": 11, "gru": 12
    }
    #Тот самый обьект в который записываем счетчик новостей (сколько новостей за даты)
    quartersPL = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0,
        "Q5": 0,
        "Q6": 0
    }
    #Счетчик для страницы
    current_page = 1

    #Обязательно все оборачиваем в try except чтобы не было вылета програмы
    try:
        while True: # Убираем ограничение по количеству страниц
            url = f"https://wyborcza.pl/0,128956.html?tag=wojna+w+Ukrainie&str={current_page}"
            browser.get(url) #Запускаем эмулятор браузера
            browser.implicitly_wait(10) #Ставим неебольшую задержку
            li_elements = browser.find_elements(By.CSS_SELECTOR, "ul.index--list > li.index--list-item") #Ищем все элементы которые нам нужны
            for li in li_elements: # Проходимся по ним циклом фор,чтобы получить дату для того чтобы записать в кварталы
                time_element = li.find_element(By.CSS_SELECTOR, 'time.index--author').get_attribute('datetime').strip()
                day, month_str, year = time_element.split()
                day = int(day)
                year = int(year)
                month = polish_months[month_str]
                if year == 2024 and month == 5: #тут можно изменить дату до которой искать новости, так в каждой функции
                    return quartersPL
                #Передаем месяц - год в функцию которая вернет квартал
                quarter = get_quarter(month, year)
                if quarter:
                    quartersPL[quarter] += 1 #Та самая имплементация о которой я говорил выше в функции get_quarter
            current_page += 1
    finally:
        #Закрываем браузер ,выводим результат и возвращаем его в виде словаря кварталов
        browser.quit()
        print(quartersPL)
        return quartersPL


def scrap_de_country(browser):
    quartersDE = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0,
        "Q5": 0,
        "Q6": 0
    }
    current_page = 1
    try:
        while True:  # Убираем ограничение по количеству страниц
            url = f"https://www.tagesschau.de/thema/ukraine?pageIndex={current_page}"
            browser.get(url)
            browser.implicitly_wait(10)
            teaser_divs = browser.find_elements(By.XPATH,
                                                '//div[contains(@class, "columns twelve teasergroup")]//div[contains(@class, "teaser") and contains(@class, "teaser--small")]')
            teaser_dates = browser.find_elements(By.CLASS_NAME, "teaser__date")#Тоже самое что и в функции с польскими новостями поиск элементов и запуск браузера
            for teaser_date in teaser_dates:
                date_str = teaser_date.text.strip()  #Извлекаем текст и методом стрип() удаляем любые начальные и конечные пробелы
                date_obj = datetime.strptime(date_str, "%d.%m.%Y • %H:%M Uhr") #Этот код преобразует строку даты и времени
                month = date_obj.month
                year = date_obj.year

                #Все также как и в польском функции
                if year == 2024 and month == 5:
                    return quartersDE

                quarter = get_quarter(month, year)
                if quarter:
                    quartersDE[quarter] += 1
            current_page += 1
    finally:
        browser.quit()
        print(quartersDE)

        return quartersDE


def scrap_lv_country(browser):
    quartersLV = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0,
        "Q5": 0,
        "Q6": 0
    }
    current_page = 1

    try:
        while True:  # Убираем ограничение по количеству страниц
            url = f"https://www.lsm.lv/temas/krievijas-iebrukums-ukraina/latvijas-atbalsts-ukrainai/?p={current_page}"
            browser.get(url)
            timeline_blocks = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.timeline-block.large.key")))
            #Все точно также как и в других функциях только мы даем немного больше времени на прогрузку контента 
            for block in timeline_blocks:
                try:
                    time_block = block.find_element(By.CSS_SELECTOR, "time.timeline-block__timeline-time.brand-mmp-tx")
                    span_element = time_block.find_element(By.TAG_NAME, "span")
                    span_text = span_element.text.strip()
                    day, month, year = map(int, span_text.split('.'))
                    #Тут были проблемы с выводом года,Год был в формате 24, и я просто решил добавить 2000 дальше все как и везде
                    yearTrue = year + 2000
                    if yearTrue <= 2024 and month <= 5:
                        return quartersLV

                    quarter = get_quarter(month, yearTrue)
                    if quarter:
                        quartersLV[quarter] += 1

                except NoSuchElementException:
                    pass

            current_page += 1

    finally:
        print(quartersLV)
        browser.quit()
        return quartersLV


def scrap_sw_country(browser):
    #Тут уже немного интереснее ведь я добавляю функцию которая преобразовывает дату и возвращает месяц - год
    def extract_month_year_from_time_element(time_element):
        datetime_str = time_element.get_attribute("datetime")
        dt = datetime.fromisoformat(datetime_str)
        return dt.month, dt.year

    current_offset = 0
    quartersSW = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0,
        "Q5": 0,
        "Q6": 0
    }

    try:
        while True:# Убираем ограничение по количеству страниц
            url = f"https://www.dn.se/om/ukraina/?offset={current_offset}"
            browser.get(url)
            #На сайте стоял куки попап и мне пришлось чтобы прогружало весь контент закрывать его,сообвстенно нашел его и закрыл
            if current_offset == 0:
                agree_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
                )
                agree_button.click()

            listing_div = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "timeline-page__listing"))
            )
            #Дальше все как и везде поиск времени - преобразование в формат с 05.05.2024 в 5 2024
            teaser_links = listing_div.find_elements(By.CLASS_NAME, "timeline-teaser__wrapper")

            for link in teaser_links:
                try:
                    time_element = link.find_element(By.TAG_NAME, "time")
                    month, year = extract_month_year_from_time_element(time_element)

                    if year == 2024 and month == 5:
                        return quartersSW

                    quarter = get_quarter(month, year)
                    if quarter:
                        quartersSW[quarter] += 1
                except Exception as e:
                    print(f"Failed to process link {link.get_attribute('href')}: {e}")
            #На этом новостном сайте нужно было нажимать кнопку далее чтобы переходить на другую страницу
            #Сообвстенно я добавил скролл вниз,чтобы найти эту кнопку и нажал
            try:
                next_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "pagination__next"))
                )
                browser.execute_script("arguments[0].scrollIntoView(true);", next_button)
                browser.execute_script("arguments[0].click();", next_button)
                #Переключение страницы
                current_offset += 24
                time.sleep(2)
            except Exception as e:
                print(f"Failed to click next button: {e}")
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit()
        print(quartersSW)
        return quartersSW


def scrap_ltv_country(browser):
    quartersLTV = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0,
        "Q5": 0,
        "Q6": 0
    }

    browser.get("https://www.lrt.lt/tema/rusijos-karas-pries-ukraina")
    #Тут также как и у функции с Швецией ,были куки попапы,я их закрываю,но сначала нахожу общее окно,а потом и кнопку
    try:
        cookie_dialog = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "CybotCookiebotDialog"))
        )

        allow_button = cookie_dialog.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        allow_button.click()

    except Exception as e:
        print(e)


    try:
        while True:# Убираем ограничение по количеству страниц
            category_list_div = browser.find_element(By.ID, "category_list")
            cols = category_list_div.find_elements(By.CLASS_NAME, 'col')

            reached_date = False

            for col in cols:

                date_element = col.find_element(By.CLASS_NAME, 'info-block__text')
                date_text = date_element.text
                #Тут пришлось поработать с регулярными варжениями чтобы вырезать дату и  далее все как везде
                match = re.search(r'(\d{4})\.(\d{1,2})', date_text)
                if match:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    if year == 2024 and month == 5:
                        reached_date = True
                        break

            if reached_date:
                break
            else:
                #На сайте швеции была загвоздка,контент подгружался динамически,пришлось искать эту кнопку ставить счетчик что весь контент записан,
                # после нажимать эту кнопку . Логика в функции немного тут я сначала достигаю даты которую я указал,после чего начинаю записывать новости в свои кварталы.
                #  В остальных функциях я все делал тут и сейчас
                load_more_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//a[@class="btn btn--lg section__button" and contains(@onclick, "_load_more")]'))
                )
                load_more_button.click()

        for col in cols:
            date_element = col.find_element(By.CLASS_NAME, 'info-block__text')
            date_text = date_element.text

            match = re.search(r'(\d{4})\.(\d{1,2})', date_text)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))

                quarter = get_quarter(month, year)
                if quarter:
                    quartersLTV[quarter] += 1
    finally:
        browser.quit()
        print(quartersLTV)
        return quartersLTV


def scarp_est_country(browser):
    quartersEst = {
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0,
        "Q5": 0,
        "Q6": 0
    }
    current_page = 1
    consent_clicked = False

    try:

        while True:# Убираем ограничение по количеству страниц
            url = f"https://news.err.ee/search?phrase=Ukraine&page={current_page}"
            browser.get(url)
            #Все также как и в остальных функциях,тут не динамическая подгрузка также работаю тут и сейчас
            content_divs = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".left-block .mb24.search-content.ng-scope"))
            )

            for content_div in content_divs:
                text_field = content_div.find_element(By.CSS_SELECTOR, ".search-lead.giveMeEllipsis.ng-binding")
                text = text_field.text
                #Дата новостей указывалась в большом тексте в новостях,также пришлось с помощью регулярки вырезать ее и также как и везде сравнивать и добавлять
                match = re.search(r'\b\d{2}\.\d{2}\.\d{2}\b', text)
                if match:
                    date_str = match.group()
                    day, month_str, year_str = date_str.split('.')
                    month = int(month_str)
                    year = int(year_str)
                    yearThs = 2000 + year

                    quarter = get_quarter(month, yearThs)
                    if quarter:
                        quartersEst[quarter] += 1

                    if yearThs == 2024 and month == 5:
                        return quartersEst

            current_page += 1

    except Exception as e:
        print(e)
    finally:
        browser.quit()
        print(quartersEst)
        return quartersEst


def plot_news_dynamics(quarters_data):
    countries = list(quarters_data.keys())
    quarters = list(quarters_data[countries[0]].keys())  # Полагаем, что все страны имеют одинаковый набор кварталов

    # Преобразуем данные в формат, удобный для построения графика
    data = {country: [quarters_data[country][q] for q in quarters] for country in countries}

    # Создаем график
    fig, ax = plt.subplots(figsize=(12, 8))

    x = np.arange(len(quarters))  # позиции на оси X

    # Отрисовываем линии для каждой страны
    for country in countries:
        ax.plot(x, data[country], marker='o', label=country)

    # Настройки осей
    ax.set_xlabel('Quarters')
    ax.set_ylabel('Number of News Articles')
    ax.set_title('Dynamics of news about the war in Ukraine')
    ax.set_xticks(x)
    ax.set_xticklabels(quarters)
    ax.legend()

    # Добавляем сетку
    ax.grid(True, linestyle='--', alpha=0.7)

    # Показ графика
    plt.show()


def main():
    #Создаю эмуляторы браузеров 
    browser1 = get_browser()
    browser2 = get_browser()
    browser3 = get_browser()
    browser4 = get_browser()
    browser5 = get_browser()
    browser6 = get_browser()

    #Записываю результат кварталов в переменные и после передаю в словарь для отрисовки на графике
    quarters_data_pl = scrap_pl_country(browser1)
    quarters_data_de = scrap_de_country(browser2)
    quarters_data_lv = scrap_lv_country(browser3)
    quarters_data_sw = scrap_sw_country(browser4)
    quarters_data_ltv = scrap_ltv_country(browser5)
    quarters_data_est = scarp_est_country(browser6)
    quarters_data = {
        "Poland": quarters_data_pl,
        "Germany": quarters_data_de,
        "Latvia": quarters_data_lv,
        "Sweden": quarters_data_sw,
        "Lithuania": quarters_data_ltv,
        "Estonia" : quarters_data_est
    }
    plot_news_dynamics(quarters_data)


if __name__ == "__main__":
    main()