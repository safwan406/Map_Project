from configparser import ConfigParser
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

config = ConfigParser()
config.read("Configurations.ini")

def config_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    chrome_manager = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_manager, options=options)
    return driver

def get_name(content):
    try:
        name = content.find("div", {"class": "qBF1Pd"}).text
    except:
        name = " "
    return name

def get_ratings(content):
    try:
        rating = content.find_all("div", {"class": "W4Efsd"})[0].text
        rating = rating.split("(")[0].strip()
    except:
        rating = " "
    return rating

def get_reviews(content):
    try:
        review = content.find_all("div", {"class": "W4Efsd"})[0].text
        review = review.split("(")[1].split(")")[0].strip()
    except:
        review = " "
    return review

def get_address(content):
    try:
        address = content.find_all("div", {"class": "W4Efsd"})[2].text.split("·")[1]
    except:
        address = " "
    return address

def get_category(content):
    try:
        category = content.find_all("div", {"class": "W4Efsd"})[2].text.split("·")[0]
    except:
        category = " "
    return category

def get_time(content):
    try:
        contact = content.find_all("div", {"class": "W4Efsd"})[4].text.split("⋅")[1]
    except:
        contact = " "
    return contact

def save_data(data, file_name):
    data.to_csv(file_name)

def get_business_info(df, content):
    soup = BeautifulSoup(content, "html.parser")
    for i in soup.find_all("div", {"class": "THOPZb"}):
        name = get_name(i)
        rating = get_ratings(i)
        review = get_reviews(i)
        address = get_address(i)
        category = get_category(i)
        time = get_time(i)
        dct = {
            "Name" : name,
            "Rating": rating,
            "Reviews": review,
            "Address": address,
            "Category": category,
            "Time": time
            }

        is_duplicate = dct["Name"] in df["Name"].values
        
        # Append the dictionary DataFrame only if it doesn't already exist in the "name" column
        if not is_duplicate:
            df = df.append(dct, ignore_index=True)
    
    print("----------")
    return df

def load_restaurants(url, driver):
    print("Getting business info", url)
    driver.get(url)
    time.sleep(5)
    panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'
    scrollable_div = driver.find_element(By.XPATH, panel_xpath)
    # scrolling
    flag = True
    i = 0
    columns = ["Name", "Rating", "Reviews", "Address", "Category", "Time"]
    df = pd.DataFrame(columns=columns)
    while i < 19:
        print(f"Scrolling to page {i + 2}")
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(2)

        if "You've reached the end of the list." in driver.page_source:
            flag = False
        
        df = get_business_info(df, driver.page_source)
        i += 1
        # print(df)
    return df

if __name__ == "__main__":
    loaction = config.get("Search_Parameters", "location")
    map_URL = config.get("URL", "map")
    file_name = config.get("Files", "file_name")

    searching_URL = map_URL + loaction.replace(' ', '+')
    print(searching_URL)
    
    browser = config_driver()
    data = load_restaurants(map_URL, browser)
    save_data(data, file_name)
