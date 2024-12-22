import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import chromedriver_autoinstaller
import undetected_chromedriver as uc

from pyvirtualdisplay import Display


from subprocess import getoutput
from bs4 import BeautifulSoup
import regex as re
import time
from datetime import datetime as date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fake_useragent import UserAgent
import os


def establish_driver():
    # display = Display(visible=0, size=(1920, 1200))  
    # display.start()
    chromedriver_autoinstaller.install()     
    

    ua = UserAgent()
    random_user_agent = ua.random
   
    # Add your options as needed    
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
    chrome_options.add_argument("--headless")  # Enable headless mode for CI/CD
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument(f"user-agent={random_user_agent}")
    # chrome_options.add_argument("--disable-javascript")  # Optional: disable JavaScript
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    )

    
   
    driver = uc.Chrome(options = chrome_options)

    return driver

#Select all option only works when at least half screen due to blockage of the all option when not in headerless option

def select_all_option(driver):
    try:
        # Click the dropdown

        dropdown = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label"))
        )
        driver.execute_script("arguments[0].click();", dropdown)
        # Click the "All" option
        all_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[3]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/label/div/select/option[1]"))
        )
        all_option.click()

        print("Successfully selected the 'All' option.")
    except Exception as e:
        print(f"Error selecting the 'All' option: {e}")


def process_page(page,game_id,game_date,home,away,driver):
    driver.get(page)
    
    driver.set_page_load_timeout(120)
    driver.implicitly_wait(10)

    ps = driver.page_source
    soup = BeautifulSoup(ps, 'html5lib')
    
    # Find all divs containing the data tables
    tables = soup.find_all('div', class_='StatsTable_st__g2iuW')
    last_updated = date.today()
    df_data = []
    # Check if tables exist
    if tables:
        for table_index, table in enumerate(tables):
            # Extract the table rows
            rows = table.find_all('tr')
            if table_index == 1:
                t1 = home
                t2 = away
            else:
                t1 = away
                t2 = home
            # Get the header row (if it exists)
            headers = [th.get_text(strip=True) for th in rows[0].find_all('th')] if rows else []
            
            # Get the data rows
            data = []
            
            for row in rows[1:-1]:  # Skip the header row
                cols = row.find_all('td')
                row_data = [col.get_text(strip=True) for col in cols]
                row_data.extend([t1,game_id,game_date,t2,page,last_updated])
                data.append(row_data)
            
            # Create a DataFrame for this table
            if headers and data:
                headers.extend(['team','game_id','game_date','matchup','url','last_updated'])
                df = pd.DataFrame(data, columns=headers)
            else:
                df = pd.DataFrame(data)  # Use generic column names if no headers
            
            df_data.append(df)
        
        df = pd.concat(df_data,ignore_index=True)
            # Append the DataFrame to the appropriate team entries in the dictionary
        return df
    else:
        print(f'Could not process: {page}')
        return game_id,game_date,home,away

def send_email(subject,body):
    sender_email = os.getenv('SERVER_EMAIL')
    receiver_email = os.getenv('EMAIL_USERNAME')
    password = os.getenv('EMAIL_PASSWORD')
    print("Sender email:", sender_email)
    print("Receiver email:", receiver_email)
    print("Password set:", password)
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body,'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(sender_email,password)
        server.send_message(msg)
    except Exception as e:
        print(f"failed due to send email: {e}")
    finally:
        server.quit()

#Makes it so we are not connecting to driver on import
if __name__ == "__main__":
    driver = establish_driver()
    select_all_option(driver)