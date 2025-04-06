import time
import helpers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

def getPageRentals(pageNr, rental):
    # Construct the URL for the page
    url = 'https://www.homegate.ch/mieten/immobilien/land-schweiz/trefferliste?ep=' + pageNr
    # Navigate to the URL
    driver.get(url)
    rentalProperties = driver.find_elements(By.CSS_SELECTOR, '[role="listitem"]')
    # Check if rentalProperties is empty
    if len(rentalProperties) == 0:
        print("No more rental properties found.")
        return rental
    # Loop through the rental properties and extract the required information
    for rentalProperty in rentalProperties:
        property_id = rentalProperty.find_element(By.CSS_SELECTOR, 'a[href*="/mieten/"]').get_attribute('href')
        # Check if the property_id is empty or does not contain a number
        if not property_id and helpers.has_numbers(property_id):
            print("Property ID not found.")
            continue
        #only get number after the last "/"
        try:
            property_id = int(property_id.split("/")[-1])
            price = rentalProperty.find_element(By.XPATH, "//*[contains(@class, 'HgListingCard_price')]").text
            price = helpers.parse_price(price)
            address = rentalProperty.find_element(By.TAG_NAME, "address").text
            space = rentalProperty.find_element(By.XPATH, "//*[contains(@class, 'HgListingRoomsLivingSpace_rooms')]")
            space = space.find_elements(By.CSS_SELECTOR, 'strong')
            rooms = float(space[0].text) if len(space) > 0 else None
            area = space[1].text if len(space) > 1 else None
            rental.append({
                'address' : address,
                'price': price,
                'property_id': property_id,
                'area': area,
                'rooms': rooms
            })
        except Exception as e:
            print(f"Error extracting data from rental property: {e}")
            continue
    return rental

# Set the maximum number of pages to scrape
maxPages = 51
# Initialize an empty list to store the rental properties
rental = []
for i in range(1, maxPages):
    pageNr = str(i)
    print("Scraping page " + pageNr)
    rental = getPageRentals(pageNr, rental)
    if i % 10 == 0:
        print("Sleeping for 3 seconds...")
        time.sleep(3)

# Save the data to a JSON file
df = pd.DataFrame(rental)
filename = 'rental_properties.json'
df.to_json(filename, orient='records', lines=True)

#quickfix to save the data in a readable format
with open(filename, 'w', encoding='utf-8') as file:
    df.to_json(file, force_ascii=False, orient='records', lines=True)
print("Data saved to " + filename)

# It's a good practice to close the browser when done
driver.quit()