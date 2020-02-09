# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 20:18:47 2020

@author: think
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
df_income_ann = sf.load_income(variant='annual', market=market)
df_income_qrt = sf.load_income(variant='quarterly', market=market)
df_prices = sf.load_shareprices(variant='daily', market=market)
tickers = ['AAPL', 'AMZN', 'MSFT']
df_income_ann = df_income_ann.loc[tickers, [REVENUE, NET_INCOME]].copy()
df_income_qrt = df_income_qrt.loc[tickers, [REVENUE, NET_INCOME]].copy()
df_prices = df_prices.loc[tickers, [CLOSE, ADJ_CLOSE]].copy()

#-----------------------------start calculating growth rate--------------
#moves the data one step foward
df.shift(periods=1).head()
#When we perform arithmetic operations with the original and shifted DataFrames, 
#they are first aligned by the index-dates. This allows us to calculate relative changes over time.
#the two commands below are the same
((df / df.shift(1))-1).head()
df.pct_change(periods=1).head()

#calculate trading days per year
df = df_prices.loc['MSFT']['2007-01-03':]
len(df['2009':'2018'])/10
df2 = df['2009':'2018']
#plot the histogram of the number of trading-days per year between 2009 ad 2018
df2.groupby(df2.index.year).apply(lambda x: len(x)).hist()

#calculate change in stock price for the 5 year period
years = 5
periods = int(round(251.67 * years))
df.pct_change(periods=periods).dropna().head()

#---------------------------------simfin helper-function-----------------
#calculate stock return
#We set the argument freq='bdays' to indicate the DataFrame contains data for 
#all business-days (roughly 252 data-points per year, as explained above). 
#set bdays=1 which means we want the relative change between successive time-steps
# setting future=True instead, to indicate that we want the change between the 
#future time-step $t+1$ and the current time-step $t$, so the function calculates 
#df_result[t] = df[t+1]/df[t] - 1. 
sf.rel_change(df=df_prices.loc['MSFT'], freq='bdays',
              bdays=1, future=False).head()
#same as 
df.pct_change(periods=1)

#calculate年同比,注意 future=False
sf.rel_change(df=df_prices.loc['MSFT'], freq='bdays',
              years=1, future=False).dropna().head()

#combine shift
sf.rel_change(df=df_prices.loc['MSFT'], freq='bdays',
              bdays=3, years=1, future=True).dropna().head()

#calculate annualized returns for 3-year investment periods
#same as df_result[t] = (df[t]/df[t-3 years]) ** (1/3) - 1
#the code has some kind of bug, be careful 
sf.rel_change(df=df_prices.loc['MSFT'], freq='bdays',
              years=3, future=False, annualized=True).dropna().head()
#combine different time-interval
sf.rel_change(df=df_prices.loc['MSFT'], freq='bdays',
              bdays=2, weeks=3, months=3, years=3,
              future=False, annualized=True).dropna().head()

#Close vs. Adj.Close
#The Close share-price is only adjusted for stock-splits, while the Adj. Close 
#share-price is adjusted for both stock-splits and dividends. This means the 
#Close share-price should be used when calculating valuation ratios such as 
#P/Sales or P/E (which is demonstrated in Tutorial 04), while the Adj. Close 
#should be used for calculating stock-returns.

#For daily stock-returns the Close and Adj. Close are identical, except on the 
#days where dividends have been paid on the stock. The Adj. Close is adjusted for 
#the dividend by assuming it is immediately reinvested in the stock, without having 
#to pay any dividend-taxes, trading commissions, etc. This is also known as the Total Return.

#calculate the future 5-year annualized returns from each stock's Total Return as follows:
sf.rel_change(df=df_prices[TOTAL_RETURN], freq='bdays',
              years=5, future=True, annualized=True).dropna()

#calculate quarterly growth rate of revenue and income
sf.rel_change(df=df_income_qrt.loc['MSFT'], freq='q',
              quarters=1, future=False).head()
#calculate 年同比 in a quaterly data
sf.rel_change(df=df_income_qrt.loc['MSFT'], freq='q',
              years=1, future=False).head(8)

#calculated compound annual growth rate 
#when one number is negative and the other is positive, so the fraction of the 
#two numbers is negative. This causes a problem when calculating annualized changes 
#for multiple years.thus 2012-06-30 is dropped as na
sf.rel_change(df=df_income_qrt.loc['MSFT'], freq='q',
              years=3, future=False, annualized=True).dropna().head()


#change column name
# New column-names.
SHARE_PRICE_3Y = 'Share Price 3-Year'
TOTAL_RETURN_3Y = 'Total Return 3-Year'

# Dict mapping old to new column-names.
new_names = {CLOSE: SHARE_PRICE_3Y,
             ADJ_CLOSE: TOTAL_RETURN_3Y}

# Calculate the annualized 3-year changes and rename columns.
sf.rel_change(df=df_prices, freq='bdays',
              years=3, future=False, annualized=True,
              new_names=new_names).dropna()

#Another way of changing the column-names is to use a lambda-function..
new_names = lambda old_name: old_name + ' 3-Year Ann. Chg.'
# Calculate the annualized 3-year changes and rename columns.
sf.rel_change(df=df_prices, freq='bdays',
              years=3, future=False, annualized=True,
              new_names=new_names).dropna()


#Plotting
# New column-names.
SALES_GROWTH = 'Sales Growth'
EARNINGS_GROWTH = 'Earnings Growth'
new_names = {REVENUE: SALES_GROWTH,
             NET_INCOME: EARNINGS_GROWTH}
