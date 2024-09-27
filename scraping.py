from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv


driver = webdriver.Chrome()
# map don't appear with this w_sizw
driver.set_window_size(1000, 641)


driver.get("https://www.zillow.com/hollywood-hills-los-angeles-ca/")


time.sleep(5)


scroll_pause_time = 3  
scroll_increment = 500  

# Open CSV file to write data 
with open('zillow_data_hollywood-hills-los-angeles-ca.csv', 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['price', 'bds', 'bat', 'sqrft', 'link', 'address']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    
    if csvfile.tell() == 0:
        writer.writeheader()

    # for smoot scroling
    def gradual_scroll():
        current_scroll_position = 0
        max_scroll_position = 4500  # next page button appear here
        #loop for scrolling
        while current_scroll_position < max_scroll_position:
            
            driver.execute_script(f"window.scrollTo(0, {current_scroll_position});")
            time.sleep(scroll_pause_time)  # Wait for new content to load
            current_scroll_position += scroll_increment

            # for load new element in my property list
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="grid-search-results"]/ul/li'))
                )
                print(f"Scrolled to {current_scroll_position}px...")
            except Exception as e:
                print(f"Failed to locate elements after scroll: {e}")
                break

    # next page
    def go_to_next_page():
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@title="Next page"]'))
            )
            current_url = driver.current_url
            next_button.click()
            print("Navigating to the next page...")
            WebDriverWait(driver, 10).until(EC.url_changes(current_url))
            print("Page URL changed, new page loaded.")
            time.sleep(5)  
            return True  
        except Exception as e:
            print(f"Could not click on the next page button: {e}")
            return False  

    # Main loop for scrolling, data extraction, and going to the next page
    page = 0
    while True:
        driver.get(f"https://www.zillow.com/hollywood-hills-los-angeles-ca/")
        
        gradual_scroll()

        
        property_list = driver.find_elements(By.XPATH, '//*[@id="grid-search-results"]/ul/li')

        # Extract data from each property
        for property in property_list:
            
            property_data = {}

            try:
                price = property.find_element(By.XPATH, './/span[@data-test="property-card-price"]').text
                property_data['price'] = price
            except Exception as e:
                property_data['price'] = None
                print(f"Price not found: {e}")

            try:
                bds = property.find_element(By.XPATH, ".//ul[@class ='StyledPropertyCardHomeDetailsList-c11n-8-105-0__sc-1j0som5-0 ldtVy']/li[position()=1]/b").text
                property_data['bds'] = bds
            except Exception as e:
                property_data['bds'] = None
                print(f"Bds not found: {e}")

            try:
                bat = property.find_element(By.XPATH, ".//ul[@class ='StyledPropertyCardHomeDetailsList-c11n-8-105-0__sc-1j0som5-0 ldtVy']/li[position()=2]/b").text
                property_data['bat'] = bat
            except Exception as e:
                property_data['bat'] = None
                print(f"Bat not found: {e}")

            try:
                sqrft = property.find_element(By.XPATH, ".//ul[@class ='StyledPropertyCardHomeDetailsList-c11n-8-105-0__sc-1j0som5-0 ldtVy']/li[position()=3]/b").text
                property_data['sqrft'] = sqrft
            except Exception as e:
                property_data['sqrft'] = None
                print(f"Sqrft not found: {e}")

            try:
                link_p = property.find_element(By.XPATH, ".//div[@class ='StyledPropertyCardDataWrapper-c11n-8-105-0__sc-hfbvv9-0 jqlVkt property-card-data']/a")
                link = link_p.get_attribute('href')
                property_data['link'] = link
            except Exception as e:
                property_data['link'] = None
                print(f"Link not found: {e}")

            try:
                address = property.find_element(By.XPATH, ".//div[@class ='StyledPropertyCardDataWrapper-c11n-8-105-0__sc-hfbvv9-0 jqlVkt property-card-data']/a/address").text
                property_data['address'] = address
            except Exception as e:
                property_data['address'] = None
                print(f"Address not found: {e}")

            # Write the row to CSV
            writer.writerow(property_data)

        #Go to the next page
        if not go_to_next_page():
            print("No more pages available. Exiting.")
            break  

        time.sleep(3)
        print(f"Scraping page {page + 1}, URL: {driver.current_url}")
        page= page + 1
        print(page)

# Close the browser after scraping is complete
driver.quit()
