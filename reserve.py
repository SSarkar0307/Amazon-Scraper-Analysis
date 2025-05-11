from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# --- SETUP CHROME DRIVER ---
options = Options()
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress ChromeDriver logs
driver = webdriver.Chrome(options=options)

# --- GO TO AMAZON & SEARCH FOR "soft toys" ---
driver.get("https://www.amazon.in/")
wait = WebDriverWait(driver, 20)  # Increased wait time
search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))

search_box.send_keys("soft toys")
search_box.send_keys(Keys.RETURN)
time.sleep(6)  # Increased wait for results to load

# --- SCROLL TO LOAD MORE PRODUCTS ---
for i in range(5):  # Increased scrolls
    driver.execute_script("window.scrollBy(0, 4000)")
    time.sleep(5)  # Increased wait per scroll

# --- PARSE PAGE WITH BEAUTIFULSOUP ---
soup = BeautifulSoup(driver.page_source, 'lxml')
products = soup.find_all('div', {'data-component-type': 's-search-result'})
print(f"Found {len(products)} total products.")

sponsored_data = []

# --- EXTRACT SPONSORED PRODUCT INFO ---
for product in products:
    # Check for sponsored label (case-insensitive, flexible)
    sponsored_tag = product.find('span', string=lambda text: text and 'sponsored' in text.lower()) or \
                    product.find('div', class_=lambda x: x and 'sponsored' in x.lower())
    if sponsored_tag:
        print(f"Processing sponsored product (Label: {sponsored_tag.text.strip()})...")
        try:
            # Title
            title_tag = product.find('span', class_='a-size-medium a-color-base a-text-normal')
            title = title_tag.text.strip() if title_tag else 'N/A'

            # Brand
            brand_tag = product.find('span', class_='a-size-base-plus a-color-base')
            brand = brand_tag.text.strip() if brand_tag else title.split()[0] if title != 'N/A' else 'Unknown'

            # Rating
            rating_tag = product.find('span', class_='a-icon-alt')
            rating = rating_tag.text.split()[0] if rating_tag and rating_tag.text.strip() else 'N/A'

            # Reviews
            review_tag = product.find('span', {'class': 'a-size-base', 'dir': 'auto'})
            reviews = review_tag.text.replace(',', '') if review_tag and review_tag.text.strip().isdigit() else '0'

            # Price
            price_tag = product.find('span', class_='a-price-whole')
            price = price_tag.text.replace(',', '').strip() if price_tag else 'N/A'
            if price and not price.isdigit():
                price = 'N/A'

            # Image URL
            image_tag = product.find('img', class_='s-image')
            image_url = image_tag['src'] if image_tag else 'N/A'

            # Product URL
            link_tag = product.find('a', class_='a-link-normal s-no-outline')
            product_url = 'https://www.amazon.in' + link_tag['href'] if link_tag else 'N/A'

            sponsored_data.append({
                'Title': title,
                'Brand': brand,
                'Rating': rating,
                'Reviews': reviews,
                'Price': price,
                'Image URL': image_url,
                'Product URL': product_url
            })
            print(f"Added sponsored product: {title}")

        except Exception as e:
            print(f"Error processing sponsored product: {e}")
            continue
    else:
        print("Skipping non-sponsored product.")

# --- CLOSE BROWSER ---
driver.quit()

# --- SAVE TO CSV ---
df = pd.DataFrame(sponsored_data)
df.to_csv("soft_toys_sponsored.csv", index=False)
print(f"✅ Scraping complete. {len(sponsored_data)} sponsored products saved to 'soft_toys_sponsored.csv'.")