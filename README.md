# Analysis Helper
This repository contains the script AnalysisHelper.py, which can be used to help clean, explore, and visualize data. It also contains folders with data for two projects for which this analysis script has been used. 

The main goal of this project was to create a living script containing functions and classes that can be reused on future behavioral and eyetracking projects, but it can also be adapted for use on other types of data.

## Inputs
This script works with CSV output from programs such as PsychoPy, ERPlab, Eyelink DataViewer, and more. If desired, it also takes a text file with lists of column names to keep, and a corresponding text file with the new names of each of those columns if renaming is necessary. See documentation in AnalysisHelper.py for more information on formatting these files.

## *EyeTrackingHelper Class*
This class within the AnalysisHelper script allows for easy manipulation of EyeLink DataViewer output. This class includes functions to create a succinct and informative dataframe that can be easily merged with other behavioral data.

## *EasyDataFrames Class*
This class is useful for creating simple dataframes from your master data to better visualize specific aspects of your data (e.g., accuracy calculated by grouping desired variables). These functions are also meant to be particularly useful for graphing.

## *Recommended Organization*
We recommend using the Cookiecutter Data Science project structure, as outlined at: <br>
https://drivendata.github.io/cookiecutter-data-science/
