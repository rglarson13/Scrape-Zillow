'''
I started writing this after hearing about the "This Face Does Not Exist" GAN project
I was going to scrape listings to build a corpus of text so that I could then
generate artificial descriptions of houses.

But this is basically three-part project:
1. Get the list of local listings
2. Iterate over each individual listing to scrape the text
3. Simulate text

This script is the first part of that project. 
It's actually adapted from another one of my scripts that scrapes Amazon reviews by ASIN.
'''

from lxml import html
import os
import requests

from time import sleep
from datetime import date

import pandas as pd
 
def Parse_Zillow(zip):
    #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	headers = {'User-Agent': 'Whatever works'}
	
    
    # sort by days on zillow
    url = 'https://www.zillow.com/homes/for_sale/{}/0_singlestory/days_sort'.format(zip)
    
    # sort by price
    #url = 'https://www.zillow.com/homes/for_sale/{}/0_singlestory/pricea_sort/''.format(zip)
     
    tries = 0
    NAME = None
    data = []
    
    XPATH_NAME = ".//h4//text()"
    XPATH_ADDRESS = ".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()"
    XPATH_CITY = ".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()"
    XPATH_STATE = ".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()"
    XPATH_POSTAL_CODE = ".//span[@itemprop='address']//span[@itemprop='postalCode']//text()"
    XPATH_INFO = ".//span[@class='zsg-photo-card-info']//text()"
    XPATH_PRICE = ".//span[@class='zsg-photo-card-price']//text()"
    XPATH_LINK = ".//a[contains(@class,'overlay-link')]/@href"
    XPATH_AVAILABILITY = ".//span[@class='zsg-icon-for-sale']" 

    while ((tries <= 3) and (NAME == None)):
        tries = tries + 1

        try:
            page = requests.get(url, headers = headers)
            sleep(3)
            doc = html.fromstring(page.text)
            results = doc.xpath("//div[@id='search-results']//article")
            
            for listing in results:
                RAW_NAME = listing.xpath(XPATH_NAME)
                RAW_ADDRESS = listing.xpath(XPATH_ADDRESS)
                RAW_CITY = listing.xpath(XPATH_CITY)
                RAW_STATE = listing.xpath(XPATH_STATE)
                RAW_POSTAL_CODE = listing.xpath(XPATH_POSTAL_CODE)
                RAW_INFO = listing.xpath(XPATH_INFO)
                RAW_PRICE = listing.xpath(XPATH_PRICE)
                RAW_LINK = listing.xpath(XPATH_LINK)
                
                RAW_AVAILABILITY = listing.xpath(XPATH_AVAILABILITY)

                NAME = ''.join(RAW_NAME).strip() if RAW_NAME else None
                ADDRESS = ''.join(RAW_ADDRESS).strip() if RAW_ADDRESS else None
                CITY = ''.join(RAW_CITY).strip() if RAW_CITY else None
                STATE = ''.join(RAW_STATE).strip() if RAW_STATE else None
                POSTAL_CODE = ''.join(RAW_POSTAL_CODE).strip() if RAW_POSTAL_CODE else None
                INFO = ' '.join(RAW_INFO).split().replace(u"\xb7",',')
                PRICE = ''.join(RAW_PRICE).strip() if RAW_PRICE else None
                AVAILABILITY = True if RAW_AVAILABILITY else None
                LINK = 'https://www.zillow.com' + RAW_LINK[0] if RAW_LINK else None 

                if page.status_code != 200:
                    raise ValueError('captcha')

                listing_data = {
                        'DATE': date.today(),
                        'NAME': NAME,
                        'ADDRESS': ADDRESS,
                        'CITY': CITY,
                        'STATE': STATE,
                        'POSTAL_CODE': POSTAL_CODE,
                        'INFO': INFO,
                        'PRICE': PRICE,
                        'AVAILABILITY': AVAILABILITY,
                        'LINK': LINK
                        }

                print(listing_data)

                data.append(listing_data)
        
        except Exception as e:
            print(e)
            
            error_delay = 10
            
            print('Sleeping for {} seconds'.format(error_delay))
            sleep(error_delay)
            
    return data
            
        
    

def ReadZip():
    ZipList = [
    55109, # Maplewood
    55128, # Oakdale
    55125 # Stillwater
    ]
    
    extracted_data = []
    
    counter = 0
    
    for i in ZipList:
        counter = counter + 1
        print("Processing: " + str(i))
        extracted_data.append(Parse_Zillow(i))
        print(str(int((counter / len(ZipList)) * 100)) + "% done.")
        sleep(3)
           
    
    df = pd.DataFrame.from_dict(extracted_data)
    
    currentPath = os.getcwd()
    csv_file = currentPath + '/zillow_data - ' + str(date.today()) + '.csv'
    df.to_csv(csv_file)

ReadZip()