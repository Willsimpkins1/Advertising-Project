from cmath import inf
from distutils.command import clean
import numpy as np
import pandas as pd
dfa = pd.read_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\client_a_data_work.xlsx')
###################################################################
#Setting Constants
#Depreciation of advert effectivness
r=0.9
#Number of adverts available
M=1000000
###################################################################    
#Writing a function to remove data with a zero as the sales multiplier
dfa["True Sales Rate"] = dfa["num_companies"]*dfa["sales_rate_multiplier"]
def data_clean(dfa,M):
    """ Algorithm for removing data points with zero sales rate or which give negative optimum advert numbers

    Parameters
    ----------
    dfa : data frame
        data frame of data points in our problem, read from a excel file

    M : int 
        total amount of adverts in our problem

    Returns
    -------
    dfa : data frame
        cleaned data frame with data points removed
    """

    #Turning our sales rates into an array
    arr=dfa["True Sales Rate"]

    #Setting Constants for our problem
    a, N = -1/np.log(r), len(dfa["sales_rate_multiplier"])
    b = M/N + (1/(N*np.log(r))) * np.sum(np.log(arr[arr!=0]))
    
    #Creating a brake condition in case the code gets stuck in the while loop
    l=0

    #looping over the condition that no more data has to be removed 
    while np.any((np.array(dfa.loc[:,"True Sales Rate"])) < np.exp(-b/a)) == True:

        l = l+1

        #Looping over our data points and removing ones which return a negative number of adverts 
        for index, row in dfa.iterrows():

            if row["True Sales Rate"]<np.exp(-b/a):

                dfa.drop(index, inplace=True)

        #Setting new constants for our data set
        N = len(dfa["True Sales Rate"])
        b = M/N + (1/(N*np.log(r))) * np.sum(np.log(dfa["True Sales Rate"]))

        #Implimenting our break condition after 100 iterations
        if l>100:
            break

    return dfa

def Optimum_adverts_fun(dfa,M):
    """ Algorithm for computing the optimum real number amount of adverts at each location, then rounding it down

    Parameters
    ----------
    dfa : data frame
        data frame of data points in our problem, read from a excel file

    M : int 
        total amount of adverts in our problem

    Returns
    -------
    dfnew : data frame
        data frame with extra column with optimum number of ads
    """

    #First we clean our data set to remove data points we dont want
    dfnew = data_clean(dfa,M)

    #Then we compute the natural log of our data 
    log_sales_rate = np.log(dfnew.loc[:,"True Sales Rate"])

    #Then we set the constants we need to compute the optimum number of adverts
    N = len(log_sales_rate)
    a = - 1 / np.log(r)
    b = M/N - (a/N) * np.sum(log_sales_rate)

    #Now we create a new column in our data set with the optimum number of adverts and round this number down for each value
    dfnew["Optimum_ads_num"] = np.floor(b+a*log_sales_rate)

    return dfnew


def Extra_ads(dfa,M):
    """ Algorithm for assigning the extra adverts left over after rounding

    Parameters
    ----------
    dfa : data frame
        data frame of data points in our problem, read from a excel file

    M : int 
        total amount of adverts in our problem

    Returns
    -------
    dfnew : data frame
        data frame with rounded number of adverts
    """

    #First we find the rounded number of optimum adverts
    dfnew = Optimum_adverts_fun(dfa,M)

    #Then we find the difference between this and the total number of ads we have to assign
    diff = int(M-np.sum(dfnew["Optimum_ads_num"]))

    #Then we create a column witht the scaled sales rate after assigning the adverts
    dfnew["excess_col"] = dfnew["True Sales Rate"] * r ** dfnew["Optimum_ads_num"]

    #then sort this column highest to lowest
    dfnew.sort_values(by=["excess_col"],ascending=False)

    #Then we add to this an array with ones in the first M_e positions and zeros after
    dfnew["Optimum_ads_num"]=dfnew["Optimum_ads_num"]+np.append(np.ones(diff),np.zeros(len(dfnew["Optimum_ads_num"])-diff))

    #Then we sort our data set and drop the excess column
    dfnew.sort_index()
    dfnew.drop("excess_col", axis=1, inplace=True)

    return dfnew


def present_df(dfa,M):
    """ Algorithm for turning our data frame into a more readable form, with an extra column for the profit

    Parameters
    ----------
    dfa : data frame
        data frame of data points in our problem, read from a excel file

    M : int 
        total amount of adverts in our problem

    Returns
    -------
    dfinal : data frame
        completed data frame ready to be returned to the excel sheet
    """

    #First we get the optimum number of ads for each location in our cleaned data set
    dfin = Extra_ads(dfa,M)

    #Then we add an extra column with the expected profit from the locations
    dfin["Profit From Loc"]=(1/(1-r))*dfin["True Sales Rate"]*(1-r**dfin["Optimum_ads_num"])

    #Then we read our origional data fram again to add these extra columns too
    dforigional = pd.read_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\client_a_data_work.xlsx')

    #Then we need to update our origional data frame with our extra columns, set here to zero
    dforigional["True Sales Rate"] = dforigional["sales_rate_multiplier"]*dforigional["num_companies"]
    dforigional["Optimum_ads_num"] = np.zeros(len(dforigional["num_companies"]))
    dforigional["Profit From Loc"] = np.zeros(len(dforigional["num_companies"]))

    #Then we concat these two data frames deleting the repeated rows 
    dfinal = pd.concat([dforigional, dfin]).sort_values('Optimum_ads_num',ascending=False).drop_duplicates('Unnamed: 0')

    #Then we sort this data frame 
    dfinal = dfinal.sort_index()

    #Then we add a pound symbol to our profits and round them to the closest penny to make it clear they are an amount of money
    #WARNING: sometimes this loop can return an error "A value is trying to be set on a copy of a slice from a DataFrame" but this can be ignored
    # or the loop can be removed if needed
    for i in range(len(dfinal["Optimum_ads_num"])):

        dfinal["Profit From Loc"][i] = '£'+str(np.round(dfinal["Profit From Loc"][i],2))

    #Then we rename our columns to make them more user freindly
    dfinal.rename(columns={'Unnamed: 0': 'Location Number',\
                           'sales_rate_multiplier': 'Sales Rates',\
                           'num_companies':'Number Of Companies',\
                           'Optimum_ads_num':'Optimum Number Of Ads',\
                           'Profit From Loc':'Expected Profits'},\
                            inplace=True)

    return dfinal

#Then we return our data frame to an excel sheet
dfinal= present_df(dfa,M)
dfinal.to_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\datafinal.xlsx', index=False)
