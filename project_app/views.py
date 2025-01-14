from django.shortcuts import render
import pandas as pd
import numpy as np
import csv
import sys
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.request as req
from urllib import parse

# Create your views here.
items=['간장', '계란', '고추장', '과자', '기저귀', '껌', '냉동만두', '된장', '두루마리화장지', '두부', '라면', '마요네즈', '맛김', '맛살', '맥주', '밀가루', '분유', '사이다', '생리대', '생수', '샴푸', '설탕', '세탁세제', '소주', '시리얼', '식용유', '쌈장', '아이스크림', '어묵', '오렌지주스', '우유', '즉석밥', '참기름', '참치 캔', '커피', '케첩', '콜라', '햄']
names = ['지역','마켓종류','마트이름','분류','품목','가격']

dir = os.path.dirname(os.path.realpath(__file__))

ldata = dir + '\static\csvs\local_mart.csv'
gdata = dir + '\static\csvs\gmarket.csv'

local = pd.read_csv(ldata, header = None,names = names)
gmarket = pd.read_csv(gdata, header = None,names=['품목','가격'])

df = pd.DataFrame(local)
df_g = pd.DataFrame(gmarket)

def mainFunc(request):
    item=items
    return render(request,'main.html', {'item':item})

def findFunc(request):
    if request.method =='GET':
        print('GET 요청 처리')
        
        irum = request.GET.get("searchInput")
        print(irum)
        dfl = df[df['분류'].str.contains(irum) & df['지역'].str.contains("종로구")].values.tolist()
        dfl.sort(key=lambda x : x[5])
        return render(request,'finder.html',{'dfl':dfl, 'irum':irum})
    else:
        print('error')


def insertFunc(request):
    if request.method =='GET':
        print('GET 요청 처리')
        return render(request,'insert.html') #forward 방식 <jsp:
        # return HttpResponseRedirect('insert.html') # redirect 방식
    elif request.method =='POST':
        print('POST 요청 처리')
        
        irum = request.POST.get('name')
        dfl = df[df['품목'].str.contains(irum) & df['지역'].str.contains("종로구 내수동")& df['마트이름'].str.contains("지씨마트")].values.tolist()
        dfl.sort(key=lambda x : x[5])
        print(dfl)
        return render(request,'finder.html',{'dfl':dfl})
        
    else:
        print('error')

def basketFunc(request):
    print('request GET : ', request.GET)
    name = request.GET.get("name")
    price = request.GET.get("price")
    print(price)
    print(name)
    product = {"name" : name, "price" : price}
    productList = []
    gmarketList = [] # 지마켓 최저가 장바구니
    fastList = [] # 당일 배송 장바구니
    
    g_df = craw_gmarket(name)
    g_product = {"name" : g_df[0],"price":g_df[1]}
    
    f_df = craw_fast(name)
    f_product = {"name" : f_df[0],"price":f_df[1]}
    
    if "prod" in request.session: #session이 생성되어있지 않으면, 즉 첫 번째 상품이 아니라면 productList에 상품 정보 저장하기
        productList = request.session["prod"]
        gmarketList = request.session["g_prod"]
        fastList = request.session["f_prod"]
        
        productList.append(product)
        gmarketList.append(g_product)
        fastList.append(f_product)
        request.session["prod"] = productList
        request.session["g_prod"] = gmarketList
        request.session["f_prod"] = fastList
        
        
        print("세션 유효 시간 : ", request.session.get_expiry_age())
    else: #session에 shop이 없으면 productList에 상품을 넣고 request.session에 "shop" 이라는 키를 만든다
        productList.append(product)
        request.session["prod"] = productList
        gmarketList.append(g_product)
        request.session["g_prod"] = gmarketList
        fastList.append(f_product)
        request.session["f_prod"] = fastList
            
    # return HttpResponseRedirect("basket")
    print(productList)
    context = {} #html에 보낼 용도
    context['products'] = request.session['prod']
    context['g_products'] = request.session['g_prod']
    context['f_products'] = request.session['f_prod']
    
    request.session.set_expiry(30) #세션 시간 결정
    

    # return render(request, 'basket.html', {'context' : context})
    return render(request, 'basket.html', context)
 
    
def craw_gmarket(item):
    
    item = parse.quote(item)
    url = "https://browse.gmarket.co.kr/search?keyword="
    # url = url+item+"&t=s"
    url = url+item
  
    html = urlopen(url)
    
    soup = BeautifulSoup(html,'html.parser')
    
    gm_names = []
    gm_prices = []
    gmarket = []
    
    names = soup.select('span.text__item')
    prices = soup.select('strong.text.text__value')
    
    for name in names:
        gm_names.append(name.text.strip())
    
    for price in prices:
        gm_prices.append(price.text.strip())
    
    g_df = pd.DataFrame({'제품명':gm_names,'가격':gm_prices})
    
    g_df = g_df.sort_values('가격')
    return g_df.iloc[0]


def craw_fast(item):
    
    item = parse.quote(item)
    url = "https://browse.gmarket.co.kr/search?keyword="
    url = url+item+"&t=e&tf=e:128935607"
  
    html = urlopen(url)
    
    soup = BeautifulSoup(html,'html.parser')
    
    gm_names = []
    gm_prices = []
    gmarket = []
    
    names = soup.select('span.text__item')
    prices = soup.select('strong.text.text__value')
    
    for name in names:
        gm_names.append(name.text.strip())
    
    for price in prices:
        gm_prices.append(price.text.strip())
    
    g_df = pd.DataFrame({'제품명':gm_names,'가격':gm_prices})
    
    g_df = g_df.sort_values('가격')
    return g_df.iloc[0]