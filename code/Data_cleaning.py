#!/usr/bin/env python
# coding: utf-8

# # Set up

# In[1]:


# import libraries 
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 
import simfin as sf
from simfin.names import *
from IPython.display import display
import datetime
get_ipython().run_line_magic('matplotlib', 'inline')

#set the local directory where data-files are stored
sf.set_data_dir('C:/Users/think/Desktop/UVA/2020Spring/STAT_4996_Capstone/simfin_data')

# 一个cell显示所有output
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'

# Set up API key
sf.set_api_key(api_key='free')

# Seaborn set plotting style.
sns.set_style("whitegrid")

#display all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[2]:


import pandas as pd


# # Define functions

# In[3]:


#calculate the proportion of non-missing value in each column
def prop_nonmissing(df):
    df2 = df.reset_index().copy()
    output = pd.DataFrame(index = df2.columns)
    nomiss_prop = []
    for c in df2.columns:
        nomiss_prop.append(round((1-(df2.loc[:,c].isnull().sum()/len(df2.loc[:,c])))*100,2))
    output['Prop'] = nomiss_prop
    return output


# In[ ]:





# # Loading Data

# ## income statement

# In[4]:


#load in entire annual income statement data
df_income_a = sf.load_income(variant='annual', market='us').reset_index()
#banks only
df_income_a_bank  = sf.load_income_banks(variant='annual', market='us').reset_index()
#insurance companies only
df_income_a_ins = df = sf.load_balance_insurance(variant='annual', market='us').reset_index()

"""
#load quarter data
df_income_q = sf.load_income(variant='quarterly', market='us')
df_income_q_bank  = sf.load_income_banks(variant='quarterly', market='us')
df_income_q_ins = df = sf.load_balance_insurance(variant='quarterly', market='us')

#load ttm data
df_income_ttm = sf.load_income(variant='ttm', market='us')
df_income_ttm_bank  = sf.load_income_banks(variant='ttm', market='us')
df_income_ttm_ins = df = sf.load_balance_insurance(variant='ttm', market='us')
"""


# ## balance sheet

# In[5]:


#load in entire annual balance sheet data 
df_balance_a = sf.load_balance(variant='annual', market='us').reset_index()
#banks only
df_balance_a_bank = sf.load_balance_banks(variant='annual', market='us').reset_index()
#insurance companies only
df_balance_a_ins = sf.load_balance_insurance(variant='annual', market='us').reset_index()

df_balance_a.columns


# ## cash flow

# In[6]:


#load in entire annual balance sheet data 
df_cashflow_a = sf.load_cashflow(variant='annual', market='us').reset_index()
#banks only
df_cashflow_a_bank = sf.load_cashflow_banks(variant='annual', market='us').reset_index()
#insurance companies only
df_cashflow_a_ins = sf.load_cashflow_insurance(variant='annual', market='us').reset_index()


# ## Shareprice 

# In[7]:


df_prices = sf.load_shareprices(variant='daily', market='us').reset_index()
df_prices_latest = sf.load_shareprices(variant='latest', market='us').reset_index()


# ## Companies details

# In[8]:


comp = sf.load_companies(market='us').reset_index()
industry = sf.load_industries().reset_index()


# # Date exploration

# ## Income Statement 

# 结论：
# 
# 
# 1. Simfin ID 和 Ticker都是唯一的
# 2. 三个表之间公司无重合
# 

# In[9]:


#display all column names 
df_income_a.columns


# In[10]:


#everything included
df_income_a.shape #(14768, 25)
df_income_a['Ticker'].nunique() #1915 stocks
df_income_a['SimFinId'].nunique() #same as above 


# In[11]:


#看income dataset是否包含banks 和 insurance
intersection = set(df_income_a['SimFinId']) & set(df_income_a_bank['SimFinId'])
intersection #无重合

intersection2 = set(df_income_a['SimFinId']) & set(df_income_a_ins['SimFinId'])
intersection2 #无重合


# In[12]:


#check non-missing value % of income statement
prop_nonmissing(df_income_a).sort_values(by = 'Prop',ascending = False)


# In[13]:


#plot distribution for each column
drop_c =['Ticker','Report Date','SimFinId','Currency','Fiscal Year','Fiscal Period', 'Publish Date' ]
df = df_income_a.drop(drop_c,axis=1)
'''
for i, col in enumerate(df.columns):
    if isinstance(df[col], object):
        tmp = df[col].dropna()
        __ = plt.figure(i)
        _ = sns.distplot(tmp)
        plt.show()
'''


# ## Balance Sheet

# In[14]:


#display all column names 
df_balance_a.columns


# In[15]:


#everything included
df_balance_a.shape #(14768, 29)
df_balance_a['Ticker'].nunique() #1915 stocks
df_balance_a['SimFinId'].nunique() #same as above 


# In[16]:


#看三张表重合度,无重合
intersection = set(df_balance_a['SimFinId']) & set(df_balance_a_bank['SimFinId'])
intersection #无重合

intersection2 = set(df_balance_a['SimFinId']) & set(df_income_a_ins['SimFinId'])
intersection2 #无重合


# In[17]:


#balance sheet
prop_nonmissing(df_balance_a).sort_values(by='Prop',ascending = False)


# ## Cash Flow

# In[18]:


#display all column names 
df_cashflow_a.columns


# In[19]:


#everything included
df_cashflow_a.shape #(14768, 27)
df_cashflow_a['Ticker'].nunique() #1915 stocks
df_cashflow_a['SimFinId'].nunique() #same as above 


