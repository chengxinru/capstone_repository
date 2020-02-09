# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 22:23:12 2020

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

#--------------------------Load data-----------------------------
hub = sf.StockHub(market='us',
                  refresh_days=30,
                  refresh_days_shareprices=1)


#----------------------- FInancial Signals----------------------
#get financial signals on latest stock
df_fin_signals = hub.fin_signals(variant='latest')
#calculate 2-year average financial signals on latest stock
df_fin_signals_2y = hub.fin_signals(variant='latest',
                                    func=sf.avg_ttm_2y)

#-----------------------Growth Signals-----------------------
#same as above
df_growth_signals = hub.growth_signals(variant='latest')
df_growth_signals_2y = hub.growth_signals(variant='latest',
                                          func=sf.avg_ttm_2y)
#-----------------------Valuation Signals--------------------
df_val_signals = hub.val_signals(variant='latest')
df_val_signals_2y = hub.val_signals(variant='latest',
                                    func=sf.avg_ttm_2y)

#------------------------Combine Signals---------------------
dfs = [df_fin_signals, df_growth_signals, df_val_signals]
df_signals = pd.concat(dfs, axis=1)
df_signals.head()

#------------------------------Screener for Net-Net Stocks--------------
#screen for valid stock to invest
#P/NetNet ratios between 0 and 1 indicate the stocks are trading at a discount 
#to their estimated liquidation values. The lower the P/NetNet ratio, the cheaper the stock is.
mask = (df_signals[P_NETNET] > 0) & (df_signals[P_NETNET] < 1)
df_signals.loc[mask, P_NETNET]


#screener for many criteria
mask = (df_signals[MARKET_CAP] > 1e9)
mask &= (df_signals[CURRENT_RATIO] > 2)
mask &= (df_signals[DEBT_RATIO] < 0.5)
mask &= (df_signals[SALES_GROWTH_YOY] > 0)
df_signals[mask]

#----------------------------sorting data-------------------------
#sort by the P/FCF ratios:
columns = [PFCF, PE, ROA, ROE, CURRENT_RATIO, DEBT_RATIO]
df_signals.loc[mask, columns].sort_values(by=PFCF, ascending=True)

#-----------------------Handling NaN Signal-Values-------------------
# Load the TTM Balance Sheets from the data-hub
df_balance_ttm = hub.load_balance(variant='ttm')

# Show the relevant data of amazon
#Consider for example the ticker AMZN, where all data for Short Term Debt is 
#missing in all the reports, while the Long Term Debt is only missing in some reports.
#That's because AMZN had actually not reported these numbers in some of their quarterly 
#reports. That is why the values are missing in the data.
columns = [ST_DEBT, LT_DEBT, TOTAL_ASSETS]
df_balance_ttm.loc['AMZN', columns]['2010':'2013']

#A simple solution is to ignore signals that are NaN. For example
# Start the screener with a market-cap condition.
mask = (df_signals[MARKET_CAP] > 1e9)
# Screener criteria where NaN signals are ignored.
mask &= ((df_signals[CURRENT_RATIO] > 2) | (df_signals[CURRENT_RATIO].isnull()))
mask &= ((df_signals[DEBT_RATIO] < 0.5) | (df_signals[DEBT_RATIO].isnull()))
mask &= ((df_signals[PE] < 20) | (df_signals[PE].isnull()))
mask &= ((df_signals[PFCF] < 20) | (df_signals[PFCF].isnull()))
mask &= ((df_signals[ROA] > 0.03) | (df_signals[ROA].isnull()))
mask &= ((df_signals[ROE] > 0.15) | (df_signals[ROE].isnull()))
mask &= ((df_signals[NET_PROFIT_MARGIN] > 0.0) | (df_signals[NET_PROFIT_MARGIN].isnull()))
mask &= ((df_signals[SALES_GROWTH] > 0.1) | (df_signals[SALES_GROWTH].isnull()))
columns = [PFCF, PE, ROA, ROE, CURRENT_RATIO, DEBT_RATIO]
df_signals.loc[mask, columns].sort_values(by=PE, ascending=True)