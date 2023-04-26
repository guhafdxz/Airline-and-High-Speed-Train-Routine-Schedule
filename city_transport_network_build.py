# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 03:57:10 2022

@author: fdulu
"""
# -*- coding: utf-8 -*-
"""
"""
# -*- coding: utf-8 -*-
"""
"""

import networkx as nx
import numpy as np
import pandas as pd
import time
import sys
import folium
import webbrowser 
from folium import plugins
from datetime import datetime,time
from collections import defaultdict


merge_table_sorted=pd.read_excel('Merge_timetable.xlsx')  #导入Airline和Railway合并出行时刻表
#############################################################################################

def time_weight(total_time):  #时间字符串转换为数字
    minutes=int(total_time.split(':')[0])*60+int(total_time.split(':')[1])
    if 'days' in total_time.split(':')[0]:
        minutes=0
    return minutes

def build_node(start_city,end_city,start_time,earlist_transport_route):
    #构建城市节点
    adj_city_df=merge_table_sorted[merge_table_sorted['出发城市']==start_city] #找到出发城市可以到达的所有相邻城市 
    # departure_time_list=merge_table_sorted[merge_table_sorted['出发城市']==start_city]['departure_time'].tolist()
    # dep_time=0
    global search
    index=0
    for i in range(len(adj_city_df)):
          if pd.to_datetime(adj_city_df.iloc[i,3])>=pd.to_datetime(start_time):
                 # dep_time=departure_time_list[i]
                 index=i
                 break       #最早的出发时间
    
    arr_city=adj_city_df.iloc[index:,2].tolist()  #到达下一城市
    arr_time=adj_city_df.iloc[index:,4].tolist()   #到达的下一个
    vid=adj_city_df.iloc[index:,0].tolist()
    vtype=adj_city_df.iloc[index:,6].tolist()
    deptime=adj_city_df.iloc[index:,3].tolist()
    tcost=adj_city_df.iloc[index:,5].tolist()
    
    
    
    for i in range(len(arr_city)):
         route_tuple=(start_city,arr_city[i],time_weight(tcost[i]))
         vehicle=(vid[i],vtype[i])
         dep_time=deptime[i]
         key=(start_city,arr_city[i],dep_time)
         if key not in  earlist_transport_route and pd.to_datetime(dep_time)>=pd.to_datetime(start_time):
             earlist_transport_route[key]={'transport_route':[],'transport_type':[],'arrival_time':[]}
             earlist_transport_route[key]['transport_route'].append(route_tuple)
             earlist_transport_route[key]['transport_type'].append(vehicle)
             earlist_transport_route[key]['arrival_time'].append(arr_time[i])  
    for route in earlist_transport_route.keys():
         if end_city in route:
               print("搜索结束！")
               break
    else:  
        print('继续搜素!')
        for i in range(len(arr_city[index:])):
            next_search_city=arr_city[i]
            next_start_time=arr_time[i]
            if next_search_city not in search:
                search.append(next_search_city)
                build_node(next_search_city,end_city,next_start_time,earlist_transport_route)
    return earlist_transport_route

def build_edge(earlist_transport_route,start_city,end_city,start_time,edge):
                 #start_city:出发城市
                 #end_city:目的地
                 #start_time:出发时间  格式要求（00：00：00）小时/分钟/秒钟
                 # edge:(start_city,end_city,time_cost)表示城市之间的交通线路（边）
                 #visit_cities:可以中转访问城市，即邻居        
   global vehicle_mid,visit_city,arrival,depature
    
   if start_city not in city_nodes or end_city not in city_nodes: #搜索城市不在名单内！
           print("Sorry,There is not a city named what you give,please try again!")
           return 0
 
   for route in earlist_transport_route.keys():
      if route[0]==start_city and  route[1] not in visit_city:
               next_city=route[1]
               df1=merge_table_sorted[merge_table_sorted['出发城市']==start_city]
               df2=df1[df1['到达城市']==next_city]
               index=0
               for i in range(len(df2['departure_time'].tolist())):
                   if pd.to_datetime(df2['departure_time'].tolist()[i])>=pd.to_datetime(start_time):
                       index=i
                       break
               route_tuple=(start_city,next_city,df2['departure_time'].values[index])
               edge.append(earlist_transport_route[route_tuple]['transport_route'][0])
               visit_city.append(route_tuple[1])
               vehicle_mid.append(earlist_transport_route[route_tuple]['transport_type'][0])
               depature.append(route_tuple[2])
               arrival.append(earlist_transport_route[route_tuple]['arrival_time'][0])       
   if end_city in visit_city:
       print("找到目的城市")
       return edge 
   
   else:
       print("无法直达目的城市，寻找中转城市！")
       visit_search=visit_city[1:]
       for i in range(len(visit_search)): 
           next_search_city=visit_search[i]
           start_time=arrival[i]
           build_edge(earlist_transport_route,next_search_city,end_city,start_time,edge)          
   return edge        





#测试 
if __name__=="__main__":
    
    city_nodes=merge_table_sorted['出发城市'].unique()   
    trans_type={0:'high speed train',1:'airplane'}
    earlist_transport_route={}
    # start_city=input("输入出发城市:")
    # end_city=input("输入目的地城市：")
    # start_time=str(input("出发时间(比如08：00：00)："))
    start_city='上海' #出发城市
    end_city='衡阳'     #到达城市
    start_time='9:13:23'   #出发时刻
    edge=[]
    search=[]
    visit_city=[]
    visit_city.append(start_city)
    arrival=[]
    depature=[]
    wait_time=[]
    vehicle_mid=[]
    kill_signal=0
    earlist_transport_route=build_node(start_city,end_city,start_time,earlist_transport_route)
    edge= build_edge(earlist_transport_route,start_city,end_city,start_time,edge)
    
                 
                            #根据城市节点和路径构建交通图并计算距离
if end_city not in visit_city:
        print("Sorry,no appropriate airlines/railway schedules for you!")
else:
        options = {
            'node_color': 'green',
            'node_size':200,
            'width':5,
            'edge_color':'blue',
            'alpha':0.8
            }
        
        edges = pd.DataFrame(
          {
        "source": [tuple_data[0] for tuple_data in edge],
        "target": [tuple_data[1] for tuple_data in edge],
        "weight": [tuple_data[2] for tuple_data in edge],
          }
          )
        G = nx.from_pandas_edgelist(edges, edge_attr=True)  #生成图
        node_mapping={visit_city[i]:i for i in range(len(visit_city))}
        city_map={i:visit_city[i] for i in range(len(visit_city))}
        G=nx.relabel_nodes(G,node_mapping)
        nx.draw(G,**options,with_labels=True)
        predecessor,distance=nx.floyd_warshall_predecessor_and_distance(G, weight='weight')
        path=nx.single_source_dijkstra(G,node_mapping[start_city],node_mapping[end_city])
        print('The possible minimum travel time from {} to {} is {} hours'.format(start_city,end_city,round(path[0]/60,1)))
        wait_mid=[]
        city_visited=[city_map[i]  for i in path[1]]
        visit=visit_city[1:]
        travel_route=[edge[visit.index(city)] for city in   city_visited[1:]]
        travel_vehicle=[vehicle_mid[visit.index(city)] for city in  city_visited[1:]]
        travel_dep=[depature[visit.index(city)] for city in  city_visited[1:]]
        travel_arr=[arrival[visit.index(city)] for city in  city_visited[1:]]
        travel_wait=[pd.to_datetime((travel_dep)[i])-pd.to_datetime(travel_arr[i-1]) for i in range(1,len(travel_arr))]
        for i in range(len(travel_route)):
          try:
            print("Start_City：:{},Arrival City:{},Travel time cost：{} hours".format( travel_route[i][0], travel_route[i][1],round( travel_route[i][2]/60,1)))
            print("Vehicle ID:{}, Transport type:{},departure_time:{}".format(travel_vehicle[i][0],trans_type[travel_vehicle[i][1]], travel_dep[i]))
          except Exception as e:
              print(e)
        for i in range(len(travel_wait)):
             print("transit waiting time from {} to {} is:{}".format(travel_route[i+1][0],travel_route[i+1][1],travel_wait[i]))
####################################################################################################  


#最后将城市映射到可视化的地图上，通过folium内嵌高德地图完成工作

"处理地图GUI-jupytor"
  
location=pd.read_excel('.\location.xlsx')

nav=location['locations'].tolist()
nav=[loc.split('[')[1].split(']')[0] for loc in nav]

nav=[[float(loc.split(',')[1]),float(loc.split(',')[0])] for loc in nav]
lattitude=[loc[0] for loc in nav]
longtitude=[loc[1] for loc in nav]
location['locations']=nav
location['lattitude']=lattitude
location['longitude']=longtitude

mean_lat=np.mean(location['lattitude'])
mean_lon=np.mean(location['longitude'])

connection_city=[city_map[path_code] for path_code in path[1]]
city_location=[]
for city in connection_city:
    city_location+=(location[location['city']==city]['locations'].tolist())
transport={'airline':[],'railway':[]}
transport_geo={'airline':[],'railway':[]}  #航班出行城市和高铁出行城市位置坐标
attr={"font-weight":"","font-size":15}
for i in range(len(travel_vehicle)):
    if travel_vehicle[i][1]==1:
       airline_connect_city=[connection_city[i],connection_city[i+1]]
       airline_connect_geo=location[location['city']==connection_city[i]]['locations'].tolist()[0]
       transport['airline'].append(((airline_connect_city)))
       airline_connect_geo=[location[location['city']==airline_connect_city[i]]['locations'].tolist()[0] for i in range(len(airline_connect_city))]
       transport_geo['airline'].append((airline_connect_geo))  #航空出行城市坐标
    else:
       railway_connect_city=[connection_city[i],connection_city[i+1]]
       transport['railway'].append(railway_connect_city)
       railway_connect_geo=[location[location['city']==railway_connect_city[i]]['locations'].tolist()[0] for i in range(len(railway_connect_city))]
       transport_geo['railway'].append(railway_connect_geo)  #高铁出行城市坐标
    

travel_map = folium.Map(location=[mean_lat, mean_lon],width=600,height=600, zoom_start=15,tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                     attr='AutoNavi', overlay=False,name='baseLayer')
if len(transport_geo['airline'])!=0:
     folium.PolyLine(  # polyline方法为将坐标用实线形式连接起来
          transport_geo['airline'],  # 将航班出行城市坐标点连接起来 
         weight=3,  # 线的大小为4
         color='blue',  # 线颜色为蓝色
         opacity=0.9,  # 线透明度
     ).add_to(travel_map)#加到地图
     plugins.AntPath(transport_geo['airline'],popup=None, color='blue',tooltip='Airline',attributes=attr).add_to(travel_map)
if len(transport_geo['railway'])!=0:
    folium.PolyLine(  # polyline方法为将坐标用虚线形式连接起来
         transport_geo['railway'],  # 将高铁出行坐标点连接起来
         weight=2,  # 线的大小为3
         color='green',  # 线颜色为绿色
         opacity=0.9,  # 线透明度
     ).add_to(travel_map)  # 将这条线添加到刚才地图
    plugins.AntPath(transport_geo['railway'],popup=None,color='green',tooltip='Railway',attributes=attr).add_to(travel_map)


 # 起始点，结束点标记蓝色，其他中转城市标记红色
folium.Marker(city_location[0], radius=3,icon=folium.Icon(color='blue',icon='glass'),tooltip='<b>出发城市 {} 出发：{}</b>'.format(connection_city[0],travel_dep[0])).add_to(travel_map) #起点城市
folium.Marker(city_location[-1],  radius=3,icon=folium.Icon(color='blue',icon='glass'),tooltip='<b>终点城市 {} 抵达：{} 耗时 {} 小时</b>'.format(connection_city[-1],travel_arr[-1],round(path[0]/60,1))).add_to(travel_map) #终点城市
for i in range(1,len(city_location)-1):
      folium.Marker(city_location[i], radius=2,icon=folium.Icon(color='red',icon='glass'),tooltip='<b>{} 抵达：{} 出发：{}</b>'.format(connection_city[i],travel_arr[i-1],travel_dep[i])).add_to(travel_map) #中转城市

travel_map.save('test_travel_map.html')   #保存地图文件
webbrowser.open('.\travel_map.html')  #在线查看地图



















