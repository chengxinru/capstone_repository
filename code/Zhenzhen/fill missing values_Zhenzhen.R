## missing value imputation
## Zhenzhen Zhu
## missing value imputations for Shares (Diluted), Revenue, Net Income Tax,
## Inventories, Long Term Debt
## Citation: http://r-statistics.co/Missing-Value-Treatment-With-R.html

setwd("/Users/zhenzhenzhu/Documents/capstone/capstone_repository/code/")
# Installing and Loading the VIM package
# install.packages("VIM", dependencies = TRUE)
library(VIM)
library(YaleToolkit)
library(dplyr)

df <- read.csv("df.csv", header=T)
sort(unique(df$Sector))
#table((df$Sector == "Technology" && df[is.na(df["Inventories"])), "Industry"])
df1 <- df[,9:34] ## continuous variables


allcol <- read.csv("allColumns.csv", header=T)
allcol$Dividends.Paid[is.na(allcol$Dividends.Paid)] <- 0 ## fill Dividends
allcol <- allcol[,12:76] ## continuous variables
#sapply(allcol, class)
allcol[which(sapply(allcol, class)!="numeric")] <- NULL ## remove non-numeric columns
#head(allcol)
complete <- allcol[, sapply(allcol, Negate(anyNA)), drop = FALSE] ## drop NAs
complete_col <- colnames(complete) ## columns with complete data
##"Pretax.Income..Loss...Adj."               "Pretax.Income..Loss."                    
## "Income..Loss..from.Continuing.Operations" "Net.Income"                              
## "Net.Income..Common."                      "Total.Assets"                            
## "Total.Current.Liabilities"                "Total.Liabilities"                       
## "Total.Liabilities...Equity"               "Net.Cash.from.Operating.Activities"      
## "Dividends.Paid"                           "Net.Change.in.Cash" 


cor(cbind(complete, df1$Shares..Diluted.), use = "complete.obs")
## Net.Cash.from.Operating.Activities                  0.7217558
## Dividends.Paid                                     -0.7297841

cor(cbind(complete, df1$Revenue), use = "complete.obs")
## Net.Cash.from.Operating.Activities                        0.7682531
## Pretax.Income..Loss...Adj.                                0.7499257
## Total.Assets                              0.73912847
## Total.Liabilities...Equity                0.73912846
## Pretax.Income..Loss.                      0.72262466

cor(cbind(complete, df1$Income.Tax..Expense..Benefit..Net), use = "complete.obs")
## Pretax.Income..Loss.                                                -0.8339238
## Pretax.Income..Loss...Adj.                                          -0.8306114
## Net.Cash.from.Operating.Activities                                  -0.7004053

cor(cbind(complete, df1$Inventories), use = "complete.obs")
## Total.Current.Liabilities                      0.6351009
## Total.Liabilities                              0.5721773

cor(cbind(complete, df1$Long.Term.Debt), use = "complete.obs")
## Total.Liabilities                                0.86829503
## Total.Liabilities...Equity                       0.81131231
## Total.Assets                                     0.81131229

## regression ##
################
ltd_reg <- 
  regressionImp(Long.Term.Debt~Total.Liabilities+Total.Liabilities...Equity+Total.Assets,
                data=allcol)

#head(ltd_reg)
#sum(is.na(ltd_reg$Long.Term.Debt)) ## 0 

it.reg<- regressionImp(Income.Tax..Expense..Benefit..Net~Pretax.Income..Loss.+ 
                              Pretax.Income..Loss...Adj. + Net.Cash.from.Operating.Activities,
                       data=allcol)

sd.reg <- regressionImp(Shares..Diluted.~Net.Cash.from.Operating.Activities+Dividends.Paid,
                        data=allcol)

rev.reg <- regressionImp(Revenue~Net.Cash.from.Operating.Activities+Pretax.Income..Loss...Adj.+
                               Total.Assets+Total.Liabilities...Equity+Pretax.Income..Loss.,
                         data=allcol)

inv.reg <- regressionImp(Inventories~Total.Current.Liabilities+Total.Liabilities ,
                         data=allcol)

imputed <- data.frame(ltd_reg$Long.Term.Debt, it.reg$Income.Tax..Expense..Benefit..Net,  
                      sd.reg$Shares..Diluted., rev.reg$Revenue, inv.reg$Inventories)
colnames(imputed) <- c("Long Term Debt", "Income Tax (Expense) Benefit, Net", "Shares (Diluted)",
                       "Revenue", "Inventories")
imputed2 <-cbind(df[,1:8], imputed)
#head(imputed2)
write.csv(imputed2, "Zhenzhen imputed columns.csv")



############################ Below is just testing code, no need to be put in the official script! ######################
## KNN ##
#########
library(DMwR) ## for KNN
knn.imp <- knnImputation(allcol[, -which(names(allcol) %in% complete_col)]) ## 14 minutes


ltd <- as.data.frame(cbind(complete$Total.Liabilities, complete$Total.Liabilities...Equity, 
                           complete$Total.Assets, df1$Long.Term.Debt))
colnames(ltd) <- c("Total.Liabilities", "Total.Liabilities...Equity", "Total.Assets", "Long.Term.Debt")
plot(Total.Liabilities ~ Long.Term.Debt, data = ltd)


