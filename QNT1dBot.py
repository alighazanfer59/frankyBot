#!/usr/bin/env python
# coding: utf-8

# ## BTC 1m test cronjob

# In[1]:


import datetime as dt
import time
# import my_functions
# import importlib
# importlib.reload(my_functions)
from main_functions import *


# In[2]:


pd.set_option('display.max_rows', 200) 


# In[3]:


# Define the time periods for the moving averages and the Bollinger Bands
length1 = 1
length2 = 34
bbPeriod = 33
bbStdDev = 2

# Define RSI configuration
rsiLength = 19
dailyRSI = 50

# Define stop loss in percentage
stop_loss = 3.5

# Define trading parameters
symbol = 'QNT/USDT'
usdt_amount = 175
timeframe = '1d'
rsi_tf = '1d'

tradesfile = "qnt1D_trades.csv"
logfile = "qnt.csv"


# In[4]:


import json

from main_functions import update_dict_value


# Load the JSON data from the file
with open('pos.json', 'r') as f:
    json_pos = f.read()
with open('qty.json', 'r') as f:
    json_qty = f.read()

# Convert the JSON data back to a dictionary
pos = json.loads(json_pos)
qty = json.loads(json_qty)

in_position = pos['qnt1d']

# In[5]:


size = calculate_order_size(symbol, usdt_amount)
qty = qty['qnt1d']


# cronjob code
 
try:
    df = getdata(symbol, timeframe, limit=100,
         length1=length1,
         length2=length2,
         bbPeriod=bbPeriod,
         bbStdDev=bbStdDev,
         rsi_tf=rsi_tf,
         rsiLength=rsiLength,
         dailyRSI=dailyRSI
         )
    print(df.iloc[-1:])
    # Check for buy and sell signals
    signal = df['buy'][-1]
    print(dt.datetime.now())
    if signal == True and not in_position:
        # Place buy order
        buyId = place_buy_order(symbol, size)
        in_position = True
        buyprice = float(buyId['info']['fills'][0]['price'])
        qty = float(buyId['info']['origQty'])
        qty = update_dict_value('qty.json', 'qnt1d', qty)
        buycsv(df, buyprice, tradesfile)
        print(f'Buy order placed for {symbol} at {buyprice}')

    elif df['sell'][-1] == True and in_position:
        # Place sell order
        sellId = place_sell_order(symbol, qty)
        in_position = False
        sellprice = float(sellId['info']['fills'][0]['price'])
        buyprice = read_buyprice(tradesfile)
        profit = ((sellprice - buyprice) / buyprice- 0.002) * 100
        sellcsv(df, buyprice, sellprice, tradesfile)
        print(f'Sell order placed for {symbol} at {sellprice}, Profit: {profit:.2f}%')

    # Check for stop loss
    elif in_position and (df['close'][-1] / read_buyprice(tradesfile) - 1) * 100 < -stop_loss/100:
        # Place sell order
        sellId = place_sell_order(symbol, qty)
        in_position = False
        sellprice = float(sellId['info']['fills'][0]['price'])
        buyprice = read_buyprice("btcTrades")
        profit = ((buyprice - sellprice) / buyprice- 0.002) * 100
        sellcsv(df, buyprice, sellprice, tradesfile)
        print(f'Sell order placed for {symbol} at {sellprice}, Profit: {profit:.2f}%')

# write the last row to the CSV file    
#         with open('btc.csv', 'a', newline='') as f:
#             df.iloc[-1:].to_csv(f, header=f.tell())   

    csvlog(df, logfile)

except Exception as e:
    print(e)

# sec_of_execution = dt.datetime.now().second+(dt.datetime.now().microsecond/1000000)
# time.sleep(60-sec_of_execution+5)