# In[20]:


#看三张表重合度,无重合
intersection = set(df_cashflow_a['SimFinId']) & set(df_cashflow_a_bank['SimFinId'])
intersection #无重合

intersection2 = set(df_cashflow_a['SimFinId']) & set(df_cashflow_a_ins['SimFinId'])
intersection2 #无重合


# In[21]:


#cash flow
prop_nonmissing(df_cashflow_a).sort_values(by='Prop', ascending = False)


# 可以drop：Net Extraordinary Gains (Losses)	,Abnormal Gains (Losses), Depreciation， too much missing value and are not useful for calculating financial ratio
# 
# R&D是否需要drop？或许R&D投资高的企业profit margin比较高
# Net extraordinary gain 和 loss或许可以做成categorical variable

# ## Stock Price

# In[22]:


#display all column names
df_prices.columns


# In[23]:


df_prices.shape #(5027050, 10)
df_prices['Ticker'].nunique()#2050 companies


# In[24]:


#check missing values 
prop_nonmissing(df_prices).sort_values(by = 'Prop', ascending = False)


# ## Company&Industry

# In[25]:


#display all column names 
comp.columns
industry.columns


# In[26]:


comp.shape #(2069, 4)
industry.shape #(71,3)
comp['Ticker'].nunique() #2069 stocks
industry['IndustryId'].nunique() #71 industries
industry['Industry'].nunique()#same as above
industry['Sector'].nunique()#12 sector


# In[27]:


#check missing values
prop_nonmissing(comp)
prop_nonmissing(industry)


# In[28]:


intersection3 = set(df_balance_a['SimFinId']) & set(df_income_a['SimFinId'])
len(intersection3) #有income和balance数据的是同一批公司

intersection4 = set(df_balance_a['SimFinId']) & set(df_cashflow_a['SimFinId'])
len(intersection4) #有income和balance数据的是同一批公司


# # Join Data

# In[29]:


comp.head(2)
industry.head(2)


# In[30]:


#left join industry on company
comp['IndustryId'] = comp[['IndustryId']].astype('float')
df = pd.merge(comp, industry, on ='IndustryId', how = 'left',suffixes=('','_right'))
df.head(5)
df.shape


# In[31]:


#left join income statement on previous df 
df2 = pd.merge(df,df_income_a,on = ['Ticker','SimFinId'], how = 'left', suffixes=('','_i'))
df2.head(2)
df2.columns
df_income_a.shape
df2.shape


# In[32]:


#left join balance sheet on previous df 
df_balance_a['Fiscal Year'] = df_balance_a[['Fiscal Year']].astype('float')
df3 = pd.merge(df2,df_balance_a,on = ['Ticker','SimFinId','Fiscal Year','Currency',"Report Date","Publish Date"], how = 'left', suffixes=('','_b'))
#take a look at the merge data
df3.head()
df3.columns
#check if merge successfully, if successful, the row number should not change
df2.shape
df3.shape


# In[33]:


#left join cash flow on previous df 
df_cashflow_a['Fiscal Year'] = df_cashflow_a[['Fiscal Year']].astype('float')
df4 = pd.merge(df3,df_cashflow_a,on = ['Ticker','SimFinId','Fiscal Year','Currency','Report Date','Publish Date'], how = 'left', suffixes=('','_c'))
#take a look at the merge data
df4.head(2)
df4.columns
#check if merge successfully, if successful, the row number should not change
df3.shape
df4.shape


# In[34]:


#the final data frame is df
df = df4.copy()
#check for missing value
temp = prop_nonmissing(df)
temp.sort_values(by = 'Prop',ascending = False)
# 只是存用一下这个code，不用理
#df_merge2 = df_merge2.drop(df_merge2.columns[df_merge2.columns.str.endswith('right')],axis = 1)


# # Calculate Financial Ratio

# lists of useful financial ratios to measure financial health
# liquidity
# 1. \* current ratio： current assets/current liabiity
# 2. \* quick ratio: (cash+marketable+ receivable)/current liabilities
# 3. net working capital to assets ratio: <br>(current asset - current liability)/total assets
# 4. Cash ratio: (cash + marketable securities)/current liabilities 
# 
# solvency(leverage measure)
# 1. long-term debt ratio: long-term debt/(long term debt +equity)
# 2. \* long-term debt-equity ratio: long-term debt/equity. <br>A downward trend over time in the D/E ratio is a good indicator<br> a company is on increasingly solid financial ground.
# 3. total debt ratio: total liabilities /total assets
# 4. times interest earned : EBIT/ interest expense
# 5. cash coverage ratio : EBIT + depreciation/ interest expense
# 
# profitability
# 1. return on asset: after tax operating income/total assets
# 2. return on capital: afer tax operating inomce/(long term debt + equity)
# 3. return on equity: after tax operating icnome/equity
# 4. EVA: after_tax operating icnome - (cost of capital * total capitalization). <br>cost of capital data not available
# operating efficiency
# 
# 1. \* operating profit margin: EBIT/net sales 
# 2. net profit marin: net income/net sales
# 3. asset turover: sales/total assets at start of year
# 4. receivable turover: sales/receivables at the start of year
# 5. inventory turnover: cost of goods sold/inventory at start of year
# 
# performance measures
# 1. Market Value added: market value of equity - book value of equity
# 2. market to book ratio: Market Market Value of equity / book value of equity 
# 3. P/E: Price per share/Earning per share <br>((net income - preferred dividends)/end of year outstanding share)
# 
