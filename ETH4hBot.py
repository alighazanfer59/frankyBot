#!/usr/bin/env python
# coding: utf-8

# ## BTC 1m test cronjob

# In[1]:


import datetime as dt
import time
# import main_functions
# import importlib
# importlib.reload(main_functions)
from main_functions import *
time.sleep(5)

# In[3]:


# Define the time periods for the moving averages and the Bollinger Bands
length1 = 1
length2 = 28
bbPeriod = 36
bbStdDev = 1

# Define RSI configuration
rsiLength = 13
dailyRSI = 48

# Define stop loss in percentage
stop_loss = 5.4

# Define trading parameters
symbol = 'ETH/USDT'
usdt_amount = 100
timeframe = '4h'
rsi_tf = '1d'

tradesfile = "eth4H_trades.csv"
logfile = "eth4H.csv"


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

in_position = pos['eth4h']


# In[5]:


size = calculate_order_size(symbol, usdt_amount)
qty = qty['eth4h']

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
        in_position = update_dict_value('pos.json', 'eth4h', True)
        buyprice = float(buyId['info']['fills'][0]['price'])
        qty = float(buyId['info']['origQty'])
        buycsv(df, buyprice, tradesfile)
        print(f'Buy order placed for {symbol} at {buyprice}')

    elif df['sell'][-1] == True and in_position:
        # Place sell order
        sellId = place_sell_order(symbol, qty)
        in_position = update_dict_value('pos.json', 'eth4h', False)
        sellprice = float(sellId['info']['fills'][0]['price'])
        buyprice = read_buyprice()
        profit = ((sellprice - buyprice) / buyprice- 0.002) * 100
        sellcsv(df, buyprice, sellprice, tradesfile)
        print(f'Sell order placed for {symbol} at {sellprice}, Profit: {profit:.2f}%')

    # Check for stop loss
    elif in_position and (df['close'][-1] / read_buyprice() - 1) * 100 < -stop_loss/100:
        # Place sell order
        sellId = place_sell_order(symbol, qty)
        in_position = update_dict_value('pos.json', 'eth4h', False)
        sellprice = float(sellId['info']['fills'][0]['price'])
        buyprice = read_buyprice("btcTrades")
        profit = ((buyprice - sellprice) / buyprice- 0.002) * 100
        sellcsv(df, buyprice, sellprice, tradesfile)
        print(f'Sell order placed for {symbol} at {sellprice}, Profit: {profit:.2f}%')

    csvlog(df, logfile)

except Exception as e:
    print(e)

# sec_of_execution = dt.datetime.now().second+(dt.datetime.now().microsecond/1000000)
# time.sleep(60-sec_of_execution+5)

