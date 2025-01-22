from __future__ import annotations

import json
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from .compress import __compress


def convert(
    source: str,
    target: str,
    timeout: int = 2,
    compress: bool = False,
    power: int = 0,
    install_driver: bool = True,
    print_options: dict = {},
):
    """
    Convert a given html file or website into PDF

    :param str source: source html file or website link
    :param str target: target location to save the PDF
    :param int timeout: timeout in seconds. Default value is set to 2 seconds
    :param bool compress: whether PDF is compressed or not. Default value is False
    :param int power: power of the compression. Default value is 0. This can be 0: default, 1: prepress, 2: printer, 3: ebook, 4: screen
    :param bool install_driver: whether or not to install using ChromeDriverManager. Default value is True
    :param dict print_options: options for the printing of the PDF. This can be any of the params in here:https://vanilla.aslushnikov.com/?Page.printToPDF
    """

    result = __get_pdf_from_html(
        source,
        timeout,
        install_driver,
        print_options,
    )

    if compress:
        __compress(result, target, power)
    else:
        with open(target, "wb") as file:
            file.write(result)


def __send_devtools(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = f"{driver.command_executor._client_config.remote_server_addr}{resource}"
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)

    if not response:
        raise Exception(response.get("value"))

    return response.get("value")


def __get_pdf_from_html(
    path: str,
    timeout: int,
    install_driver: bool,
    print_options: dict,
):
    webdriver_options = Options()

    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")
    webdriver_options.add_argument("--no-sandbox")
    webdriver_options.add_argument("--disable-dev-shm-usage")

    prefs = {
        "profile.default_content_settings": {"notifications": 2},
    }
    webdriver_options.add_experimental_option("prefs", prefs)

    if install_driver:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=webdriver_options)
    else:
        driver = webdriver.Chrome(options=webdriver_options)

    driver.get(path)

    temp_height = 0
    while True:
        driver.execute_script("window.scrollBy(0,100)")
        driver.implicitly_wait(1)
        check_height = driver.execute_script(
            "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;",
        )
        if check_height == temp_height:
            break
        temp_height = check_height

    try:
        WebDriverWait(driver, timeout).until(
            staleness_of(driver.find_element(by=By.TAG_NAME, value="html")),
        )
    except TimeoutException:
        calculated_print_options = {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
        }
        calculated_print_options.update(print_options)
        result = __send_devtools(
            driver,
            "Page.printToPDF",
            calculated_print_options,
        )
        driver.quit()
        return base64.b64decode(result["data"])
