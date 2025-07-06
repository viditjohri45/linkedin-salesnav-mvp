import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Credentials are read from environment variables for safety
LINKEDIN_EMAIL = os.getenv("LI_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LI_PASSWORD")


def run_sales_nav_search(criteria):
    """Run a Sales Navigator search and return {'total': int, 'links': [urls...]}."""

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # run headless

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        # 1. Log in to LinkedIn
        driver.get("https://www.linkedin.com/login")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD, Keys.RETURN)

        # 2. Navigate to Sales Navigator People search
        wait.until(EC.url_contains("/feed"))
        driver.get("https://www.linkedin.com/sales/search/people")

        # 3. Apply filters
        # Current title
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Current job title']/../..//button"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add current titles']"))).send_keys(criteria["title"])
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Include')]"))).click()

        # Geography
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Geography']/../..//button"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add locations']"))).send_keys(criteria["location"])
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Include')]"))).click()

        # Industry
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Industry']/../..//button"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add industries']"))).send_keys(criteria["industry"])
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Include')]"))).click()

        # Company headcount
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Company headcount']/../..//button"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//label[contains(.,'{criteria['company_size']}')]"))).click()

        # Give results time to load
        time.sleep(3)

        # 4. Extract total count
        total_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ph5 > span"))).text
        total = int(total_text.split()[0].replace(",", ""))

        # 5. Collect top 5 public profile URLs
        links = []
        people_cards = driver.find_elements(By.CSS_SELECTOR, "a.app-aware-link")[:5]
        for card in people_cards:
            card.click()
            driver.switch_to.window(driver.window_handles[-1])
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='More actions']"))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Copy LinkedIn.com URL']"))).click()
            url = driver.execute_script("return navigator.clipboard.readText();")
            links.append(url)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        return {"total": total, "links": links}

    finally:
        driver.quit()
