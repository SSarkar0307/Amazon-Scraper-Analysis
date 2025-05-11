from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def set_up_driver():
    """Set up and configure the Chrome WebDriver"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Enable images to make sure we can detect image-based sponsored labels
    # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    
    # Add debugging options
    options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation
    
    print("Setting up Chrome WebDriver with optimized options...")
    driver = webdriver.Chrome(options=options)
    
    # Add a small delay to ensure the browser is fully initialized
    time.sleep(1)
    
    return driver

def search_amazon(driver, search_term):
    """Navigate to Amazon and search for the specified term"""
    print(f"Navigating to Amazon India and searching for '{search_term}'...")
    driver.get("https://www.amazon.in/")
    
    # Wait for and interact with the search box
    wait = WebDriverWait(driver, 30)
    try:
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Short pause after search submission
    except TimeoutException:
        print("Timeout waiting for search box. Trying alternative approach...")
        driver.get(f"https://www.amazon.in/s?k={search_term.replace(' ', '+')}")
        time.sleep(3)

def scroll_page(driver, scroll_pauses=8, scroll_amount=1000):
    """Scroll the page to load more products with improved reliability"""
    print(f"Scrolling page to load more products ({scroll_pauses} pauses)...")
    
    # Get initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(scroll_pauses):
        print(f"Scroll {i+1}/{scroll_pauses}...")
        
        # Scroll down in smaller increments for better content loading
        for _ in range(3):
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(1)
        
        # Wait for page to load new content
        time.sleep(3)
        
        # Calculate new scroll height and check if we've reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the end of the page or no new content loading")
            # Try one more aggressive scroll to be sure
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            break
        last_height = new_height
    
    # Scroll back to top for complete page parsing
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

def is_sponsored(product):
    """Improved detection of sponsored products on Amazon India"""
    try:
        # Check for explicit 'Sponsored' badge via text
        badge = product.select_one("span.a-color-secondary, span.a-text-bold")
        if badge and badge.text.strip().lower() == "sponsored":
            return True

        # Look for 'Sponsored' inside nested spans/divs
        for tag in product.find_all(['span', 'div']):
            if tag.text.strip().lower() == "sponsored":
                return True

        # Sponsored label via ARIA label or data attribute (used in mobile view and newer Amazon layouts)
        if 'data-component-type' in product.attrs and product['data-component-type'] == 's-sponsored-result':
            return True

        # Search inside specific divs used for sponsored labeling
        possible_labels = product.select("div.s-sponsored-label-info-icon, span.sponsored-label-text, span.puis-sponsored-label")
        for label in possible_labels:
            if "sponsored" in label.text.strip().lower():
                return True
    except Exception:
        pass
    return False


def extract_product_info(product):
    """Extract all required information from a product element with improved robustness"""
    try:
        # Title extraction - try multiple possible selectors
        title = "N/A"
        title_selectors = [
            ('span', {'class': 'a-size-medium a-color-base a-text-normal'}),
            ('span', {'class': 'a-size-base-plus a-color-base a-text-normal'}),
            ('h2', {'class': 'a-size-mini'}),
            ('h5', {'class': 'a-color-base s-line-clamp-2'})
        ]
        for selector in title_selectors:
            title_element = product.find(selector[0], selector[1])
            if title_element and title_element.text.strip():
                title = title_element.text.strip()
                break
        
        # Brand extraction
        brand = "Unknown"
        brand_element = product.find('span', {'class': 'a-size-base-plus a-color-base'})
        if brand_element and brand_element.text.strip():
            brand = brand_element.text.strip()
        else:
            # Alternative: try to get brand from the product URL
            link_elem = product.find('a', {'class': 'a-link-normal'})
            if link_elem and 'href' in link_elem.attrs:
                href = link_elem['href']
                brand_match = re.search(r'\/stores\/node\/\d+\/(\w+)', href)
                if brand_match:
                    brand = brand_match.group(1).replace('-', ' ').title()
                elif title != "N/A":
                    # Use first word of title as fallback for brand
                    brand = title.split()[0]
        
        # Rating extraction
        rating = "N/A"
        rating_elem = product.find('span', {'class': 'a-icon-alt'})
        if rating_elem and rating_elem.text:
            rating_text = rating_elem.text.strip()
            rating_match = re.search(r'([\d\.]+)', rating_text)
            if rating_match:
                rating = rating_match.group(1)
            
        # Reviews count extraction
        reviews = "0"
        reviews_elem = product.find('span', {'class': 'a-size-base', 'dir': 'auto'})
        if reviews_elem and reviews_elem.text.strip():
            reviews_text = reviews_elem.text.strip()
            # Extract only digits from the reviews text
            reviews_digits = re.sub(r'[^\d]', '', reviews_text)
            if reviews_digits:
                reviews = reviews_digits
        
        # Price extraction
        price = "N/A"
        price_whole_elem = product.find('span', {'class': 'a-price-whole'})
        if price_whole_elem and price_whole_elem.text.strip():
            price = price_whole_elem.text.strip().replace(',', '').rstrip('.')
        
        # Image URL extraction
        image_url = "N/A"
        image_elem = product.find('img', {'class': 's-image'})
        if image_elem and 'src' in image_elem.attrs:
            image_url = image_elem['src']
        
        # Product URL extraction
        product_url = "N/A"
        link_elem = product.find('a', {'class': 'a-link-normal'})
        if link_elem and 'href' in link_elem.attrs:
            href = link_elem['href']
            if href.startswith('/'):
                product_url = f"https://www.amazon.in{href}"
            else:
                product_url = href
        
        return {
            'Title': title,
            'Brand': brand,
            'Rating': rating,
            'Reviews': reviews,
            'Price': price,
            'Image URL': image_url,
            'Product URL': product_url
        }
    
    except Exception as e:
        print(f"Error extracting product info: {e}")
        return None

def extract_sponsored_products(soup):
    """Extract all sponsored products from the page with comprehensive parsing"""
    print("Extracting sponsored products from page...")
    sponsored_data = []
    
    # Find all product containers
    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    if not products:
        print("No standard product containers found, trying alternative selectors...")
        # Try alternative product container selector
        products = soup.find_all('div', {'class': lambda c: c and 'sg-col-' in c})
    
    print(f"Found {len(products)} total product elements to analyze")
    sponsored_count = 0
    non_sponsored_count = 0
    
    for idx, product in enumerate(products, 1):
        # Debug output to help identify issues
        debug_id = product.get('data-asin', f'unknown-{idx}')
        
        if is_sponsored(product):
            sponsored_count += 1
            print(f"Processing SPONSORED product {idx} [ASIN: {debug_id}]...")
            product_info = extract_product_info(product)
            if product_info:
                # Add a sponsored marker to the data
                product_info['Is Sponsored'] = 'Yes'
                sponsored_data.append(product_info)
                print(f"✓ Added sponsored product: {product_info['Title'][:40]}...")
            else:
                continue  # Skip non-sponsored products completely
        else:
            non_sponsored_count += 1
            print(f"Skipping NON-SPONSORED product {idx} [ASIN: {debug_id}]")
    
    print(f"\nSUMMARY: Found {sponsored_count} sponsored products and {non_sponsored_count} non-sponsored products")
    
    # Verification check
    if sponsored_count == 0:
        print("\n⚠️ WARNING: No sponsored products were found. This might indicate an issue with detection.")
        print("Consider reviewing the HTML structure or enabling debug mode.")
    
    return sponsored_data

def main():
    """Main function to run the scraper"""
    driver = set_up_driver()
    search_term = "soft toys"
    all_sponsored_data = []
    
    try:
        # Search and navigate to results page
        search_amazon(driver, search_term)
        
        # Add a debug function to help identify sponsored elements
        print("\n🔍 DEBUG: Looking for sponsored elements in page source...")
        page_source_sample = driver.page_source[:10000]  # Look at first 10K chars
        common_sponsor_patterns = [
            "Sponsored", "sponsored-label", "s-sponsored-label", 
            "puis-sponsored-label", "data-component-type=\"s-sponsored"
        ]
        
        for pattern in common_sponsor_patterns:
            if pattern in page_source_sample:
                print(f"✓ Found pattern '{pattern}' in page source!")
            else:
                print(f"✗ Pattern '{pattern}' NOT found in page source.")
        
        # Take a screenshot before scrolling (optional but helpful)
        try:
            screenshot_file = "amazon_before_scroll.png"
            driver.save_screenshot(screenshot_file)
            print(f"Saved screenshot to {screenshot_file}")
        except:
            print("Could not save screenshot")
        
        # Scroll to load more products
        scroll_page(driver, scroll_pauses=10, scroll_amount=800)
        
        # Parse the page
        print("Parsing page with BeautifulSoup...")
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        # Extract sponsored products
        sponsored_data = extract_sponsored_products(soup)
        all_sponsored_data.extend(sponsored_data)
        
        # Optional: Enable pagination if needed
        enable_pagination = False  # Set to True to scrape multiple pages
        if enable_pagination:
            try:
                for page in range(2, 3):  # Limit to first 2 pages
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '.s-pagination-next:not(.s-pagination-disabled)'))
                    )
                    if next_button:
                        print(f"Navigating to page {page}...")
                        next_button.click()
                        time.sleep(5)
                        scroll_page(driver, scroll_pauses=5)
                        soup = BeautifulSoup(driver.page_source, 'lxml')
                        page_sponsored_data = extract_sponsored_products(soup)
                        all_sponsored_data.extend(page_sponsored_data)
                    else:
                        print("No more pages available")
                        break
            except Exception as e:
                print(f"Error navigating to next page: {e}")
        
    except Exception as e:
        print(f"Error during scraping process: {e}")
    
    finally:
        # Close the browser
        driver.quit()
    
    # Save the data to CSV
    if all_sponsored_data:
        df = pd.DataFrame(all_sponsored_data)
        filename = f"{search_term.replace(' ', '_')}_sponsored.csv"
        df.to_csv(filename, index=False)
        print(f"\n✅ Scraping complete! {len(all_sponsored_data)} sponsored products saved to '{filename}'")
        print(f"Columns in CSV: {', '.join(df.columns)}")
        
        # Print a sample of the data
        if len(df) > 0:
            print("\nSample data (first 2 rows):")
            print(df.head(2).to_string())
            
            # Verify we only have sponsored products
            if 'Is Sponsored' in df.columns:
                if df['Is Sponsored'].all() == 'Yes':
                    print("\n✓ VERIFICATION: All products in the CSV are confirmed sponsored.")
                else:
                    print("\n⚠️ WARNING: Some products may not be sponsored!")
    else:
        print("❌ No sponsored products found or error in scraping!")
        print("This could be due to:")
        print("1. No sponsored products on the page")
        print("2. Sponsored product detection needs adjustment")
        print("3. Amazon changed their HTML structure")
        print("Try enabling debug mode or check the saved screenshot for visual verification.")

if __name__ == "__main__":
    main()