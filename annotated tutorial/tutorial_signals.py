# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 00:19:49 2020

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

#---------------------------------Load Datasets-----------------------------
# Data for USA.
market = 'us'
df_income_ttm = sf.load_income(variant='ttm', market=market)
df_income_qrt = sf.load_income(variant='quarterly', market=market)
df_balance_ttm = sf.load_balance(variant='ttm', market=market)
df_cashflow_ttm = sf.load_cashflow(variant='ttm', market=market)
df_cashflow_qrt = sf.load_cashflow(variant='quarterly', market=market)
df_prices = sf.load_shareprices(variant='daily', market=market)


tickers = ['AAPL', 'AMZN', 'MSFT']
df_income_qrt = df_income_qrt.loc[tickers].copy()
df_income_ttm = df_income_ttm.loc[tickers].copy()
df_balance_ttm = df_balance_ttm.loc[tickers].copy()
df_cashflow_ttm = df_cashflow_ttm.loc[tickers].copy()
df_cashflow_qrt = df_cashflow_qrt.loc[tickers].copy()
df_prices = df_prices.loc[tickers].copy()

#------------------------------Price Signals----------------------
# Plot the raw share-prices.
df_prices.loc['AAPL', CLOSE].plot()
# Overlay plot of 200-day moving average.
df_prices.loc['AAPL', CLOSE].rolling(window=200).mean().plot()

#Because these signals are calculated from multiple rows of data, 
#we MUST use Pandas' groupby operator when calculating the signals for multiple stocks in a DataFrame.
df_mavg = df_prices.groupby(TICKER, group_keys=False).rolling(window=200).mean()
df_prices.loc['AAPL', CLOSE].plot()
df_mavg.loc['AAPL', CLOSE].plot()

#calculate multiple price-signals for a single stock
#create a function
def price_signals(df_prices):
    """
    Calculate price-signals for a single stock.
    Use sf.apply() with this function for multiple stocks.
    
    :param df_prices:
        Pandas DataFrame with raw share-prices for a SINGLE stock.
    
    :return:
        Pandas DataFrame with price-signals.
    """
    
    # Create new DataFrame for the signals.Setting the index improves performance.
    df_signals = pd.DataFrame(index=df_prices.index)

    # Moving Average for past 20 days.
    df_signals[MAVG_20] = df_prices[CLOSE].rolling(window=20).mean()

    # Moving Average for past 200 days.
    df_signals[MAVG_200] = df_prices[CLOSE].rolling(window=200).mean()
    
    # Buy and Sell signals generated from the two moving averages.
    df_above = df_signals[MAVG_20] >= df_signals[MAVG_200]
    df_signals[BUY] = df_above & ~df_above.shift(1, fill_value=True)
    df_signals[SELL] = ~df_above & df_above.shift(1, fill_value=False)

    # Exponential Moving Average for past 20 days.
    df_signals[EMA] = df_prices[CLOSE].ewm(span=20).mean()
    
    # Moving Average Convergence Divergence for 12 and 26 days.
    # https://en.wikipedia.org/wiki/MACD
    df_signals[MACD] = df_prices[CLOSE].ewm(span=12).mean() - df_prices[CLOSE].ewm(span=26).mean()
    
    # MACD with extra smoothing by Exp. Moving Average for 9 days.
    df_signals[MACD_EMA] = df_signals[MACD].ewm(span=9).mean()

    # The last trading volume relative to 20-day moving average.
    df_signals[REL_VOL] = np.log(df_prices[VOLUME] / df_prices[VOLUME].rolling(window=20).mean())
    
    return df_signals

#use this function for a single stock
df_price_signals = price_signals(df_prices=df_prices.loc['AAPL'])
df_price_signals.dropna().head()

# Calculate all the price-signals for MULTIPLE stocks.
df_price_signals = sf.apply(df=df_prices, func=price_signals)
df_price_signals.dropna()

#try plot
df_price_signals.loc['MSFT', [REL_VOL, MACD_EMA]].plot()


#simfin help function
df_price_signals = sf.price_signals(df_prices=df_prices)
df_price_signals.dropna().head()
# Calculate a new signal and add as a new column to the DataFrame.
REL_MAVG = 'MAVG 20 / MAVG 200'
df_price_signals[REL_MAVG] = df_price_signals[MAVG_20] / df_price_signals[MAVG_200]
df_price_signals.loc['MSFT', REL_MAVG].plot()

