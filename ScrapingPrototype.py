from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from tempfile import mkdtemp

from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import random
import platform

def handler(event = {"n_pages" : 2, "keywords" : ["head of sustainability", "procurement manager"], "n_records" : 10}, context = None):
    start_time = time.time()
    print("Started")
    if platform.system() == 'Linux':
        options = webdriver.ChromeOptions()
        service = webdriver.ChromeService("/opt/chromedriver")

        options.binary_location = '/opt/chrome/chrome'
                
        # Set the path to the chrome binary
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")
        driver = webdriver.Chrome(options=options, service=service)
    
    else:
        c_service = webdriver.ChromeService('/Users/rohan/Downloads/chromedriver-mac-arm64/chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=c_service, options=options)
    
    print("Driver started")
    
    # Open the LinkedIn login page
    driver.get("https://www.linkedin.com/login")
    
    print(driver.page_source)
    
    print("Opened LinkedIn")
    
    # Pass in your username and password
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    username.send_keys("Enter a valid username")
    password.send_keys("Enter a valid password")
    time.sleep(3)
    password.send_keys(Keys.RETURN)
    
    keywords = event.get("keywords")
    n_pages = event.get("n_pages")
    n_records = event.get("n_records")
    
    linkedin_df = pd.DataFrame(columns=['Name', 'Works At', 'Linked Company/Institution' 'Location', 'URL'])
    
    for keyword in keywords:
        print(keyword)
        # Specify the number of pages you want to scrape
        for i in range(1, n_pages+1):
            driver.get(f"https://www.linkedin.com/search/results/PEOPLE/?keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL?geoUrn=%5B'103644278'%&page={i}")
            time.sleep(3)
            
            soup = bs(driver.page_source, 'html.parser')
            potential_profiles = soup.find_all('a', {'class': 'app-aware-link'})
            print(soup)
            print(potential_profiles)
                    
            profile_links = set()
            for element in potential_profiles:
                if time.time() - start_time > 830:
                    break
                
                if '/in/' in element['href'] and element['href'] not in profile_links:
                    time.sleep(random.randint(1, 15))
                    profile_links.add(element['href'])
                    driver.get(element['href'])
                    print("Opened a profile")
                    soup = bs(driver.page_source, 'html.parser')
                    
                    intro = soup.find('div', {'class': 'mt2 relative'})
                    
                    if intro is None:
                        continue
                    
                    name = intro.find('h1').text
                    
                    print(name)
                    
                    works_at_loc = intro.find('div', {'class': 'text-body-medium break-words'})
                    
                    works_at = works_at_loc.get_text().strip()
                    
                    location_loc = intro.find_all("span", {"class": "text-body-small inline t-black--light break-words"})
                    
                    location = location_loc[0].get_text().strip()
                    
                    try:                
                        recent_places = soup.find('div', {'class': 'YyaWuAtCQdSIuXQMvBdIyKRyVYRxGSXMotGw'}).get_text().strip()
                    except:
                        recent_places = 'N/A'
                                    
                    row = {
                        'Name': name,
                        'Works At': works_at,
                        'Location': location,
                        'Linked Company/Institution': recent_places,
                        'URL': element['href']
                    }
                    
                    linkedin_df = pd.concat([linkedin_df, pd.DataFrame([row])], ignore_index=True)
                    
                    if len(linkedin_df) >= n_records:
                        break
                    
    driver.quit()
    res = linkedin_df.to_json()
    print(res)
    return res
    
    
if __name__ == "__main__":
    handler()