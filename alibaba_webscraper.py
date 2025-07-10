# LIBRARIES AND PACKAGES

import os
import sys
import time
import re
import csv
import math
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Fully suppress ChromeDriver logs
service = Service(log_path=os.devnull)
# Suppress all stderr output globally
sys.stderr = open(os.devnull, 'w')

# SETUP CHROME DRIVER
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")  # suppress Chrome logs
driver = webdriver.Chrome(service=service, options=chrome_options)

# CONFIGURATION
BASE_URL = "https://sourcing.alibaba.com/rfq/rfq_search_list.htm?country=AE&recently=Y&page={}"
TODAY_DATE_FOR_FILENAME = datetime.datetime.now().strftime("%Y-%m-%d")
OUTPUT_CSV = f"alibaba_rfq_{TODAY_DATE_FOR_FILENAME}.csv"
WAIT_TIME = 5  # seconds
TODAY_DATE = datetime.datetime.now().strftime("%d-%m-%Y")


# CSV HEADERS
HEADERS = [
    "RFQ ID", "Title", "Buyer Name", "Buyer Image", "Inquiry Time", "Quotes Left", "Country",
    "Quantity Required", "Email Confirmed", "Experienced Buyer", "Complete Order via RFQ",
    "Typical Replies", "Interactive User", "Inquiry URL", "Inquiry Date", "Scraping Date"
]

# TOTAL RFQ COUNT
print("Checking total RFQ count...")

driver.get(BASE_URL.format(1))
time.sleep(WAIT_TIME)

try:
    count_text = driver.find_element(By.CSS_SELECTOR, ".content-header-count").text
    total_rfq_count = int(count_text.strip().split()[0].replace(",", ""))
    rfqs_per_page = 20
    total_pages = math.ceil(total_rfq_count / rfqs_per_page)
    total_pages = min(total_pages, 100)  # cap at 100 pages
    print(f"Detected total RFQs: {total_rfq_count}, capped total pages: {total_pages}")
except Exception as e:
    print(f"Failed to detect total RFQs. Defaulting to 1 page. Error: {e}")
    total_pages = 1

#  CREATE CSV FILE 
if os.path.exists(OUTPUT_CSV):
    os.remove(OUTPUT_CSV)

with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(HEADERS)

all_rows = []

# LOOP THROUGH ALL PAGES 
for page in range(1, total_pages + 1):
    print(f"\nScraping page {page}/{total_pages}")
    driver.get(BASE_URL.format(page))
    time.sleep(WAIT_TIME)

    # Get all RFQ cards on this page
    rfq_cards = driver.find_elements(By.CSS_SELECTOR, ".brh-rfq-item")
    print(f"Found {len(rfq_cards)} RFQs on this page.")

    if not rfq_cards:
        print("No RFQs found on this page. Skipping.")
        continue

    for idx, card in enumerate(rfq_cards, start=1):
        print(f"Scraping RFQ {idx} of {len(rfq_cards)}")

        try:
            # TITLE and LINK 
            title_elem = card.find_element(By.CSS_SELECTOR, "a.brh-rfq-item__subject-link")
            title = title_elem.text.strip()
            rfq_link = title_elem.get_attribute("href")
            if rfq_link.startswith("//"):
                rfq_link = "https:" + rfq_link

            # BUYER NAME and IMAGE
            try:
                avatar_section = card.find_element(By.CSS_SELECTOR, ".avatar")
                
                # BUYER NAME
                try:
                    buyer_name = avatar_section.find_element(By.CSS_SELECTOR, ".text").text.strip()
                except:
                    buyer_name = ""
                
                # BUYER IMAGE
                try:
                    buyer_image = avatar_section.find_element(By.CSS_SELECTOR, "img").get_attribute("src").strip()
                except:
                    buyer_image = ""
            except:
                buyer_name = ""
                buyer_image = ""


            # INQUIRY TIME AND DATE
            try:
                raw_inquiry_time = card.find_element(By.CSS_SELECTOR, ".brh-rfq-item__publishtime").text.strip()
                if "Date Posted:" in raw_inquiry_time:
                    inquiry_time = raw_inquiry_time.replace("Date Posted:", "").strip()
                else:
                    inquiry_time = raw_inquiry_time
            except:
                inquiry_time = ""

            # Compute inquiry_date from inquiry_time
            inquiry_date = TODAY_DATE  # Default: today
            if "day" in inquiry_time:
                match = re.search(r"(\d+)", inquiry_time)
                if match:
                    days_ago = int(match.group(1))
                    dt_obj = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                    inquiry_date = dt_obj.strftime("%d-%m-%Y")

            # QUOTES LEFT
            try:
                quotes_left = card.find_element(By.CSS_SELECTOR, ".brh-rfq-item__quote-left span").text.strip()
            except:
                quotes_left = ""

            # COUNTRY
            try:
                country = card.find_element(By.CSS_SELECTOR, ".brh-rfq-item__country").text.strip().split("\n")[-1].strip()
            except:
                country = ""

            # QUANTITY REQUIRED (number + unit)
            try:
                quantity_section = card.find_element(By.CSS_SELECTOR, ".brh-rfq-item__quantity")
                quantity_num = quantity_section.find_element(By.CSS_SELECTOR, ".brh-rfq-item__quantity-num").text.strip()
                
                # All spans inside quantity_section 
                spans = quantity_section.find_elements(By.TAG_NAME, "span")
                
                unit_text = ""
                for span in spans:
                    if span.get_attribute("class") != "brh-rfq-item__quantity-num":
                        if "Quantity Required" not in span.text:
                            unit_text = span.text.strip()
                            break
                
                quantity = f"{quantity_num} {unit_text}".strip()
            except:
                quantity = ""



            # EMAIL CONFIRMATION, EXPERIENCED BUYER, COMPLETE ORDER, TUPICAL REPLIES, INTERACTIVE USER
            card_text = card.text
            card_text_lower = card_text.lower()
            email_confirmed = "Yes" if "email confirmed" in card_text_lower else "No"
            experienced_buyer = "Yes" if "experienced buyer" in card_text_lower else "No"
            complete_order = "Yes" if "complete order via rfq" in card_text_lower else "No"
            typical_replies = "Yes" if "typical replies" in card_text_lower else "No"
            interactive_user = "Yes" if "interactive user" in card_text_lower else "No"


            # GET RFQ ID
            driver.execute_script("window.open(arguments[0]);", rfq_link)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)
            rfq_id = ""
            try:
                if "p=" in driver.current_url:
                    rfq_id = driver.current_url.split("p=")[-1].split("&")[0]
            except:
                pass
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # Append to memory list 
            row = [
                rfq_id, title, buyer_name, buyer_image, inquiry_time, quotes_left, country,
                quantity, email_confirmed, experienced_buyer, complete_order,
                typical_replies, interactive_user, rfq_link, inquiry_date, TODAY_DATE
            ]
            all_rows.append(row)

            # Write to CSV incrementally 
            with open(OUTPUT_CSV, "a", newline='', encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(row)

        except Exception as e:
            print(f"Error parsing RFQ card: {e}")
            continue

driver.quit()
print(f"Done! {len(all_rows)} RFQs saved to {OUTPUT_CSV}")
