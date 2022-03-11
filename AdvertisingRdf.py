import numpy as np
import pandas as pd
dfr = pd.read_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\client_a_data_workr.xlsx')
###################################################################
#Number of adverts available
M=1000000
###################################################################   
dfr["True Sales Rate"] = dfr["num_companies"]*dfr["sales_rate_multiplier"]
def aibi(x,r,M):
    """ Function for finding the value of a_i, b_i for each data point

    Paramaters
    ----------
    x : float
        the true sales rate for the given data point 
    
    r : float
        retention value for the given data point

    M : int
        total number of adverts for our system

    Returns 
    -------
    a : float 
        a_i for the data point

    b : float
        b_i for the data point

    """

    # First we set the value for a_i
    a = 1 / np.log(r)

    # Then we set the values for A and C
    delta = (r - 1) * a
    A = np.sum(a)
    C = (1/A) * (M + np.sum(a * np.log(x/delta)))

    # Then we can find b_i
    b = a * (np.log(delta) + C)

    return b, a


def data_clean(df):
    """ Function for removing unwanted data points from our data set

    Parameters
    ----------
    df : data frame
        data frame of data points as read from excel

    Returns
    -------
    df : data frame
        data frame with unwanted data points removed

    """

    #First we loop through and remove all data points with zero sales rate multiplier
    for index, row in df.iterrows():

        if row["True Sales Rate"] == 0:

            df.drop(index, inplace=True)
    
    #Now we set a variable to end our while loop after a certian number of iterations
    l = 0

    #Then we set an array of values for the a_i , b_i values at each data point
    b, a = aibi(df.loc[:,"True Sales Rate"],df.loc[:,"r"],M)

    #Then we use a while loop to keep removing data that returns a negative value for the optimum number of adverts
    while np.any(df.loc[:,"True Sales Rate"] < np.exp(b/a)):

        for index, row in df.iterrows():

            if row["True Sales Rate"] < np.exp(b[index]/a[index]):

                df.drop(index, inplace=True)

        #Then we find the new values of a_i, b_i after each data clean
        b, a = aibi(df.loc[:,"True Sales Rate"],df.loc[:,"r"],M)

        #Then we count the number of loops and terminate if we reach 1000
        l = l + 1

        if l == 1000:

            break

    return df


def Optimum_ads_func(df):
    """ Function to find the rounded optimum number of adverts for each location

    Parameters 
    ----------
    df : data frame
        data frame o data points as read from excel

    returns
    -------
    df : data frame
        data frame with extra column for the optimum number of adverts at that location

    """

    #First we use our data clean function to get only the data points we are interested in
    df = data_clean(df)

    #Then we find an array of the vales for a_i and b_i
    b, a = aibi(df.loc[:,"True Sales Rate"],df.loc[:,"r"],M)

    #Then we use these to set the optimum number of adverts at each location
    df["Optimum_Ads_Num"] = np.floor(b-a*np.log(df.loc[:,"True Sales Rate"]))#

    return df


def excess_ads(df,M):
    """ Algorithm for assigning the extra adverts left over after rounding

    Parameters
    ----------
    df : data frame
        data frame of data points in our problem, read from a excel file

    M : int 
        total amount of adverts in our problem

    Returns
    -------
    df : data frame
        data frame with rounded number of adverts
    """

    #First we find the rounded number of optimum adverts
    df = Optimum_ads_func(df)

    #Then we find the difference between this and our total number of adverts
    diff = int(M-np.sum(df["Optimum_Ads_Num"]))

    #Then we create the excess column to find the scaled sales rate
    df["excess_col"] = df["True Sales Rate"] * df["r"] ** df["Optimum_Ads_Num"]

    #Then we sort the df by these values and add one to the number of ads on the top M_e scaled sales rates
    df.sort_values(by = ["excess_col"], ascending = False)
    df["Optimum_Ads_Num"] = df["Optimum_Ads_Num"] + np.append(np.ones(diff), np.zeros(len(df["Optimum_Ads_Num"])-diff))

    #Then we resort the data frame and remove the excess column 
    df.sort_index()
    df.drop("excess_col", axis=1, inplace=True)

    return df


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

    #First we find the optimum number of adverts
    dfin = excess_ads(dfa,M)

    #Then we assign the profit for each location
    dfin["Profit From Loc"] = (1 / (1 - dfin["r"])) * dfin["True Sales Rate"] * (1 - dfin["r"] ** dfin["Optimum_Ads_um"])

    #Then we get our origional data frame from the excel sheet again
    dforigional = pd.read_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\client_a_data_workr.xlsx')

    #Then we add extra columns to this and concat it with our new data frame with the optimum number of adverts in it
    dforigional["True Sales Rate"] = dforigional["sales_rate_multiplier"]*dforigional["num_companies"]
    dforigional["Optimum_Ads_Num"] = np.zeros(len(dforigional["num_companies"]))
    dforigional["Profit From Loc"] = np.zeros(len(dforigional["num_companies"]))
    
    dfinal = pd.concat([dfin,dforigional]).sort_values('Optimum_Ads_Num',ascending=False).drop_duplicates('Unnamed: 0')
    dfinal = dfinal.sort_index()

    #Then we loop over the rows to convert the profit into a currency amount
    for i in range(len(dfinal["Optimum_Ads_Num"])):
        dfinal["Profit From Loc"][i] = "£{:,.2f}".format(dfinal.loc[i,"Profit From Loc"])

    #Then we rename our columns to make them more readable
    dfinal.rename(columns={'Unnamed: 0': 'Location Number',\
                           'sales_rate_multiplier': 'Sales Rates',\
                           'num_companies':'Number Of Companies',\
                           'r':'Retention Value',\
                           'Optimum_Ads_Num':'Optimum Number Of Ads',\
                           'Profit From Loc':'Expected Profits'},\
                            inplace=True)

    dfinal = dfinal[["Location Number","Sales Rates","Number Of Companies","Retention Value","True Sales Rate","Optimum Number Of Ads","Expected Profits"]]

    return dfinal

#Then we return this data frame to a new excel sheet
dfinal = present_df(dfr,M)
dfinal.to_excel(r'C:\Users\will simpkins\Documents\Engineering Mathematics\Term 2\data\datafinalR.xlsx', index=False)