#--------------------------------Trade Signal simfin function---------------
#th rule is
#When signal1 >= signal2 a Hold-signal is generated.
#When signal1 crosses above signal2 a Buy-signal is generated.
#When signal1 crosses below signal2 a Sell-signal is generated.

#For example, we can use the Moving Average for 20 and 200 days to generated these:
df_trade = sf.trade_signals(df=df_price_signals,
                            signal1=MAVG_20, signal2=MAVG_200)

#plot the share prices along with the Buy and Sell signals
def plot_trade_signals(df_prices, df_trade):
    """
    Plot the closing share-price and buy/sell trade-signals
    for DataFrames with a single stock.
    """
    # Plot the closing share-price.
    ax = df_prices[CLOSE].plot()
    
    # Plot the buy-signals as vertical green dashed lines.
    for row in df_trade[df_trade[BUY]].iterrows():
        date = row[0]
        ax.axvline(x=date, linestyle='--', color='green')

    # Plot the sell-signals as verical red dotted lines.
    for row in df_trade[df_trade[SELL]].iterrows():
        date = row[0]
        ax.axvline(x=date, linestyle=':', color='red')
        
    return ax

#plot the share-price along with Buy and Sell signals for ticker AAPL:
ticker = 'AAPL'
plot_trade_signals(df_prices=df_prices.loc[ticker],
                   df_trade=df_trade.loc[ticker])

#---------------------------Volume Signals simfin function----------------
# Get the share-counts from the Income Statements.
df_shares = df_income_ttm[SHARES_BASIC]

# Calculate the trading-volume signals.
# The function takes an argument window for how many days to use 
#in the moving average calculations that are explained below.
df_vol_signals = sf.volume_signals(df_prices=df_prices,
                                   df_shares=df_shares,
                                   window=20)
# Show the result.
#The Relative Volume (REL_VOL) is the logarithm of the ratio between the daily 
#trading-volume and its moving average. We can plot it for the ticker MSFT:
#The Volume Market-Cap (VOLUME_MCAP) is the daily trading-volume multiplied by 
#the shares outstanding, so it is the Market Capitalization of the daily trading volume.
#The Volume Turnover (VOLUME_TURNOVER) is the fraction of the shares outstanding 
#that are being traded in a single day.
df_vol_signals.dropna().head()
df_vol_signals.loc['MSFT', REL_VOL].dropna().plot(grid=True)
df_vol_signals.loc['MSFT', VOLUME_MCAP].dropna().plot(grid=True)
df_vol_signals.loc['MSFT', VOLUME_TURNOVER].dropna().plot(grid=True)

#-----------------------------Financial Signals-----------------------------
#Net Profit Margin
#the fraction of the company's sales that are turned into profits for the shareholders. 
#It is defined as: net income/revenue
df_npm = df_income_ttm[NET_INCOME] / df_income_ttm[REVENUE]
df_npm.loc['MSFT'].plot()

#Sales Growth
#revenue this year/revenue last year
# Function for calculating growth for a single company using quater data
sales_growth = lambda df_grp: df_grp / df_grp.shift(4) - 1
df_growth = df_income_qrt[REVENUE].groupby(TICKER).apply(sales_growth)
df_growth.loc['MSFT'].plot()

#simfin helper function 
df_growth = sf.rel_change(df=df_income_qrt[REVENUE], freq='q',
                          years=1, future=False)
df_growth


#return on equity
#net income/equity in the same time
# Get the relevant data for a single company.
ticker = 'MSFT'
df_inc = df_income_ttm.loc[ticker]
df_bal = df_balance_ttm.loc[ticker]
df_roe = df_inc[NET_INCOME] / df_bal[TOTAL_EQUITY]
#calculate the ROE from the Net Income in a given year $t$ divided by the Equity in the previous year
df_roe = df_inc[NET_INCOME] / df_bal[TOTAL_EQUITY].shift(4)
#We might also argue that the above formula for $ROE_t$ using shifted Equity data 
#is inaccurate, for example if the company has raised new equity capital by issuing 
#new shares during the year, then $Equity_{t - 1\ Year}$ would be too low for calculating $ROE_t$.
# Calculate the ROE for a single ticker.
df_roe = df_inc[NET_INCOME] / 0.5 * (df_bal[TOTAL_EQUITY] + df_bal[TOTAL_EQUITY].shift(4))

