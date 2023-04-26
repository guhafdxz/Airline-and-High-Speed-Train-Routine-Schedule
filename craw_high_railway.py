# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 21:28:54 2022

@author: fdulu
"""
import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote
from avi_railway_schedule import city


headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}

search_url='https://trains.ctrip.com/webapp/train/list/?dstation={}&astation={}&dDate=2022-11-17&rDate=&hubCityName=&ticketType=0'

depart_arri=[]
for i in range(len(city)):
    depart_arri+=list(zip([city[i]]*len(city),city))[1:]

railway_info={}
i=19263
for city_pair in depart_arri[19263:]:
   time.sleep(1)
   print(i)
   railway_info[city_pair]={'departure_time':None,'departure_station':None,'travel_time':None,'train_num':None,'arrival_time':None,'arrival_station':None}
   resp=requests.get(search_url.format(quote(city_pair[0]),quote(city_pair[1])),headers=headers)
   soup=BeautifulSoup(resp.text,'html')
   departure_time=[]
   departure_station=[]
   travel_time=[]
   train_num=[]
   arrival_time=[]
   arrival_station=[]
   for element in soup.find_all(class_='card-white list-item'):
        try:
            departure_time.append(element.find(class_='from').find(class_='time').text)
            departure_station.append(element.find(class_='from').find(class_='station').text)
            travel_time.append(element.find(class_='mid').find(class_='haoshi').text)
            train_num.append(element.find(class_='mid').find(class_='checi').text)
            arrival_time.append(element.find(class_='to').find(class_='time').text)
            arrival_station.append(element.find(class_='to').find(class_='station').text)
        except Exception as e:
            print(e)
        if (len(departure_time)>len(arrival_time)):
            departure_time=departure_time[:len(arrival_time)]
            departure_station= departure_station[:len(arrival_time)]
   railway_info[city_pair]['departure_time']=departure_time
   railway_info[city_pair]['departure_station']=departure_station
   railway_info[city_pair]['travel_time']=travel_time
   railway_info[city_pair]['train_num']=train_num
   railway_info[city_pair]['arrival_time']=arrival_time
   railway_info[city_pair]['arrival_station']=arrival_station
   i+=1
   if len( railway_info[city_pair]['departure_time'])!=0:
       print('total{} num of train'.format( railway_info[city_pair]['train_num']))
       print("a train from{} to{} departure at {},arrive at{}".format(city_pair[0],city_pair[1],railway_info[city_pair]['departure_time'][-1], railway_info[city_pair]['arrival_time'][-1]))
   if i%60==0:
       time.sleep(5)

railway_info_df2=pd.DataFrame(railway_info).T
railway_info_df2.to_excel('crawl_train_info2.xlsx')