from playwright.sync_api import sync_playwright
from tqdm import tqdm
#from pathlib import Path
from bs4 import BeautifulSoup
import os
from utils import get_logger, cleanInfo, dateToTimestamp, stringToInt
import pandas as pd
import numpy as np
from constants import TMCARS_URL, DATA_FOLDER

logger = get_logger()

class TmcarsParser:
    pass
    def __init__(self, car_type='all', scroll_count=50, wait_time=2000):
        self.car_type = car_type
        self.scroll_count = scroll_count
        self.wait_time = wait_time

    def fetch_data(self):
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER, exist_ok=True)
        if not os.path.exists("{DATA_FOLDER}/tmcars_saved.html"):
            with sync_playwright() as p:
                # INFO: Starting to fetch data from url
                logger.info('Starting to fetch data from url')
                browser = p.chromium.launch(headless=True) # Needed error checking here, maybe didn't write the command <playwright install>
                page = browser.new_page()
                try:
                    page.goto(f"{TMCARS_URL}/{self.car_type}") # Needed error checking here, maybe invalid URL or something
                except Exception as e:
                    logger.info('An error occured: {e}')
            
                logger.info('Started scrolling the page')
                for _ in tqdm(range(self.scroll_count), desc='Scrolling through pages'):
                    page.mouse.wheel(0, 10000)
                    page.wait_for_timeout(self.wait_time)
                

                
                # INFO: Finished scrolling
                logger.info('Finished scrolling the page')
                logger.info('Saving the page to hmtl file')
                # INFO: Saving the html file

                html = page.content()

                with open("{DATA_FOLDER}/tmcars_saved.html", "w", encoding="utf-8") as f:
                    f.write(html) # Needed error checking here 
                
                logger.info('Successfully saved the html file')
                # INFO: Successfully saved the html file
                browser.close()
        else:
            logger.info('html file already exists, loading from cache')

    def process_and_save(self):
        with open("{DATA_FOLDER}/tmcars_saved.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        items = soup.select(".item-card9")
        cars = []

        logger.info('Starting processing data')

        for item in tqdm(items, desc="Processing data"):
            cars.append(cleanInfo(item.get_text()))

        logger.info('Successfully finished processing')

        price = []
        brands = []
        models = []
        year = []
        place = []
        pubtime = []

        logger.info('Preparing data to save to csv')

    ##### CONSIDER UNITING THE LOOP ABOVE AND BELOW INTO ONE LOOP
    ##### adding logic to check if the .csv file already exists or not, if yes don't process
        for car in tqdm(cars, desc="Sptilling data, and preparing to save to CSV"):
            
            price.append(stringToInt(car[0].split()[0]))
            model_info = car[1].split()
            brands.append(model_info[0])
            models.append(model_info[1:-1][0])
            year.append(model_info[-1])
            place.append(car[-2])
            pubtime.append(dateToTimestamp(car[-1]))
        
        logger.info('Data successfully prepared')

        car_info = pd.DataFrame(
        {
            "Price 10^3 TMT": price,
            "Brands": brands,
            "Models": models,
            "Year": year,
            "Place": place,
            "Pubtime": pubtime
         }
        )

        car_info.to_csv("{DATA_FOLDER}/Car_info.csv", index=False)
        logger.info('Data Successfully saved to csv')
    
    @staticmethod
    def create_training_data():
        # create training data to use with gradient descent
        # consider using error checking, exception handling and logging
        cars = pd.read_csv("{DATA_FOLDER}/Car_info.csv")
        cars = pd.get_dummies(cars, columns=['Brands', 'Models', 'Place'])
        cars[cars.select_dtypes(bool).columns] = cars.select_dtypes(bool).astype(int)

        cars.to_csv("{DATA_FOLDER}/Cars_training_data.csv")


    @staticmethod
    def load_training_data():
        dataset = pd.read_csv("data/Cars_training_Data.csv", index_col=0)

        y = dataset[['Price 10^3 TMT']].to_numpy()
        dataset.drop("Pubtime", axis=1, inplace=True)
        dataset.drop("Price 10^3 TMT", axis=1, inplace=True)
        X = dataset.to_numpy()

        return X, y
                     




parser = TmcarsParser()
parser.fetch_data()
parser.process_and_save()
parser.create_training_data()

