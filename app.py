from flask import Flask, request, send_file, jsonify
import csv
from bs4 import BeautifulSoup
from PIL import Image
import keras.backend.tensorflow_backend as tb
import numpy as np
import requests
import base64
import io
import food_keras as food
#
import os
#
#
from flask_cors import CORS

import mysql.connector

# config = {'user': '','password': '', 'host': '', 'db': ''}
config = {'user': 'root','password': '', 'host': 'localhost', 'db': 'fitfood_v1'}
conn = mysql.connector.connect(**config)
cur = conn.cursor(buffered=True)
#

app = Flask(__name__)

@app.route('/test2', methods=['POST'])
def getBalance():
    food = request.form['food']
    url= "https://www.fatsecret.kr/칼로리-영양소/일반명/" + str(food)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    infos = [ i.text for i in soup.select('div.nutrition_facts div')]
    menuInfo = [" " for i in range(10)]
    for i in range(len(infos)):
        if (infos[i] == "열량"):
            menuInfo[3] = (infos[i + 4][:-4])
            kcal = infos[i + 4][:-4]
        elif(infos[i] == "탄수화물"):
            menuInfo[4] = float(infos[i + 1][:-1])
            carbon = infos[i + 1][:-1]
        elif(infos[i] == "단백질"):
            menuInfo[5] = float(infos[i + 1][:-1])
            protein = infos[i + 1][:-1]
        elif(infos[i] == "지방"):
            menuInfo[6] = float(infos[i + 1][:-1])
            fat = infos[i + 1][:-1]
        elif(infos[i] == "나트륨"):
            menuInfo[7] = (infos[i + 1][:-2])
            na = infos[i + 1][:-2]
        elif(infos[i] == "칼륨"):
            menuInfo[8] = (infos[i + 1][:-2])
            cal = infos[i + 1][:-2]
        elif(infos[i] == "식이섬유"):
            menuInfo[9] = (infos[i + 1][:-1])
            sik = infos[i + 1][:-1]
    if not menuInfo:
        return menuInfo
    else:
        #
        # fw = open('calList3.csv', 'r', encoding='UTF8')
        # #
        # calRdr = csv.reader(fw)

        # goodTan = [330, 400]
        # goodDan = [42, 120]
        # goodJi = [40, 80]

        # menuList = [ line for line in calRdr ]
        # foodList = []
        # resList = {}
        # for i in menuList:
        #     resList[i[1]] = i[0]

        # for i in range(0, len(menuList)):
        #     for j in range(i ,len(menuList)):
        #         if (goodTan[0] - menuInfo[4])  <= float(menuList[i][4]) + float(menuList[j][4]) <= (goodTan[1]  - menuInfo[4]) :
        #             if (goodDan[0]  - menuInfo[5])   <= float(menuList[i][5]) + float(menuList[j][5]) <= (goodDan[1]  - menuInfo[5]) :
        #                 if (goodJi[0]  - menuInfo[6])  <= float(menuList[i][6]) + float(menuList[j][6]) <= (goodJi[1]  - menuInfo[6]) :
        #                     if not menuList[i][1] == menuList[j][1] and not food == menuList[i][1]  and not food == menuList[j][1]:
        cur.execute('select * from foods join nutrients on foods.food_id = nutrients.food_id;')
        menuList = cur.fetchall()
        goodTan = [330 - menuInfo[4], 400  - menuInfo[4]]
        goodDan = [42 - menuInfo[5], 120 - menuInfo[5]]
        goodJi = [40 - menuInfo[6], 80  - menuInfo[6]]

        foodList = []
        resList = {}
        for i in menuList:
            resList[i[1]] = i[3]

        for i in range(0, len(menuList)):
            for j in range(i ,len(menuList)):
                if goodTan[0] <= float(menuList[i][6]) + float(menuList[j][6]) <= goodTan[1] :
                    if goodDan[0] <= float(menuList[i][7]) + float(menuList[j][7]) <= goodDan[1] :
                        if goodJi[0] <= float(menuList[i][8]) + float(menuList[j][8]) <= goodJi[1] :
                            if not food == menuList[i][1] and not food == menuList[j][1] and not menuList[i][1] == menuList[j][1]:
                                foodList.append(tuple([menuList[i][1], menuList[j][1]]))
        
        foodList = list(set(foodList))
        resultList = []
        #
        for i in foodList:
            lunch_img = os.path.abspath('./images2/' + str(resList[i[0]]) + '/' + str(i[0]) + '/' + '0.png')
            dinner_img = os.path.abspath('./images2/' + str(resList[i[1]]) + '/' + str(i[1]) + '/' + '0.png')
            resultList.append({'resNum_lunch': resList[i[0]], 'lunch' : i[0], 'resNum_dinner':  resList[i[1]], 'dinner': i[1] ,
                                'lunch_img': lunch_img, 'dinner_img': dinner_img})
        #
        return jsonify(resultList)

