import requests
from bs4 import BeautifulSoup

def fetch_discounted_items():
    # URL of the Shein website with discounted items
    url = 'https://us.shein.com/'
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all elements with the specified class that contain discounted items
        discounted_items = soup.find_all(class_='j-switch-grid-view _j-goods-grid')
        
        # Print the details of each discounted item
        for item in discounted_items:
            item_name = item.find(class_='j-goods-info').find('a').text.strip()
            item_price = item.find(class_='j-switch-price').text.strip()
            item_discount = item.find(class_='j-switch-discount').text.strip()
            
            print(f'Item: {item_name}')
            print(f'Price: {item_price}')
            print(f'Discount: {item_discount}')
            print('---')
    else:
        print('Failed to fetch data. Status code:', response.status_code)

if __name__ == "__main__":
    fetch_discounted_items()
