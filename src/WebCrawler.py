import os, csv, time, requests, pymysql
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
def get_notebook_link():
    url = "https://store.asus.com/tw/category/A15061"
    # through browser and hidden window
    chromeOption = Options()
    chromeOption.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver', chrome_options = chromeOption)

    # enter the url and waiting loading
    driver.get(url)
    time.sleep(3)

    # use bs4 crawler "notebook link" and close the browser
    content = bs(driver.page_source, "html.parser")
    linkList = content.select("a.photo")
    hrefs = []
    for link in linkList:
        hrefs.append(link.get("href"))
    driver.close()
    return hrefs

if __name__ == "__main__":
    hrefs = get_notebook_link()
    wants = ["型號", "價格", "CPU", "GPU", "RAM", "資料儲存應用", "保固"]
    # connect database
    DB = {"DB":"db_name","user":"db_user", "password":"db_password"}
    db = pymysql.connect("localhost", DB["user"], DB["password"], DB["DB"])
    cursor = db.cursor()
    product = []
    productID = 1
    for href in hrefs:
        # request website
        resource = requests.get("https:" + href)
        content = bs(resource.text, "html.parser")

        # find product name and price
        product.append(productID)
        product.append(content.find("h1", id="pro_title").text)
        product.append(content.find("span", {'class':"price"}).text)

        # find product detail
        check = 0
        itemsTitle = content.select(".css-spec-item")
        itemsData = content.select(".css-spec-data")
        for index in range(len(itemsTitle)):
            itemsTitle[index] = itemsTitle[index].text
            itemsData[index] = itemsData[index].text.replace("\n","")
        for index, item in enumerate(itemsTitle):
            if item in wants:
                product.append(itemsData[index])
                check += 1
        # checking data, transform "price" type and store in database
        if check == 5:
            product[2] = int(product[2].replace(",",""))
            cursor.execute('insert into laptop value(%s,%s,%s,%s,%s,%s,%s,%s,null,"ASUS")',[product[i] for i in range(8)])
            productID += 1
        product.clear()
    db.commit()