@app.route('/test', methods=['POST'])
def getCal():
    str_img = request.form['img']
    #
    resNum = request.form['resNum']
    #
    print(str_img)
    image = base64.b64decode(str_img)
    img = Image.open(io.BytesIO(image))
    tb._SYMBOLIC_SCOPE.value = True 
    # image = request.files['img']
    #
    caltech_dir = './images/' + str(resNum)
    categories = os.listdir(caltech_dir)
    if ".DS_Store" in categories :
           categories.remove('.DS_Store')
    categories = sorted(categories)
    #
    image_size = 64
    #
    # categories = ["dongas", "kimchi", "onion", "ttukbul", "rice"]
    # calories = [600, 300, 100, 500, 200]
    #
    X = []
    files = []

    # img = Image.open(image)
    img = img.convert("RGB")
    img = img.resize((image_size, image_size))
    in_data = np.asarray(img)
    X.append(in_data)
    files.append(in_data)
    X = np.array(X)

    model = food.build_model(X.shape[1:], resNum)
    #
    # model.load_weights("./input/image/food-model.hdf5")
    model.load_weights("./models/" + str(resNum) + ".hdf5")
    #
    pre = model.predict(X)
    for i, p in enumerate(pre):
        y = p.argmax()
    return str(categories[y])

@app.route('/break', methods=['GET'])
def checkBreak():
    # result = {}
    if os.path.isfile('./break.txt'):
        return str('true')
    else:
        return str('false')

