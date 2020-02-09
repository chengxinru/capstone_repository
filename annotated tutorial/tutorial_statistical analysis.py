# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 23:22:19 2020

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
offset = pd.DateOffset(days=60)
# Refresh the fundamental datasets (Income Statements etc.)
# Refresh the dataset with shareprices every 10 days.
hub = sf.StockHub(market='us', offset=offset,
                  refresh_days=30,
                  refresh_days_shareprices=10)

#calculating signal data
df_fin_signals = hub.fin_signals(variant='daily')
df_growth_signals = hub.growth_signals(variant='daily')
df_val_signals = hub.val_signals(variant='daily')
dfs = [df_fin_signals, df_growth_signals, df_val_signals]
df_signals = pd.concat(dfs, axis=1)


#-----------------------Missing Data----------------------------------
# First Remove all rows with only NaN values.
df = df_signals.dropna(how='all').reset_index(drop=True)

# For each column, show the fraction of the rows that are NaN.
(df.isnull().sum() / len(df)).sort_values(ascending=False)

#Let us remove all signals that have more than 25% missing data:

# List of the columns before removing any.
columns_before = df_signals.columns

# Threshold for the number of rows that must be NaN for each column.
thresh = 0.75 * len(df_signals.dropna(how='all'))
# Remove all columns which don't have sufficient data.
df_signals = df_signals.dropna(axis='columns', thresh=thresh)

# List of the columns after the removal.
columns_after = df_signals.columns
# Show the columns that were removed.
columns_before.difference(columns_after)

#----------------------------Screen for NetNet Stocks----------------
#only use the signal-rows that have a P/NetNet ratio between zero and one, 
#thus indicating the stock is trading at a discount to its NetNet liquidation estimate.

mask_netnet = (df_signals[P_NETNET] > 0) \
            & (df_signals[P_NETNET] < 1)
df_signals.loc[mask_netnet, P_NETNET]

#count the number of NetNet stock in each months
mask_netnet.groupby(DATE).sum().plot(grid=True)

#draw out all the tickers that have traded at NetNet discounts at some point
tickers_netnet = mask_netnet[mask_netnet].reset_index()[TICKER].unique()
print('Number of unique tickers:', len(tickers_netnet))
print(tickers_netnet)

#plot P/NetNet ratio against 1-day stock-returns
# Calculate 1-day stock-returns and limit the dail returns between -10% and +10%
df_returns_1d = hub.returns(name='Total Return 1-Day',
                            bdays=1, future=True, annualized=False)
df_returns_1d = df_returns_1d.clip(-0.1, 0.1)

#combine stock return data and P/NetNet data
dfs = [df_signals.loc[mask_netnet], #contains P/NetNet
       df_returns_1d.loc[mask_netnet]] #contain stock return
df_sig_rets = pd.concat(dfs, axis=1)

#make a scatter-plot of the P/NetNet ratio versus the daily stock-returns:
sns.scatterplot(x=P_NETNET, y='Total Return 1-Day', hue=TICKER,
                data=df_sig_rets.reset_index(), legend=False)

#do the same thing for 1-3 Year returns
TOTAL_RETURN_1_3Y = 'Total Return 1-3 Years'
df_returns_1_3y = hub.mean_log_returns(name=TOTAL_RETURN_1_3Y,
                         future=True, annualized=True,
                         min_years=1, max_years=3)
# Combine the signals and stock-returns.
# We are only using the rows which are NetNet discounts.
dfs = [df_signals.loc[mask_netnet],
       df_returns_1_3y.loc[mask_netnet]]
df_sig_rets = pd.concat(dfs, axis=1)
sns.scatterplot(x=P_NETNET, y=TOTAL_RETURN_1_3Y, hue=TICKER,
                data=df_sig_rets.reset_index(), legend=False)


#--------------------removing outliers------------------------

# Winsorization is basically limits or clips the data between e.g. the 5% and 95% quantiles of the data
# Select all columns except for the P/NetNet ratio.
columns = df_sig_rets.columns.drop(P_NETNET)
# Winsorize all the other signals and stock-returns.
df_sig_rets2 = sf.winsorize(df_sig_rets, columns=columns)
#plot to see the difference 
#see all the dots above or blow the bound are stocked around the boarder 
sns.scatterplot(x=P_NETNET, y=TOTAL_RETURN_1_3Y, hue=TICKER,
                data=df_sig_rets2.reset_index(), legend=False)

# Winsorize all the other signals and stock-returns.
# Instead of clipping values beyond the bounds, set them to NaN.
df_sig_rets = sf.winsorize(df_sig_rets, columns=columns, clip=False)
sns.scatterplot(x=P_NETNET, y=TOTAL_RETURN_1_3Y, hue=TICKER,
                data=df_sig_rets.reset_index(), legend=False)

#---------------------Linear Correlation---------------------
#We will study the linear correlation between the signals and stock-returns, 
#to roughly assess which signals might be the best predictors for stock-returns.
#We will also study the linear correlation between the signals themselves, 
#to assess whether some of the signals seem to be redundant and can be removed.

