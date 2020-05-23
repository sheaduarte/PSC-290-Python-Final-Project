import pandas as pd
import numpy as np
import scipy.stats as stats
from glob import glob
from scipy.stats import iqr
from functools import reduce

#this list of packages should be reduced (& probably also expanded) 

########## Importing and Cleaning Data ##########



def import_all_csvs(folder):
	'''Given a folder, this function finds .csv files and
	concatenates them into a master dataframe'''
	files = glob(folder + '/*.csv')
	master_df = pd.concat([pd.read_csv(f) for f in files ])
	return master_df


def filter_columns(txt_file, df):
	'''Reads in a .txt file with column names &
	makes a new dataframe with only those columns'''
	file = open(txt_file,'r')
	cols = file.readlines()
	names = [col.strip('\n') for col in cols ]
	filtered_df = pd.DataFrame()
	for name in names:
		if name in df.columns:
			rel_col = df[[name]]
			filtered_df[[name]]= rel_col
	return filtered_df

def rename_columns(txt_file, df):
	'''Reads in a .txt file with each new column name on
	a new line and renames columns in a given dataframe'''
	file = open(txt_file,'r')
	cols = file.readlines()
	names = [col.strip('\n') for col in cols ]
	# if there are extra columns at the end that you don't want, this cuts them off:
	if len(df.columns) == len(names):
		df.columns = names
	else:
		df = df.iloc[:,0:(len(names))]
		df.columns = names
	return df

def SjAcc(df):
	'''Subject Accuracy: Uses a column with boolean values 
	(0: incorrect, 1: correct) and calculates percent accuracy'''
	acc = (df['corrCheck'].value_counts()[1])/((df['corrCheck'].value_counts()[0])+(df['corrCheck'].value_counts()[1]))
	print(acc)

def remove_outliers(df, var, outlier_constant = 1.5):
	'''Outlier Remover: Removes outliers from a set of data 
	using IQR method, constant (c) defaults to 1.5'''
	IQR = iqr(df[var].dropna())
	outliers = IQR*outlier_constant
	lowerOutliersCalc = (df[var].quantile([.25])) - outliers
	upperOutliersCalc = (df[var].quantile([.75])) + outliers
	lowerOutliers = lowerOutliersCalc.iloc[0]
	upperOutliers = upperOutliersCalc.iloc[0]
	cleanTrials = df[df[var].between(lowerOutliers, upperOutliers)]
	return(cleanTrials)		
	
def EyeTracking_MasterDF(df, currentFixationIdx, nearestIAVar, currentFixDurationVar, fixationTotalVar, trialVar = 'trial', participantVar = 'participant'):
    '''This function takes a raw eye tracking dataframe and condenses it down to 
    the number of trials in the task by creating a summary row for each trial'''
    EyeDF_cols = []
    EyeTracking_MasterDF = pd.DataFrame(columns = EyeDF_cols)
    Fix0 = df[df[currentFixationIdx] == 1]
    EyeTracking_MasterDF['trial'] = Fix0[trialVar]
    EyeTracking_MasterDF['participant'] = Fix0[participantVar]
    EyeTracking_MasterDF['total_fixations'] = Fix0[fixationTotalVar]
    EyeTracking_MasterDF['latency'] = Fix0[currentFixDurationVar]
    EyeTracking_MasterDF['fixation0'] = Fix0[nearestIAVar]
    keep_cols = [trialVar, participantVar, nearestIAVar, currentFixDurationVar]
    dfs = [EyeTracking_MasterDF]
    for x in list(range(2,7)):
        FixDFs = df[df[currentFixationIdx] == x]
        FixDFs = FixDFs[keep_cols]
        FixDFs = FixDFs.rename(columns = {nearestIAVar:'fixation' + str(x), currentFixDurationVar:'fix_dur' + str(x)})
        dfs.append(FixDFs)
    EyeTracking_MasterDF = reduce(lambda left,right: pd.merge(left,right,on=['trial', 'participant'], how='outer'), dfs)
    return EyeTracking_MasterDF
	
def First_Fixation(df, fixation1Var, fixation2Var, fixation3Var, fixationIA = 'fixationIA'):
	'''Used to disregard first fixations that are on the fixation cross (the fixation interest area (IA)) 
	so that first fixations refer to the first non-fixation interest area that participants look at'''
	df['first_fixation'] = df[fixation1Var]
	df['first_fixation'] = df['first_fixation'].replace(fixationIA, df[fixation2Var])
	df['first_fixation'] = df['first_fixation'].replace(fixationIA, df[fixation3Var])
	return df
	
def Add_FirstFixDwell(df, fixation1Var, fixation2Var, fixDuration1, fixDuration2, fixDuration3, fixationIA = 'fixationIA'):
	idx = df.index[df[fixation1Var]==fixationIA]
	df['first_fix_dwell'] = df[fixDuration1]
	df.loc[idx, 'first_fix_dwell'] = df[fixDuration2]
	idx2 = df.index[(df[fixation1Var]==fixationIA) & (df[fixation2Var]==fixationIA)]
	df.loc[idx2, 'first_fix_dwell'] = df[fixDuration3]
	return df
	
	
	
	
########## Creating Figures ##########



##### Data Subsetting for Eyetracking Data Figures #####

def FirstFixProportions(df, condition_list, IA_1='targetIA', IA_2='distIA', trialVar = 'trial'):
    '''Uses dataframe of count values & finds proportion of first fixations to two interest areas, 
    not suitable for more than two interest areas'''
    result = pd.DataFrame()
    for condition in condition_list:
        target = (df[(trialVar, condition)][IA_1])/((df[(trialVar,condition)][IA_2])+
                                                          (df[(trialVar, condition)][IA_1]))
        distractor = (df[(trialVar, condition)][IA_2])/((df[(trialVar, condition)][IA_2])+
                                                            (df[(trialVar, condition)][IA_1]))
        Proportion_Dict = {'condition':condition,'target': target,'distractor':distractor}
        result = result.append(Proportion_Dict, ignore_index =True)
    return result



