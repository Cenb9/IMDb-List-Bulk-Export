import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
service = Service(r"chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# Open IMDb in the first tab
driver.get("https://www.imdb.com")

# Wait 5 seconds
time.sleep(5)

# Open chrome://settings/content in the SAME tab
driver.get("chrome://settings/content/all")

input("Press Enter to close...")
driver.quit()