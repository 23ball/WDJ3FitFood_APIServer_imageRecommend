import os
import csv
from selenium import webdriver
import json
import urllib.request

import mysql.connector

config = {'user': 'root','password': '', 'host': 'localhost', 'db': 'fitfood_v1'}
conn = mysql.connector.connect(**config)
cur = conn.cursor(buffered=True)

browser = webdriver.Chrome("./chromedriver.exe")
header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}


image_dir = "./images/"
# resCsv = open('resList.csv','r', encoding="iso-8859-1")
# menuCsv = open('menuList.csv','r')
# resReader = csv.reader(resCsv)
# menuReader = csv.reader(menuCsv)
# cur.execute('select * from foods')
# menuReader = cur.fetchall()
# menuList = list(menuReader)
cur.execute('select * from stores')
resReader = cur.fetchall()
# for menuInfo in menuReader:
#     print(menuInfo[0])
# asdfafsd
resInfoList = [list(resInfo) for resInfo in resReader]
print("ok")
# adsfsadf
# def main():
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "" # CPU만 사용할 경우 설정
# for i in range(len(resInfoList)):
for i in range(len(resInfoList)):
    menusImageDir = image_dir + str(resInfoList[i][0])
    if(not os.path.isdir((menusImageDir))):
        os.mkdir(menusImageDir)
    menus = []
    cur.execute('select * from foods where store_id = ' + str(resInfoList[i][0]))
    menuReader = cur.fetchall()
    for menuInfo in menuReader:
        print(menuInfo)
        menus.append(str(menuInfo[1])) 
        
    for menu in menus:
        oneMenuImageDir = menusImageDir + '/' + menu
        print(oneMenuImageDir)
        if(not os.path.isdir((oneMenuImageDir))):
            os.mkdir(oneMenuImageDir)
        else:
            break
        url = "https://www.google.co.in/search?q=" + menu + "&tbm=isch"
        browser.get(url)
        counter = 0
        for i in range(20):
            browser.execute_script('window.scrollBy(0,10000)')
        for idx , el in enumerate(browser.find_elements_by_class_name("rg_i")):
            counter = counter + 1
            el.screenshot(oneMenuImageDir +'/' + str(idx) + ".png")
browser.close()

# if __name__ == "__main__":
#     main()