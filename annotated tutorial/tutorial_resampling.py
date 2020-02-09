# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 13:41:11 2020

@author: Yimeng
"""

#-----------------------------------Set up-----------------------------
#import packages for data analysis
import pandas as pd
import matplotlib as plt
import seaborn as sns

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
#---------------------------------Load Datasets-----------------------------
market = 'us'
df_income = sf.load_income(variant='annual', market=market)
df_prices = sf.load_shareprices(variant='daily', market=market)
df_prices_latest = sf.load_shareprices(variant='latest', market=market)

tickers = ['AAPL', 'AMZN', 'MSFT']
df_income = df_income.loc[tickers, [REVENUE, NET_INCOME]].copy()
df_prices = df_prices.loc[tickers, [CLOSE, ADJ_CLOSE]].copy()
df_prices_latest = df_prices_latest.loc[tickers, [CLOSE, ADJ_CLOSE]].copy()

#-----------------------------Start resampling------------------------------
#forward-filling the missing values from the value before it 
df_income.loc['MSFT']
df_income.loc['MSFT'].asfreq(freq='D', method='ffill')
df_income.loc['MSFT'].asfreq(freq='D', method='ffill').plot()

#asfreq on multiindex
def _asfreq(df_grp):
    # Remove TICKER from the MultiIndex.
    df_grp = df_grp.reset_index(TICKER, drop=True)
    
    # Perform the operation on this group.
    df_result = df_grp.asfreq(freq='D', method='ffill')

    return df_result

# Split the DataFrame into sub-groups and apply the _asfreq()
# function on each of those sub-groups, and then glue the
# results back together into a single DataFrame.
df_income.groupby(TICKER).apply(_asfreq)

#other asfreq function
df_daily = sf.asfreq_daily(df=df_income, method='ffill')
# Plot.
sns.lineplot(x=REPORT_DATE, y=REVENUE, hue=TICKER, data=df_daily.reset_index())


#resample funcion
df_income.loc['MSFT'].resample('D').ffill().plot() #forward filling
# filling with straight lines between the known points.
df_income.loc['MSFT'].resample('D').interpolate(method='linear').plot() 
# use mean to fill the empty point
df_prices.loc['MSFT'].resample('M').mean().plot()

#resample with multiple index
def _resample(df_grp):
    # Remove TICKER from the MultiIndex.
    df_grp = df_grp.reset_index(TICKER, drop=True)
    
    # Resample and forward-fill NA values.
    df_result = df_grp.resample('D').ffill()

    return df_result

# Split the DataFrame into sub-groups and apply the _resample()
# function on each of those sub-groups, and then glue the
# results back together into a single DataFrame.
df_income.groupby(TICKER).apply(_resample)

#or go for another way
df_daily = sf.resample(df=df_income, rule='D', method='linear')
sns.lineplot(x=REPORT_DATE, y=REVENUE, hue=TICKER,
             data=df_daily.reset_index())

# Custom method for the resampling, use quadratic
method = lambda x: x.interpolate(method='quadratic')
# Do the resampling using the custom method.
df_daily = sf.resample(df=df_income, rule='D', method=method)
# Plot.
sns.lineplot(x=REPORT_DATE, y=REVENUE, hue=TICKER,
             data=df_daily.reset_index())


#down sample: change monthly data to 3 months
df_monthly = sf.resample(df=df_prices, rule='3M', method='mean')
# Drop rows with any empty data.
df_monthly = df_monthly.dropna(how='any')
# Normalize so the time-series for each stock begins at 1.0
# div是divide，每个值都除以起始值，rescaling
_normalize = lambda df_grp: df_grp.div(df_grp.iloc[0])
df_norm = df_monthly.groupby(TICKER).apply(_normalize)
# Plot.
sns.lineplot(x=DATE, y=ADJ_CLOSE, hue=TICKER,
             data=df_monthly.reset_index())


-------------------------------------Reindex data-----------------------

#get index for Microsoft stock price
new_index = df_prices.loc['MSFT'].index
new_index

#use that index to reindex income statement
df_income2 = df_income.loc['MSFT'].reindex(index=new_index)
df_income2.head()
df_income2.dropna()

#union index
# Index for the annual Income Statements.
index_src = df_income.loc['MSFT'].index
# Index for the valid trading-days of the Share-Prices.
index_target = df_prices.loc['MSFT'].index
# Union of the two indices.
new_union_index = index_src.union(index_target)
# reindex the income statement data with union index
df_income.loc['MSFT'].reindex(index=new_union_index,
                              method='ffill').dropna()


#we can actually perform a reindex operation directly on a DataFrame with MultiIndex.
# Index for the annual Income Statements.
index_src = df_income.index
# Index for the valid trading-days of the share-prices.
index_target = df_prices.index
# Union of the two indices.
new_union_index = index_src.union(index_target)
# Set the names of the new index, this is not set by union().
new_union_index.names = index_target.names
# Reindex the annual Income Statements using the union-index.
# The new data-points are not filled so they are NaN.
df_income2 = df_income.reindex(index=new_union_index)

#to fill the missing value using forward filling, we have to do it by ticker
# , and then glue the results back together into a single DataFrame.
df_income3 = df_income2.groupby(TICKER).ffill()
# Remove empty rows.
df_income3.dropna(inplace=True)
# Plot.
sns.lineplot(x=DATE, y=REVENUE, hue=TICKER,
             data=df_income3.reset_index())

#helper function in simfin
#example1
df_daily = sf.reindex(df_src=df_income, df_target=df_prices,
                      group_index=TICKER, method='ffill').dropna()
#example2
# Custom method for the reindexing.
method = lambda x: x.interpolate(method='quadratic')
# Do the resampling using the custom method.
df_daily = sf.reindex(df_src=df_income, df_target=df_prices,
                      group_index=TICKER, method=method).dropna()
sns.lineplot(x=DATE, y=REVENUE, hue=TICKER,
             data=df_daily.reset_index())

#we want to reindex the annual Income Statements, so that we have both the 
#original data and a new data-point for the same date as the latest share-prices. 
#This can be achieved by performing the reindexing with union=True so we use the 
#indices of both the DataFrames, and only_target_index=False so we keep the rows 
#from df_income whose dates were not in df_prices_latest.
df_latest = sf.reindex(df_src=df_income,
                       df_target=df_prices_latest,
                       union=True, only_target_index=False,
                       method='ffill')

# Show the last 3 rows for each Ticker.
df_latest.groupby(TICKER).tail(3)



