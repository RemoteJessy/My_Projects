## Writen by Jessenia Lorenzo and George Napier
## contact George.Napier@nexteraenergy.com if errors occur

# # KML to CSV converter

# ## Imports

# In[1]:


from tkinter import Tk
from tkinter.filedialog import askopenfilename
import geopandas as gpd
import pandas as pd
import fiona
import pprint
from xml.dom.minidom import *
import pandas as pd
import csv
import xml.etree.ElementTree as ET
import re
import numpy as np
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import shapely
import math
from zipfile import ZipFile
from pyproj import Geod
from shapely import wkt


# Functions

# In[2]:


# Function to import file and turn into dataframe and returns the dataframe and the filepath-
def importKML():
    #Tkinter open GUI box, two calls on the TK object to make it just the box and always show topmost
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file = askopenfilename()
    #print out the file path of the uploaded file
    print("File Uploaded:", str(file))
    
    #grab driver support to read the KML/KMZ
    fiona.drvsupport.supported_drivers['kml'] = 'rw'
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    fiona.drvsupport.supported_drivers['KMZ'] = 'rw'
    fiona.drvsupport.supported_drivers['kmz'] = 'rw'
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
    
    #Open fine in fiona
    f =  fiona.open(file)

    # empty GeoDataFrame
    df = gpd.GeoDataFrame()

    #KML/KMZ if statment, KMZ files are unzipped then read
    if file[-3:] == 'kml':
        for layer in fiona.listlayers(f.path):
            #try catch block to check for errors in the KML
                try:
                    s = gpd.read_file(f.path, driver='KML', layer=layer)
                    df = pd.concat([df, s], ignore_index=True)
                except: 
                    print("Error in the KML File, line with only one point in layer", str(layer))
    
    # iterate over layers
    if file[-3:] == 'kmz':
        for layer in fiona.listlayers(f.path):
            #try catch block to check for errors in the KML
                try:
                    s = gpd.read_file(f.path, driver='KMZ', layer=layer)
                    df = pd.concat([df, s], ignore_index=True)
                except: 
                    print("Error in the KML File, line with only one point in layer ", str(layer))
        
    return df, file


# In[3]:


# This function cleans the "Shape", "Number of Points", "Description", and "0" into "Perimete/Length (feet)" columns:
def NameCleanUp(df):
    #all names lowercase to prevent errors
    df.columns = df.columns.str.lower()
    
    # Creates a new column named "Points" that is the "geometry" column as a string type
    df['points'] = df['geometry'].astype(str)
    
    # Clean up the "Description" column:
    df["Description"] = df['description'].replace("Dimension: <br>description:", "")
    
    # Split column "Points" into two columns: column "Shape" and column "Number of Points":
    df[['Shape', 'toThrowAway']] = df['points'].str.split('(', 1, expand=True)
    
    # Renaming the "Shape" column using the "my_recode" function:
    df['Shape Type'] = df['Shape'].apply(my_recode)
    
    # Re-capitalize Name
    df = df.rename(columns = {'name' : 'Name' })
    return df


# In[4]:


# This function is for recoding the "Shape Type" column so that it is named relevantly:
def my_recode(Shape):
    if Shape == "POLYGON Z ":
        return "Polygon"
    if Shape == "LINESTRING Z ":
        return "Linestring"
    if Shape == "POINT Z ":
        return "Point"



# In[5]:


# This function manipulates the "Folder" column:
def PathFolderColumn(df):
    # Create a "Folder" column that will hold the folder and file from the filepath:
    df['Folder'] = ''
    # PathArray from file (Global Variable):
    pathArray = file.split("/")
    # Adding the file path parent folder and file name into the string "ParentChildFolderPath" variable:
    ParentChildFolderPath = "/".join(pathArray[-2:])
    # Modifying existing DF by assigning the "Folder" column to be: "ParentChildFolderPath":
    df = df.assign(Folder = ParentChildFolderPath)
    return df


# In[6]:


def areaPerimPointColumns(df):
    #arrays to store output before merge with df
    areaArr = []
    perimArr = []
    pointsNumArr = []
    
    #name shape of earth
    geod = Geod(ellps="WGS84")
    
    #loop through and get all of the geometry broken down based on geomtery type
    for i in range(df.shape[0]):
        #if polygon return area and perimiter of polygon
        if df['geometry'][i].type == 'Polygon':
            #grab shape
            poly = df['geometry'][i]
            #get area in abs so no negative areas
            area = abs(geod.geometry_area_perimeter(poly)[0])
            #get perim in abs so no negative perim
            perim = abs(geod.geometry_area_perimeter(poly)[1])
            #convert from m^2 to acers and add to array
            areaArr.append(round((area/4046.86),2))
            #convert from meters to miles and add to array
            perimArr.append(round((perim/1609.344),2))
            #add number of points in polygon by counting x cordinates
            pointsNumArr.append(int(len(df['geometry'][i].exterior.coords.xy[0])-1))
            
        elif df['geometry'][i].type == 'LineString':
            #grab shape
            line = df['geometry'][i]
            #get length
            length = abs(geod.geometry_length(line))
            #convert from meters to miles and add to array
            perimArr.append(round((length/1609.344),2))
            #add np.nan to area array
            areaArr.append(np.nan)
            #add number of points in linestring by counting x cordinates
            pointsNumArr.append(int(len(df['geometry'][i].coords.xy[0])))
        
        elif df['geometry'][i].type == 'Point':
            #add np.nan to area array
            areaArr.append(np.nan)
            #add np.nan to perim array
            perimArr.append(np.nan)
            #add 1 to the points array
            pointsNumArr.append(1)
            
    #turn arrays into dataframe and merge
    
    tempDF = pd.DataFrame([areaArr, perimArr, pointsNumArr]).T
    tempDF = tempDF.rename({0 : 'Area (Acres)', 1 : 'Perimiter/Length (Miles)' , 2 : 'Number of Points' }, axis =1)
    
    #concat dataframes
    df = pd.concat([tempDF, df], axis=1)
    
    return df


# In[7]:


# This function ia for dropping unused columns
def DropUnusedColumns(df):
    #Drop everything except the named columns
    df.drop(df.columns.difference(['Folder', 'Name', 'Shape Type', 'Number of Points', 'Area (Acres)', 'Perimiter/Length (Miles)']), 1, inplace=True)
    return df


# In[8]:


# This function is for exporting in csv file format:
def SaveAsCSV(df):
    df.to_csv(file[:-3]+"csv")


# In[17]:


# This function is for exporting in excel file format:
def SaveAsExcel(df):
    try:
        df.to_excel(file[:-3]+"xlsx")
        print("File Saved as: ", str(file[:-3]+"xlsx"))
    except:
        print("Error Saving File")


# ## Main

# In[18]:


# Run the function to import file and turn into dataframe and returns the dataframe and the filepath-
df, file = importKML()

# Run the following functions:

# This function cleans the "Shape", "Number of Points", "Description", and "0" into "Perimete/Length (feet)" columns:
df = NameCleanUp(df)
# This function manipulates the "Folder" column:
df = PathFolderColumn(df)
# add the perimiter, area and number of points column
df = areaPerimPointColumns(df)
#drop any not uses columns
df = DropUnusedColumns(df)
# Reorder:
df = df.loc[:,['Folder', 'Name', 'Shape Type', 'Number of Points', 'Area (Acres)', 'Perimiter/Length (Miles)']]
# Save the excelfile to the parent folder
SaveAsExcel(df)

