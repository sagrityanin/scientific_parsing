from selenium import webdriver
from selenium.webdriver.common.by import By
from time import time, sleep
import re
import os
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


search_string = "Ellenberg indicator values & vegetation changes"
key_words = []

# search_string = "glycyrrhiza uralensis fisch water"


def get_article(browser, article, file):
    article.click()
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "ul")))
    link = browser.find_element(By.TAG_NAME, "cite").find_element(By.TAG_NAME, "a")
    link.click()
    sleep(2)
    try:
        journal = browser.find_element(By.XPATH, '//div[@data-document-source="source"]').text
        year = re.search(r"(\d{4})", re.search(r"(\(\d{4}\))", journal).group(1)).group(1)
    except Exception:
        journal = ""
        year = ""
    try:
        title = browser.find_element(By.TAG_NAME, "h1").text
        authors = ", ".join([a.text for a in browser.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "a")])
        abstract = browser.find_element(By.XPATH, '//p[@data-name="content"]').text
        doi = browser.find_element(By.XPATH, '//a[@data-name="doi"]').text
        doi_link = browser.find_element(By.XPATH, '//a[@data-name="doi"]').get_attribute("href")
        citate = browser.find_element(By.XPATH, '//p[@data-name="citation"]').text
        file.write(f"{title}; {journal}; {authors}; {year}; {doi}; {doi_link}; {citate}; {abstract}\n")
    except NoSuchElementException:
        print("Broken article")
        return None
    try:
        key_words_list = [x.text for x in browser.find_element(
            By.XPATH, '//div[@data-name="author-supplied-keywords"]').find_elements(By.TAG_NAME, "li")]
        key_words.append(str(doi + "; " + "; ".join(key_words_list) + "\n"))
    except NoSuchElementException:
        pass
    return True


def find_element(browser, curent_url, i, file):
    browser.get(curent_url)
    sleep(2)
    papers = browser.find_element(By.ID, "search-results").find_elements(By.TAG_NAME, "cite")
    get_article(browser, papers[i], file)


def get_article_list(current_browser, file):
    current_url = current_browser.current_url
    papers = current_browser.find_element(By.ID, "search-results").find_elements(By.TAG_NAME, "cite")
    for i in range(len(papers)):
        print(i)
        try:
            get_article(current_browser, papers[i], file)
            sleep(1)
        except StaleElementReferenceException:
            find_element(current_browser, current_url, i, file)
            sleep(1)


def main():
    if os.path.isfile("result.csv"):
        os.remove("result.csv")
    with webdriver.Chrome() as browser:
        with open("result.csv", "a") as file:
            file.write("title; journal; authors; year; doi; doi_link; citate; abstract\n")
            browser.get("https://www.mendeley.com/search/")
            browser.find_element(By.ID, "search-mendeley").send_keys(search_string)
            sleep(1)
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable(
                (By.ID, "onetrust-accept-btn-handler"))).click()
            submit_button = browser.find_elements(By.TAG_NAME, "button")
            submit_button[2].click()
            sleep(1)
            current_url = browser.current_url
            get_article_list(browser, file)

            while True:
                browser.get(current_url)
                sleep(2)
                past_url = current_url
                try:
                    n_p = browser.find_elements(By.XPATH, "//*[contains(text(), 'Next')]")[0]
                    n_p.click()
                    sleep(1)
                    current_url = browser.current_url
                    if browser.current_url == past_url:
                        print("Search has done")
                        break
                    print(current_url)
                    get_article_list(browser, file)
                except Exception as e:
                    print(e)
                    break


def write_keyword():
    with open("keyword_list.scv", "w") as key_file:
        for item in key_words:
            key_file.write(item)


if __name__ == "__main__":
    main()
    write_keyword()