# Calculate annualized 3-year growth-rates and rename columns.
sf.rel_change(df=df_income_ann.loc['MSFT'], freq='y',
              years=3, future=False, annualized=True,
              new_names=new_names).dropna().plot(kind='bar')



#If we want to make a single plot for multiple stocks, then we can use the Seaborn plotting package.
df_growth = sf.rel_change(df=df_income_ann, freq='y',
                          years=3, future=False, annualized=True,
                          new_names=new_names).dropna(how='all')

# Title of the plot.
title = '3-Year Annualized Sales Growth'

# Plot with connected lines.
sns.lineplot(x=REPORT_DATE, y=SALES_GROWTH, hue=TICKER,
            data=df_growth.reset_index()).set_title(title)
#plot bar-chart
sns.barplot(x=REPORT_DATE, y=SALES_GROWTH, hue=TICKER,
            data=df_growth.reset_index()).set_title(title)

#use fiscal year as x-axis
# Load annual Income Statements and set the index.
df = sf.load_income(variant='annual', market='us',
                    index=[TICKER, FISCAL_YEAR])
# Select the tickers and columns we are interested in.
df = df.loc[tickers, [REVENUE, NET_INCOME]]
#calculate annualized 3-year growth-rates
df_growth = sf.rel_change(df=df, freq='y', years=3, future=False, 
                          annualized=True, new_names =new_names).dropna(how='all')
sns.barplot(x=FISCAL_YEAR, y=SALES_GROWTH, hue = TICKER,
            data=df_growth.reset_index()).set_title(title)

#mean-log annualized stock-return
# New column-names.
SHARE_PRICE_1_3Y = 'Mean-Log Share-Price Return 1-3 Years'
TOTAL_RETURN_1_3Y = 'Mean-Log Total Return 1-3 Years'
new_names_1_3y = {SHARE_PRICE: SHARE_PRICE_1_3Y,
                  TOTAL_RETURN: TOTAL_RETURN_1_3Y}
# Calculate the future mean-log annualized 1-3 year changes.
df_mean_chg = sf.mean_log_change(df=df_prices, freq='bdays',
                                 future=True, annualized=True,
                                 min_years=1, max_years=3,
                                 new_names=new_names_1_3y)
#Plot
title = 'Future 1-3 Years Mean-Log Ann. Total Return'
data = df_mean_chg.dropna().reset_index()
sns.lineplot(x=DATE, y=TOTAL_RETURN_1_3Y, hue=TICKER,
             data=data).set_title(title)

#how to interpret mean-log annualized return?
df_mean_chg.loc[('MSFT', '2016-11-15'), TOTAL_RETURN_1_3Y]
#This value of about 0.34 is the mean-log annualized return for all periods 
#starting on 2016-11-15 and ending somewhere between 2017-11-15 and 2019-11-15. 
#So if you had bought the MSFT stock on 2016-11-15 and held it somewhere between
# 1 and 3 years, then on average, you would have made a log-return of 0.34 per year.

#when setting future = False, then 
df_mean_chg.loc[('MSFT', '2019-11-15'), TOTAL_RETURN_1_3Y]
#This value of about 0.31 is the mean-log annualized return for all 1-3 year 
#periods ending on 2019-11-15 that started somewhere between 2016-11-15 and 2018-11-15
# So if you had bought the MSFT stock somewhere between 2016-11-15 and 2018-11-15 
#and sold it on 2019-11-15, then on average, you would have made a log-return of 0.31 per year. 
#Because the log-transform underestimates the normal returns for values beyond $\pm 20\%$, 
#the mean annualized return was probably around 36%.


#Geometric Mean Daily Stock-Returns
#The annualized returns are particularly useful for longer periods of several years, 
#but for shorter periods the annualization formula can produce extreme values. So it 
#is sometimes more useful to calculate the geometric mean, based on the frequency of the original data.
#We switch from Annualization to Geometric Mean simply by setting the function's argument 
#annualized=False:

#mean-log geometric-mean for all future stock-returns between 1-3 months
# New column-names.
SHARE_PRICE_1_3M = 'Mean-Log Share-Price Return 1-3 Months'
TOTAL_RETURN_1_3M = 'Mean-Log Total Return 1-3 Months'
new_names_1_3m = {SHARE_PRICE: SHARE_PRICE_1_3M,
                  TOTAL_RETURN: TOTAL_RETURN_1_3M}

# Calculate the future mean-log 1-3 month changes.
df_mean_chg = sf.mean_log_change(df=df_prices, freq='bdays',
                                 future=True, annualized=False,
                                 min_months=1, max_months=3,
                                 new_names=new_names_1_3m)
title = 'Future 1-3 Months Mean-Log Total Return'
# Plot the result.
data = df_mean_chg.dropna().reset_index()
sns.lineplot(x=DATE, y=TOTAL_RETURN_1_3M, hue=TICKER,
             data=data).set_title(title)

#use cache to store data
# Refresh the cache once a day.
cache_refresh_days = 1
# Name for the cache. Use the concatenated tickers.
cache_name = '-'.join(tickers) + '-1-3y'
# Dict with the cache-arguments. This makes it easier to pass the arguments to multiple functions.
cache_args = {'cache_name': cache_name,
              'cache_refresh' : cache_refresh_days}

#unpacks the arguments in the dict as if they were normal arguments passed to the function.
df_mean_chg = sf.mean_log_change(df=df_prices, freq='bdays',
                                 future=True, annualized=True,
                                 min_years=1, max_years=3,
                                 new_names=new_names_1_3y,
                                 **cache_args)