@app.route('/recommendFood', methods=['POST'])
def recommendFood():
    # if os.path.isfile('./break.txt'):
    #     f = open('break.txt', encoding='utf-8')
    #     food = f.readline()
    #     print(food)
    # else:
    #     food = request.form['food']
    #     f = open('break.txt','w', encoding='utf-8')
    #     f.write(str(food))
    # f.close()
    # cur.execute("select * from foodeatens where user_id = \"3\";")
    # todayEatenList = cur.fetchall()
    # print("##############")
    # print(todayEatenList)
    # print("##############")
    # cur.execute("select * from foodeatens where user_id = \"3\" and DATE_FORMAT(eaten_start, \"%Y-%m-%d\") = '2020-05-16'")
    # todayEatenList = cur.fetchall()
    # print("##############")
    # print(todayEatenList)
    # print("##############")
    menuInfo = [" " for i in range(10)]
    menuInfo[4] = 0
    menuInfo[5] = 0
    menuInfo[6] = 0
    # for i in todayEatenList:
    #     cur.execute("select * from nutrients where nutrient_id = \""+ i[8] +"\";")
    #     eatList = cur.fetchall()
    #     menuInfo[4] += float(eatList[0][2])
    #     menuInfo[5] += float(eatList[0][3])
    #     menuInfo[6] += float(eatList[0][4])
    # print(menuInfo)
    # print("##############")
    # eatFoods = []
    # todayEatenList = [1, 2]
    todayEatenList = [['','','','','','','제육덮밥'], ['','','','','','','콩나물국밥']]
    # eatFoods = ['제육덮밥', '콩나물국밥']
    for i in todayEatenList:
        
        # cur.execute("select food_name from foods where food_id =" + str(i[6]) + ";")
        # food = cur.fetchall()[0][0]
        # eatFoods.append(food)
        eatFoods = ['제육덮밥', '콩나물국밥']
        food = i[6]
        url= "https://www.fatsecret.kr/칼로리-영양소/일반명/" + str(food)
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        infos = [ i.text for i in soup.select('div.nutrition_facts div')]
        # menuInfo = [" " for i in range(10)]
        for i in range(len(infos)):
            if (infos[i] == "열량"):
                menuInfo[3] += (infos[i + 4][:-4])
                kcal = infos[i + 4][:-4]
            elif(infos[i] == "탄수화물"):
                menuInfo[4] += float(infos[i + 1][:-1])
                carbon = infos[i + 1][:-1]
            elif(infos[i] == "단백질"):
                menuInfo[5] += float(infos[i + 1][:-1])
                protein = infos[i + 1][:-1]
            elif(infos[i] == "지방"):
                menuInfo[6] += float(infos[i + 1][:-1])
                fat = infos[i + 1][:-1]
            elif(infos[i] == "나트륨"):
                menuInfo[7] += (infos[i + 1][:-2])
                na = infos[i + 1][:-2]
            elif(infos[i] == "칼륨"):
                menuInfo[8] += (infos[i + 1][:-2])
                cal = infos[i + 1][:-2]
            elif(infos[i] == "식이섬유"):
                menuInfo[9] += (infos[i + 1][:-1])
                sik = infos[i + 1][:-1]
            
    if not menuInfo:
        os.remove('./break.txt')
        return menuInfo
    else:
        cur.execute('select * from foods join nutrients on foods.food_id = nutrients.food_id;')
        menuList = cur.fetchall()
        goodTan = [330 - menuInfo[4], 400  - menuInfo[4]]
        goodDan = [42 - menuInfo[5], 120 - menuInfo[5]]
        goodJi = [40 - menuInfo[6], 80  - menuInfo[6]]
        # 330 : 42 : 40 ~ 400 : 120 : 80
        # 412 600

        foodList = []
        resList = {}
        for i in menuList:
            resList[i[1]] = i[3]

        #
        if len(todayEatenList) == 1:
            food = eatFoods[0]
            for i in range(0, len(menuList)):
                for j in range(i ,len(menuList)):
                    if goodTan[0] <= float(menuList[i][6]) + float(menuList[j][6]) <= goodTan[1] :
                        if goodDan[0] <= float(menuList[i][7]) + float(menuList[j][7]) <= goodDan[1] :
                            if goodJi[0] <= float(menuList[i][8]) + float(menuList[j][8]) <= goodJi[1] :
                                if not food == menuList[i][1] and not food == menuList[j][1] and not menuList[i][1] == menuList[j][1]:
                                    # foodList.append(tuple([menuList[i][1], menuList[j][1]]))
                                    foodList.append(tuple([menuList[i][1]]))
                                    foodList.append(tuple([menuList[j][1]]))
        elif len(todayEatenList) == 2:
            # food = eatFoods[0]
            # food2 = eatFoods[1]
            # print(food)
            # print(food2)
            # for i in range(0, len(menuList)):
            #     if goodTan[0] <= float(menuList[i][6]) <= goodTan[1] :
            #         if goodDan[0] <= float(menuList[i][7]) <= goodDan[1] :
            #             if goodJi[0] <= float(menuList[i][8]) <= goodJi[1] :
            #                 if not food == menuList[i][1] and not food2 == menuList[i][1]:
            #                     # foodList.append(tuple([menuList[i][1], menuList[j][1]]))
            #                     foodList.append(tuple([menuList[i][1]]))
            for i in range(0, len(menuList)):
                for j in range(i ,len(menuList)):
                    tan = float(menuList[i][6]) + float(menuList[j][6]) 
                    dan = float(menuList[i][7]) + float(menuList[j][7])
                    ji = float(menuList[i][8]) + float(menuList[j][8])
                    alcal = tan + dan + ji
                    if 400 / 600 <= tan / alcal <= 330 / 412:
                        if 42 / 412 <= dan / alcal <= 120 / 600:
                            if 40 / 412 <= ji / alcal <= 80 / 600:
                    # if goodTan[0] <= float(menuList[i][6]) + float(menuList[j][6]) <= goodTan[1] :
                    #     if goodDan[0] <= float(menuList[i][7]) + float(menuList[j][7]) <= goodDan[1] :
                    #         if goodJi[0] <= float(menuList[i][8]) + float(menuList[j][8]) <= goodJi[1] :
                    #             if not food == menuList[i][1] and not food == menuList[j][1] and not menuList[i][1] == menuList[j][1]:
                                    # foodList.append(tuple([menuList[i][1], menuList[j][1]]))
                                    foodList.append(tuple([menuList[i][1]]))
                                    foodList.append(tuple([menuList[j][1]]))
        #
        print(foodList)
        foodList = list(set(foodList))
        resultList = []
        for i in foodList:
            # img_path = os.path.abspath('/images2/' + str(resList[i[0]]) + '/' + str(i[0]) + '/' + '0.png')
            img_path = '/static/' + '/images2/' + str(resList[i[0]]) + '/' + str(i[0]) + '/' + '0.png'
            resultList.append({'id': resList[i[0]], 'recommend_name' : i[0],
                            'image' : img_path})
        result = {"recommend" : resultList }

        return jsonify(result)

