
# =============================================================================
# Income Statement Column definition
# 1. Revenue: the amount of money that a company actually receives during a 
# specific period, including discounts and deductions for returned merchandise. 
# It is the top line or gross income figure from which costs are subtracted to 
# determine net income.

# 2. Cost of Revenue

# 3. Gross profit: the profit a company makes after deducting the costs associated 
# with making and selling its products, or the costs associated with providing its 
# services.

# 4. Operating expenses: those expenditures that a business incurs to engage in 
# activities not directly associated with the production of goods or services. 
# These expenditures are the same as selling, general and administrative expenses.

# 5. Selling, General & Administrative Expense

# 6. Research & Development Expense

# 7. Depreciation, depletion and amortization (DD&A): noncash expenses used in 
# accrual accounting. Depreciation is a means of allocating the cost of a material 
# asset over its useful life, and depletion is used to allocate the cost of 
# extracting natural resources from the Earth and is the actual physical 
# depletion of a natural resource by a company. Amortization is the deduction 
# of capital expenses over a specified time period, typically the life of an 
# asset.

# 8. Operating Income(EBIT): In accounting and finance, earnings before interest and 
# taxes (EBIT), is a measure of a firm's profit that includes all expenses except 
# interest and income tax expenses.

# 9. Non-operating income: in accounting and finance, is gains or losses from 
# sources not related to the typical activities of the business or organization. 

# 10. Interest Expense, Net

# 11. Pretax Income Adj. 

# 12. Abnormal Gains (Losses): Abnormal Gains (Loss) Abnormal gains are usually 
# gains of a non-recurring nature. For example, an unrealised gain from currency 
# hedging would be written back as an abnormal because it is not congruent with 
# the normal operations of the business. Abnormal loss means that loss which is 
# caused by unexpected or abnormal conditions such as accident, machine breakdown,
# substandard material etc. 

# 13. Pretax Income (Loss)

# 14. Income Tax (Expense) Benefit, Net

# 15. Income (Loss) from Continuing Operations: Net Income after taxation, smaller than EBIT

# 16. Net Extraordinary Gains (Losses): economic events coming from continuing 
# operations that are both infrequent and unusual. In other words, these gains 
# and losses stem from the normal business activities of the company, but do not 
# happen regularly, and are abnormal in nature. For example a tornado in Michigan
#  that destroys a factory is both infrequent and unusual.

# 17. Net Income: usually equal to infome from continuing operations

# 18. Net Income: Net profit, also referred to as the top line, net income, 
# or net earnings is a measure of the profitability of a venture after accounting 
# for all costs. It is the actual profit, and includes the operating expenses that
# are excluded from gross profit.

# 18. Shares (Basic) 

# 19. Shares (Diluted) : a more conservative measure 
# =============================================================================


# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 00:22:16 2020

