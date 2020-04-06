df<- read.csv('/Users/xinrucheng/Desktop/capstone/capstone_repository/data/ratios_return.csv')
unique(df['Sector'])
tech=df[df['Sector']=='Technology',]
nrow(tech)/nrow(df) # %19.34%data
tech$Fiscal.Year
myvars <- c('Ticker_x','SimFinId','Report.Date','Fiscal.Year',
            "Current.Ratio", "Quick.Ratio", "Total.Debt.Ratio",'Debt.to.Asset.Ratio',
            'Cash.Coverage.Ratio','Interest.Coverage.Ratio')
tech_sub <- tech[myvars]
#-----------------------------current ratio----------------------------------------
cr<-df['Current.Ratio']
cr_tech<-tech['Current.Ratio']
df_no_real_estate= df[!(df$Sector=="Real Estate" | df$Sector=="Financial Services" ),]
#maximuu current ratio is almost 1000 (real estate)
bar1 <- ggplot(df_no_real_estate, aes(x=Sector, y=Current.Ratio))
bar1 + geom_boxplot()  #identity take the exact value
df[order(cr),]['Sector']
#real estate, healthcare and financial service has extremely high current ratio
d <- density(df$Current.Ratio) # returns the density data
plot(d)
d2 <- density(log(df$Current.Ratio)) # returns the density data
plot(d2)
d3 <- density(log(tech$Current.Ratio)) # returns the density data
plot(d3) #while only using tech data --> can have better distribution
# log transformation!

tech_sub['Current.Ratio.T']<-log (tech_sub['Current.Ratio'])


#----------------------------#Quick.Ratio--------------------------
qr<-df['Quick.Ratio']
qr_tech<-tech['Quick.Ratio']
bar1 <- ggplot(df_no_real_estate, aes(x=Sector, y=Quick.Ratio))
bar1 + geom_boxplot()  #financial service has high debt ratio
df[order(qr),]['Sector'] 
#Real estate, financial services and consumer cyclical have high quick ratio
d <- density(df$Quick.Ratio) # returns the density data
plot(d) #extremely skewed
d2 <- density(log(df$Quick.Ratio)) # returns the density data
plot(d2) #normal distribution with long tail 
d3 <- density(tech$Quick.Ratio) # returns the density data
plot(d3) #while only using tech data --> right skewed, shorter tail
d4 <- density(log(tech$Quick.Ratio)) # returns the density data
plot(d4) #while only using log tech data -->normal dist, shorter tail 


# log transformation!
tech_sub['Quick.Ratio.T']<-log (tech_sub['Quick.Ratio'])
#-----------------------Total.Debt.Ratio------------------
td<-df['Total.Debt.Ratio']
td_tech<-tech['Total.Debt.Ratio']
df_no_fin= df[!( df$Sector=="Financial Services" ),]
df_no_fin_he= df[!( df$Sector=="Financial Services" |df$Sector=="Healthcare" ),]
bar1 <- ggplot(df, aes(x=Sector, y=Total.Debt.Ratio))
bar1 + geom_boxplot()  #financial service has high debt ratio
bar2 <- ggplot(df_no_fin, aes(x=Sector, y=Total.Debt.Ratio))
bar2 + geom_boxplot()  #healthcare has high debt ratio
bar3 <- ggplot(df_no_fin_he, aes(x=Sector, y=Total.Debt.Ratio))
bar3 + geom_boxplot() 
df[order(td),]['Sector'] #financial service,and healthcare have very high debt ratio
d <- density(df$Total.Debt.Ratio)
plot(d) #extremely skewed
d2 <- density(log(df$Total.Debt.Ratio)) 
plot(d2) #normal distribution with long tail 
d3 <- density(tech$Total.Debt.Ratio) # returns the density data
plot(d3) #while only using tech data --> right skewed, shorter tail
#d4 <- density(log(tech$Total.Debt.Ratio)) # returns the density data
#plot(d4) #while only using log tech data -->normal dist, shorter tail

# original data is already normal, no need to do any additiona transformation
tech_sub['Total.Debt.Ratio.T']<-log (tech_sub['Total.Debt.Ratio']) 
#they are the same
#-----------------------Debt.to.Asset.Ratio--------------------
da<-df['Debt.to.Asset.Ratio']
td_tech<-tech['Debt.to.Asset.Ratio']
tech[order(tech$Debt.to.Asset.Ratio,decreasing = TRUE),]['Debt.to.Asset.Ratio']
eliminated_pre<-subset(tech, tech$Debt.to.Asset.Ratio<100)
deleted_companies<-subset(tech, tech$Debt.to.Asset.Ratio>100) 
index <- tech_sub$Debt.to.Asset.Ratio >100
#Delete Mark -2011-12/31/11
tech_sub$Debt.to.Asset.Ratio.T[index]<-NA
tech_sub[tech_sub$SimFinId==652365 & tech_sub$Fiscal.Year==2011,]
tech[order(tech$Debt.to.Asset.Ratio),]['Debt.to.Asset.Ratio']
eliminated<-subset(eliminated_pre, eliminated_pre$Debt.to.Asset.Ratio!=0)
deleted_companies2<-subset(tech, eliminated_pre$Debt.to.Asset.Ratio==0) 
# delete 44 rows with 0 values in debt to asset ratio
d <- density(df$Debt.to.Asset.Ratio)
plot(d) #super skewed
d2 <- density(log(tech$Debt.to.Asset.Ratio)) 
plot(d2) #normal distribution with super long tail 
d3 <- density(eliminated$Debt.to.Asset.Ratio) # returns the density data
plot(d3) #while only using tech data --> right skewed, shorter tail
d4 <- density(log(eliminated$Debt.to.Asset.Ratio)) # returns the density data
plot(d4) #while only using log tech data -->normal dist, shorter tail