#get return on equity for multiple stock
#join data
df1 = df_income_ttm[NET_INCOME]
df2 = df_balance_ttm[TOTAL_EQUITY]
df_join = pd.concat([df1, df2], axis=1)
df_join
#then calculate
roe = lambda df_grp: df_grp[NET_INCOME] / df_grp[TOTAL_EQUITY].shift(4)
df_roe = df_join.groupby(TICKER, group_keys=False).apply(roe)

#helper function for financial signal all together
#Join data
df1 = df_income_ttm[[NET_INCOME, REVENUE]]
df2 = df_balance_ttm[[TOTAL_ASSETS, TOTAL_EQUITY]]
df_join = pd.concat([df1, df2], axis=1)
#create helper function
def fin_signals(df):
    """
    :param df:
        Pandas DataFrame with required data from
        Income Statements, Balance Sheets, etc.
        Assumed to be TTM-data.
    
    :return:
        Pandas DataFrame with financial signals.
    """
    # Create new DataFrame for the signals.
    # Setting the index improves performance.
    df_signals = pd.DataFrame(index=df.index)
    # Net Profit Margin.
    df_signals[NET_PROFIT_MARGIN] = df[NET_INCOME] / df[REVENUE]
    # Return on Assets.
    df_signals[ROA] = df[NET_INCOME] / df[TOTAL_ASSETS].shift(4)
    # Return on Equity.
    df_signals[ROE] = df[NET_INCOME] / df[TOTAL_EQUITY].shift(4)
    return df_signals

#then use apply to apply the function
df_fin_signals = sf.apply(df=df_join, func=fin_signals)
df_fin_signals
df_fin_signals.loc['AAPL'].plot()

#sf built-in simfin function
# if we do not supply the DataFrame with share-prices, the financial signals 
#are not reindexed to daily data-points:
df_fin_signals = sf.fin_signals(df_income_ttm=df_income_ttm,
                                df_balance_ttm=df_balance_ttm)
df_fin_signals.dropna().head()

#If we do supply a DataFrame with share-prices, then the financial signals are 
#reindexed to daily data-points using the index of the share-prices. We can also
#set a fill-method which is 'ffill' (forward-fill) by default, so the missing 
#data-points are filled with the last-known values.
df_fin_signals = sf.fin_signals(df_prices=df_prices,
                                df_income_ttm=df_income_ttm,
                                df_balance_ttm=df_balance_ttm,
                                fill_method='ffill')
df_fin_signals.dropna().head()
sns.lineplot(x=DATE, y=ROA, hue=TICKER,
             data=df_fin_signals.reset_index())
df_fin_signals.loc['AAPL'].plot()

#The function sf.fin_signals lets us apply another function to the signals 
#before reindexing them to daily data-points, e.g. to get multi-year averages. 
#For example, we may calculate the 2-year averages by passing the argument func=sf.avg_ttm_2y.
df_fin_signals_2y = sf.fin_signals(df_prices=df_prices,
                                   df_income_ttm=df_income_ttm,
                                   df_balance_ttm=df_balance_ttm,
                                   func=sf.avg_ttm_2y,
                                   fill_method='ffill')
sns.lineplot(x=DATE, y=ROA, hue=TICKER,
             data=df_fin_signals_2y.reset_index())

#----------------------------Growth Signals---------------------------------
#calculate the year-over-year growth-rates from TTM data as follows:
df = df_income_ttm[[REVENUE, NET_INCOME]]
new_names = {REVENUE: SALES_GROWTH,
             NET_INCOME: EARNINGS_GROWTH}
df_growth = sf.rel_change(df=df, freq='q', quarters=4,
                          future=False, annualized=False,
                          new_names=new_names)
df_growth.head(8)
# to get daily data-points like the share-prices we can reindex the DataFrame:
df_growth_daily = sf.reindex(df_src=df_growth,
                             df_target=df_prices, method='ffill')
df_growth_daily.dropna().head()

#simfin function of growth signal
df_growth_signals = \
    sf.growth_signals(df_income_ttm=df_income_ttm,
                      df_income_qrt=df_income_qrt,
                      df_cashflow_ttm=df_cashflow_ttm,
                      df_cashflow_qrt=df_cashflow_qrt)
df_growth_signals.dropna().head()

#pass daily stock prices
df_growth_signals = \
    sf.growth_signals(df_prices=df_prices,
                      df_income_ttm=df_income_ttm,
                      df_income_qrt=df_income_qrt,
                      df_cashflow_ttm=df_cashflow_ttm,
                      df_cashflow_qrt=df_cashflow_qrt,
                      fill_method='ffill')
df_growth_signals.dropna().head()

