# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 21:21:29 2020

@author: think
"""
#-----------------------------------Set up-----------------------------
#import packages for data analysis
import pandas as pd
import matplotlib as plt
import seaborn as sns
import numpy as np
# Import the main functionality from the SimFin Python API.
import simfin as sf

# Import names used for easy access to SimFin's data-columns.
from simfin.names import *

#Set the local directory where data-files are stored.
sf.set_data_dir('C:/Users/think/Desktop/UVA/2020 Spring/STAT 4996 Capstone\python code/simfin_data/')

# Set up API key
sf.set_api_key(api_key='free')

#set plotting style 
sns.set_style("whitegrid")

#---------------------------Create Data Hub---------------------------
#Using these settings, we can then create the data-hub object. This basically 
#just creates and configures the data-hub. It does not load any data or perform 
#any calculations at this point, so it returns nearly instantly.

#example
market = 'us'
tickers = ['AAPL', 'AMZN', 'MSFT']
offset = pd.DateOffset(days=60)
refresh_days = 30
refresh_days_shareprices = 10
hub = sf.StockHub(market=market, tickers=tickers, offset=offset,
                  refresh_days=refresh_days,
                  refresh_days_shareprices=refresh_days_shareprices)
#load data from data hub
df_prices = hub.load_shareprices(variant='daily')
df_income_ttm = hub.load_income(variant='ttm')

#warning
# you should NEVER modify the DataFrames returned by the data-hub's functions
# If you want to modify the DataFrames returned by the data-hub, you should 
# ALWAYS make a copy first!
#i f you accidentally modified any of the DataFrames returned by the data-hub
# it is recommended that you simply create a new data-hub and start over

#---------------------------Use hub to calculate ratio--------------
hub.price_signals().head()
df_vol_signals = hub.volume_signals(window=20)
df_growth_signals_qrt = hub.growth_signals(variant='quarterly')
#By setting variant='latest' we only calculate the valuation signals for the 
#latest day of the share-prices
df_val_signals_latest = hub.val_signals(variant='latest')
df_val_signals_daily = hub.val_signals(variant='daily')
#calculate the annualized future stock-returns for all 3-year investment periods.
df_returns_3y = hub.returns(name='Total Return 3-Year', years=3,
                            future=True, annualized=True)
df_returns_3y.loc['AAPL']['2007-01-03':'2007-01-09']
#mean-log return 
df_returns_1_3y = \
    hub.mean_log_returns(name=TOTAL_RETURN_1_3Y,
                         min_years=1, max_years=3,
                         future=True, annualized=True)
#If we call the same function with a different argument, then the data-hub 
#automatically changes the cache-name so as to keep the different results in 
#separate cache-files:
    
#combine signals and returns
# List of all the DataFrames with different signals.
dfs = [df_price_signals, df_fin_signals_daily,
       df_growth_signals_daily, df_val_signals_daily]
signals = [PE, PSALES, CURRENT_RATIO, MAVG_20]
# Combine all the signal DataFrames into a single DataFrame.
#select only the signals interested 
df_all_signals = pd.concat(dfs, axis=1)
df_signals = df_all_signals[signals]
# combine the signals with the stock-returns.
dfs = [df_signals, df_returns_3y, df_returns_1_3y]
df_combined = pd.concat(dfs, axis=1)
# Remove rows with any NaN values.
df_combined = df_combined.dropna(how='any')
    


    
    
    
    
    