#!/usr/bin/env python
# coding: utf-8

# In[7]:


import requests as rq
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xlwings as xw
#import plotly.graph_objects
#import plotly.subplots`
import datetime
import plotly.graph_objects
import plotly.subplots



t1= datetime.datetime(2021, 12, 21) #固定日期,日期不可改變
t2= datetime.datetime(2022, 4, 15) #可更動日期,日期不可小於t1
epoch = datetime.datetime.utcfromtimestamp(0)



def t1970(t):
    return str(round((t - epoch).total_seconds()))


# 網址
#site = "https://query1.finance.yahoo.com/v8/finance/chart/2330.TW?period1="+t1970(t1)+"&period2="+t1970(t2)+"&interval=1mo&events=history&=hP2rOschxO0"
#site = "https://query1.finance.yahoo.com/v8/finance/chart/2330.TW?period1="+t1970(t1)+"&period2="+t1970(t2)+"&interval=1d&events=history&crumb=hP2rOschxO0"
site = "https://query1.finance.yahoo.com/v8/finance/chart/2330.TW?period1="+t1970(t1)+"&period2="+t1970(t2)+"&interval=1d&events=history"


# 利用 requests 來跟遠端 server 索取資料
#response = requests.get(site)

headers = {
    'User-Agent': 'Mozilla/5.0'
}

r = rq.get(url=site, headers = headers)
data = json.loads(r.text)

#print(data)

#df = pd.DataFrame(data['chart']['result'][0]['indicators']['quote'][0], index=pd.to_datetime(np.array(data['chart']['result'][0]['timestamp'])*1000*1000*1000))


dataDates = np.array(data['chart']['result'][0]['timestamp'], dtype='datetime64[s]')
df = pd.DataFrame(data['chart']['result'][0]['indicators']['quote'][0], index=dataDates)


df=df.sort_index() #依照日期重新排列
# df.tail(10)
TXF_1DAYK = df

# 計算 9 日內最高成交價
TXF_1DAYK['9DAYMAX'] = TXF_1DAYK['high'].rolling(9).max()

# 計算 9 日內最低成交價
TXF_1DAYK['9DAYMIN'] = TXF_1DAYK['low'].rolling(9).min()

# 計算每日 RSV 值
TXF_1DAYK['RSV'] = 0
TXF_1DAYK['RSV'] = 100 * (TXF_1DAYK['close'] - TXF_1DAYK['9DAYMIN']) / (TXF_1DAYK['9DAYMAX'] - TXF_1DAYK['9DAYMIN'])
 #RSV = ( 今日收盤價 - 最近九天的最低價 ) / ( 最近九天的最高價 - 最近九天最低價 )

TXF_1DAYK=TXF_1DAYK[8:]
    




# print(TXF_1DAYK)

# 計算 K 值
K = 78.19
def KValue(rsv):
    global K
    #print("K="+str(K))
    K = (2/3) * K + (1/3) * rsv
    return K


TXF_1DAYK['K']= TXF_1DAYK['RSV'].apply(KValue)
print(TXF_1DAYK['K'])

# 計算 D 值
D = 67.89
def DValue(k):
    global D
    #print("D="+str(D))
    D = (2/3) * D + (1/3) * k
    return D
TXF_1DAYK['D'] = 0
TXF_1DAYK['D'] = TXF_1DAYK['K'].apply(DValue)
print(TXF_1DAYK['D'])

   #繪製圖形
figure = plotly.graph_objects.Figure(
    data=[
        # K
        plotly.graph_objects.Scatter(
            x=TXF_1DAYK.loc[TXF_1DAYK['K'] != 0].index,
            y=TXF_1DAYK['K'],
            name='K',
            mode='lines',
            line=plotly.graph_objects.scatter.Line(
                color='Blue'
            )
        ), 
        # D
        plotly.graph_objects.Scatter(
            x=TXF_1DAYK.loc[TXF_1DAYK['D'] != 0].index,
            y=TXF_1DAYK['D'],
            name='D',
            mode='lines',
            line=plotly.graph_objects.scatter.Line(
                color='Orange'
            )
        ),
        #高檔鈍化
        plotly.graph_objects.Scatter(
            mode='lines',
            name='高檔鈍化',
            x=[TXF_1DAYK.index[0],TXF_1DAYK.index[-1]],
            y=[80,80],
            line=plotly.graph_objects.scatter.Line(
               color='Green',dash='dash'
           )
        ),
        #低檔鈍化
         plotly.graph_objects.Scatter(
            mode='lines',
            name='低檔鈍化',
            x=[TXF_1DAYK.index[0],TXF_1DAYK.index[-1]],
            y=[20,20],
            line=plotly.graph_objects.scatter.Line(
               color='Gray',dash='dash'
           )
        ),
        ],
    # 設定 XY 顯示格式
    layout=plotly.graph_objects.Layout(
        xaxis=plotly.graph_objects.layout.XAxis(
            tickformat='%Y-%m-%d'
        ),
        yaxis=plotly.graph_objects.layout.YAxis(
            tickformat='.2f'
        )
    )
)

figure.show()



# In[ ]:




