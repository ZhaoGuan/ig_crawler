#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import requests
import json
import mechanicalsoup
import random
import logging
import string
import re
from .config import sms_token


def get_random_identity(country):
    gender = random.choice(["male", "female"])
    logging.info("Gender: {}".format(gender))
    URL = "https://it.fakenamegenerator.com/gen-{}-{}-{}.php".format(gender, country, country)
    logging.info("Url generated: {}".format(URL))
    browser = mechanicalsoup.StatefulBrowser(
        raise_on_404=True,
        user_agent='MyBot/0.1'
    )
    page = browser.get(URL)
    address_div = page.soup.find(
        "div",
        {"class": "address"}
    )
    completename = address_div.find(
        "h3"
    )

    extra_div = page.soup.find(
        "div",
        {"class": "extra"}
    )

    all_dl = page.soup.find_all(
        "dl",
        {'class': 'dl-horizontal'}
    )

    birthday = all_dl[5].find("dd").contents[0]
    logging.info("Birthday: {}".format(birthday))

    return completename.contents[0], birthday


def get_password():
    a = string.ascii_letters + string.digits
    key = random.sample(a, 10)
    password = "".join(key)
    return password


class SmsPva:
    def __init__(self):
        self.token = sms_token
        # self.country = "US"
        self.country = "RU"
        self.service = "opt16"
        self.id = None
        self.number = None

    def get_balance(self):
        url = "http://smspva.com/priemnik.php?" \
              "metod={METHOD}" \
              "&service={SERVICE}" \
              "&apikey={API_KEY}".format(
            METHOD="get_userinfo", SERVICE="opt16", API_KEY=self.token
        )
        response = requests.get(url)
        json_data = json.loads(response.text)
        print(json_data)
        return float(json_data["balance"]), int(json_data["karma"])

    def get_price(self):
        url = "http://smspva.com/priemnik.php?" \
              "metod=get_service_price" \
              "&country={COUNTRY}" \
              "&service={SERVICE}" \
              "&apikey={API_KEY}".format(
            COUNTRY=self.country, SERVICE=self.service, API_KEY=self.token
        )
        response = requests.get(url)
        json_data = json.loads(response.text)
        print(json_data)
        if json_data["response"] == "1":
            return json_data["price"]
        else:
            return self.get_price()

    def get_number(self):
        url = "http://smspva.com/priemnik.php?" \
              "metod=get_number" \
              "&country={COUNTRY}" \
              "&service={SERVICE}" \
              "&apikey={API_KEY}".format(
            COUNTRY=self.country, SERVICE=self.service, API_KEY=self.token
        )
        response = requests.get(url)
        json_data = json.loads(response.text)
        print(json_data)
        if json_data["response"] == "1":
            self.id = json_data["id"]
            self.number = json_data["number"]
            return json_data["CountryCode"] + json_data["number"]
        else:
            time.sleep(60)
            return self.get_number()

    def get_number_count(self):
        url = "http://smspva.com/priemnik.php?" \
              "metod=get_count_new" \
              "&service={SERVICE}" \
              "&apikey={API_KEY}" \
              "&country={COUNTRY}".format(
            COUNTRY=self.country, SERVICE=self.service, API_KEY=self.token
        )
        response = requests.get(url)
        print(response.text)
        if json.loads(response.text)["total"] > 0:
            return True
        else:
            return False

    def get_proverka(self):
        url = "http://smspva.com/priemnik.php?" \
              "metod=get_proverka" \
              "&service={SERVICE}" \
              "&number={NUMBER}" \
              "&apikey={API_KEY}".format(
            SERVICE=self.service, API_KEY=self.token, NUMBER=self.number
        )
        response = requests.get(url)
        print(response.text)
        json_data = json.loads(response.text)
        if json_data["response"] is "ok":
            return False
        else:
            # self.ban()
            return True

    def ban(self):
        url = "http://smspva.com/priemnik.php?" \
              "metod=ban" \
              "&service={SERVICE}" \
              "&apikey={API_KEY}" \
              "&id={ID}".format(
            SERVICE=self.service, API_KEY=self.token, ID=self.id
        )
        response = requests.get(url)
        print(response.text)
        if json.loads(response.text)["response"] == "1":
            return False
        else:
            return True

    def get_sms(self):
        self.get_balance()
        count = 0
        url = "http://smspva.com/priemnik.php?" \
              "metod=get_sms" \
              "&country={COUNTRY}" \
              "&service={SERVICE}" \
              "&id={ID}" \
              "&apikey={API_KEY}".format(
            COUNTRY=self.country, SERVICE=self.service, API_KEY=self.token, ID=self.id
        )
        time.sleep(20)
        response = requests.get(url)
        json_data = json.loads(response.text)
        print(json_data)
        if json_data["response"] == "1":
            return json_data["sms"].replace(" ", "")
        elif json_data["response"] == "2":
            time.sleep(20)
            count += 1
            if count > 5:
                return False
            return self.get_sms()
        else:
            return False

    def denial(self):
        url = "http://smspva.com/priemnik.php?" \
              "metod=denial" \
              "&country={COUNTRY}" \
              "&service={SERVICE}" \
              "&id={ID}" \
              "&apikey={API_TOKEN}".format(
            COUNTRY=self.country, SERVICE=self.service, API_TOKEN=self.token, ID=self.id
        )
        response = requests.get(url)
        if json.loads(response.text)["response"] == "1":
            return True
        else:
            return False

    def get_the_number(self):
        balance, karma = self.get_balance()
        price = float(self.get_price())
        if balance > price and karma > 0:
            if self.get_number_count():
                number = self.get_number()
                return number
            else:
                return self.get_the_number()
        else:
            assert False is True, "balance or karma false!"

    def get_the_sms(self):
        sms = self.get_sms()
        return sms


