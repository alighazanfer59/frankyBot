import ccxt
from frankyConfig import binanceAPI
import pandas as pd
import pandas_ta as ta
import numpy as np
import csv
import os
import time

def binanceActive():
    exchange = ccxt.binance({
        'apiKey': binanceAPI['apiKey'],
        'secret': binanceAPI['secretKey'],
        'enableRateLimit': True,
        'rateLimit': 10000,
        'options': {
            # 'recvWindow': 9000,  # replace with your desired recv_window value
            'test': False,  # use testnet (sandbox) environment
            # 'adjustForTimeDifference': True,
        }
    })
    # exchange.set_sandbox_mode(enable=False)
    return exchange

exchange = binanceActive()


def servertime():
    time = exchange.fetch_time()
    time = pd.to_datetime(time, unit ='ms')
    print(time)


def getqty(coin):
    for item in exchange.fetch_balance()['info']['balances']:
        if item['asset'] == coin:
            qty = float(item['free'])
    return qty

# print(getqty('ETH'))

# Define function to place buy order
def place_buy_order(symbol, size):
    try:
        buyId = exchange.create_market_buy_order(symbol, size)
        return buyId
    except:
        return False
    
# Define function to place sell order
def place_sell_order(symbol, size):
    # try:
    sellId = exchange.create_market_sell_order(symbol, size)
    return sellId
    # except:
    #     return False
    
def calculate_order_size(symbol, usdt_amount):
    # Get the current market price of the coin
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']
    # Calculate the order size based on the USDT amount and the market price
    size = usdt_amount / price
    return size


# Load historical price data
def getdata(symbol, timeframe, limit=100, length1=5, length2=26, bbPeriod=32,bbStdDev=1,rsi_tf='1d',rsiLength=18, dailyRSI = 50):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe,limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
#     df['shifted_close'] = df['close'].shift(1)
    # Calculate the moving averages and Bollinger Bands
    df['sma1'] = df['close'].rolling(window=length1).mean()
    df['sma2'] = df['close'].rolling(window=length2).mean()
    bb = ta.bbands(df.close, length=bbPeriod, std=bbStdDev)
    df['bb_upper'] = bb.iloc[:,2:3]

    # Calculate RSI on daily timeframe
    df_rsi = df.resample(rsi_tf).agg({'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
    df_rsi['hcc4'] = (df_rsi.high + df_rsi.close + df_rsi.close) / 3
    df_rsi['RSI'] = ta.rsi(df_rsi.hcc4, lenght=rsiLength)
    df_rsi = df_rsi[['RSI']]

    # Merge the dataframes
    df = pd.concat([df, df_rsi], axis=1).ffill()
    
    df['buy'] = np.where((df['sma1'] > df['sma2']) & 
                      (df['close'] > df['bb_upper']) & 
                      (df['close'].shift(1) < df['bb_upper'].shift(1)) & 
                      (df['RSI'] > dailyRSI), True, False)
        
    df['sell'] = df['sma1'] < df['sma2']
    return df


# code for appending a new row to the trades CSV file
def csvlog(df, filename):
    headers = ['timestamp','open','high','low','close','volume','sma1','sma2','bb_upper','RSI','buy','sell']
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)


    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = df.index[-1]
        row_to_write = [timestamp] + df.iloc[-1].tolist()
        writer.writerow(row_to_write)

# code for appending a new row to the trades CSV file
def buycsv(df, buyprice,filename):
    headers = ['timestamp', 'buyprice', 'sellprice', 'profit%']
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)


    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        buy_price = buyprice # replace with actual buy price
        sell_price =  "position still open"# replace with actual sell price
        profit_percentage = "nan" #((sell_price - buy_price) / buy_price) * 100
        timestamp = df.index[-1]
        writer.writerow([timestamp,buy_price,sell_price,profit_percentage])
        


def sellcsv(df, buyprice, sellprice, filename):
    headers = ['timestamp', 'buyprice', 'sellprice', 'profit%']
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        buy_price = buyprice # replace with actual buy price
        sell_price =  sellprice # replace with actual sell price
        profit_percentage = ((sell_price - buy_price) / buy_price) * 100
        timestamp = df.index[-1]
        writer.writerow([timestamp,buy_price,sell_price,profit_percentage])


# asset = 0
# balance = np.nan
def in_pos(coin):
    balance = exchange.fetch_balance()['info']['balances']
    try:
        asset = float([i['free'] for i in balance if i['asset'] == coin][0])
        if asset > 0:
            in_position = True
        else:
            in_position = False
    except Exception as e:
        print(e)
        in_position = False
        asset = 0
    return in_position, balance, asset

def read_buyprice(filename):
    try:
        trades = pd.read_csv(filename)
        buyprice = trades['buyprice'].iloc[-1]
    except:
        buyprice = np.nan
    return buyprice

import json

def update_dict_value(filename, key, value):
    with open(filename, 'r') as f:
        d = json.load(f)
    d[key] = value
    with open(filename, 'w') as f:
        json.dump(d, f)


# trades = exchange.fetch_trades('ETHUSDT')[-2:]
# print(trades)


# async def get_qty(coin):
#     balance = exchange.fetch_balance()
#     qty = [float(item['free']) for item in balance['info']['balances'] if item['asset'] == coin][0]
#     return qty

# async def main():
#     qty_task = asyncio.create_task(get_qty(coin))
#     qty_task2 =  asyncio.create_task(getqty(coin))
#     qty = await qty_task
#     print(servertime())
#     qty2 = await qty_task2
#     print(servertime())
#     print(qty)
#     print(f"qty = {qty2}")


# asyncio.run(main())