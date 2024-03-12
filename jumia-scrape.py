import requests,logging,sqlite3,re
from bs4 import BeautifulSoup,SoupStrainer
#DATABASE CONNECTION
CONN = sqlite3.connect("jumia-products")
CUR = CONN.cursor()

def create_database():
    ###
    # THIS FUNCTION CREATES THE DATABASE AND ADDS SOME INITIAL DATA
    # DATA TO BE INSERTED IN THE CATEGORIES TABLE { category data }
    ###

    CUR.execute("PRAGMA foreign_keys = ON;")

    category_data  = (

        {'category_id' : 'M','category_name' : 'Milk'},
        {'category_id': 'CK', 'category_name': 'CookingOil'},
        {'category_id': 'SF', 'category_name': 'SugarFlour'},
        {'category_id': 'GR', 'category_name': 'GrainsRice'},
    )

    CUR.execute("""
                CREATE TABLE Category (
               category_id VARCHAR(5) PRIMARY KEY UNIQUE,
               category_name VARCHAR(50)
                
               );
               
               """)
    CUR.execute("""
                    
               CREATE TABLE Products(
               Category VARCHAR(5) NOT NULL,
               Name VARCHAR(50) NOT NULL,
               Original_price VARCHAR(50) NOT NULL,
               Price VARCHAR(50) NOT NULL,
               Discount VARCHAR(50) NOT NULL,
               Quantity VARCHAR(50),
               
               FOREIGN KEY (Category) REFERENCES Category (category_id )
               );
    
    """)

    #POPOLATING THE DB
    CUR.executemany('INSERT INTO Category VALUES (:category_id , :category_name)',category_data)

    CONN.commit()


def Scrape(Key,url,headers):
    URL_KEY = Key
    page = requests.get(url,headers)
    if page.status_code == 200:
        try:
            soup = BeautifulSoup(page.text, 'html.parser', )
            main_content = soup.body.main
            main_children = main_content.contents
            products_shelf = main_children[3]
            product_contents = products_shelf.contents[2]
            product_content = product_contents.section
            products = product_content.contents[1]
            for product in products:
                product_details = product.a.contents
                info = product.a.contents[1]

                product_name = info.h3.string
                product_price = info.find('div', class_="prc").string
                product_discount = 0
                product_original_price = product_price

                quantity = re.search('(?P<Quantity>\d+(\w+?)?\s\w+|\d\w+)',product_name,re.IGNORECASE)
                if quantity:
                    product_quantity = quantity.group('Quantity') + " 80% ACC."
                else:
                    product_quantity = 0

                if info.find('div', class_="s-prc-w"):
                    product_discount = info.find('div', class_="s-prc-w").contents[1].string
                    product_original_price = info.find('div', class_="s-prc-w").contents[0].string

                product = (
                    {'Category' : URL_KEY,
                     'Name' : product_name,
                     'Original_price':product_original_price,
                     'Price': product_price,
                     'Discount':product_discount,
                     'Quantity': product_quantity
                     }
                )


                CUR.execute("INSERT INTO Products VALUES (:Category,:Name,:Original_price,:Price,:Discount,:Quantity )",product)
                CONN.commit()
                print(f"""PRODUCT : {product_name},\n
                                            PRICE {product_price}\n
                                            DISCOUNT/PROMOTION : {product_discount}\n
                                            PRICE BEFORE DISCOUNT : {product_original_price}\n
                                            QUANTITY = {product_quantity}\n
                                            KEY  = {URL_KEY}""")

        except:
            logging.exception("An error occured while parsing")
            return 1

def SCRAPE(Urls):
    URLS= urls
    for key,url in URLS.items():
        Scrape(key,url,headers)


#URL FOR PAGE AND SETTING CUSTOM HEADERS

#url = "https://www.jumia.co.ke/cooking-oil/"
#url = "https://www.jumia.co.ke/sugar-flour/"
url = "https://www.jumia.co.ke/grains-rice/"
# url = "https://www.jumia.co.ke/milk/"

urls = {'GR':'https://www.jumia.co.ke/grains-rice/',
        'M':'https://www.jumia.co.ke/milk/',
        'SF':'https://www.jumia.co.ke/sugar-flour/',
        'CK':'https://www.jumia.co.ke/cooking-oil/'
        }
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'
}

try:
    create_database()
    SCRAPE(urls)
except sqlite3.OperationalError:
    SCRAPE(urls)


#Scrape("GR","https://www.jumia.co.ke/grains-rice/",headers)

