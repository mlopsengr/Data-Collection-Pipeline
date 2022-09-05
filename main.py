import os
import json
import numpy as np
from selenium import webdriver



class Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

    def get_data(self):
        data = self.driver.execute_script("return window.__PRELOADED_STATE__")
        return data