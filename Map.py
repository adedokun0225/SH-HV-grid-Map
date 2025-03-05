from bokeh.plotting import figure, show
from bokeh.models import WMTSTileSource
from bokeh.models import ColumnDataSource, HoverTool
from geopy.distance import geodesic 
import pandas as pd
import numpy as np


#Range for the size of the map 
x_range, y_range = ((800000, 1100000),(7000000,8000000))

#Convert dec lat/long to web_mercator formart
class Convert:
    K = 6378137

    def __init__(self, dataframe, lat1="Latstat", lat2="Latend", lon1="Longstat", lon2="Longend"):
        self.df = dataframe
        self.lat1 = lat1
        self.lat2 = lat2
        self.lon1 = lon1
        self.lon2 = lon2
        self.K = 6378137

    def web_mercetor_convert1(self):
    
        self.df["A"] = self.df[self.lon1] * (self.K * np.pi/180)
        self.df["B"] = np.log(np.tan((90 + self.df[self.lat1]) * np.pi / 360 )) * self.K
        self.df["C"] = self.df[self.lon2] * (self.K * np.pi/180)
        self.df["D"] = np.log(np.tan((90 + self.df[self.lat2]) * np.pi / 360 )) * self.K
    
        return self.df
    


def web_mercetor_convert(df, lon="Longitude", lat="Latitude"):
    K = 6378137

    df["X"] = df[lon] * (K * np.pi/180)
    df["Y"] = np.log(np.tan((90 + df[lat]) * np.pi / 360 )) * K
    
    return df 


#Load data
def data_frame(data):
    df = pd.read_csv(data, encoding="utf-8-sig")
    return df


#Load the substation data
df = data_frame("Substation/Substations2.csv")
df1 = data_frame("Substation/Substations4.csv")
df2 = data_frame("Substation/Substations6.csv")
df3 = data_frame("Substation/Substations8.csv")
#print(df3)


#Drop row with NAN
df1 = df1.dropna(subset=['Latstat'])
df2 = df2.dropna(subset=['Latstat'])
df3 = df3.dropna(subset=['Latstat'])
# print(df1)


df1 = df1.dropna(subset=['Latend'])
df2 = df2.dropna(subset=['Latend'])
df3 = df3.dropna(subset=['Latend'])
# print(df1)


#Remove  columns with NAN values
df1 = df1.dropna(axis=1)
df2 = df2.dropna(axis=1)
df3 = df3.dropna(axis=1)
# print(df1)


#Convert data to web_mercetor format
maped_data = web_mercetor_convert(df)
maped_data1 = Convert(df1)
maped_data2 = Convert(df2)
maped_data3 = Convert(df3)
maped_data4= maped_data1.web_mercetor_convert1()
maped_data6 = maped_data2.web_mercetor_convert1()
maped_data8 = maped_data3.web_mercetor_convert1()



# Convert numerical columns to the correct data types
num_cols = [ "Latstat","Longstat", 'Latend','Longend', 'A', 'B','C','D']
for col in num_cols:
     maped_data4[col] = pd.to_numeric(maped_data4[col], errors="coerce")

# Measure the distance from each data point
class Distance:
    #dist =[]
    def __init__(self, maped_datas, output_file):
        self.maped_datas = maped_datas
        self.output_file = output_file

    def Measured_dist(self, append=True):
        mode= "a" if append else "w" 
        with open(self.output_file, mode) as file:
            for i in range (len(self.maped_datas)-1):
                point1 = (self.maped_datas.iloc[i]["Latstat"], self.maped_datas.iloc[i]["Longstat"])
                point2 = (self.maped_datas.iloc[i]["Latend"], self.maped_datas.iloc[i]["Longend"])
                distance = geodesic(point1,point2).kilometers
                
                output= (
                        f"Measured dist betweeen {self.maped_datas.iloc[i]['Start point Station']}"
                            f" and {self.maped_datas.iloc[i]['End point substation']}:{distance:.2f} km\n"
                            )
                file.write(output)
            
            return distance


output_file = "distance.txt"

Dist1 = Distance(maped_data4, output_file)
Dist01 = Dist1.Measured_dist(append=False)

Dist2 = Distance(maped_data6, output_file)
Dist02 = Dist2.Measured_dist(append=True )

Dist3 = Distance(maped_data8, output_file)
Dist03 = Dist3.Measured_dist(append=True)

#Create a column data for the map
source = ColumnDataSource(maped_data)
# print(source.data)

#Size and construct the map
P = figure(tools="pan, wheel_zoom, reset", x_range= x_range, y_range= y_range,  width=1450, height=800,
                x_axis_type= "mercator", y_axis_type= "mercator")
 
#Load the map and add title
url = "https://tile.openstreetmap.de/{z}/{x}/{y}.png"
attribution = "xyz.OpenStreetMap.Mapnik"
P.add_tile(WMTSTileSource(url=url, attribution = attribution))

#Add locations to the map
P.circle(x='X', y='Y', fill_color="firebrick", size= 10, hover_color= "blue", source= source)

#Add lines to the map
class Lines:
    def __init__(self, maped_data):
        self.maped_data = maped_data
    
    def Input_line(self):

        lines_data = {
            "xs": [[row["A"], row["C"]] for _, row in self.maped_data.iterrows()], 
            "ys": [[row["B"], row["D"]] for _, row in self.maped_data.iterrows()] 
        }
        return lines_data
    
line_data1 = Lines(maped_data4)
line_data2 = Lines(maped_data6)
line_data3 = Lines(maped_data8)

lines_data4 = line_data1.Input_line()
lines_data6 = line_data2.Input_line()
lines_data8 = line_data3.Input_line()

source1= ColumnDataSource(lines_data4)
source2= ColumnDataSource(lines_data6)
source3= ColumnDataSource(lines_data8)

# print(lines_data)
# print(source1)

P.multi_line(xs="xs", ys="ys", source=source1, line_width=2, color="green")
P.multi_line(xs="xs", ys="ys", source=source2, line_width=2, color="red")
P.multi_line(xs="xs", ys="ys", source=source3, line_width=2, color="purple")


hover = HoverTool()
hover.tooltips= [("Name","@Name"),
                ("Voltage","@Voltage"),
                ("Coordinate","(@Latitude, @Longitude)")]
#hover.mode = 'vline'

P.add_tools(hover)

show(P)