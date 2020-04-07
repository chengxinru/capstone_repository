## Clean Share Prices data, calculate stock return

library(dplyr)
library(tidyverse)

#Set up
stock <- read.csv2("simfin_data/us-shareprices-daily.csv")
stock2 <- stock[c(1,2,3,4,7,9)] ## select relative columns
date <- as.Date(stock2$Date)
stock2$Year <- substring(date,1,4) ## extract Year
stock2$Date <- str_remove_all(stock2$Date, "-")
stock2$day <- str_sub(str_remove_all(stock2$Date, "-"), start = 5)
head(stock2)



## fill NAs values in Dividend with 0
stock2$Dividend <- as.numeric(as.character(stock2$Dividend))
stock2$Dividend <- ifelse(is.na(stock2$Dividend),0,stock2$Dividend)

############################## response 1: (P_fiscal_year_end - P_fiscal_year_start + Dividens)/ (P_fiscal_year_start) #################

#calculate total dividends each year
totDiv <- stock2 %>% group_by(Ticker, Year) %>% summarise(totDiv =sum(Dividend)) ##total Dividend within a year



## the beginning and last entries of each Ticker and Year
first_last <- stock2 %>% group_by(Ticker, Year) %>% filter(row_number() %in% c(1, n()))
## https://stackoverflow.com/questions/31528981/select-first-and-last-row-from-grouped-data
first_last$Open <- as.numeric(as.character(first_last$Open))
first_last$Close <- as.numeric(as.character(first_last$Close))


stock_return <- first_last[!duplicated(first_last[c("Ticker","Year")]), c("Ticker","SimFinId","Year")] ## unique Ticker and their SimFinId, years
stock_return <- merge(stock_return, totDiv, by=c("Ticker", "Year")) ## merge annual Dividend

stock_return$Return <- 0

for (i in 1:nrow(stock_return)) {
  thisTicker <- stock_return$Ticker[i]
  thisYear <- stock_return$Year[i]
  open <- as.numeric(first_last[first_last$Ticker==thisTicker & first_last$Year==thisYear, "Open"][1,])
  close <- as.numeric(first_last[first_last$Ticker==thisTicker & first_last$Year==thisYear, "Close"][2,])
  div <- as.numeric(stock_return$totDiv[i])
  stock_return$Return[i] <- (close - open + div) / open
}



###############################Response 2: (P_accounting_year_end - P_accounting_year_start + Dividens)/ (P_accounting_year_start) #######



#get the sum of dividends
stock2$day <- as.integer(stock2$day)
stock2$Year <- as.integer(stock2$Year)
stock2 <- stock2 %>% group_by(Year) %>% mutate(Year.adj = ifelse(day <= 1031, Year, Year+1))
totDiv.adj <- stock2 %>% group_by(Ticker, Year.adj) %>% summarise(totDiv.adj =sum(Dividend)) ##total Dividend within a year


#get the stock price on 10-31 each year
first_last2 <- stock2 %>% group_by(Ticker, Year.adj) %>% filter(row_number() %in% c(1, n()))
first_last2$Open <- as.numeric(as.character(first_last2$Open))
first_last2$Close <- as.numeric(as.character(first_last2$Close))


#calculate stock return 
totDiv.adj$Year.adj <- as.character(totDiv.adj$Year.adj)
stock_return <- left_join(stock_return, totDiv.adj, by=c("Ticker" = "Ticker", "Year" = "Year.adj")) ## merge annual Dividend

stock_return$Return2 <- 0
first_last2$Year.adj <- as.character(first_last2$Year.adj)

for (i in 1:nrow(stock_return)) {
  thisTicker <- stock_return$Ticker[i]
  thisYear <- stock_return$Year[i]
  open <- as.numeric(first_last2[first_last2$Ticker==thisTicker & first_last2$Year.adj==thisYear, "Open"][1,])
  close <- as.numeric(first_last2[first_last2$Ticker==thisTicker & first_last2$Year.adj==thisYear, "Close"][2,])
  div <- as.numeric(stock_return$totDiv.adj[i])
  stock_return$Return2[i] <- (close - open + div) / open
}

####################################response 3: log price difference(accounting year) #####################################



stock_return$Return3 <- 0

for (i in 1:nrow(stock_return)) {
  thisTicker <- stock_return$Ticker[i]
  thisYear <- stock_return$Year[i]
  open <- as.numeric(first_last2[first_last2$Ticker==thisTicker & first_last2$Year.adj==thisYear, "Open"][1,])
  close <- as.numeric(first_last2[first_last2$Ticker==thisTicker & first_last2$Year.adj==thisYear, "Close"][2,])
  div <- as.numeric(stock_return$totDiv.adj[i])
  stock_return$Return3[i] <- (log(close + div) - log(open))
}

