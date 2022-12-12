import json
import os
import shutil
import time
import urllib.request
from email.mime import image
from pickle import NONE
from tkinter.ttk import Style
from unicodedata import name
import pandas as pd
import psycopg2
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from this import d
import sqlalchemy

from utils.scraper import CoverScraper


class Scraper:
    def __init__(self, url: str = 'https://soundcloud.com/discover'):   
        '''
        Initializes the driver and opens the webpage
        Parameters
        ----------
        url: str
        The url of the webpage to be opened
        '''
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        service = Service('/Users/tobijohn/miniforge3/envs/soundscrape-env/bin/chromedriver')
        self.url = url
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(self.url)
        self.driver.maximize_window()  
       
        self.charts = { 1: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                   2: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                   3: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                   4: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                     5: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                        6: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                        7: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                        8: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                        9: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
                        10: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
        }

        
   
    def get_data(self):
        data = self.driver.execute_script("return window.__PRELOADED_STATE__")
        return data

    def click_element(self, xpath:str):
        '''
        Finds and clicks an element on the webpage  
        Parameters
        ----------
        xpath: str
        The xpath of the element to be clicked
        '''
        element = self.driver.find_element(By.XPATH, xpath)
        element.click(xpath)

    def accept_cookies(self, xpath:str = '//button[@id="onetrust-accept-btn-handler"]'):
        '''
        Opens Soundcloud and Accepts cookies
        Returns
        -------
        driver: webdriver.Chrome
        This driver is already on the soundcloud webpage
        '''  
        driver = self.driver
        delay = 10
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//div[@class="ot-sdk-container"]')))
            print('Frame is ready')
           
            accept_cookies_button = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')))
            print('Accept cookies button is ready')
            time.sleep(1)
            accept_cookies_button.click()
        except TimeoutException:
            print('Loading took too much time')
            
        return driver

    def empty_image_directory(self, path:str = 'images'):
        '''
        Empties the images directory
        Parameters
        ----------
        path: str
        The path to the images directory
        '''
        for file in os.listdir('images'): 
                                    if file.endswith('.jpg'):
                                        os.remove(os.path.join('images', file))

    def get_top_50_links(self):
        '''
        Returns
        -------
        top_50: list
        A list of the top 50 playlist categories on soundcloud
        '''
        chart_links =  {'links': [] }
        
        top50_list = self.driver.find_elements(By.XPATH, '//div[@class="systemPlaylistTile playableTile sc-mb-6x"]')

        for record in top50_list:
            a_tag = record.find_element(by=By.TAG_NAME, value = 'a')
            link = a_tag.get_attribute('href')
            chart_links['links'].append(link)
        print(f"There are {chart_links['links'].__len__()} chart lists")

        return chart_links 
            
    def get_chart_category(self, xpath:str = '//span[@class="fullHero__titleTextTitle"]'):
        '''
        Returns
        -------
        category: str
        The category of the chart
        '''
        chart_links = self.get_top_50_links()
        categories =  {'links': [],'category': [] }
        i = 1
        for link in chart_links['links']:
            self.driver.get(link)
            time.sleep(1)
            chart_name = self.driver.find_element(By.XPATH, xpath).text
            categories['category'].append(chart_name)
            categories['links'].append(link)
            i += 1
            
        return categories

    def get_track_info(self, xpath:str = '//div[@class="systemPlaylistTrackList lazyLoadingList"]//li'):
        ''' 
        Returns
        -------
        tracks: list
        A list of the tracks in the chart
        '''
        categories = self.get_chart_category()
        tracks = {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]}
        i = 1
        for element in categories['links']:
            self.driver.get(element)
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            self.driver.execute_script("window.scrollTo(0, 2 * document.body.scrollHeight);")
            time.sleep(4)
            self.driver.execute_script("window.scrollTo(0, 3 * document.body.scrollHeight);")
            artiste_list = self.driver.find_elements(By.XPATH, xpath)

            tracks['category'].append(categories['category'][i-1])


            for artiste in artiste_list:
                   time.sleep(1)
                   stream = artiste.find_element(By.XPATH, '//span[@class="trackItem__playCount sc-ministats sc-ministats-medium  sc-ministats-plays"]').text
                   tracks['streams'].append(stream)

                   artiste_case = artiste.find_elements(By.XPATH, './/div[@class="trackItem g-flex-row sc-type-small sc-text-body sc-type-light sc-text-secondary m-interactive m-playable"]')
                   for case in artiste_case:
                        artiste = case.find_elements(by=By.TAG_NAME, value ='a') 
                        tracks['artist'].append(artiste[1].text)
                        tracks['track'].append(artiste[2].text)   

                        
                        images = case.find_elements(By.XPATH, './/div[@class="trackItem__image sc-py-1x sc-mr-2x"]')
                        for image in images:
                            image =  image.find_element(By.TAG_NAME, value = 'span').get_attribute('style')
                            tracks['image'].append(image)
                            
                            try:    
                                image = image.split('url("')[1].split('")')[0]
                                urllib.request.urlretrieve(image, f"image{i}.jpg")  # using the url to get the image with urllib
                                os.rename(f"image{i}.jpg", f"{artiste[2].text}.jpg")     # rename the image as the tr empty the image folderack name
                                shutil.move(f"{artiste[2].text}.jpg", f"images/{artiste[2].text}.jpg")
                                
                            except:
                                # if image not found, use a default image
                                #urllib.request.urlretrieve('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', f"image{i}.jpg")
                                pass
             
                    
        i += 1 
           
        # convert chart to table
        table =  pd.DataFrame(tracks)

        # table to sql
        table.to_sql('charts', con=self.engine, if_exists='replace', index=False)


        # creating a new dataframe with two colums
        df = pd.DataFrame(columns=['category', 'track', 'artist', 'streams', 'image'])
        # adding the data to the dataframe
        df['category'] = tracks['category']

      
     





        

        print(table)
        
        return table




if __name__ == '__main__':
    bot = Scraper()
   
    data = bot.get_data()
    bot.accept_cookies()
    bot.empty_image_directory()
    bot.get_track_info()

    
    # %%
   
    
   
# %%
