import sys
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


MIN_CARAT = sys.argv[1]
MAX_CARAT = sys.argv[2]
OUTPUT_FILE = sys.argv[3]
BASE_URL = "https://www.brilliantearth.com"
SEARCH_PAGE = "/diamond/round/"

df_cols = [
    'stock_number',
    'gemstone',
    'origin',
    'price',
    'carat',
    'shape',
    'cut',
    'color',
    'clarity',
    'measurements',
    'table',
    'depth',
    'symmetry',
    'polish',
    'girdle',
    'culet',
    'fluorescence',
    'diamond_id'
]
df = pd.DataFrame(columns=df_cols)
driver = webdriver.Chrome()
driver.get(BASE_URL + SEARCH_PAGE)
time.sleep(20)

count = 0
while True and count < 10:
    try:
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "bx-close-xsvg"))).click()
        print(f"Managed to close image")
        break
    except Exception as e:
        print(f"Didn't manage to close image, retrying in 5 seconds")
        count += 1
        time.sleep(5)

count = 0
while True and count < 10:
    try:
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='min_carat_display']"))).send_keys(Keys.BACK_SPACE, Keys.BACK_SPACE, Keys.BACK_SPACE, Keys.BACK_SPACE, MIN_CARAT, Keys.TAB, Keys.TAB)
        print(f"Managed to set min carat")
        break
    except Exception as e:
        print(f"Failed to set min carat, retrying in 5 seconds")
        count += 1
        time.sleep(5)

count = 0
while True and count < 10:
    try:
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='max_carat_display']"))).send_keys(Keys.BACK_SPACE, Keys.BACK_SPACE, Keys.BACK_SPACE, Keys.BACK_SPACE, Keys.BACK_SPACE, MAX_CARAT, Keys.TAB, Keys.TAB)
        print(f"Managed to set max carat")
        break
    except Exception as e:
        print(f"Failed to set max carat, retrying in 5 seconds")
        count += 1
        time.sleep(5)

results_div = driver.find_element(By.ID, "diamond_search_wrapper")
scroll_size = 0
for i in range(0, 4):
    driver.execute_script(f"arguments[0].scroll({scroll_size}, {scroll_size + 7000});", results_div)
    scroll_size += 7000
    time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
all_links = soup.findAll('a')
diamond_details_links = []

for link in all_links:
    if link.has_key('href'):
        if "view_detail" in link['href']:
            diamond_details_links.append(link['href'])

count = 0
output_all_ids = ""
for link in diamond_details_links:
    count += 1
    diamond_id = link.split('/')[-2]
    output_all_ids += f"Diamond number {count}, ID {diamond_id}\n"

with open("all_ids.log", "w") as f:
    f.write(output_all_ids)

print(f"Found {len(diamond_details_links)} diamonds\n\n")

count = 0
for link in diamond_details_links:
    count += 1

    try:
        diamond_id = link.split('/')[-2]
        print(f"Working on diamond number {count}, ID {diamond_id}")

        DETAILS_URL = BASE_URL + link
        driver.get(DETAILS_URL)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_details = soup.findAll('dd')

        if "$" in all_details[4].text.strip():
            del all_details[4]

        row_dict = {}
        row_dict['diamond_id'] = diamond_id
        for i in range(0, len(all_details)):
            row_dict[df_cols[i]] = all_details[i].text.strip()
        
        df_row = pd.DataFrame([row_dict])
        df = pd.concat([df, df_row], axis=0, ignore_index=True)
        time.sleep(3)

    except Exception as e:
        print(f"Failed fetching data for diamond number {count}, link {link}")
        print(e)

df.to_csv(f"data/{OUTPUT_FILE}.csv", encoding='utf-8', index=False)
