#!/usr/bin/env python
# coding: utf-8

# In[8]:

import pandas as pd
import geopandas as gpd
from eomaps import Maps
import folium
import matplotlib.pyplot as plt



#dados de entrada
contorno = gpd.read_file("../shp/batimetria/GEBCO_SA_bath_contours.shp")
contorno = contorno.set_crs(epsg = "4326", inplace = True, allow_override = True)
PR3 = pd.read_excel("../inputs/Poços_GIS.xlsx",header = 0 ,# index_col = 0, 
                          usecols = ['Nome','LATITUDE','LONGITUDE'] )

#Transforma em um geodataframe
PR3 = gpd.GeoDataFrame(PR3,
            geometry = 
            gpd.points_from_xy(x=PR3.LONGITUDE, y=PR3.LATITUDE),
            crs = "EPSG:4326"
            )


print(contorno)
print(PR3)

#Processamento
m = Maps(crs=Maps.CRS.Mercator.GOOGLE)
m.set_extent((-72.0, -30.0, -35.0, 0.0))

#Batimetria
m.add_gdf(contorno, column="DEPTH", legend=True)


#Adiciona os poços como uma nova camada do mapa
m.add_gdf(PR3, fc="r", ec="b", lw=3, legend=True)


#ESRI
m.add_wms.ESRI_ArcGIS.SERVICES.World_Imagery.add_layer.xyz_layer()


#Adiciona norte e escala
m.add_scalebar()
m.add_compass()

#saída
plt.ylabel('Latitude')
plt.xlabel('Longitude')
plt.show()
