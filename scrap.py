import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_product_details(url):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
    session = requests.Session()
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    asinv=''
    manufcr=''
    div_element = soup.select_one('div#detailBullets_feature_div')
    if div_element:
    # Find the ul element inside the selected div
        ul_element = div_element.select_one('ul')
        if ul_element:
            # Select the 4th li element inside the ul
            li_elements = ul_element.select('li')
            if len(li_elements) >= 4:
                fourth_li = li_elements[3]
                soup1 = BeautifulSoup(fourth_li.prettify(),'html.parser')
                span_elements1 = soup1.select_one('span.a-text-bold')
                asinv = span_elements1.find_next_sibling('span', class_=False).text.strip()
                third_li = li_elements[2]
                soup2 = BeautifulSoup(third_li.prettify(),'html.parser')
                span_elements = soup2.select_one('span.a-text-bold')
                manufcr = span_elements.find_next_sibling('span', class_=False).text.strip()

            else:
                print("4th li element not found inside the ul.")
        else:
            print("ul element not found inside the div.")
    else:
        print("div element with id 'detailBullets_feature_div' not found.")
    desc = soup.select_one('div#feature-bullets')
    desc_res = ''
    if desc:
        li_elements = desc.select('ul.a-unordered-list.a-vertical.a-spacing-mini li')
        # Loop through each <li> element and get the inner text of the <span> element inside it
        for li_element in li_elements:
            span_element = li_element.select_one('span.a-list-item')
            if span_element:
                print(span_element.text.strip())
                desc_res += span_element.text.strip()
    description = desc_res.strip()
    asin = asinv
    manufacturer = manufcr
    return description, asin, manufacturer

def scrape_amazon_products(base_url, num_pages):
    all_data = []
    for page_num in range(1, num_pages + 1):
        url = f"{base_url}&page={page_num}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
        session = requests.Session()
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.select('div.s-list-col-right')
        for product in products:
            # purl = product.select_one('a.a-link-normal')
            try:
                prdt = product.select_one('h2')
                print("product name:",product.select_one('h2').text)
                print("product price:",product.select_one('div span.a-price-whole').text)
                print("rating:",product.select_one('div i span').text)
                print("no of review:",product.select_one('span.a-size-base.s-underline-text').text)
                urltem =  prdt.select_one('a.a-link-normal')['href']
                if urltem.find("http") != -1:
                    product_url = urltem
                else:
                    product_url = "https://www.amazon.in" + prdt.select_one('a.a-link-normal')['href']        
                print("url:",product_url)
                data = {}
                try:
                    description, asin, manufacturer = scrape_product_details(product_url)
                    data = {
                        'Product URL': product_url,
                        'Product Name': product.select_one('h2').text,
                        'Product Price': product.select_one('div span.a-price-whole').text,
                        'Rating': product.select_one('div i span').text,
                        'Number of Reviews': product.select_one('span.a-size-base.s-underline-text').text,
                        'Description': description,
                        'ASIN': asin,
                        'Manufacturer': manufacturer
                    }
                except Exception as e:
                    print(e)
                    data = {
                        'Product URL': product_url,
                        'Product Name': product.select_one('h2').text,
                        'Product Price': product.select_one('div span.a-price-whole').text,
                        'Rating': product.select_one('div i span').text,
                        'Number of Reviews': product.select_one('span.a-size-base.s-underline-text').text,
                        'Description': "description exception",
                        'ASIN': "asin exception",
                        'Manufacturer': "manufacturer exception"
                    }
                all_data.append(data)
                time.sleep(1)  # Adding a delay to be polite to the server
            except Exception as e:
                print("excp")
    return all_data

if __name__ == "__main__":
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C6104MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
    num_pages_to_scrape = 40
    scraped_data = scrape_amazon_products(base_url, num_pages_to_scrape)
    df = pd.DataFrame(scraped_data)
    df.to_csv('amazon_products_details.csv', index=False)