@app.route('/recommendFood/<key_value>', methods=['GET'])
def recommendFoodUser(key_value):
    if not session.get(str(key_value), 'not found') == 'not found':
        usersEaten_select_query = select_str('foodeatens',
            ['*'],
            {'user_id': key_value})[:-1]
        usersEaten_select_query += "and DATE_FORMAT(eaten_start, \"%Y-%m-%d\") = CURDATE()"
        print(usersEaten_select_query)

        cur.execute(usersEaten_select_query)
        eatenList = cur.fetchall()
        todayEatNum = len(eatenList)
        print(eatenList)
        print(todayEatNum)

        cur.execute('select nutrient_carbohydrate, nutrient_protein, nutrient_fat, nutrients.food_id, food_name  from foods join nutrients  on foods.food_id = nutrients.food_id')

        foodList = cur.fetchall()

        cur.execute('select food_id  from nutrients')
        allNutrientIdList = [i[0] for i in cur.fetchall()]

        # print(allNutrientIdList)
        # asfweaawawawefafe
        allNutrientList = combinations(allNutrientIdList,3 - todayEatNum)
        # print(list(allNutrientList))
        # asdwfaefweawf
        # ((67,), (46,), (1,)),
        # (67,), (46,), (1,)
        user_select_query = select_str('users',
                                ['user_height'],
                                {'user_id': key_value})
        print(user_select_query)
        cur.execute(user_select_query)

        userInfo = cur.fetchall()[0]
        rightCal = (userInfo[0] - 100) * 0.9 * 32
        # rightCal = (170 - 100) * 0.9 * 25
        print(userInfo)
        print(rightCal)
        # 단백질 7~20% 4

        # 탄수화물 55~65% 4

        # 지방 15~30% 9 
        goodTan = [rightCal/4 * 0.07, rightCal/4 * 0.2]
        goodDan = [rightCal/4 * 0.55, rightCal/4 * 0.65]
        goodJi = [rightCal/9 * 0.15, rightCal/9 * 0.3]
        # goodTan = [330 , 400]
        # goodDan = [42 , 120]
        # goodJi = [40 , 80]
        print(goodTan)
        print(goodDan)
        print(goodJi)
        
        sumAllNutrientList = []
        RightMealList = []
        FailMealList = []
        for i in list(allNutrientList):
            tan = 0
            dan = 0
            ji = 0
            foodIdList = []
            foodNameList = []
            for j in range(3 - todayEatNum):
                for k in foodList:
                    if k[3] == i[j]:
                        tan += k[0]
                        dan += k[1]
                        ji += k[2]
                        foodNameList.append(k[4])
            foodIdList.append(i)
            eatSmallcheckTan = tan - goodTan[0]
            eatBigcheckTan = tan - goodTan[1]
            eatSmallcheckDan = dan - goodDan[0]
            eatBigcheckDan = dan - goodDan[1] 
            eatSmallcheckJi = ji - goodJi[0]
            eatBigcheckJi = ji - goodJi[1]
            failTanScore = 0
            failDanScore = 0
            failJiScore = 0
            if eatSmallcheckTan > 0 and eatBigcheckTan < 0:
                if eatSmallcheckDan > 0 and eatBigcheckDan < 0:
                    if eatSmallcheckJi > 0 and eatBigcheckJi < 0:
                        RightMealList.append(foodIdList)
                        RightMealList.append(foodNameList)
                        continue
            if eatSmallcheckTan < 0 :
                failTanScore = eatSmallcheckTan
            elif eatBigcheckTan > 0:
                failTanScore = eatBigcheckTan
            else:
                failTanScore = 0 
            
            if eatSmallcheckDan < 0 :
                failDanScore = eatSmallcheckDan
            elif eatBigcheckDan > 0:
                failDanScore = eatBigcheckDan
            else:
                failDanScore = 0 
            
            if eatSmallcheckJi < 0 :
                failJiScore = eatSmallcheckJi
            elif eatBigcheckJi > 0:
                failJiScore = eatBigcheckJi
            else:
                failJiScore = 0 
            FailScore = failTanScore * 4 + failDanScore * 4 + failJiScore * 9
            FailAbsScore = abs((failTanScore * failTanScore * 4 * 4 + failDanScore * failDanScore * 4 * 4 + failJiScore * failJiScore * 9 * 9) / (16 * 16 * 81))
            FailMealList.append((failTanScore, failDanScore, failJiScore, foodIdList, foodNameList, FailScore, FailAbsScore))
        print(RightMealList)
        # print(FailMealList) 

        FailMealList = sorted(FailMealList, key = lambda FailMealListItem : FailMealListItem[6])
        # print(FailMealList)
        
        returnMealList = []
        smallFailList = []
        for i in range((todayEatNum + 1) * 10):
            smallFailList.append(FailMealList[i])
        for i in RightMealList:
            todayMeals = []
            for j in range(3 - todayEatNum):
                img_path = '/static/images2/' + str(i[0][j]) + '/' + str(i[1][j]) + '/' + '0.png'
                todayMeals.append({'id': i[0][j], 'foodName' : i[1][j], 'image': img_path})
            returnMealList.append({'dayMeal' : todayMeals})

        # print(smallFailList)
        for i in smallFailList:
            todayMeals = []
            for j in range(3 - todayEatNum):
                img_path = 'images2/' + str(i[3][0][j]) + '/' + str(i[4][j]) + '/' + '0.png'
                todayMeals.append({'id': i[3][0][j], 'foodName' : i[4][j], 'image': img_path})
            returnMealList.append(todayMeals)
       
        result = {"recommendMeals" : returnMealList }

        return jsonify(result)
    else:
        return 'fail'

