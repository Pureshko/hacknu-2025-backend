import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time

from urllib.parse import urlparse
glampings = pd.read_csv("data/2gis_all.csv")


names = glampings["name"]
print(names)

# create a Chrome web driver instance
driver = webdriver.Chrome(service=Service())
wait = WebDriverWait(driver, 20)
driver.get("https://instagram.com")

wait = WebDriverWait(driver=driver, timeout=600)

cookie_xpath = "/html/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]"
btn = WebDriverWait(driver, 50).until(
    EC.element_to_be_clickable((By.XPATH, cookie_xpath))
)
btn.click()
time.sleep(1)

email_xpath = "//*[@id=\"loginForm\"]/div[1]/div[1]/div/label/input"

loc_email = (By.XPATH, email_xpath)  # or By.XPATH, etc.
email = wait.until(EC.element_to_be_clickable(loc_email))
email.click()
email.send_keys(Keys.CONTROL, "a")      # or COMMAND on macOS
email.send_keys(Keys.DELETE)
email.send_keys("dauk.ok")
time.sleep(2)
# Password
pass_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form/div[1]/div[1]/div/label/input"
pwd = wait.until(EC.element_to_be_clickable((By.XPATH, pass_xpath)))
pwd.click()
pwd.clear()
pwd.send_keys("daukokkuka")
enter_xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/article/div[2]/div[1]/div[2]/div/form/div[1]/div[2]/div/label/input"
btn = wait.until(
    EC.element_to_be_clickable((By.XPATH, enter_xpath))
)
btn.click()
auth_reg = False
while not auth_reg:
    if driver.current_url == "instagram.com":
        auth_reg = True
    time.sleep(1)


driver.quit()