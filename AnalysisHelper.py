import pandas as pd
import numpy as np
import scipy.stats as stats
from glob import glob
from scipy.stats import iqr
from functools import reduce

#this list of packages should be reduced (& probably also expanded) 

########## Importing and cleaning Data ##########



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

def EyeDF_func(df):
	'''This function still needs work'''
	EyeDF_cols = []
	EyeDF = pd.DataFrame(columns = EyeDF_cols)
	Fix0 = df[df['current fix idx'] == 1]
	EyeDF['trial'] = Fix0['trial']
	EyeDF['participant'] = Fix0['participant']
	EyeDF['total fixations'] = Fix0['total fixations']
	EyeDF['latency'] = Fix0['current fix dur']
	EyeDF['fixation0'] = Fix0['nearest IA label']
	keep_cols = ['trial', 'participant', 'nearest IA label', 'current fix dur']
	Fix1 = df[df['current fix idx'] == 2]
	Fix1 = Fix1[keep_cols]
	Fix1 = Fix1.rename(columns = {'nearest IA label':'fixation1','current fix dur':'fix dur1'})
	Fix2 = df[df['current fix idx'] == 3]
	Fix2 = Fix2[keep_cols]
	Fix2 = Fix2.rename(columns = {'nearest IA label':'fixation2','current fix dur':'fix dur2'})
	Fix3 = df[df['current fix idx'] == 4]
	Fix3 = Fix3[keep_cols]
	Fix3 = Fix3.rename(columns = {'nearest IA label':'fixation3','current fix dur':'fix dur3'})
	Fix4 = df[df['current fix idx'] == 5]
	Fix4 = Fix4[keep_cols]
	Fix4 = Fix4.rename(columns = {'nearest IA label':'fixation4','current fix dur':'fix dur4'})
	Fix5 = df[df['current fix idx'] == 6]
	Fix5 = Fix5[keep_cols]
	Fix5 = Fix5.rename(columns = {'nearest IA label':'fixation5','current fix dur':'fix dur5'})
	dfs = [EyeDF, Fix1, Fix2, Fix3, Fix4, Fix5]
	EyeDF = reduce(lambda left,right: pd.merge(left,right,on=['trial', 'participant'],how='outer'), dfs)
	return EyeDF
	
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



##### Typical Data Subsetting for Eyetracking Data #####