@app.route('/store/<store_id>', methods=['GET'])
def getStore(store_id):
    storeId = store_id
    cur.execute('select * from stores where store_id = '+ str(storeId))
    storeInfo = cur.fetchall()
    # print(storeInfo)
    cur.execute('select food_name from foods where store_id = '+ str(storeId))
    menuInfo = [ i[0] for i in cur.fetchall() ]
    resultList = []
    gps_l = str(storeInfo[0][2]).split(',')[0]
    gps_r = str(storeInfo[0][2]).split(',')[1]
    resultList.append({'recommend_address' : storeInfo[0][3], 'store_name': storeInfo[0][1],
            'recommend_menu': menuInfo, 'gps_l': gps_l, 'gps_r': gps_r})
    result = {"recommend" : resultList }
    # print(result)

    return jsonify(result)


@app.route('/recipe', methods=['POST'])
def getRecipe():
    # if os.path.isfile('./break.txt'):
    #     f = open('break.txt', encoding='utf-8')
    #     food = f.readline()
    # else:
    #     food = request.form['food']
    #     f = open('break.txt','w', encoding='utf-8')
    #     f.write(str(food))
    # f.close()
    # food = request.form['food']
    # url= "https://www.fatsecret.kr/칼로리-영양소/일반명/" + str(food)
    # html = requests.get(url).text
    # soup = BeautifulSoup(html, 'html.parser')
    # infos = [ i.text for i in soup.select('div.nutrition_facts div')]
    # menuInfo = [" " for i in range(10)]
    # for i in range(len(infos)):
    #     if (infos[i] == "열량"):
    #         menuInfo[3] = (infos[i + 4][:-4])
    #         kcal = infos[i + 4][:-4]
    #     elif(infos[i] == "탄수화물"):
    #         menuInfo[4] = float(infos[i + 1][:-1])
    #         carbon = infos[i + 1][:-1]
    #     elif(infos[i] == "단백질"):
    #         menuInfo[5] = float(infos[i + 1][:-1])
    #         protein = infos[i + 1][:-1]
    #     elif(infos[i] == "지방"):
    #         menuInfo[6] = float(infos[i + 1][:-1])
    #         fat = infos[i + 1][:-1]
    #     elif(infos[i] == "나트륨"):
    #         menuInfo[7] = (infos[i + 1][:-2])
    #         na = infos[i + 1][:-2]
    #     elif(infos[i] == "칼륨"):
    #         menuInfo[8] = (infos[i + 1][:-2])
    #         cal = infos[i + 1][:-2]
    #     elif(infos[i] == "식이섬유"):
    #         menuInfo[9] = (infos[i + 1][:-1])
    #         sik = infos[i + 1][:-1]

    # cur.execute("select * from foodeatens where user_id = \"3\" and DATE_FORMAT(eaten_start, \"%Y-%m-%d\") = CURDATE();")
    # # cur.execute("select * from foodeatens where user_id = \"3\" and DATE_FORMAT(eaten_start, \"%Y-%m-%d\") = '2020-05-16'")
    # todayEatenList = cur.fetchall()
    menuInfo = [" " for i in range(10)]
    menuInfo[4] = 0
    menuInfo[5] = 0
    menuInfo[6] = 0
    # print("##############")
    # print(todayEatenList)
    # print("##############")
    todayEatenList = [['','','','','','','제육덮밥'], ['','','','','','','콩나물국밥']]

    # eatFoods = ['제육덮밥', '콩나물국밥']
    eatFoods = []
    for i in todayEatenList:
        # cur.execute("select food_name from foods where food_id =" + str(i[6]) + ";")
        # food = cur.fetchall()[0][0]
        # eatFoods.append(food)
        eatFoods = ['제육덮밥', '콩나물국밥']
        food = i[6]
        url= "https://www.fatsecret.kr/칼로리-영양소/일반명/" + str(food)
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        infos = [ i.text for i in soup.select('div.nutrition_facts div')]
        # menuInfo = [" " for i in range(10)]
        for i in range(len(infos)):
            if (infos[i] == "열량"):
                menuInfo[3] += (infos[i + 4][:-4])
                kcal = infos[i + 4][:-4]
            elif(infos[i] == "탄수화물"):
                menuInfo[4] += float(infos[i + 1][:-1])
                carbon = infos[i + 1][:-1]
            elif(infos[i] == "단백질"):
                menuInfo[5] += float(infos[i + 1][:-1])
                protein = infos[i + 1][:-1]
            elif(infos[i] == "지방"):
                menuInfo[6] += float(infos[i + 1][:-1])
                fat = infos[i + 1][:-1]
            elif(infos[i] == "나트륨"):
                menuInfo[7] += (infos[i + 1][:-2])
                na = infos[i + 1][:-2]
            elif(infos[i] == "칼륨"):
                menuInfo[8] += (infos[i + 1][:-2])
                cal = infos[i + 1][:-2]
            elif(infos[i] == "식이섬유"):
                menuInfo[9] += (infos[i + 1][:-1])
                sik = infos[i + 1][:-1]

    # for i in todayEatenList:
    #     cur.execute("select * from nutrients where nutrient_id = \""+ i[8] +"\";")
    #     eatList = cur.fetchall()
    #     menuInfo[4] += float(eatList[0][2])
    #     menuInfo[5] += float(eatList[0][3])
    #     menuInfo[6] += float(eatList[0][4])
    # print(menuInfo)
    # print("##############")

    if not menuInfo:
        return menuInfo
    else:
        fw = open('recipe.csv', 'r')
        recipeRdr = csv.reader(fw)

        recipeList = [ line for line in recipeRdr ]

        goodTan = [330 - menuInfo[4], 400  - menuInfo[4]]
        goodDan = [42 - menuInfo[5], 120 - menuInfo[5]]
        goodJi = [40 - menuInfo[6], 80  - menuInfo[6]]

        foodList = []
        foodList1 = []
        foodList2 = []

        if len(todayEatenList) == 1:
            food = todayEatenList[0][6]
            for i in range(1, len(recipeList)):
                for j in range(i ,len(recipeList)):
                    if goodTan[0] <= float(recipeList[i][6]) + float(recipeList[j][6]) <= goodTan[1] :
                        if goodDan[0] <= float(recipeList[i][7]) + float(recipeList[j][7]) <= goodDan[1] :
                            if goodJi[0] <= float(recipeList[i][8]) + float(recipeList[j][8]) <= goodJi[1] :
                                if not food == recipeList[i][1] and not food == recipeList[j][1] and not recipeList[i][1] == recipeList[j][1]:
                                    foodList.append(tuple([recipeList[i][0]]))
                                    foodList.append(tuple([recipeList[j][0]]))
        elif len(todayEatenList) == 2:
            # food = todayEatenList[0][6]
            # food2 = todayEatenList[1][6]
            # for i in range(1, len(recipeList)):
            #         if goodTan[0] <= float(recipeList[i][6]) <= goodTan[1] :
            #             if goodDan[0] <= float(recipeList[i][7]) <= goodDan[1] :
            #                 if goodJi[0] <= float(recipeList[i][8]) <= goodJi[1] :
            #                     if not food == recipeList[i][1] and not food2 == recipeList[i][1]:
            #                         foodList.append(tuple([recipeList[i][0]]))
            food = todayEatenList[0][6]
            food2 = todayEatenList[1][6]
            for i in range(1, len(recipeList)):
                for j in range(i ,len(recipeList)):
                    if goodTan[0] <= float(recipeList[i][6]) + float(recipeList[j][6]) <= goodTan[1] :
                        if goodDan[0] <= float(recipeList[i][7]) + float(recipeList[j][7]) <= goodDan[1] :
                            if goodJi[0] <= float(recipeList[i][8]) + float(recipeList[j][8]) <= goodJi[1] :
                                if not food == recipeList[i][1] and not food == recipeList[j][1] and not recipeList[i][1] == recipeList[j][1]:
                                    foodList.append(tuple([recipeList[i][0]]))
                                    foodList.append(tuple([recipeList[j][0]]))

        # foodList = list(set(foodList))

        resList = {}
        recipes = {}
        for i in recipeList:
            recipe = []
            for j in range(14, len(i)):
                if str(i[j]).find('http') == -1:
                    recipe.append(i[j])
            recipes[i[0]] = recipe
            resList[i[0]] = [i[1],i[6],i[7],i[8],i[12], i[4], i[5], i[9], i[13] ]

        resultList = []
        index  = 0
        recipeIdList = []
        randomId = random.randrange(1, len(foodList), 2)
        for i in range(100):
            while randomId in recipeIdList:
                randomId = random.randrange(1, len(foodList), 2)
            recipeIdList.append(randomId)
        test = []
        for i in recipeIdList:
            recipeids = [i -1 , i]
            for i in recipeids:
                test.append({'foot_id': foodList[i][0], 'foot_name' : resList[foodList[i][0]][0]})
                resultList.append({'foot_id': foodList[i][0], 'foot_name' : resList[foodList[i][0]][0], 'foot_img' : resList[foodList[i][0]][4],
                    'foot_weight': resList[foodList[i][0]][5], 'foot_calorimetry':  resList[foodList[i][0]][6], 'foot_Carbohydrate' : resList[foodList[i][0]][1],
                    'foot_protein' : resList[foodList[i][0]][2], 'foot_local': resList[foodList[i][0]][3], 'foot_natrium': resList[foodList[i][0]][7],
                    'material' : resList[foodList[i][0]][8], 'foot_recipe': recipes[foodList[i][0]]}, )

        # for i in foodList:
        #     resultList.append({'foot_id': i[0], 'foot_name' : resList[i[0]][0], 'foot_img' : resList[i[0]][4],
        #     'foot_weight': resList[i[0]][5], 'foot_calorimetry':  resList[i[0]][6], 'foot_Carbohydrate' : resList[i[0]][1],
        #      'foot_protein' : resList[i[0]][2], 'foot_local': resList[i[0]][3], 'foot_natrium': resList[i[0]][7],
        #        'material' : resList[i[0]][8], 'foot_recipe': recipes[i[0]]}, )
        result = {"footrecommend" : resultList }
        # print(result)
        print(test)

        return jsonify(result)


@app.route('/recipe/<recipe_id>', methods=['GET'])
def getRecipe2(recipe_id):
    fw = open('recipe.csv', 'r')
    recipeRdr = csv.reader(fw)

    recipeList = [ line for line in recipeRdr ]
    
    resList = {}
    recipes = {}
    for i in recipeList:
        recipe = []
        for j in range(14, len(i)):
            if str(i[j]).find('http') == -1:
                recipe.append(i[j])
        recipes[i[0]] = recipe
        resList[i[0]] = [i[1],i[6],i[7],i[8],i[12], i[4], i[5], i[9], i[13] ]

    resultList = []

    resultList.append({'foot_id': recipe_id, 'foot_name' : resList[recipe_id][0], 'foot_img' : resList[recipe_id][4],
    'foot_weight': resList[recipe_id][5], 'foot_calorimetry':  resList[recipe_id][6], 'foot_Carbohydrate' : resList[recipe_id][1],
        'foot_protein' : resList[recipe_id][2], 'foot_local': resList[recipe_id][3], 'foot_natrium': resList[recipe_id][7],
        'material' : resList[recipe_id][8], 'foot_recipe': recipes[recipe_id]}, )

    result = {"footrecommend" : resultList }
    # print(result)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