index <- tech_sub$Debt.to.Asset.Ratio >100 | tech_sub$Debt.to.Asset.Ratio ==0
tech_sub$Debt.to.Asset.Ratio.T<-log(tech_sub$Debt.to.Asset.Ratio)
tech_sub$Debt.to.Asset.Ratio.T[index]<-NA
tech_sub[tech_sub$SimFinId==111052 & tech_sub$Fiscal.Year==2012,] 
# check whether it has been transfomred to na


# after deleted 45 companies (Debt.to.Asset.Ratio=0 / >100), do log transformation !

#-----------------------Cash.Coverage.Ratio---------------
tech[order(tech$Cash.Coverage.Ratio,decreasing = TRUE),]['Cash.Coverage.Ratio']
tech[order(tech$Cash.Coverage.Ratio),]['Cash.Coverage.Ratio']
eliminated<-subset(tech, tech$Cash.Coverage.Ratio<5000 &tech$Cash.Coverage.Ratio>-1000) 
deleted_companies2<-subset(tech, tech$Cash.Coverage.Ratio>5000|tech$Cash.Coverage.Ratio<-1000) 
#delete four companies with the highest cash coverage ratio - 
#FSLR (124817.167),IPGP（220683.000),KE (29722.000), LOGM(4265.765)
# add the absolute value of min 
Cash.Coverage.Ratio_N_E<-eliminated$Cash.Coverage.Ratio+abs(min(eliminated$Cash.Coverage.Ratio))+1
d5 <- density(log(Cash.Coverage.Ratio_N_E)) 
plot(d5) 
#plot(density(Cash.Coverage.Ratio_N_E))
#does not follow normal distribution, not required for linear regression 
#range is 0~9.19, acceptable 
#it is ok to transform data that are orignal negative to positive, becasue negative data simply means
#that certain company has low cash coverage ratio, its operation income cannot cover the interest expense 

#delete FSLR-12/31/10, IPGP-12/31/13 ,KE-6/30/16, LOGM-12/31/17 (Cash.Coverage.Ratio>5000)
#then do log transofrmation on all other data

index <- (tech$Cash.Coverage.Ratio>5000)|(tech$Cash.Coverage.Ratio<(-1000))
eliminated<-subset(tech_sub, tech_sub$Cash.Coverage.Ratio<5000 &tech_sub$Cash.Coverage.Ratio>-1000) 
#Cash.Coverage.Ratio_N_E<-tech_sub$Cash.Coverage.Ratio+abs(min(eliminated$Cash.Coverage.Ratio))+1
tech_sub$Cash.Coverage.Ratio.T<-log(tech_sub$Cash.Coverage.Ratio+abs(min(eliminated$Cash.Coverage.Ratio))+1)
tech_sub$Cash.Coverage.Ratio.T[index]<-NA
#sum(is.na(tech_sub$Cash.Coverage.Ratio.T))


#-----------------------Interest.Coverage.Ratio--------------------------
d <- density(tech$Interest.Coverage.Ratio)
plot(d) #super skewed
tech[order(tech$Interest.Coverage.Ratio,decreasing = TRUE),]['Interest.Coverage.Ratio']
deleted_companies1<-subset(tech, tech$Interest.Coverage.Ratio>4000) 
#delete four companies with the highest cash coverage ratio - 
#FSLR (156598.26),IPGP（256336.25),KE (53720), LOGM(15155.78), same as the previous one since two ratios are connected
tech$Interest.Coverage.Ratio_N<-tech$Interest.Coverage.Ratio+abs(min(tech$Interest.Coverage.Ratio))+1
Interest.Coverage.Ratio_N_E<-eliminated$Interest.Coverage.Ratio+abs(eliminated$Interest.Coverage.Ratio)+1
d4 <- density(log(tech$Interest.Coverage.Ratio_N))
plot(d4) #heavy tail
d5 <- density(log(Interest.Coverage.Ratio_N_E)) 
plot(d5) 

#the deleted rows are stored as deleted_companies2 
#delete FSLR-12/31/10, IPGP-12/31/13 ,KE-6/30/16, LOGM-12/31/17 (Cash.Coverage.Ratio>5000)
#then do log transofrmation on all other data

tech_sub$Interest.Coverage.Ratio.T<-log(tech_sub$Interest.Coverage.Ratio+abs(min(eliminated$Interest.Coverage.Ratio))+1)
tech_sub$Interest.Coverage.Ratio.T[index]<-NA
tech_sub
write.csv(tech_sub, "/Users/xinrucheng/Desktop/capstone/capstone_repository/data/ratios_transformed.csv")
