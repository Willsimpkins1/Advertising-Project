from distutils.command import clean
import numpy as np
import pandas as pd
dfa = pd.read_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\client_a_data_work.xlsx')
testdata=dfa[:100]
sales_rate_multipliers=dfa.loc[:,'sales_rate_multiplier']
num_companies=dfa.loc[:,'num_companies']
###################################################################
#Setting Constants
#Depreciation of advert effectivness
r=0.9
#Number of adverts available
M=1000000
###################################################################    
#Writing a function to remove data with a zero as the sales multiplier
def data_clean(sales_rate_multipliers,num_companies):
    true_sales_rate=sales_rate_multipliers*num_companies
    clean_sales_rate=np.array([])
    index_sales_rate=np.array([],dtype=int)
    for i in range(len(num_companies)):
        if true_sales_rate[i]!=0:
            clean_sales_rate=np.append(clean_sales_rate,true_sales_rate[i])
            index_sales_rate=np.append(index_sales_rate,int(i))
    a=-1/np.log(r)
    k=1
    l=0
    new_clean_data = clean_sales_rate
    while k>0:
        l=l+1
        b=M/len(new_clean_data)+(1/(len(new_clean_data)*np.log(r)))*np.sum(np.log(new_clean_data))
        new_new_clean_data = np.array([])
        for i in range(len(new_clean_data)):
            if new_clean_data[i]>=np.exp(-b/a):
                new_new_clean_data=np.append(new_new_clean_data,new_clean_data[i])
        k=len(new_clean_data)-len(new_new_clean_data)
        new_clean_data=new_new_clean_data
        if l>100:
            break
    new_index=np.zeros(len(new_clean_data))
    print(np.where(true_sales_rate==new_clean_data[291]))
    k=0
    for i in range(len(new_clean_data)):
        n=len(np.where(true_sales_rate==new_clean_data[i])[0])
        print(np.where(true_sales_rate==new_clean_data[i])[0])
        print(np.where(true_sales_rate==new_clean_data[i])[0][k])
        print(k)
        print(n)
        new_index[i]=np.where(true_sales_rate==new_clean_data[i])[0][k]
        k=k+1
        if k==n:
            k=0
    new_index=np.array(new_index,dtype=int)
    return new_clean_data, new_index
#Now using my formulas to find the optimum number of adverts for each location
def Optimum_adverts_fun(sales_rate_multiplier,num_companies,r,M):
    clean_sales_rate, index_sales_rate=data_clean(sales_rate_multiplier,num_companies)
    log_sales_rate = np.log(clean_sales_rate)
    N=len(clean_sales_rate)
    a=-1/np.log(r)
    b=M/N-(a/N)*np.sum(log_sales_rate)
    Optimum_ads_num=np.zeros(N)
    Optimum_ads_num=b+a*log_sales_rate
    total_profit=(1/(1-r))*np.sum(clean_sales_rate)-((N*r**b)/(1-r))
    return Optimum_ads_num, index_sales_rate, total_profit
#And now one to get the indexs back to the whole data set
def allocate_advert_num(sales_rate_multiplier,num_companies,r,M):
    Optimum_ads_num, index_sales_rate, total_profit = Optimum_adverts_fun(sales_rate_multiplier,num_companies,r,M)
    Optimum_ads_round=np.round(Optimum_ads_num)
    advert_num=np.zeros(len(num_companies))
    print(Optimum_ads_round)
    for i in range(len(index_sales_rate)):
        advert_num[index_sales_rate[i]]=int(Optimum_ads_round[i])
    return advert_num, total_profit
advert_num, index_sales_rate, total_profit = Optimum_adverts_fun(sales_rate_multipliers,num_companies,r,M)
a=np.where(index_sales_rate==298)
print(index_sales_rate[280:300])
print(a)
print(advert_num[a])
#Now we return our data to a data frame in order to pass it back into a spreadsheet
def Make_df(sales_rate_multipliers,num_companies,r,M):
    true_sales_rate=sales_rate_multipliers*num_companies
    advert_num, total_profit = allocate_advert_num(sales_rate_multipliers,num_companies,r,M)
    df = pd.DataFrame({'Sales Rate Multipliers':sales_rate_multipliers,'Number of Companies':num_companies,'True Sales Rate':true_sales_rate,'Optimum Number Of Adverts':advert_num})
    return df, total_profit
#Now we export the data back into a spread sheet
df, total_profit = Make_df(sales_rate_multipliers,num_companies,r,M)
df.to_excel('./datafinal.xlsx')



