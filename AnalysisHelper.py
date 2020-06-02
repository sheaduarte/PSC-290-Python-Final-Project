import pandas as pd
import numpy as np
import scipy.stats as stats
from glob import glob
from scipy.stats import iqr
from functools import reduce
import altair as alt
from altair_saver import save
import seaborn as sns

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
	
	
########## Creating Figures ##########

def histogram(df, y, output_directory = None):
	'''Requires altair and altair saver. Plots a histogram of y and can save a html file 
	to output directory, if provided. Won't work if df has more than 5000 rows.'''
	if df.shape[0] >5000:
        	return 'The dataframe is too large. Subset the data or use a different dataframe.'
	else:
        	chart = alt.Chart(df).mark_bar(
        	).encode(alt.X(y,title= y, bin = True), y = 'count()', 
        	).properties(title = 'Distribution of '+y)
        	if output_directory != None:
        		chart.save(output_directory+'Histogram of '+y+'.html')
        	return chart

def bar_graph(df,x,y,z, output_directory = None, custom_scheme = 'deep', custom_style = 'darkgrid', order = None, label_rotation = None):
	'''Requires seaborn. Plots a bar graph of x by y, grouped by z (a factor) if desired. Can save 
	a png file to output directory, edit color scheme and styles, and rotate x axis labels, if desired. '''
	sns.set(style= custom_style, palette = custom_scheme)
	g = sns.catplot(x=x, y=y, 
                hue=z, # use this to group, if needed
                data=df,
                height=6, kind="bar", order = order)
	g.despine(left=True)
	g.set_ylabels(y)
	g.set_xlabels(x)
	if label_rotation != None:
		g.set_xticklabels(rotation= label_rotation) 
	g.set(title ='Mean Differences in '+y)
	if output_directory != None:
		g.savefig(output_directory+ 'Mean Differences in '+y+'.png')
	return g
	
def stacked_bar_graph(df,id_vars_list, value_vars_list, var_name_str, value_name_str, x, y, z, output_directory = None, custom_scheme = 'dark2'):
	'''Requires pandas, altair and altair saver. First converts a df to long format using melt. ID_vars_list is the list of column names to keep the same 
	(group or condition, for example). Value_vars_list is the column name that contains the value to sum (such as output values, percentages or proportions). 
	Var_name_str will correspond to the different colors within a stacked bar, so this would be a categorical factor that goes beyond group/condition (such as 
	location). Value_name_str will correspond to the string label for the y axis (such as 'proportion of fixations'). X is the column name to group by for the 
	plot on the x axis. Next, plots a standardized stacked bar graph of x by y (value_name_str), where z (var_name_str) is different subgroups within X. 
	Option to  save a html file to output directory and make aesthetic changes if desired. '''
	# convert df to long format
	long_df = pd.melt(df, id_vars = id_vars_list, 
			    value_vars = value_vars_list, 
			    var_name = var_name_str, 
			    value_name = value_name_str)

	# plot stacked bar graph
	chart = alt.Chart(long_df).mark_bar().encode(
		x = x,
		y = 'sum('+y+')',
		color = alt.Color(z, 
		scale = alt.Scale(scheme=custom_scheme)) #changes color scheme. 
		# see https://vega.github.io/vega/docs/schemes/ for examples
	    ).properties(
		title = 'Proportions of '+z+' by '+x, width = 450)
	chart.save(output_directory+'Proportions of '+z+' by '+x+'.html')
	return chart

def scatter_plot(df,x,y,z, tt_interactive, output_directory = None, custom_scheme = 'dark2'):
	'''Requires altair and altair saver. Plots a scatter plot of x and y, where z 
	is a factor that changes point color (optional). Tooltip functionality enabled, but will 
	need to specify desired columns in a list ahead of time (tt_interactive_. Option to save a html file to output directory and make aesthetic changes. '''
	chart= alt.Chart(df).mark_circle(size=60).encode(
	x=x,
	y=y,
	color=alt.Color(z, 
		scale=alt.Scale(scheme=custom_scheme)),
	tooltip= tt_interactive
	).interactive().properties(
	title='Scatterplot of '+x+' by '+y)
	if output_directory != None:
		chart.save(output_directory+'Scatterplot of '+x+' by '+y+'.html')
	return chart

def scatter_matrix(df,x,z, output_directory = None, custom_scheme = 'dark2'):
	'''Requires altair and altair saver. Plots a scatter matrix of a list of variables (x), where z 
	is a factor that changes point color (optional). Option to save a html file to output directory. '''
	x_inverse = x[::-1] 
	chart= alt.Chart(df).mark_circle().encode(
		alt.X(alt.repeat("column"), type='quantitative'),
		alt.Y(alt.repeat("row"), type='quantitative'),
		color=alt.Color(z+':N', 
		scale=alt.Scale(scheme=custom_scheme))
	).properties(
		width=150,
		height=150
	).repeat(
		row=x,
		column= x_inverse
	).interactive()
	if output_directory != None:
		chart.save(output_directory+'Scatterplot Matrix.html')
	return chart

