import os
import json
from this import d
from unicodedata import name
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
import time

#chrome_options = Options()
#chrome_options.add_argument('--headless')
#driver = webdriver.Chrome('/Users/tobijohn/miniforge3/envs/soundscrape-env/bin/chromedriver', chrome_options=chrome_options)




class Scraper:
    def __init__(self, url: str = 'https://soundcloud.com/discover'):
        self.url = url
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

        

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
        top50_chart_list = {'links': [], 'titles': []}

        for record in top50_list:

            a_tag = record.find_element(by=By.TAG_NAME, value = 'a')
            link = a_tag.get_attribute('href')
            top50_chart_list['links'].append(link)
    
        print(f"There are {top50_chart_list['links'].__len__()} chart lists")

  
        for link in top50_chart_list['links']:
            self.driver.get(link)
            time.sleep(1)
            chart_name = self.driver.find_element(By.XPATH, '//span[@class="fullHero__titleTextTitle"]').text
            top50_chart_list['titles'].append(chart_name)

 

           
          
        print (top50_chart_list['titles'])
        return top50_chart_list

    def get_top_50_tracks(self):
        '''
        gets the top 50 tracks for each chart
        '''
        
        top50_chart_list = self.get_top_50_links()
        top_50_tracks = []
        top_50_artists = []
        top_50_image = []

        for link in top50_chart_list:
            self.driver.get(link)
            time.sleep(1)
            track_holder = self.driver.find_element(By.XPATH, '//div[@class="trackItem__content sc-truncate"]')
            tracks = track_holder.find_element(By.XPATH, '//a[@class="trackItem__content sc-truncate"]')
            track = tracks.text
            top_50_tracks.append(track)





if __name__ == '__main__':
    bot = Scraper()
    #data = bot.get_data()
    #print(data)
    bot.accept_cookies()
 
   