#apply another function to the signals before reindexing them to daily data-points
#notice that the 2-year average probably does not make sense on the Quarter-Over-Quarter (QOQ) growth-rates.
df_growth_signals_2y = \
    sf.growth_signals(df_prices=df_prices,
                      df_income_ttm=df_income_ttm,
                      df_income_qrt=df_income_qrt,
                      df_cashflow_ttm=df_cashflow_ttm,
                      df_cashflow_qrt=df_cashflow_qrt,
                      fill_method='ffill',
                      func=sf.avg_ttm_2y)
df_growth_signals_2y.dropna().head()

#----------------------------Valuation Signals---------------------------
#valuation ratios measure how the shares are valued relative to e.g. the 
#company's Earnings, Sales, Book-Value, etc.

#P/Sales Ratio=share price/sales per shares
#first calculate sales per share
#axis =0同一行相除
df_sales_per_share = df_income_ttm[REVENUE].div(df_income_ttm[SHARES_DILUTED], axis=0)
df_sales_per_share
#then calculate P/sales ratio daily data
df_sps_daily =sf.reindex(df_src = df_sales_per_share,
                         df_target = df_prices, method = 'ffill')
df_sps_daily.dropna()
df_psales = df_prices[CLOSE].div(df_sps_daily,axis = 0)
df_psales.rename(PSALES, inplace=True)
df_psales.dropna()
sns.lineplot(x=DATE, y=PSALES, hue=TICKER,
             data=df_psales.reset_index())


#P/E ratio = share price/earnings per share 
#The difference is that NET_INCOME is for the earnings that are available to
# both common and preferred shareholders, while NET_INCOME_COMMON is only the
# part of the earnings that are available to common shareholders
#needtoNET_INCOME_COMMON when calculating the P/E ratio

#first calclate earning per share
df_earnings_per_share = df_income_ttm[NET_INCOME_COMMON].div(df_income_ttm[SHARES_DILUTED], axis=0)
df_earnings_per_share
#reindex and fill NA
df_eps_daily = sf.reindex(df_src=df_earnings_per_share,
                          df_target=df_prices, method='ffill')
df_eps_daily.dropna()
#calculate P/E

# Calculate the P/E ratio.
df_pe = df_prices[CLOSE] / df_eps_daily
df_pe.rename(PE, inplace=True)
df_pe.dropna()

#P/FCF ratio
#In order to get a more cash-based measure of earnings, we must estimate the 
#recurring cash-flows from operations, and subtract the cash used for investing 
#in new factories, equipment and other assets. This is called Free Cash Flow (FCF).

# FCF = Net Cash from Operations (NET_CASH_OPS) - the Capital Expenditures (CAPEX) used to buy new productive assets
#note that The NET_CASH_OPS is basically the company's Net Income with adjustments 
#for non-cash items and changes in working-capital. Some of these items may be 
#non-recurring, so it is not a perfect estimate of the recurring cashflow from operations.
#The CAPEX is actually a data-column named "Change in Fixed Assets & Intangibles"

#Because CAPEX is defined as the Disposition minus Acquisition of Fixed Assets 
#and Intangibles, we have to add CAPEX to NET_CASH_OPS in order to calculate FCF:
#FCF = NET_CASH_OPS + (DISP_FIX_ASSETS_INT - ACQ_FIX_ASSETS_INT) = NET_CASH_OPS + CAPEX
df_fcf_ttm = df_cashflow_ttm[NET_CASH_OPS] + df_cashflow_ttm[CAPEX]
df_fcf_ttm.rename(FCF, inplace=True)
df = pd.concat([df_fcf_ttm.loc['MSFT'],
                df_income_ttm.loc[ticker, NET_INCOME_COMMON]], axis=1)
df.plot()

#calculate per-share FCF
df_fcf_per_share = df_fcf_ttm.div(df_income_ttm[SHARES_DILUTED])
df_fcf_per_share
#reindex it
df_fcf_daily = sf.reindex(df_src=df_fcf_per_share,
                          df_target=df_prices, method='ffill')
# Calculate the P/FCF ratio.
df_pfcf = df_prices[CLOSE] / df_fcf_daily
df_pfcf.rename(PFCF, inplace=True)
df_pfcf.dropna()

#2-year average
#first calculate the average between the current TTM data-point, and the data-point 
#4 quarters in the past. This gives us the average of the 2 last years of earnings.
avg_ttm_2y = lambda df: 0.5 * (df + df.shift(4))
df_earnings_2y = sf.apply(df=df_income_ttm[NET_INCOME_COMMON],
                          func=avg_ttm_2y)
