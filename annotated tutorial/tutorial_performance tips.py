# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 22:10:32 2020

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

#--------------------------Load dataframe-----------------------------
df_prices = sf.load_shareprices(variant='daily', market='us')

#--------------------------Add Columns-----------------------------
#simple way
df2 = pd.DataFrame()
df2[FOO] = df_prices[CLOSE] / df_prices[ADJ_CLOSE]
df2[BAR] = df_prices[CLOSE] * df_prices[ADJ_CLOSE]
df2[QUX] = df_prices[CLOSE] * df_prices[VOLUME]

#much faster to add new columns to the DataFrame  if index match 
df3 = pd.DataFrame(index=df_prices.index)
df3[FOO] = df_prices[CLOSE] / df_prices[ADJ_CLOSE]
df3[BAR] = df_prices[CLOSE] * df_prices[ADJ_CLOSE]
df3[QUX] = df_prices[CLOSE] * df_prices[VOLUME]

#another way: use dict
df_foo = df_prices[CLOSE] / df_prices[ADJ_CLOSE]
df_bar = df_prices[CLOSE] * df_prices[ADJ_CLOSE]
df_qux = df_prices[CLOSE] * df_prices[VOLUME]
data = {FOO: df_foo, BAR: df_bar, QUX: df_qux}
df5 = pd.DataFrame(data=data)

#Caching Your Own Functions
#略






