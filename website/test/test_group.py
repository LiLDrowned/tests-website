import time 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support.expected_conditions import \
     visibility_of_element_located, presence_of_element_located

with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
    driver.maximize_window()
    
    driver.get('http://localhost:5000/')

    email_input = WebDriverWait(driver,10).until(
        visibility_of_element_located((By.CSS_SELECTOR, 'input[test-id="email-input"]'))) 
    
    email_input.clear()

    email_input.send_keys('Adamko@Faemail.com')

    password_input = WebDriverWait(driver,10).until(
        presence_of_element_located((By.CSS_SELECTOR, 'input[test-id="password-input"]'))) 
    
    password_input.clear()

    password_input.send_keys('adam13')

    login_btn = WebDriverWait(driver,10).until(
        visibility_of_element_located((By.CSS_SELECTOR, 'input[test-id="login-btn"]'))) 

    login_btn.click()

    goto_btn = WebDriverWait(driver,10).until(
        visibility_of_element_located((By.CSS_SELECTOR, 'a[test-id="go-to"]'))) 

    goto_btn.click()

    time.sleep(5)


