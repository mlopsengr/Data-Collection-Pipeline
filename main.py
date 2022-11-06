from email.mime import image
import os
import json
from pickle import NONE
from this import d
from tkinter.ttk import Style
from unicodedata import name
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
import time
import urllib.request
from utils.scraper import CoverScraper
from selenium.webdriver.chrome.service import Service
import shutil









class Scraper:
    def __init__(self, url: str = 'https://soundcloud.com/discover'):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        service = Service('/Users/tobijohn/miniforge3/envs/soundscrape-env/bin/chromedriver')
        self.url = url
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(self.url)
        self.driver.maximize_window()

        

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

    def get_top_50_links(self):
        '''
        Returns
        -------
        top_50: list
        A list of the top 50 playlist categories on soundcloud
        '''
        
        top50_list = self.driver.find_elements(By.XPATH, '//div[@class="systemPlaylistTile playableTile sc-mb-6x"]')
        top50_chart_list = {'links': [] }
        charts = { 1: {'category':[], 'artist': [], 'track':[],'streams':[], 'image':[]},
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

        for record in top50_list:

            a_tag = record.find_element(by=By.TAG_NAME, value = 'a')
            link = a_tag.get_attribute('href')
            top50_chart_list['links'].append(link)
            
    
        print(f"There are {top50_chart_list['links'].__len__()} chart lists")

        i = 1
        for link in top50_chart_list['links']:
           
            self.driver.get(link)
            time.sleep(1)
            chart_name = self.driver.find_element(By.XPATH, '//span[@class="fullHero__titleTextTitle"]').text
            charts[i]['category'].append(chart_name)
            i += 1
            
           

        i = 1
        for link in top50_chart_list['links']:
            self.driver.get(link)
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            self.driver.execute_script("window.scrollTo(0, 2 * document.body.scrollHeight);")
            time.sleep(4)
            self.driver.execute_script("window.scrollTo(0, 3 * document.body.scrollHeight);")
            
        

       

           

            artiste_list = self.driver.find_elements(By.XPATH, '//div[@class="systemPlaylistTrackList lazyLoadingList"]//li')
            for artiste in artiste_list:
                   time.sleep(1)
                   
                   stream = artiste.find_element(By.XPATH, '//span[@class="trackItem__playCount sc-ministats sc-ministats-medium  sc-ministats-plays"]').text
                   charts[i]['streams'].append(stream)

                   artiste_case = artiste.find_elements(By.XPATH, './/div[@class="trackItem g-flex-row sc-type-small sc-text-body sc-type-light sc-text-secondary m-interactive m-playable"]')
                   for case in artiste_case:
                        artiste = case.find_elements(by=By.TAG_NAME, value ='a') 
                        
                        charts[i]['artist'].append(artiste[1].text)
                      
                        charts[i]['track'].append(artiste[2].text)   

                        
                        images = case.find_elements(By.XPATH, '//div[@class="trackItem__image sc-py-1x sc-mr-2x"]')
                        for image in images:
                            
                            image =  image.find_element(By.TAG_NAME, value = 'span').get_attribute('style')
                            charts[i]['image'].append(image)
                            
                            image = image.split('url("')[1].split('")')[0]
                            # using the url to get the image with urllib
                            urllib.request.urlretrieve(image, f"image{i}.jpg")
                            # rename the image as the track name
                            os.rename(f"image{i}.jpg", f"{artiste[2].text}.jpg")
                            shutil.move(f"{artiste[2].text}.jpg", f"images/{artiste[2].text}.jpg")
                            #charts[i]['image'].append(f"image{i}.jpg")
                            # add the image to the images folder
                            
                            
                            
                            
                    
            i += 1 
           

            
            
        # convert chart to table
        table =  pd.DataFrame(charts)

        report = table.to_json

        

        print(table)
        print (charts)
        return top50_chart_list, table




if __name__ == '__main__':
    bot = Scraper()
    data = bot.get_data()
    
    #print(data)
    bot.accept_cookies()
    bot.get_top_50_links()
    
    # %%
   
    
   
# %%