df_eps_2y = df_earnings_2y.div(df_income_ttm[SHARES_DILUTED])
df_eps_2y_daily = sf.reindex(df_src=df_eps_2y,
                             df_target=df_prices, method='ffill')
# Calculate the P/E ratios using 2-year earnings average.
df_pe_2y = df_prices[CLOSE].div(df_eps_2y_daily, axis=0)
PE_2Y = 'P/E (2Y Avg. Earnings)'
df_pe_2y.rename(PE_2Y, inplace=True)
df_pe_2y.dropna()

#helper function, calculate several valuation signals at the same time
def val_signals(df_prices, df_income_ttm, df_cashflow_ttm,
                shares_index=SHARES_DILUTED):
    """
    Calculate valuation signals for all stocks in the DataFrames.

    :param df_prices:
        Pandas DataFrame with share-prices for multiple stocks.
        
    :param df_income_ttm:
        Pandas DataFrame with Income Statement TTM data for multiple stocks.
    
    :param df_cashflow_ttm:
        Pandas DataFrame with Cash-Flow Statement TTM data for multiple stocks.

    :param shares_index:
        String with the data-column name for the share-count
        e.g. SHARES_DILUTED or SHARES_BASIC.
    
    :return:
        Pandas DataFrame with valuation signals.
    """

    # Create a DataFrame with the financial data we need.
    #calculate sales per share and earning per share and free cash flow per share
    df = df_income_ttm[[REVENUE, NET_INCOME_COMMON]].copy()
    df[FCF] = df_cashflow_ttm[NET_CASH_OPS] + df_cashflow_ttm[CAPEX]
    df_per_share = df.div(df_income_ttm[shares_index], axis=0)
    
    # Reindex the per-share financial data to daily data-points.
    df_daily = sf.reindex(df_src=df_per_share,
                          df_target=df_prices,
                          method='ffill')
    
    # Create new DataFrame for the signals. Setting the index improves performance.
    df_signals = pd.DataFrame(index=df_prices.index)
    
    # Use the closing share-price for all these signals.
    df_price = df_prices[CLOSE]
    
    # P/Sales ratio.
    df_signals[PSALES] = df_price / df_daily[REVENUE]
    
    # P/E ratio.
    df_signals[PE] = df_price / df_daily[NET_INCOME_COMMON]

    # P/FCF ratio.
    df_signals[PFCF] = df_price / df_daily[FCF]

    return df_signals

#use the helper function
df_val_signals = val_signals(df_prices=df_prices,
                             df_income_ttm=df_income_ttm,
                             df_cashflow_ttm=df_cashflow_ttm,
                             shares_index=SHARES_DILUTED)
df_val_signals.dropna()
df_val_signals.loc['AMZN', [PE, PFCF]].dropna().plot()
sns.lineplot(x=DATE, y=PFCF, hue=TICKER,
             data=df_val_signals.loc[['AAPL', 'MSFT']].reset_index())

#simfin helper function
df_val_signals = sf.val_signals(df_prices=df_prices,
                                df_income_ttm=df_income_ttm,
                                df_balance_ttm=df_balance_ttm,
                                df_cashflow_ttm=df_cashflow_ttm)
df_val_signals.dropna().head()
sns.lineplot(x=DATE, y=PBOOK, hue=TICKER, data=df_val_signals.reset_index())

#apply moving average
df_val_signals_3y = sf.val_signals(df_prices=df_prices,
                                   df_income_ttm=df_income_ttm,
                                   df_balance_ttm=df_balance_ttm,
                                   df_cashflow_ttm=df_cashflow_ttm,
                                   func=sf.avg_ttm_3y)

#limiting extreme values
df_val_signals.describe()
#set lower and upper limit
lower = {PE: 5, PFCF: 6}
upper = {PE: 1000, PFCF: 60}
#use simfin function clip 
#the P/E and P/FCF signals have been clipped between the specified bounds, 
#while the other columns remain unchanged:
df_clipped = sf.clip(df=df_val_signals, lower=lower, upper=upper)
df_clipped.describe()
df_val_signals.loc['AMZN', PE].dropna().plot()
df_clipped.loc['AMZN', PE].dropna().plot()

#or use quantile to clip the data
#use the 0.05 and 0.95 quantiles as the lower and upper boundaries when clipping
#if columns is not specified, then clip all columns
df_winsorized = sf.winsorize(df=df_val_signals, quantile=0.05, columns = [PE, PFCF])

