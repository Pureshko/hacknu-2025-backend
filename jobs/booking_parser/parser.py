from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse

# create a Chrome web driver instance
driver = webdriver.Chrome(service=Service())
driver.get("https://www.booking.com/glamping/city/kz/almaty.ru.html")

more_hotels_xpath = "//*[@id=\"c-lp-top-hotels\"]/div/div/div[3]/div[2]/div[2]/a"
more_hotels_page_xpath = "//*[@id=\"b2theme_landing_cityPage\"]/div[27]/div/div/div/div/div[2]/div/div[2]/a"
btn = WebDriverWait(driver, 50).until(
    EC.element_to_be_clickable((By.XPATH, more_hotels_xpath))
)
btn.click()
btn = WebDriverWait(driver, 50).until(
    EC.element_to_be_clickable((By.XPATH, more_hotels_page_xpath))
)
old_handles = driver.window_handles[:]
old_url = driver.current_url
btn.click()
WebDriverWait(driver, 30).until(
    lambda d: len(d.window_handles) > len(old_handles) or d.current_url != old_url
)
# If a new tab/window opened, switch to it
if len(driver.window_handles) > len(old_handles):
    new_handle = (set(driver.window_handles) - set(old_handles)).pop()
    driver.switch_to.window(new_handle)

# Optional: wait for the page to fully load
WebDriverWait(driver, 30).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)


# --- 3) Verify destination site (domain check) ---
target_domain = "booking.com"  # your expected site
current_domain = urlparse(driver.current_url).netloc.lower()

# Accept subdomains like www.booking.com, secure.booking.com, etc.
if not current_domain.endswith(target_domain):
    raise TimeoutException(f"Ended on {current_domain}, expected *.{target_domain}")

print("Arrived at:", driver.current_url)



