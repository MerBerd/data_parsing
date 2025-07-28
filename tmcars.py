from playwright.sync_api import sync_playwright
from tqdm import tqdm
#from pathlib import Path
from bs4 import BeautifulSoup
import os
import pandas as pd
from utils import dateToTimestamp, stringToInt

def cleanInfo(info):
    ### Have to add error handling, exceptions and other safety measures
    info = info.strip().split('\n')
    n = len(info)
    if n == 6:
        return [info[0]] + [info[2]] + info[-2:]
    else:
        return [info[0]] + [info[1]] + info[-2:]

if not os.path.exists("tmcars_saved.html"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://tmcars.info/cars/toyota")

        
        for _ in tqdm(range(50)):  
            page.mouse.wheel(0, 10000)
            page.wait_for_timeout(2000)

        
        html = page.content()
        with open("tmcars_saved.html", "w", encoding="utf-8") as f:
            f.write(html)
        


        browser.close()
else:
    print("Getting data from cache")



    with open("tmcars_saved.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    items = soup.select(".item-card9")
    cars = []
    for item in items:
        cars.append(cleanInfo(item.get_text()))


    for car in cars:
        print(car)
        print('_________')

    price = []
    brands = []
    models = []
    year = []
    place = []
    pubtime = []

    for car in cars:
        
        price.append(stringToInt(car[0].split()[0]))
        model_info = car[1].split()
        brands.append(model_info[0])
        models.append(model_info[1:-1][0])
        year.append(model_info[-1])
        place.append(car[-2])
        pubtime.append(dateToTimestamp(car[-1]))
    
    print(len(price))
    print(len(pubtime))
    print(pubtime)


    car_info = pd.DataFrame(
    {
        "Price": price,
        "Brands": brands,
        "Models": models,
        "Year": year,
        "Place": place,
        "Pubtime": pubtime
    }
    )


    car_info.to_csv("Car_info.csv", index=False)