def violin(df,x,y,z, custom_scheme = 'deep', custom_style = 'darkgrid', order = None):
	'''Requires seaborn. Plots a violin distribution plot of y by x	 where z 
	is a factor that allows for grouping, if desired. DOES NOT AUTOMATICALLY SAVE OUTPUT. '''
	sns.set(style= custom_style, palette = custom_scheme)
	ax = sns.violinplot(x=x, y=y, 
		hue=z, #optional
		data=df, order = order)
	ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	ax.set(title ='Distribution of '+y+' by '+x)
	return ax

def regression_plot(df,x,y,z, output_directory = None, custom_scheme = 'deep', custom_style = 'darkgrid'):
	'''Requires seaborn. Plots a regression plot of x by y with regression lines, where z 
	is a factor that allows for grouping, if desired. Option to save output as a png file. '''
	sns.set(style= custom_style, palette = custom_scheme)
	g = sns.lmplot(x=x, y=y, hue=z,
		       data=df)
	g.set(title ='Regression Plot of '+x+' and '+y)
	if output_directory != None:
		g.savefig(output_directory+ 'Regression Plot of '+x+' and '+y+'.png')
	return g

def boxplot(df,x,y,z, custom_scheme = 'deep', custom_style = 'darkgrid', order = None):
	'''Requires seaborn. Plots a boxplot of y by x with marks for outliers,, where z 
	is a factor that allows for grouping, if desired. DOES NOT AUTOMATICALLY SAVE OUTPUT. '''
	sns.set(style= custom_style, palette = custom_scheme)
	ax = sns.boxplot(x=x, y=y,
			 hue=z,
			 data=df, 
			 order = order)
	sns.despine(offset=10, trim=True)
	ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	ax.set(title ='Distribution of '+y+' by '+x)
	return ax


##### Data Subsetting for Eyetracking Data Figures #####


class EyeTrackingHelper:
	def __init__(self, RawEyeDF):
		'''Takes a raw eyetracking dataframe that has had columns filtered and renamed'''
		self.RawEyeDF = RawEyeDF
		
	def CleanEyeTracking_MasterDF(self, currentFixationIdx, nearestIAVar, currentFixDurationVar, fixationTotalVar, trialVar = 'trial', participantVar = 'participant'):
		EyeDF_cols = ['trial','participant', 'total_fixations', 'latency', 'fixation0']
		EyeTracking_MasterDF = pd.DataFrame(columns = EyeDF_cols)
		Fix0 = self.RawEyeDF[self.RawEyeDF[currentFixationIdx] == 1]
		EyeTracking_MasterDF['trial'] = Fix0[trialVar]
		EyeTracking_MasterDF['participant'] = Fix0[participantVar]
		EyeTracking_MasterDF['total_fixations'] = Fix0[fixationTotalVar]
		EyeTracking_MasterDF['latency'] = Fix0[currentFixDurationVar]
		EyeTracking_MasterDF['fixation0'] = Fix0[nearestIAVar]
		keep_cols = [trialVar, participantVar, nearestIAVar, currentFixDurationVar]
		dfs = [EyeTracking_MasterDF]
		for x in list(range(2,7)):
			FixDFs = self.RawEyeDF[self.RawEyeDF[currentFixationIdx] == x]
			FixDFs = FixDFs[keep_cols]
			FixDFs = FixDFs.rename(columns = {nearestIAVar:'fixation' + str(x-1), currentFixDurationVar:'fix_dur_' + str(x-1)})
			dfs.append(FixDFs)
		EyeTracking_MasterDF = reduce(lambda left,right: pd.merge(left,right,on=['trial', 'participant'], how='outer'), dfs)
		EyeTracking_MasterDF = EyeTracking_MasterDF.iloc[:, [0,1,2,3,4,5,6,8,9,11,12,14]]
		EyeTracking_MasterDF = pd.DataFrame(EyeTracking_MasterDF)
		return EyeTracking_MasterDF
		
	def Add_First_Fixation(self, df, fixation1Var, fixation2Var, fixation3Var, fixDuration1, fixDuration2, fixDuration3, fixationIA = 'fixationIA'):
		'''If dat has an interest area on fixation, this function can be used to disregard first fixations on fixation IAs 
		so that first fixations refer to the first non-fixation interest area that participants look at'''
		df['first_fixation'] = df[fixation1Var]
		df['first_fixation'] = df['first_fixation'].replace(fixationIA, df[fixation2Var])
		df['first_fixation'] = df['first_fixation'].replace(fixationIA, df[fixation3Var])
		idx = df.index[df[fixation1Var]==fixationIA]
		df['first_fix_dwell'] = df[fixDuration1]
		df.loc[idx, 'first_fix_dwell'] = df[fixDuration2]
		idx2 = df.index[(df[fixation1Var]==fixationIA) & (df[fixation2Var]==fixationIA)]
		df.loc[idx2, 'first_fix_dwell'] = df[fixDuration3]
		df = pd.DataFrame(df)
		return df

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
		result = pd.DataFrame(result)
	return result


















