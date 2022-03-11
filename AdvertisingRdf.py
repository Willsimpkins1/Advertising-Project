import numpy as np
import pandas as pd
dfr = pd.read_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\client_a_data_workr.xlsx')
###################################################################
#Number of adverts available
M=1000000
###################################################################   
dfr["True Sales Rate"] = dfr["num_companies"]*dfr["sales_rate_multiplier"]
def aibi(x,r,M):
    a=1/np.log(r)
    delta=(r-1)*a
    A=np.sum(a)
    C=(1/A)*(M+np.sum(a*np.log(x/delta)))
    b=a*(np.log(delta)+C)
    return b, a
def data_clean(df):
    for index, row in df.iterrows():
        if row["True Sales Rate"]==0:
            df.drop(index, inplace=True)
    l=0
    b, a = aibi(df.loc[:,"True Sales Rate"],df.loc[:,"r"],M)
    while np.any(df.loc[:,"True Sales Rate"]<np.exp(b/a)):
        for index, row in df.iterrows():
            if row["True Sales Rate"]<np.exp(b[index]/a[index]):
                df.drop(index, inplace=True)
        b, a = aibi(df.loc[:,"True Sales Rate"],df.loc[:,"r"],M)
        l=l+1
        if l==1000:
            break
    return df
dfin=data_clean(dfr)
dfin.to_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\datacleanfinalR.xlsx', index=False)

def Optimum_ads_func(df):
    df = data_clean(df)
    b, a = aibi(df.loc[:,"True Sales Rate"],df.loc[:,"r"],M)
    df["Optimum_Ads_Num"]=np.floor(b-a*np.log(df.loc[:,"True Sales Rate"]))
    return df
def excess_ads(df,M):
    df = Optimum_ads_func(df)
    diff = int(M-np.sum(df["Optimum_Ads_Num"]))
    df["excess_col"]=df["True Sales Rate"]*df["r"]**df["Optimum_Ads_Num"]
    df.sort_values(by=["excess_col"],ascending=False)
    df["Optimum_Ads_Num"]=df["Optimum_Ads_Num"]+np.append(np.ones(diff),np.zeros(len(df["Optimum_Ads_Num"])-diff))
    df.sort_index()
    df.drop("excess_col", axis=1, inplace=True)
    return df
def present_df(dfa,M):
    dfin = excess_ads(dfa,M)
    dfin["Profit From Loc"]=(1/(1-dfin["r"]))*dfin["True Sales Rate"]*(1-dfin["r"]**dfin["Optimum_Ads_um"])
    dforigional = pd.read_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\client_a_data_workr.xlsx')
    dforigional["True Sales Rate"] = dforigional["sales_rate_multiplier"]*dforigional["num_companies"]
    dforigional["Optimum_Ads_Num"] = np.zeros(len(dforigional["num_companies"]))
    dforigional["Profit From Loc"] = np.zeros(len(dforigional["num_companies"]))
    dfinal = pd.concat([dfin,dforigional]).sort_values('Optimum_Ads_Num',ascending=False).drop_duplicates('Unnamed: 0')
    dfinal = dfinal.sort_index()
    for i in range(len(dfinal["Optimum_Ads_Num"])):
        dfinal["Profit From Loc"][i] = "£{:,.2f}".format(dfinal.loc[i,"Profit From Loc"])
    dfinal.rename(columns={'Unnamed: 0': 'Location Number', 'sales_rate_multiplier': 'Sales Rates','num_companies':'Number Of Companies','r':'Retention Value','Optimum_Ads_Num':'Optimum Number Of Ads','Profit From Loc':'Expected Profits'}, inplace=True)
    dfinal = dfinal[["Location Number","Sales Rates","Number Of Companies","Retention Value","True Sales Rate","Optimum Number Of Ads","Expected Profits"]]
    return dfinal
dfinal = present_df(dfr,M)
print(dfinal)
print(np.sum(dfinal["Optimum Number Of Ads"]))
dfinal.to_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\datafinalR.xlsx', index=False)