####################################response 4: (P_accounting_year_end + Div)/P_accounting_year_start



stock_return$Return4 <- 0

for (i in 1:nrow(stock_return)) {
  thisTicker <- stock_return$Ticker[i]
  thisYear <- stock_return$Year[i]
  open <- as.numeric(first_last2[first_last2$Ticker==thisTicker & first_last2$Year.adj==thisYear, "Open"][1,])
  close <- as.numeric(first_last2[first_last2$Ticker==thisTicker & first_last2$Year.adj==thisYear, "Close"][2,])
  div <- as.numeric(stock_return$totDiv.adj[i])
  stock_return$Return4[i] <- (close + div)/open
}


head(stock_return)
stock_return <- stock_return[c("Ticker","Year", "SimFinId", "Return", "Return2", "Return3", "Return4", )]

write.csv(stock_return, "capstone_repository/data/stock_return.csv")

###############################join data############################################

#write.csv(stock_return[,-4], "capstone_repository/data/Stock Rerturn.csv")
stock_return <- stock_return[order(stock_return$Ticker),]

ratios <- read.csv('capstone_repository/data/financial_ratios.csv')
ratios$Fiscal.Year <- as.integer(ratios$Fiscal.Year)
ratios$Ticker <- as.character(ratios$Ticker)
stock_return$Year <- as.integer(stock_return$Year)
stock_return$Ticker <- as.character(stock_return$Ticker)



ratio_return <- left_join(ratios,na.omit(stock_return[,c("Ticker","Year", "SimFinId", "Return", "Return2", "Return3", "Return4" )]), 
                          by = c("Fiscal.Year" = "Year", "Ticker" = 'Ticker', "SimFinId" = 'SimFinId'))
dim(ratio_return) #10810 34
dim(na.omit(ratio_return)) #10788    34
ratio_return <- na.omit(ratio_return)

names(ratio_return)
# [1] "Ticker"                      "SimFinId"                    "Company.Name"                "IndustryId"                 
# [5] "Sector"                      "Industry"                    "Report.Date"                 "Fiscal.Year"                
# [9] "Current.Ratio"               "Quick.Ratio"                 "NWC.to.Asset.Ratio"          "Cash.Ratio"                 
# [13] "Long.Term.Debt.Ratio"        "Liabilities.to.Equity.Ratio" "Total.Debt.Ratio"            "Debt.to.Asset.Ratio"        
# [17] "Interest.Coverage.Ratio"     "Cash.Coverage.Ratio"         "Return.On.Assets"            "Return.On.Capital"          
# [21] "Return.On.Equity"            "Operating.Profit.Margin"     "Net.Profit.Margin"           "Asset.Turnover"             
# [25] "Receivable.Turnover"         "Close"                       "Book.to.Market.Ratio"        "Earning.Per.Share"          
# [29] "Sales.Per.Share"             "Price.to.Earning.Ratio"      "Return"                      "Return2"                    
# [33] "Return3"                     "Return4"  
# 

write.csv(ratio_return, "capstone_repository/data/ratios_return.csv")


###############################################check dsitribution ###########################

hist(ratio_return$Return)
summary(ratio_return$Return)
#Min.   1st Qu.    Median      Mean   3rd Qu.      Max. 
#-0.9871   -0.1051    0.1041    0.5133    0.3223 2127.0000 

hist(ratio_return$Return2)
summary(ratio_return$Return2)
#Min.   1st Qu.    Median      Mean   3rd Qu.      Max. 
#-0.9833   -0.0680    0.1222    0.3917    0.3424 1176.3333 

hist(ratio_return$Return3)
summary(ratio_return$Return3)
#Min.  1st Qu.   Median     Mean  3rd Qu.     Max. 
#-4.09112 -0.07046  0.11531  0.09478  0.29449  7.07101 

hist(ratio_return$Return4)
summary(ratio_return$Return4)
#Min.   1st Qu.    Median      Mean   3rd Qu.      Max. 
#0.0167    0.9320    1.1222    1.3917    1.3424 1177.3333 

#find outlying observation
ratio_retun[ratio_return$Return == max(ratio_return$Return), c("Ticker", "Fiscal.Year")]
first_last[first_last$Ticker == "ARA" & first_last$Year == "2016",]
# Ticker SimFinId Date      Open Close Dividend Year  day  
# <fct>     <int> <chr>    <dbl> <dbl>    <dbl> <chr> <chr>
#   1 ARA       84598 20160104  0.01  0.01        0 2016  0104 
# 2 ARA       84598 20161230 21.3  21.3         0 2016  1230 

