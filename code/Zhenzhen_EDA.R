library(YaleToolkit)
## load industies
industry <- read.csv2("industries.csv")
names(industry)  ## "IndustryId" "Sector"     "Industry"
whatis(industry)

## load companies
co <- read.csv2("us-companies.csv")
names(co)  ## "Ticker"       "SimFinId"     "Company.Name" "IndustryId"
whatis(co) ## IndustryID has 183 missing values

## merge with "industry" by colum "IndustryID"
co_ind <- merge(industry,co)  ## 1887 companies, 71 industries, 12 sectors, 
whatis(co_ind)

## load cash flow
cf <- read.csv2("us-cashflow-annual.csv")
cf.sfID <- unique(cf$SimFinId)
## merge w/ companies
df1 <- merge(co_ind, cf) ## 1823 observations
whatis(df1)


####-----------------------------------------------------#####

## merge with cashflow_i by Ticker
insurance_CF <- merge(co_ind, cashflow_i) ## 1035 observations
whatis(insurance_CF)


## load cash flow (BANK) statement
cashflow_b <- read.csv2("us-cashflow-banks-quarterly.csv")
columns <- names(cashflow_b)
whatis(cashflow_b)
b.sfID <- unique(cashflow_b$SimFinId)
length(b.sfID[b.sfID %ni% cf.sfID]) ## 65 = length(b.sfID) So, the three data sets are separate

## load  cash flow (INSURANCE) statement
cashflow_i <- read.csv2("us-cashflow-insurance-quarterly.csv")
columns <- names(cashflow_i)
whatis(cashflow_i)



##merge co_ind with cashflow_b by Ticker
banks_CF <- merge(co_ind, cashflow_b) ## 1823 observations
whatis(banks_CF)

## merge co_ind with cashflow_i by Ticker
insurance_CF <- merge(co_ind, cashflow_i) ## 1035 observations
whatis(insurance_CF)

## inconsistant columns
'%ni%' <- Negate('%in%')
names(banks_CF)[names(banks_CF) %ni% names(insurance_CF)]

##"Provision.for.Loan.Losses"                 "Change.in.Working.Capital"                
##"Net.Cash.from.Operating.Activities"        "Net.Change.in.Loans...Interbank"          
##"Net.Cash.from.Acquisitions...Divestitures"

names(insurance_CF)[names(insurance_CF) %ni% names(banks_CF)]
##"Net.Change.in.Investments"

## load stock prices
stock <- read.csv2("us-shareprices-daily.csv")