@author: Yimeng 
"""
#-----------------------------------Set up-----------------------------
#import packages for data analysis
import pandas as pd
import matplotlib as plt

# Import the main functionality from the SimFin Python API.
import simfin as sf

# Import names used for easy access to SimFin's data-columns.
from simfin.names import *

#Set the local directory where data-files are stored.
sf.set_data_dir('C:/Users/think/Desktop/UVA/2020 Spring/STAT 4996 Capstone\python code/simfin_data/')

# Set up API key
sf.set_api_key(api_key='free')

#---------------------------------General Load Function--------------------

#load in entire annual,quaterly, monthly US income statement data
df_a = sf.load_income(variant='annual', market='us')
df_q = sf.load_income(variant='quarterly', market='us')
df_m = sf.load_income(variant='ttm', market='us')

#check how the dataframe looks like
df_a.head()
df_q.head()
df_m.head()

#Plot Microsoft's revenue across years
#don't have to add quatation marks when using pyhon shortcut
df_q.loc['MSFT'][REVENUE].plot(grid=True)

#Load in income statement for banks and insurance companies
df = sf.load_income_banks(variant='annual', market='us')
df = sf.load_balance_insurance(variant='annual', market='us')

#load share prices
df_prices_latest = sf.load_shareprices(variant='latest', market='us')
df_prices = sf.load_shareprices(variant='daily', market='us')
df_prices_latest.head()

#Load Companies Detail
df_companies = sf.load_companies(index=TICKER, market='us')

#Load sector and industry details
df_industries = sf.load_industries()

#Look up industry detail of Microsoft 
industry_id = df_companies.loc['MSFT'][INDUSTRY_ID]
df_industries.loc[industry_id]

#try to load full income statement data
try:
    df = sf.load_income(variant='annual-full', market='us')
except sf.ServerException as e:
    print(e)
    
#Get info about certain datasets
sf.info_datasets('companies')
#Get info about certain columns
col_info = sf.info_columns(COMPANY_NAME)


#find all columns whose name, shortcuts or description contain the word 'shares': 
sf.info_columns('shares')

#------------------------------------Pandas Introduction----------------
#get subset
df_income = sf.load_income(variant='annual', market='us')
tickers = ['AAPL', 'AMZN', 'MSFT']
df = df_income.loc[tickers]

#selecting columns,must use double brackets to get data frame
df[[REVENUE, NET_INCOME]].head()

#selectig rows
df.loc['MSFT'].head()
df.loc[('MSFT', '2010-06-30')]

#selecting columns and rows
df.loc[('MSFT', '2010-06-30'), [REVENUE, NET_INCOME]]

#slicing, the two commands below are the same
df[('MSFT', '2010-06-30'):('MSFT', '2013-06-30')]
df.loc[('MSFT', '2010-06-30'):('MSFT', '2013-06-30')]

#slicing not only rows but also columns
df.loc[('MSFT', '2010-06-30'):('MSFT', '2013-06-30'),
       REVENUE:OP_EXP].head()

#filtering
mask1 = (df[REVENUE] > 2e11)
mask2 = (df[NET_INCOME] > 5e10)
df[mask1 & mask2][[REVENUE, NET_INCOME]]

#divide entire column by a number
df2 = df.copy()
df2[[REVENUE, NET_INCOME]] /= 1e9
df2.head()

#allocating values
df2.loc[mask1, [REVENUE, NET_INCOME]] = [123, 456]

#caveat:Because chained assignment can wreak havoc in your code that can be 
# very hard to detect and fix, it may be a good idea to NEVER use chained lookups 
# when also updating the data!


#add new columns
df2 = df.copy()
df2[NET_PROFIT_MARGIN] = df2[NET_INCOME] / df2[REVENUE]

#group by
#the following command calculate movin average of window 2 for every company
df.groupby(TICKER, group_keys=False).rolling(2, min_periods=1).mean() #有问题
df[[REVENUE, NET_INCOME]].groupby(TICKER).mean()
df[[REVENUE, NET_INCOME]].groupby(TICKER).describe()

#iterate all groups 
for ticker, df_grp in df.groupby(TICKER):
    print("Ticker:", ticker)
    print(df_grp[[REVENUE, NET_INCOME]].head())
    print()

#calculates the sum of all the columns in each DataFrame sub-group.
    
# Function to apply to each DataFrame sub-group.
def func(df_grp):
    # Calculate sum of all columns.
    result = df_grp.sum()
    
    # Print the original DataFrame sub-group.
    print("Group DataFrame:")
    print(df_grp)
    print()
    
    # Print the result.
    print("Result:")
    print(result)
    print()
    
    return result

# Split the DataFrame into sub-groups according to TICKER,
# then call func() on each of those DataFrames, and glue the
# results together to a single DataFrame again.
df.groupby(TICKER).apply(func)

# or easier way
df.groupby(TICKER).apply(lambda df_grp: df_grp.sum())

#plot each firm's stock price time series plot
for ticker, df_grp in df.groupby(TICKER):
    df_grp.reset_index(TICKER)[[REVENUE, NET_INCOME]].plot(title=ticker, grid=True)
    

# Filter out tickers that net income is negative 
func = lambda df_grp: (df_grp[NET_INCOME]>0.0).all()
df_result = df.groupby(TICKER).filter(func)

# Show two columns from the result.
df = df_income.loc[tickers, [REVENUE, NET_INCOME]]
def func(df):
    return df.sum()
sf.apply(df=df, func=func)
#By default the sf.apply function groups the data by the Ticker. 
# If you are using another index such as SIMFIN_ID, then you simply pass 
# it as an argument to the function: 
sf.apply(df=df, func=func, group_index=SIMFIN_ID)


#datasets and columns information
sf.info_datasets()
sf.info_datasets('shareprices')
sf.info_columns(COMPANY_NAME)