from selenium import webdriver
from selenium.webdriver.common.by import By
from time import time, sleep
import re
import os
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

search_string = "Ellenberg indicator values & vegetation changes"
# search_string = "glycyrrhiza uralensis fisch water"


def get_article(browser, article):
    article.click()
    sleep(1)
    link = browser.find_element(By.TAG_NAME, "cite").find_element(By.TAG_NAME, "a")
    link.click()
    sleep(2)
    try:
        title = browser.find_element(By.TAG_NAME, "h1").text
        journal = browser.find_element(By.XPATH, '//div[@data-document-source="source"]').text
        authors = ", ".join([a.text for a in browser.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "a")])
        year = re.search(r"(\d{4})", re.search(r"(\(\d{4}\))", journal).group(1)).group(1)
        abstract = browser.find_element(By.XPATH, '//p[@data-name="content"]').text
        doi = browser.find_element(By.XPATH, '//a[@data-name="doi"]').text
        doi_link = browser.find_element(By.XPATH, '//a[@data-name="doi"]').get_attribute("href")
        citate = browser.find_element(By.XPATH, '//p[@data-name="citation"]').text
        key_words_list = [x.text for x in browser.find_element(
            By.XPATH, '//div[@data-name="author-supplied-keywords"]').find_elements(By.TAG_NAME, "li")]
        file.write(f"{title}; {journal}; {authors}; {year}; {doi}; {doi_link}; {citate}; {abstract}\n")
        # print(str(doi + "; " + "; ".join(key_words_list)))
        key_words.append(str(doi + "; " + "; ".join(key_words_list) + "\n"))
    except Exception:
        print("Broken article")

def find_element(browser, curent_url, i):
    browser.get(curent_url)
    sleep(2)
    papers = browser.find_element(By.ID, "search-results").find_elements(By.TAG_NAME, "cite")
    get_article(browser, papers[i])


def get_article_list(current_browser):
    current_url = current_browser.current_url
    papers = current_browser.find_element(By.ID, "search-results").find_elements(By.TAG_NAME, "cite")
    for i in range(len(papers)):
        try:
            get_article(current_browser, papers[i])
            sleep(2)
        except StaleElementReferenceException:
            # break
            # print("retry")
            find_element(current_browser, current_url, i)
            sleep(2)


if os.path.isfile("result.csv"):
    os.remove("result.csv")
# if os.path.isfile("keyword_list.scv"):
#     os.remove("keyword_list.scv")

key_words = []
with webdriver.Chrome() as browser:
    with open("result.csv", "a") as file:
        headers = "title; journal; authors; year; doi; doi_link; citate; abstract\n"
        file.write(headers)
        browser.get("https://www.mendeley.com/search/")
        browser.find_element(By.ID, "search-mendeley").send_keys(search_string)
        sleep(1)

        browser.find_element(By.ID, "onetrust-accept-btn-handler").click()
        sleep(2)
        submit_button = browser.find_elements(By.TAG_NAME, "button")
        submit_button[2].click()
        sleep(1)
        current_url = browser.current_url
        get_article_list(browser)

        while True:
            browser.get(current_url)
            sleep(2)
            past_url = current_url
            try:
                n_p = browser.find_elements(By.XPATH, "//*[contains(text(), 'Next')]")[0]
                n_p.click()
                sleep(1)
                if browser.current_url == past_url:
                    print("Search has done")
                    break
                print(current_url)
                get_article_list(browser)
            except Exception as e:
                print(e)
                break
with open("keyword_list.scv", "w") as key_file:
    for item in key_words:
        key_file.write(item)

