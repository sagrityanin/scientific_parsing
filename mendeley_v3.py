from selenium import webdriver
from selenium.webdriver.common.by import By
from time import time, sleep
import re
import os
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service


search_string = 'Braun-Blanquet'
# url = "https://www.mendeley.com/search"
url = "https://www.mendeley.com/search/?page=180&query=Braun-Blanquet&sortBy=relevance"
key_words = []
start_page = 181
# search_string = "glycyrrhiza uralensis fisch water"


def get_article(browser, article, file):
    article.click()
    sleep(1)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "ul")))
    link = browser.find_element(By.TAG_NAME, "cite").find_element(By.TAG_NAME, "a")
    link.click()
    sleep(2)
    try:
        journal = browser.find_element(By.XPATH, '//div[@data-document-source="source"]').text
        only_journal = browser.find_element(By.XPATH, '//div[@data-document-source="source"]').text.split("(")[0]
        year = re.search(r"(\d{4})", re.search(r"(\(\d{4}\))", journal).group(1)).group(1)
    except Exception as e:
        journal = ""
        only_journal = ""
        year = ""
        # print(e)
    try:
        title = browser.find_element(By.TAG_NAME, "h1").text
        authors = ", ".join([a.text for a in browser.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "a")])
        abstract = browser.find_element(By.XPATH, '//p[@data-name="content"]').text.replace(";", ",")
        doi = browser.find_element(By.XPATH, '//a[@data-name="doi"]').text
        doi_link = browser.find_element(By.XPATH, '//a[@data-name="doi"]').get_attribute("href")
        citate = browser.find_element(By.XPATH, '//p[@data-name="citation"]').text
        file.write(f"{title}; {only_journal}; {journal}; {authors}; {year}; {doi}; {doi_link}; {citate}; {abstract}\n")
    except NoSuchElementException:
        print("Broken article")
        return None
    try:
        key_words_list = [x.text for x in browser.find_element(
            By.ID, "author supplied keywords-title").find_elements(By.TAG_NAME, "li")]
        key_words.append(str(doi + "; " + title + "; ".join(key_words_list) + "\n"))
    except NoSuchElementException as e:
        print(e)
    return True


def find_element(browser, curent_url, i, file):
    browser.get(curent_url)
    sleep(3)
    papers = browser.find_element(By.ID, "search-results").find_elements(By.TAG_NAME, "cite")
    # papers = browser.find_element(By.ID, "search-results").find_element(
    #     By.ID, "main-content").find_elements(By.TAG_NAME, "cite")
    get_article(browser, papers[i], file)


def get_article_list(current_browser, file):
    current_url = current_browser.current_url
    # papers1 = current_browser.find_element(By.ID, "search-results").find_elements(By.TAG_NAME, "cite")
    papers1 = current_browser.find_element(By.ID, "search-results").find_element(
        By.ID, "main-content").find_elements(By.TAG_NAME, "cite")
    for i in range(len(papers1)):
        print(i)
        find_element(current_browser, current_url, i, file)
        sleep(1)
        # print("Go to find element")


def main():
    if os.path.isfile("result.csv"):
        os.remove("result.csv")
    service = Service(executable_path = "./chromedriver")
    options = webdriver.ChromeOptions()
    with webdriver.Chrome(service=service, options=options) as browser:
        with open("result.csv", "a") as file:
            file.write("title; only_journal; journal; authors; year; doi; doi_link; citate; abstract\n")
            browser.get(url)
            # browser.find_element(By.ID, "search-mendeley").send_keys(search_string)
            # sleep(1)

            WebDriverWait(browser, 10).until(EC.element_to_be_clickable(
                (By.ID, "onetrust-accept-btn-handler"))).click()
            submit_button = browser.find_elements(By.TAG_NAME, "button")
            # submit_button[2].click()
            sleep(1)
            current_url = browser.current_url
            if start_page <= 1:
                get_article_list(browser, file)

            while True:
                browser.get(current_url)
                sleep(1)
                past_url = current_url
                try:
                    n_p = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='Next']")))
                    # n_p = browser.find_elements(By.XPATH, "//*[contains(text(), 'Next')]")[0]
                    # n_p = browser.find_element(By.XPATH, "//*[normalize-space()='Next']")
                    n_p.click()
                    page_label = browser.find_elements(By.XPATH, "//*[contains(text(), 'Page')]")


                    sleep(1)
                    current_url = browser.current_url
                    print(page_label[4].text)
                    if int(page_label[4].text.split()[1]) < start_page:
                        continue
                    if browser.current_url == past_url:
                        print("Search has done")
                        break
                    print(current_url)
                    get_article_list(browser, file)
                except Exception as e:
                    print("Try get next page", e)
                    break


def write_keyword():
    with open("keyword_list.scv", "w") as key_file:
        for item in key_words:
            key_file.write(item)


if __name__ == "__main__":
    main()
    write_keyword()