def free_proxy():
    sockets = []
    # r = requests.get("https://www.sslproxies.org/")
    r = requests.get("https://www.us-proxy.org/")
    matches = re.findall(r"<td>\d+.\d+.\d+.\d+</td><td>\d+</td>", r.text)
    revised_list = [m1.replace("<td>", "") for m1 in matches]
    for socket_str in revised_list:
        data = socket_str[:-5].replace("</td>", ":")
        if "-" in data:
            pass
        else:
            sockets.append(data)
    return sockets


def proxy_test(proxy):
    print(proxy)
    try:
        response = requests.get("https://www.instagram.com/",
                                proxies={"https": "https://{}".format(proxy), "http": "http://{}".format(proxy)},
                                timeout=10)
    except Exception as e:
        print(e)
        return False
    print(response.status_code)
    if response.status_code == 200:
        return True
    else:
        return False


def select_proxy(proxy_list):
    proxy = random.choice(proxy_list)
    if len(proxy_list) < 5:
        return False
    if proxy_test(proxy) is True:
        return proxy
    else:
        proxy_list.remove(proxy)
        return select_proxy(proxy_list)


def get_proxy():
    proxy_list = free_proxy()
    proxy = select_proxy(proxy_list)
    if proxy is False:
        return proxy_list
    return proxy


"""docker run -d -p 4445:4444 --shm-size=2g selenium/standalone-chrome"""


def register(proxy=False):
    # base data
    sp = SmsPva()
    month_mapping = {"January": "1",
                     "February": "2",
                     "March": "3",
                     "April": "4",
                     "May": "5",
                     "June": "6",
                     "July": "7",
                     "August": "8",
                     "September": "9",
                     "October": "10",
                     "November": "11",
                     "December": "12",
                     }
    name, birthday = get_random_identity("US")
    name = name.replace(" ", "")
    user_name = name.lower() + str(random.choice(list(range(0, 100))))
    year = birthday.split(",")[1].replace(" ", "")
    day = birthday.split(",")[0].split(" ")[1]
    month = birthday.split(",")[0].split(" ")[0]
    print(name, user_name, year, day, month)
    # selenium
    chrome_options = webdriver.ChromeOptions()
    if proxy is not False:
        chrome_options.add_argument("--proxy-server={}".format(proxy))
    # chrome_options.add_argument('--lang=en-US')
    prefs = {'intl.accept_languages': 'en-US'}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("./chromedriver", chrome_options=chrome_options)
    driver.set_window_size(800, 600)
    driver.get("https://www.instagram.com/accounts/emailsignup/")
    time.sleep(10)
    try:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input')
    except:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[3]/div/label/input')
    phone_number = sp.get_the_number()
    password = get_password()
    try:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input').send_keys(
            phone_number)
    except:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[3]/div/label/input').send_keys(
            phone_number)
    time.sleep(2)
    try:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/div/label/input').send_keys(name)
    except:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[4]/div/label/input').send_keys(name)
    time.sleep(2)
    try:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[5]/div/label/input').send_keys(
            user_name)
    except:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[5]/div/label/input').send_keys(
            user_name)
    time.sleep(2)
    try:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[6]/div/label/input').send_keys(
            password)
    except:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[6]/div/label/input').send_keys(
            password)
    time.sleep(2)
    try:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[7]/div/button').click()
    except:
        driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[7]/div/button').click()
    time.sleep(20)
    s_year = Select(driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/div[4]/div/div/span/span[3]/select'))
    s_year.select_by_value(year)
    s_day = Select(driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/div[4]/div/div/span/span[2]/select'))
    s_day.select_by_index(str(day))
    s_month = Select(driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/div[4]/div/div/span/span[1]/select'))
    s_month.select_by_value(month_mapping[month])
    driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/div[5]/div[2]/button').click()
    time.sleep(20)
    if len(driver.find_elements_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/div/div/form/div[1]/div/label/input')) == 0:
        print("create Account number Fail!!!!")
        driver.close()
        return False
    sms = sp.get_the_sms()
    if sms is False:
        driver.close()
        return False
    driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/div/div/form/div[1]/div/label/input').send_keys(
        sms)
    driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/div/div/form/div[2]/button').click()
    print(user_name + "," + password + "," + name + "," + phone_number)
    time.sleep(20)
    if driver.title != "Instagram":
        assert True is False, "sign up fail!!"
    if "Help" in driver.title:
        print("my be ip problem!!")
        "Sorry, something went wrong creating your account. Please try again soon."
    else:
        print("sign up Success")
        print(user_name + "," + password + "," + name + "," + phone_number)
        with open("./user.csv", "a+") as f:
            f.write(user_name + "," + password + "," + name + "," + phone_number + "\n")
    time.sleep(10)
    driver.close()


if __name__ == "__main__":
    count = 0
    print()
    for i in range(0, 200):
        # proxy = get_proxy()
        try:
            if register() is False:
                count += 1
            if count > 5:
                break
        except Exception as e:
            print(e)
            pass
