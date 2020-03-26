## Clean Share Prices data, calculate stock return

setwd("/Users/zhenzhenzhu/Documents/capstone/")
library(dplyr)


stock <- read.csv2("us-shareprices-daily.csv")
stock2 <- stock[c(1,2,3,4,7,9)] ## select relative columns
date <- as.Date(stock2$Date)
stock2$Year <- substring(date,1,4) ## extract Year
stock2$Dividend <- as.numeric(as.character(stock2$Dividend))
stock2$Dividend <- ifelse(is.na(stock2$Dividend),0,stock2$Dividend)
## fill NAs values in Dividend with 0

totDiv <- stock2 %>% group_by(Ticker, Year) %>% summarise(totDiv =sum(Dividend)) ##total Dividend within a year

## the beginning and last entries of each Ticker and Year
first_last <- stock2 %>% group_by(Ticker, Year) %>% filter(row_number() %in% c(1, n()))
## https://stackoverflow.com/questions/31528981/select-first-and-last-row-from-grouped-data
first_last$Open <- as.numeric(as.character(first_last$Open))
first_last$Close <- as.numeric(as.character(first_last$Close))


stock_return <- first_last[!duplicated(first_last[c(1,7)]), c(1,2,7)] ## unique Ticker and their SimFinId, years
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

stock_return <- stock_return[order(stock_return$Ticker),]

write.csv(stock_return[,-4], "Stock Rerturn.csv")