### test accuracy on induced missing values ###
###############################################
set.seed(100)
## Long term Debt
# non-missing/complete data frame
nonmissing <- allcol[!is.na(allcol$Long.Term.Debt), ]
original <- nonmissing
# artificially drop some data values
nonmissing[sample(1:nrow(nonmissing), 1000), "Long.Term.Debt"] <- NA
# regression
regtest.ltd <- 
  regressionImp(Long.Term.Debt~Total.Liabilities+Total.Liabilities...Equity+Total.Assets,
                data=nonmissing)
# knn
knntest.ltd <- knnImputation(nonmissing[, -which(names(nonmissing) %in% complete_col)])
# MSE
actuals <- original$Long.Term.Debt[is.na(nonmissing$Long.Term.Debt)]
predicteds <- regtest.ltd[regtest.ltd$Long.Term.Debt_imp, "Long.Term.Debt"]
regr.eval(actuals, predicteds) #2.194048e+19

predicteds2 <- knntest.ltd[regtest.ltd$Long.Term.Debt_imp, "Long.Term.Debt"]
regr.eval(actuals, predicteds2) #8.361698e+19

## Income Tax, Net 
nonmissing <- allcol[!is.na(allcol$Income.Tax..Expense..Benefit..Net), ]
original <- nonmissing
nonmissing[sample(1:nrow(nonmissing), 1000), "Income.Tax..Expense..Benefit..Net"] <- NA
regtest.it <- regressionImp(Income.Tax..Expense..Benefit..Net~Pretax.Income..Loss.+ 
                              Pretax.Income..Loss...Adj. + Net.Cash.from.Operating.Activities,
                            data=nonmissing)
knntest.it <- knnImputation(nonmissing[, -which(names(nonmissing) %in% complete_col)])
# MSE
actuals <- original$Income.Tax..Expense..Benefit..Net[is.na(nonmissing$Income.Tax..Expense..Benefit..Net)]
predicteds <- regtest.it[regtest.it$Income.Tax..Expense..Benefit..Net_imp, "Income.Tax..Expense..Benefit..Net"]
regr.eval(actuals, predicteds) #6.125550e+17

predicteds2 <- knntest.it[regtest.it$Income.Tax..Expense..Benefit..Net_imp, "Income.Tax..Expense..Benefit..Net"]
regr.eval(actuals, predicteds2) #1.190469e+18

## Shares (Diluted)
nonmissing <- allcol[!is.na(allcol$Shares..Diluted.), ]
original <- nonmissing
nonmissing[sample(1:nrow(nonmissing), 1000), "Shares..Diluted."] <- NA
regtest.sd <- regressionImp(Shares..Diluted.~Net.Cash.from.Operating.Activities+Dividends.Paid,
                            data=nonmissing)
knntest.sd <- knnImputation(nonmissing[, -which(names(nonmissing) %in% complete_col)])
# MSE
actuals <- original$Shares..Diluted.[is.na(nonmissing$Shares..Diluted.)]
predicteds <- regtest.sd[regtest.sd$Shares..Diluted._imp, "Shares..Diluted."]
regr.eval(actuals, predicteds) #1.069906e+17

predicteds2 <- knntest.sd[is.na(nonmissing$Shares..Diluted.), "Shares..Diluted."]
regr.eval(actuals, predicteds2) #2.566889e+17

## Revenue
nonmissing <- allcol[!is.na(allcol$Revenue), ]
original <- nonmissing
nonmissing[sample(1:nrow(nonmissing), 1000), "Revenue"] <- NA
regtest.rev <- regressionImp(Revenue~Net.Cash.from.Operating.Activities+Pretax.Income..Loss...Adj.+
                               Total.Assets+Total.Liabilities...Equity+Pretax.Income..Loss.,
                            data=nonmissing)
knntest.rev <- knnImputation(nonmissing[, -which(names(nonmissing) %in% complete_col)])
# MSE
actuals <- original$Revenue[is.na(nonmissing$Revenue)]
predicteds <- regtest.rev[regtest.rev$Revenue_imp, "Revenue"]
regr.eval(actuals, predicteds) #1.694817e+20

predicteds2 <- knntest.rev[is.na(nonmissing$Revenue), "Revenue"]
regr.eval(actuals, predicteds2) #2.711137e+20

## Inventories
nonmissing <- allcol[!is.na(allcol$Inventories), ]
original <- nonmissing
nonmissing[sample(1:nrow(nonmissing), 1000), "Inventories"] <- NA
regtest.inv <- regressionImp(Inventories~Total.Current.Liabilities+Total.Liabilities ,
                             data=nonmissing)
knntest.inv <- knnImputation(nonmissing[, -which(names(nonmissing) %in% complete_col)])
# MSE
actuals <- original$Inventories[is.na(nonmissing$Inventories)]
predicteds <- regtest.inv[regtest.inv$Inventories_imp, "Inventories"]
regr.eval(actuals, predicteds) #2.154893e+18

predicteds2 <- knntest.inv[is.na(nonmissing$Inventories), "Inventories"]
regr.eval(actuals, predicteds2) #1.588233e+19


## regression ##
################