#show the correlation between all the signals and the 1-3 year average stock-returns
#sorted according to the absolute correlation strength
df_corr = df_sig_rets.corr()
df_corr_returns = df_corr[TOTAL_RETURN_1_3Y].abs().sort_values(ascending=False)
df_corr_returns
#plot correlation matrix but only show the larger correlations
df_corr2 = df_corr[(df_corr.abs() > 0.7) & (df_corr != 1)].round(2)
# Transform the table to give a better overview.
df_corr2 = df_corr2.stack()
# we see that P/NetNet, P/Book and P/NCAV are strongly correlated, so we should only keep one of these. 

#check their correlations with stock return
#find that P_NETNET is more highly correlated 
df_corr_returns[[P_NETNET, P_BOOK, P_NCAV]]
#先看有哪些变量之间是highly correlated，再看这些变量 哪个和target的correlation更高，保留高的那一个
#Return on Assets (ROA) and Return on Equity (ROE) are strongly correlated.
#ROE is better correlated with the stock-returns than ROA, so we will keep ROE
df_corr_returns[[ROA, ROE]]
df_corr_returns[[EARNINGS_YIELD, FCF_YIELD]]
#thus remove the P/NCAV, P/Book, P/Sales, ROA, and Earnings Yield from the signals
columns = [P_NCAV, P_BOOK, P_SALES, ROA, EARNINGS_YIELD]
df_sig_rets = df_sig_rets.drop(columns=columns)

#-------------------------Linear Regression----------------------------
import statsmodels.api as sm
def regression(df, use_constant=True):
    """
    Perform multiple linear-regression on the given data.
    
    :param df:
        Pandas DataFrame with signals and returns.
        
    :param use_constant:
        Boolean whether to add a 'Constant' column to
        find the bias.
    
    :return:
        StatsModels Regression Results.
    """
    # Remove rows where all values are missing.
    df = df.dropna(how='any')

    # DataFrame which only contains the signals.
    df_x = df.drop(columns=[TOTAL_RETURN_1_3Y])
    
    # DataFrame which only contains the stock-returns.
    df_y = df[TOTAL_RETURN_1_3Y]

    # Standardize the signals so they have mean 0 and std 1.
    df_x = (df_x - df_x.mean()) / df_x.std()

    # Add a "constant" column so the regression can find the bias.
    if use_constant:
        df_x['Constant'] = 1.0

    # Perform the regression on this data.
    model = sm.OLS(df_y, df_x).fit()
    
    return model

#now perform regression on the signals selected
model = regression(df=df_sig_rets)

# Show the results.
model.summary()

#Regression usiing only significant signals
# Remove the signals that are statistically insignificant
# because they have high p-values in the regression above.
columns = [P_FCF, PE, SALES_GROWTH_YOY, FCF_YIELD]
df_sig_rets2 = df_sig_rets.drop(columns=columns)
# Perform the Linear Regression again using remaining signals.
model2 = regression(df=df_sig_rets2)
# Show the results.
model2.summary()

# Because we have standardized the signals so they have zero mean and one 
#standard deviation, the regression coefficients can be used to roughly assess 
#which signals are most important in predicting the stock-returns.
#order coefficient
def sort_coefs(model):
    """Helper-function to sort regression coefficients."""
    return pd.Series(model.params).abs().sort_values(ascending=False)
sort_coefs(model=model2)
#There is an important caveat, because if we remove just one signal, then the 
#regression coefficients may change completely.

#------------------------Scatter Plot---------------------------
#check the linear relationship assumption of regression modle
import seaborn as sns
# Plot these signals on the x-axis.
x_vars = [GROSS_PROFIT_MARGIN, P_NETNET, MARKET_CAP]

# Plot the stock-returns on the y-axis
y_vars = [TOTAL_RETURN_1_3Y]

# Create the plots.
g = sns.PairGrid(df_sig_rets.reset_index(), height=4,
                 x_vars=x_vars, y_vars=y_vars, hue=TICKER)
g.map(sns.scatterplot);

#The colours in these plots represent different stock-tickers. 
#The Gross Profit Margin was found to be the most important signal 
#for predicting the future stock-returns over 1-3 year investment periods, 
#because it had the highest R-squared value. But when we look at its scatter-plot, 
#there is no clear relation between the Gross Profit Margin and stock-returns.

#The second scatter-plot is for the P/NetNet signal. This had a lower R-squared 
#value than the Gross Profit Margin. But in this plot we see clear and characteristic 
#downward-sloping curves, if we separate them by the ticker-colours.

#The third scatter-plot is for the Market-Cap signal. This had nearly zero 
#R-squared value when regressing only with this signal, thus indicating that 
#it had nearly zero ability to predict the stock-returns. But once again we see 
#characteristic downward-sloping curves similar to the P/NetNet signal.















