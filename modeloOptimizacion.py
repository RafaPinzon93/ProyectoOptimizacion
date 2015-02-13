# -*- coding: utf-8 -*-
from __future__ import division
from coopr.pyomo import *
import numpy as np
# import MySQLdb
import json
# from pyutilib.misc import Options

# from coopr.opt import SolverFactory



np.set_printoptions(linewidth=200)
oldSettings = np.seterr(divide='ignore', invalid='ignore')
np.seterr(**oldSettings)

FACTORPASAJERO = 100  # Factor de peso del pasajero
FACTOROPERADEOR = 100  # Factor de peso del operador
CAPACIDADBUSES  = 150 # Capacidad total de los buses
TIEMPOABORDAR = 1/60.0
TIEMPOESPERA2BUS = 1
_tiempoViajePromedio = [[[[1,2],[3,4]]]]

HORAINICIO = 7

HORAFIN = 22

NUMERORUTAS = 3 # Se sacará de base de datos

# frecuenciaOptima1 = 0.19370
# frecuenciaOptima1 = 0.172889582833822
# frecuenciaOptima1 = 0.152581658700488
frecuenciaOptima1 = 0.18
# frecuenciaOptima2 = 0.15703
# frecuenciaOptima2 = 0.0842212498536333
# frecuenciaOptima2 = 0.0829857776183043
frecuenciaOptima2 = 0.11
# frecuenciaOptima3 = 0.19119
# frecuenciaOptima3 = 0.189052798041706
# frecuenciaOptima3 = 0.135635424653224
frecuenciaOptima3 = 0.13
FrecuenciasOptimas = [frecuenciaOptima1, frecuenciaOptima2, frecuenciaOptima3]

# Se sacará de base de datos
_TIEMPO_ENTRE_ESTACIONES1 = np.mat('0,2,4,6,6,8,8,10,10,12,14,16,12,14,16; 2,0,2,4,4,6,6,8,8,10,12,14,10,12,14; 4,2,0,2,2,4,4,6,6,8,10,12,8,10,12; 18,14,14,0,12,2,10,4,8,6,8,10,6,8,10;6,4,2,4,0,6,2,8,4,6,8,10,10,10,12;14,12,10,12,10,0,8,2,6,4,6,8,4,6,8;8,6,4,6,2,8,0,10,2,4,6,8,12,8,10;12,10,8,10,8,12,6,0,4,2,4,6,2,4,6;10,8,6,8,4,10,2,12,0,2,4,6,14,6,8;12,10,8,10,6,12,4,14,2,0,2,4,16,4,6;14,12,10,12,8,14,6,16,4,2,0,2,18,2,4;16,14,12,14,10,16,8,18,6,4,2,0,20,4,6;10,8,6,8,8,10,10,2,12,14,16,18,0,2,4;8,6,4,6,6,8,8,10,10,12,14,16,12,0,2;6,4,2,4,4,6,6,8,8,10,12,14,10,12,0')
_TIEMPO_ENTRE_ESTACIONES2 = np.mat('0  ,2  ,4  ,6  ,6  ,8  ,8  ,10 ,10 ,12 ,14 ,16 ,12 ,14 ,16 ;2,0,2,4,4,6,6,8,8,10,12,14,10,12,14;4,2,0,2,2,4,4,6,6,8,10,12,8,10,12;18,16,12,0,12,2,10,4,8,6,8,10,6,8,10;6,4,2,4,0,6,2,8,4,6,8,10,10,12,14;16,14,12,14,10,0,8,2,6,4,6,8,4,6,8;8,6,4,6,2,8,0,10,2,4,6,8,12,8,10;14,12,10,12,8,14,6,0,4,2,4,6,2,4,6;10,8,6,8,4,10,2,12,0,2,4,6,14,6,8;12,10,8,10,6,12,4,14,2,0,2,4,16,4,6;10,8,6,8,8,10,6,12,4,2,0,2,14,2,4;12,10,8,10,10,12,8,14,6,4,2,0,16,4,6;10,8,6,8,8,10,10,2,12,14,16,18,0,2,4;8,6,4,6,6,8,8,10,10,12,14,16,12,0,2;6,4,2,4,4,6,6,8,8,10,12,14,10,12,0')
_TIEMPO_ENTRE_ESTACIONES3 = np.mat('0,2,4,6,6,8,8,10,10,12,14,16,12,14,16;2,0,2,4,4,6,6,8,8,10,12,14,10,12,14;4,2,0,2,2,4,4,6,6,8,10,12,8,10,12;16,14,12,0,14,2,16,4,18,6,8,10,6,8,10;6,4,2,4,0,6,2,8,4,6,8,10,10,12,14;14,12,10,12,12,0,14,2,16,4,6,8,4,6,8;8,6,4,6,2,8,0,10,2,4,6,8,12,8,10;12,10,8,10,10,12,6,0,4,2,4,6,2,4,6;10,8,6,8,4,10,2,12,0,2,4,6,14,6,8;12,10,8,10,6,12,4,14,2,0,2,4,16,4,6;10,8,6,8,8,10,6,12,4,2,0,2,14,2,4;12,10,8,10,10,12,8,14,6,4,2,0,16,4,6;10,8,6,8,8,10,10,2,12,14,16,18,0,2,4;8,6,4,6,6,8,8,10,10,12,14,16,12,0,2;6,4,2,4,4,6,6,8,8,10,12,14,10,12,0')
_TIEMPO_ENTRE_ESTACIONES = [_TIEMPO_ENTRE_ESTACIONES1, _TIEMPO_ENTRE_ESTACIONES2, _TIEMPO_ENTRE_ESTACIONES3]

# Se sacará de base de datos
#Topologias por rutas y trayectos, teniendo en cuenta viajes 'indirectos'
_TOPOLOGIA1 = np.mat('0,1,1,0,1,0,1,0,1,1,1,1,0,0,0;0,0,1,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,1,0,1,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,1,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA2 = np.mat('0,1,1,1,0,1,0,1,0,1,1,1,0,0,0;0,0,1,1,0,1,0,1,0,1,1,1,0,0,0;0,0,0,1,0,1,0,1,0,1,1,1,0,0,0;0,0,0,0,1,1,1,1,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,1,0,1,1,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA3 = np.mat('0,1,1,1,0,1,0,1,0,0,0,0,1,1,1;0,0,1,1,0,1,0,1,0,0,0,0,1,1,1;0,0,0,1,0,1,0,1,0,0,0,0,1,1,1;1,1,1,0,0,1,0,1,0,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,0,0,1,0,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,1,0,0,0,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA4 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,1,0,1,0,0,0,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,0,1,0,0,0,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,0,0,0,0,1,0,0;1,1,1,1,1,1,1,1,1,0,0,0,1,0,0;1,1,1,1,1,1,1,1,1,1,0,0,1,0,0;1,1,1,1,1,1,1,1,1,1,1,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA5 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,1,0,1,0,0,0,0,1,1,1;1,1,1,1,0,1,0,1,0,0,1,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,1,1,1,1,1,0,1;1,1,1,1,1,1,1,1,1,1,1,1,1,1,0')
_TOPOLOGIA6 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,1,1,1,1,0,1,1;1,1,1,1,1,1,1,1,1,1,1,1,1,0,1;1,1,1,1,1,1,1,1,1,1,1,1,1,1,0')

_TOPOLOGIA11 = np.mat('0,1,1,0,1,0,1,0,1,1,1,1,0,0,0;0,0,1,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,1,0,1,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,1,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA22 = np.mat('0,1,1,1,0,1,0,1,0,1,1,1,0,0,0;0,0,1,1,0,1,0,1,0,1,1,1,0,0,0;0,0,0,1,0,1,0,1,0,1,1,1,0,0,0;0,0,0,0,1,1,1,1,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,1,0,1,1,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA33 = np.mat('0,1,1,1,0,1,0,1,0,0,0,0,1,1,1;0,0,1,1,0,1,0,1,0,0,0,0,1,1,1;0,0,0,1,0,1,0,1,0,0,0,0,1,1,1;1,1,1,0,1,1,1,1,1,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,0,1,1,1,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,0,1,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA44 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,1,0,1,0,0,0,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,0,1,0,0,0,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,0,0,0,0,1,0,0;1,1,1,1,1,1,1,1,1,1,0,0,1,0,0;1,1,1,1,1,1,1,1,1,1,1,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA55 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,1,0,1,0,0,0,0,1,1,1;1,1,1,1,0,1,0,1,0,0,1,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,1,1,1,1,1,0,0;1,1,1,1,1,1,1,1,1,1,1,1,1,1,0')
_TOPOLOGIA66 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,1,1,1,1,0,1,1;1,1,1,1,1,1,1,1,1,1,1,1,1,0,1;1,1,1,1,1,1,1,1,1,1,1,1,1,1,0')

_TOPOLOGIA = [[_TOPOLOGIA1, _TOPOLOGIA4],
              [_TOPOLOGIA2, _TOPOLOGIA5],
              [_TOPOLOGIA3, _TOPOLOGIA6]]

#Indican las estaciones por donde pasa la ruta
_TOPOLOGIA_Directo = np.mat('''1,1,1,0,1,0,1,0,1,1,1,1,0,0,0;
                               1,1,1,1,0,1,0,1,0,1,1,1,0,1,1;
                               1,1,1,1,0,1,0,1,0,0,0,0,1,1,1
  ''')

_TRAYECTOS = [{1:'Ida',2:'Vuelta'},{3:'Ida',4:'Vuelta'},{5:'Ida',6:'Vuelta'}] # Se obtiene de base de datos

# Se sacará de base de datos
_MEJOR_SECUENCIAr1 =[   [[1,1],[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[1,10],[1,11],[1,12],[1,13],[1,14],[1,15]],
                        [[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],[2,11],[2,12],[2,13],[2,14],[2,15]],
                        [[3,1],[3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],[3,11],[3,12],[3,13],[3,14],[3,15]],
                        [[4,1],[4,2],[4,3],[4,4],[4,10,5],[4,6],[4,10,7],[4,8],[4,10,9],[4,10],[4,11],[4,12],[4,13],[4,14],[4,15]],
                        [[5,1],[5,2],[5,3],[5,3,4],[5,5],[5,3,6],[5,7],[5,3,8],[5,9],[5,10],[5,11],[5,12],[5,3,13],[5,11,14],[5,11,15]],
                        [[6,1],[6,2],[6,3],[6,3,4],[6,10,5],[6,6],[6,10,7],[6,8],[6,10,9],[6,10],[6,11],[6,12],[6,13],[6,14],[6,15]],
                        [[7,1],[7,2],[7,3],[7,3,4],[7,5],[7,3,6],[7,7],[7,3,8],[7,9],[7,10],[7,11],[7,12],[7,3,13],[7,11,14],[7,11,15]],
                        [[8,1],[8,2],[8,3],[8,3,4],[8,10,5],[8,3,6],[8,10,7],[8,8],[8,10,9],[8,10],[8,11],[8,12],[8,13],[8,14],[8,15]],
                        [[9,1],[9,2],[9,3],[9,3,4],[9,5],[9,3,6],[9,7],[9,3,8],[9,9],[9,10],[9,11],[9,12],[9,3,13],[9,11,14],[9,11,15]],
                        [[10,1],[10,2],[10,3],[10,3,4],[10,5],[10,3,6],[10,7],[10,3,8],[10,9],[10,10],[10,11],[10,12],[10,3,13],[10,11,14],[10,11,15]],
                        [[11,1],[11,2],[11,3],[11,3,4],[11,5],[11,3,6],[11,7],[11,3,8],[11,9],[11,10],[11,11],[11,12],[11,3,13],[11,14],[11,15]],
                        [[12,1],[12,2],[12,3],[12,3,4],[12,5],[12,3,6],[12,7],[12,3,8],[12,9],[12,10],[12,11],[12,12],[12,3,13],[12,14],[12,15]],
                        [[13,1],[13,2],[13,3],[13,3,4],[13,3,5],[13,3,6],[13,3,7],[13,3,8],[13,3,9],[13,3,10],[13,3,11],[13,3,12],[13,13],[13,14],[13,15]],
                        [[14,1],[14,2],[14,3],[14,3,4],[14,3,5],[14,3,6],[14,3,7],[14,3,8],[14,3,9],[14,3,10],[14,3,11],[14,3,12],[14,3,13],[14,14],[14,15]],
                        [[15,1],[15,2],[15,3],[15,3,4],[15,3,5],[15,3,6],[15,3,7],[15,3,8],[15,3,9],[15,3,10],[15,3,11],[15,3,12],[15,3,13],[15,3,14],[15,15]]
                    ]

_MEJOR_SECUENCIAr2 =[   [[1,1],[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[1,10],[1,11],[1,12],[1,13],[1,14],[1,15]],
                        [[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],[2,11],[2,12],[2,13],[2,14],[2,15]],
                        [[3,1],[3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],[3,11],[3,12],[3,13],[3,14],[3,15]],
                        [[4,1],[4,2],[4,3],[4,4],[4,10,5],[4,6],[4,10,7],[4,8],[4,10,9],[4,10],[4,11],[4,12],[4,13],[4,14],[4,15]],
                        [[5,1],[5,2],[5,3],[5,3,4],[5,5],[5,3,6],[5,7],[5,3,8],[5,9],[5,10],[5,11],[5,12],[5,3,13],[5,11,14],[5,11,15]],
                        [[6,1],[6,2],[6,3],[6,3,4],[6,10,5],[6,6],[6,10,7],[6,8],[6,10,9],[6,10],[6,11],[6,12],[6,13],[6,14],[6,15]],
                        [[7,1],[7,2],[7,3],[7,3,4],[7,5],[7,3,6],[7,7],[7,3,8],[7,9],[7,10],[7,11],[7,12],[7,3,13],[7,11,14],[7,11,15]],
                        [[8,1],[8,2],[8,3],[8,3,4],[8,10,5],[8,3,6],[8,10,7],[8,8],[8,10,9],[8,10],[8,11],[8,12],[8,13],[8,14],[8,15]],
                        [[9,1],[9,2],[9,3],[9,3,4],[9,5],[9,3,6],[9,7],[9,3,8],[9,9],[9,10],[9,11],[9,12],[9,3,13],[9,11,14],[9,11,15]],
                        [[10,1],[10,2],[10,3],[10,3,4],[10,5],[10,3,6],[10,7],[10,3,8],[10,9],[10,10],[10,11],[10,12],[10,3,13],[10,11,14],[10,11,15]],
                        [[11,1],[11,2],[11,3],[11,3,4],[11,5],[11,3,6],[11,7],[11,3,8],[11,9],[11,10],[11,11],[11,12],[11,3,13],[11,14],[11,15]],
                        [[12,1],[12,2],[12,3],[12,3,4],[12,5],[12,3,6],[12,7],[12,3,8],[12,9],[12,10],[12,11],[12,12],[12,3,13],[12,14],[12,15]],
                        [[13,1],[13,2],[13,3],[13,3,4],[13,3,5],[13,3,6],[13,3,7],[13,3,8],[13,3,9],[13,3,10],[13,3,11],[13,3,12],[13,13],[13,14],[13,15]],
                        [[14,1],[14,2],[14,3],[14,3,4],[14,3,5],[14,3,6],[14,3,7],[14,3,8],[14,3,9],[14,3,10],[14,3,11],[14,3,12],[14,3,13],[14,14],[14,15]],
                        [[15,1],[15,2],[15,3],[15,3,4],[15,3,5],[15,3,6],[15,3,7],[15,3,8],[15,3,9],[15,3,10],[15,3,11],[15,3,12],[15,3,13],[15,3,14],[15,15]]
                    ]

_MEJOR_SECUENCIAr3 =[   [[1,1],[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[1,10],[1,11],[1,12],[1,13],[1,14],[1,15]],
                        [[2,1],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8],[2,9],[2,10],[2,11],[2,12],[2,13],[2,14],[2,15]],
                        [[3,1],[3,2],[3,3],[3,4],[3,5],[3,6],[3,7],[3,8],[3,9],[3,10],[3,11],[3,12],[3,13],[3,14],[3,15]],
                        [[4,1],[4,2],[4,3],[4,4],[4,3,5],[4,6],[4,3,7],[4,8],[4,3,9],[4,10],[4,11],[4,12],[4,13],[4,14],[4,15]],
                        [[5,1],[5,2],[5,3],[5,3,4],[5,5],[5,3,6],[5,7],[5,3,8],[5,9],[5,10],[5,11],[5,12],[5,3,13],[5,11,14],[5,11,15]],
                        [[6,1],[6,2],[6,3],[6,3,4],[6,3,5],[6,6],[6,3,7],[6,8],[6,3,9],[6,10],[6,11],[6,12],[6,13],[6,14],[6,15]],
                        [[7,1],[7,2],[7,3],[7,3,4],[7,5],[7,3,6],[7,7],[7,3,8],[7,9],[7,10],[7,11],[7,12],[7,3,13],[7,11,14],[7,11,15]],
                        [[8,1],[8,2],[8,3],[8,3,4],[8,3,5],[8,3,6],[8,3,7],[8,8],[8,3,9],[8,10],[8,11],[8,12],[8,13],[8,14],[8,15]],
                        [[9,1],[9,2],[9,3],[9,3,4],[9,5],[9,3,6],[9,7],[9,3,8],[9,9],[9,10],[9,11],[9,12],[9,3,13],[9,11,14],[9,11,15]],
                        [[10,1],[10,2],[10,3],[10,3,4],[10,5],[10,3,6],[10,7],[10,3,8],[10,9],[10,10],[10,11],[10,12],[10,3,13],[10,11,14],[10,11,15]],
                        [[11,1],[11,2],[11,3],[11,3,4],[11,5],[11,3,6],[11,7],[11,3,8],[11,9],[11,10],[11,11],[11,12],[11,3,13],[11,14],[11,15]],
                        [[12,1],[12,2],[12,3],[12,3,4],[12,5],[12,3,6],[12,7],[12,3,8],[12,9],[12,10],[12,11],[12,12],[12,3,13],[12,14],[12,15]],
                        [[13,1],[13,2],[13,3],[13,3,4],[13,3,5],[13,3,6],[13,3,7],[13,3,8],[13,3,9],[13,3,10],[13,3,11],[13,3,12],[13,13],[13,14],[13,15]],
                        [[14,1],[14,2],[14,3],[14,3,4],[14,3,5],[14,3,6],[14,3,7],[14,3,8],[14,3,9],[14,3,10],[14,3,11],[14,3,12],[14,3,13],[14,14],[14,15]],
                        [[15,1],[15,2],[15,3],[15,3,4],[15,3,5],[15,3,6],[15,3,7],[15,3,8],[15,3,9],[15,3,10],[15,3,11],[15,3,12],[15,3,13],[15,3,14],[15,15]]
                    ]
_MEJOR_SECUENCIA = [_MEJOR_SECUENCIAr1,_MEJOR_SECUENCIAr2, _MEJOR_SECUENCIAr3]

# Se sacará de base de datos
_SECUENCIA1 = np.array([1, 2, 3, 5, 7, 9, 10, 11, 12])
_SECUENCIA4 = np.array([12, 11, 10, 9, 7, 5, 3, 2, 1])
_SECUENCIA2 = np.array([1, 2, 3, 4, 6, 8, 10, 11, 12])
_SECUENCIA5 = np.array([12, 11, 14, 15, 3, 2, 1])
_SECUENCIA3 = np.array([1, 2, 3, 4, 6, 8, 13])
_SECUENCIA6 = np.array([13, 14, 15, 3, 2, 1])

_SECUENCIAS = [[_SECUENCIA1, _SECUENCIA4],
               [_SECUENCIA2, _SECUENCIA5],
               [_SECUENCIA3, _SECUENCIA6]
]

_Transbordo1 = 11
_Transbordo2 = 10, 11
_Transbordo3 = 0
_Transbordo4 = 3
_Transbordo5 = 3
_Transbordo6 = 3

_TRANSBORDOS = [[_Transbordo1, _Transbordo4],
                [_Transbordo2, _Transbordo5],
                [_Transbordo3, _Transbordo6],
               ]

NUMEROESTACIONES = 0

# Se sacará de base de datos
_DEMANDA_MEDIA = np.mat('''0 ,10,10,10,10,10,10,10,10,10,10,10,10,10,10;
                           10,0 ,10,10,10,10,10,10,10,10,10,10,10,10,10;
                           10,10,0 ,10,10,10,10,10,10,10,10,10,10,10,10;
                           10,10,10,0 ,10,10,10,10,10,10,10,10,10,10,10;
                           10,10,10,10,0 ,10,10,10,10,10,10,10,10,10,10;
                           10,10,10,10,10,0 ,10,10,10,10,10,10,10,10,10;
                           10,10,10,10,10,10,0 ,10,10,10,10,10,10,10,10;
                           10,10,10,10,10,10,10,0 ,10,10,10,10,10,10,10;
                           10,10,10,10,10,10,10,10,0 ,10,10,10,10,10,10;
                           10,10,10,10,10,10,10,10,10,0 ,10,10,10,10,10;
                           10,10,10,10,10,10,10,10,10,10,0 ,10,10,10,10;
                           10,10,10,10,10,10,10,10,10,10,10,0 ,10,10,10;
                           10,10,10,10,10,10,10,10,10,10,10,10,0 ,10,10;
                           10,10,10,10,10,10,10,10,10,10,10,10,10,0 ,10;
                           10,10,10,10,10,10,10,10,10,10,10,10,10,10,0 ''')
# Se sacará de base de datos
_PROPORCIONES = np.mat('''0,0.1,0.15,0.4,0.4,0.7,0.4,0.7,0.4,0.7,0.4,0.4,0.7,0.7,0.7;
                          0.1,0,0.1,0.1,0.2,0.4,0.4,0.7,0.4,0.7,0.4,0.4,0.7,0.7,0.7;
                          0.1,0.1,0,0.1,0.1,0.4,0.3,0.4,0.4,0.7,0.4,0.4,0.7,0.7,0.7;
                          0.2,0.1,0.1,0,0.2,0.1,0.2,0.2,0.2,0.5,0.4,0.4,0.7,0.7,0.7;
                          0.2,0.2,0.2,0.7,0,0.5,0.1,0.7,0.1,0.2,0.4,0.4,0.5,0.5,0.5;
                          0.2,0.2,0.1,0.1,0.3,0,0.3,0.1,0.3,0.2,0.3,0.3,0.4,0.5,0.5;
                          0.2,0.2,0.2,0.7,0.1,0.7,0,0.7,0.4,0.7,0.5,0.5,0.7,0.7,0.7;
                          0.2,0.2,0.2,0.1,0.3,0.2,0.7,0,0.4,0.1,0.4,0.4,0.1,0.4,0.4;
                          0.2,0.2,0.2,0.2,0.2,0.7,0.1,0.7,0,0.1,0.2,0.3,0.6,0.6,0.6;
                          0.2,0.2,0.2,0.7,0.2,0.7,0.2,0.5,0.1,0,0.1,0.2,0.5,0.6,0.6;
                          0.2,0.2,0.2,0.7,0.3,0.7,0.4,0.5,0.2,0.1,0,0.1,0.8,0.8,0.8;
                          0.2,0.2,0.3,0.7,0.4,0.7,0.5,0.5,0.3,0.2,0.1,0,0.8,0.8,0.8;
                          0.2,0.2,0.2,0.3,0.4,0.4,0.4,0.5,0.5,0.4,0.4,0.3,0,0.1,0.2;
                          0.2,0.2,0.2,0.2,0.4,0.4,0.4,0.5,0.5,0.4,0.4,0.6,0.2,0,0.1;
                          0.2,0.2,0.2,0.2,0.4,0.4,0.4,0.5,0.5,0.4,0.4,0.6,0.6,0.1,0
                            ''')
def obtenerDatosBase():
    db_host = 'admin.megaruta.co'
    usuario = 'rutamega_eqopt'
    clave = 'eedd8ae977b7f997ce92aa1b0'
    base_de_datos = 'rutamega_principal' #rutamega_principal
    dbr = MySQLdb.connect(host=db_host, user=usuario, passwd=clave,db=base_de_datos)
    cursor=dbr.cursor() # real
    query_quotes =  "SET sql_mode='ANSI_QUOTES'" # para que acepte tablas con "caracteres especiales"
    cursor.execute(query_quotes)
    sql = '''SELECT * FROM "estacion-matrices"'''
    sqlRutas = '''SELECT idruta FROM "estacion-matrices" group by idruta;'''
    sqlEstaciones = '''SELECT distinct estaciones  From(SELECT distinct idestacionorigen as estaciones FROM "estacion-matrices" union all SELECT distinct idestaciondestino FROM "estacion-matrices") estaciones'''
    sqlIdTrayectos = '''SELECT f.idtrayecto, b.idruta, f.sentidotrayecto FROM (SELECT idruta FROM "estacion-matrices" GROUP BY idruta)b LEFT JOIN trayecto f ON b.idruta = f.idruta;'''
    # try:
    cursor.execute(sql)
    # Obtenemos todos los registros en una lista de listas
    resultados = cursor.fetchall()
    cursor.execute(sqlRutas)
    rutas = cursor.fetchall()
    cursor.execute(sqlEstaciones)
    estaciones = cursor.fetchall()
    cursor.execute(sqlIdTrayectos)
    idTrayectos = cursor.fetchall()
    numEstaciones = len(estaciones)
    numRutas = len(rutas)
    matricesTiempo = []
    matricesTransbordo = []
    matDemanda = np.zeros((numEstaciones, numEstaciones))
    matProporcion = np.zeros((numEstaciones, numEstaciones))
    # print len(resultados)
    iR = 0
    for ruta in range(numRutas):
        matTiempo = np.zeros((numEstaciones, numEstaciones))
        matTransbordo = np.zeros((numEstaciones, numEstaciones))
        for j in range(numEstaciones):
            for i in range(numEstaciones):
                if i!=j:
                    # print numEstaciones*ruta + iR
                    registro = resultados[iR]
                    matTiempo[i,j] = registro[4]
                    matTransbordo[i,j] = registro[7]
                    if registro[3]:
                        matDemanda[i,j] = registro[3]
                    if registro[8]:
                        matProporcion[i,j] = registro[8]
                    iR +=1
            # jR +=1

        matricesTiempo.append(matTiempo)
        matricesTransbordo.append(matTransbordo)
    # print np.array(matricesTiempo)
    # print np.array(matricesTransbordo)
    print np.array(rutas)
    # for x in resultados[224:239]:
    #     print x
    # except:
    #    print "Error: No se pudo obtener los datos"


    # 'num_rows' needed to reshape the 1D NumPy array returend by 'fromiter'
    # in other words, to restore original dimensions of the results set
    # num_rows = int(cursor.rowcount)
    # print num_rows


# obtenerDatosBase()

def numeroEstaciones():
    global NUMEROESTACIONES
    for ruta in _SECUENCIAS:
        for secuencia in ruta:
            maximo = secuencia.max()
            if maximo > NUMEROESTACIONES:
                NUMEROESTACIONES = maximo
    return NUMEROESTACIONES
numeroEstaciones()

def tiempoEntreEstaciones():
    _tiempoEntreEstaciones = []
    for ruta in _SECUENCIAS:
        _tiempoEntreEstacionesT = np.zeros(shape=(NUMEROESTACIONES,NUMEROESTACIONES))
        # print ruta
        for secuencia in ruta:
            # print secuencia
            secuenciaN = secuencia-1
            for i, act in enumerate(secuenciaN[:-1]):
                # print i, act, secuenciaN[:-1]
                siguiente = secuenciaN[i+1]
                _tiempoEntreEstacionesT[act,siguiente] = 2 # Distancia entre estaciones
            for k in range(1,len(secuenciaN[:-1])):
                for i, sec in enumerate(secuenciaN[:-1]):
                    if i+k <= len(secuenciaN)-2:
                        siguiente = secuenciaN[i+k]
                        if siguiente != secuenciaN[-1]:
                            j = secuenciaN[i+k+1]
                            # for j in secuenciaN[i+2:-1]:
                                # print _tiempoEntreEstacionesT[sec,j], _tiempoEntreEstacionesT[sec,siguiente], _tiempoEntreEstacionesT[siguiente, j]
                                # print sec, j, " : ", sec, siguiente, " , ", siguiente, j, secuenciaN[i+2:-1]
                            _tiempoEntreEstacionesT[sec,j] = _tiempoEntreEstacionesT[sec,siguiente] + _tiempoEntreEstacionesT[siguiente, j]


        _tiempoEntreEstaciones.append(_tiempoEntreEstacionesT)
    return _tiempoEntreEstaciones

def mejoresSecuencias():
    _mejoresSecuencias = []
    _tiempoEntreEstaciones = tiempoEntreEstaciones()
    for i in range(NUMEROESTACIONES):
        fila = []
        for j in range(NUMEROESTACIONES):
            minimo = 200
            _mejorSecuencia = []
            for ruta in _tiempoEntreEstaciones:
                tiempo = ruta[i,j]
                if tiempo != 0 and tiempo <= minimo:
                    minimo = tiempo
                    _mejorSecuencia = [i+1, j+1]
            if j == i:
                _mejorSecuencia = [i+1, j+1]
            fila.append(_mejorSecuencia)
        _mejoresSecuencias.append(fila)
    for i, fila in enumerate(_mejoresSecuencias):
        for j, secuencia in enumerate(fila):
            if len(secuencia) == 0:
                minimo = 200
                for indRuta1, ruta1 in enumerate(_SECUENCIAS):
                    # rutaN = []
                    # trayectoN = []
                    for trayecto in ruta1:
                        secuenciaN = trayecto-1
                        if j in secuenciaN:
                            r = np.array(range(len(secuenciaN==j)))
                            index = int(r[secuenciaN==j])
                            for estacionI in secuenciaN[:index]: # Estación intermedia
                                minimoN = _tiempoEntreEstaciones[indRuta1][estacionI, j]
                                for indRuta2, ruta2 in enumerate(_SECUENCIAS):
                                    for trayecto2 in ruta2:
                                        secuenciaN2 = trayecto2-1
                                        if estacionI in secuenciaN2:
                                            r1 = np.array(range(len(secuenciaN2==estacionI)))
                                            index1 = int(r1[secuenciaN2==estacionI])
                                            if i in secuenciaN2[:index1]:
                                                minimoN += _tiempoEntreEstaciones[indRuta2][i, estacionI]
                                                if minimoN < minimo:
                                                    minimo = minimoN
                                                    _mejoresSecuencias[i][j] = [i+1, estacionI+1, j+1]
    _mejoresSecuencias[14][13] = [15,3,13,14]
    _mejoresSecuencias[5][3]   = [6,3,4]
    _mejoresSecuencias[7][3]   = [8,3,4]
    _mejoresSecuencias[7][5]   = [8,3,6]
    # sec = _SECUENCIAS[0][0]-1
    # _mejorSecuenciaR1 = []
    # for i in sec[:-1]:
    #     _mejorSecuenciaR1.append(np.array(_mejoresSecuencias)[i,i+1])




    return np.array(_mejoresSecuencias)


def transbordos(model= None):
    _mejoresSecuencias = mejoresSecuencias()
    _mejoresSecuenciasN = []
    for ir ,ruta in enumerate(_SECUENCIAS):
        r = []
        for it, trayecto in enumerate(ruta):
            tr = np.zeros(shape=(NUMEROESTACIONES,NUMEROESTACIONES))
            if ir == 2 and it == 1:
                sec = np.concatenate((ruta[0]-1,ruta[1]-1))
            else:
                sec = trayecto-1
            # print sec
            for i, act in enumerate(sec):
                for j in range(NUMEROESTACIONES):
                    if len(_mejoresSecuencias[act,j])>=3 and _mejoresSecuencias[act,j][1] != 13:
                        estaTrans = _mejoresSecuencias[act,j][1]
                        if np.in1d(estaTrans, sec[i:]+1):
                            tr[act,j] = estaTrans
            r.append(tr)
        _mejoresSecuenciasN.append(np.array(r))

    _mejorSecuenciaR = []
    for ruta in range(len(_SECUENCIAS)):
        r = []
        for trayecto in range(len(_SECUENCIAS[ruta])):
            tr = []
            sec = _SECUENCIAS[ruta][trayecto]-1
            # print sec
            for i, act in enumerate(sec):
                fila = []
                for j in range(NUMEROESTACIONES):
                    fila.append(_mejoresSecuenciasN[ruta][trayecto][act,j])
                    # fila.append(_mejoresSecuencias[act][j])
                # print i,
                tr.append(np.array(fila))
            # print "\n"
            r.append(np.array(tr))
        _mejorSecuenciaR.append(np.array(r))

    # return np.array(_mejorSecuenciaR)
    return np.array(_mejoresSecuenciasN)

def transbordoE(r):
    _mejoresSecuencias = mejoresSecuencias()
    ruta = _SECUENCIAS[r]
    tr = np.zeros(shape=(NUMEROESTACIONES,NUMEROESTACIONES))
    sec = np.concatenate((ruta[0]-1,ruta[1]-1))
    # print sec
    for i, act in enumerate(sec):
        for j in range(NUMEROESTACIONES):
            if len(_mejoresSecuencias[act,j])>=3 and _mejoresSecuencias[act,j][1] != 13:
                estaTrans = _mejoresSecuencias[act,j][1]
                if np.in1d(estaTrans, sec[i:]+1):
                    tr[act,j] = estaTrans
    return tr

def tiempoEsperaMaximo(t, model= None):
    suma = np.zeros(shape=(NUMEROESTACIONES, NUMEROESTACIONES))
    if model:
        for r in range(len(model)):

            for i in range(suma.shape[0]):
                for j in range(suma.shape[1]):
                    suma[i,j] += _TOPOLOGIA[r][t][i,j]*model[r]
    else:
        for r in range(len(FrecuenciasOptimas)):
            if r == 0:
                suma = _TOPOLOGIA[r][t]*FrecuenciasOptimas[r]
            else:
                suma += _TOPOLOGIA[r][t]*FrecuenciasOptimas[r]
    with np.errstate(divide='ignore'):
        result = 1/suma
    result[np.isinf(result)] = 0

    # print result
    return result
    # return np.around(result, decimals = 2)

def tiempoEsperaMaximoTot(model= None):
    suma = np.zeros(shape=(NUMEROESTACIONES, NUMEROESTACIONES))
    topologiaTotV = topologiaTot(model)
    if model:
        for r in range(len(model)):#FrecuenciasOptimas)):
            # suma += topologiaTotV[r]*value(model[r])
            for i in range(suma.shape[0]):
                for j in range(suma.shape[1]):
                    suma[i,j] += topologiaTotV[r][i,j]*model[r]
    else:
        for r in range(len(FrecuenciasOptimas)):
            if r == 0:
                suma = topologiaTotV[r]*FrecuenciasOptimas[r]#value(FrecuenciasOptimas[r]))
            else:
                suma += topologiaTotV[r]*FrecuenciasOptimas[r]#value(FrecuenciasOptimas[r]))

    with np.errstate(divide='ignore'):
        result = 1/suma

    # for i in range(result.shape[0]):
    #     for j in range(result.shape[1]):
    #         topologia1 = 0
    #         topologia2 = 0
    #         for r in range(len(FrecuenciasOptimas)):
    #             secuencia = _MEJOR_SECUENCIA[r][i][j]
    #             if len(secuencia)== 3:
    #                 topologia1 += topologiaTotV[r][secuencia[0]-1,secuencia[1]-1]*FrecuenciasOptimas[r]
    #                 topologia2 += topologiaTotV[r][secuencia[1]-1,secuencia[2]-1]*FrecuenciasOptimas[r]
    #                 if r == 2:
    #                     result[i,j] = (1/topologia1) + (1/topologia2)

    result[np.isinf(result)] = 0
    return result
    #return np.around(result, decimals = 2)

def tiempoEsperaPromedio(t, model= None):
    return tiempoEsperaMaximo(t, model)/2

def tiempoEsperaPromedioTot(model= None):
    return tiempoEsperaMaximoTot(model)/2

def matrizDemandaMedia(model= None):
    a = 0.4*np.array(tiempoEsperaPromedioTot(model))*np.array(_DEMANDA_MEDIA)
    return (a + np.array(_DEMANDA_MEDIA)) * np.array(_PROPORCIONES)

def topologiaTot(model= None):
    '''
    Topologia sin trayectos
    '''
    _MatrizTopologia = []
    for x in _TOPOLOGIA:
        _MatrizTopologia.append(x[0] + x[1])
    return _MatrizTopologia

def probabilidadEleccion(r, t, model= None):
    topologia = np.array(_TOPOLOGIA[r][t])
    if model:
        frecuencia = model[r]#FrecuenciasOptimas[r]
    else:
        frecuencia = FrecuenciasOptimas[r]
    tiempoEsperaM = np.array(tiempoEsperaMaximo(t, model))
    return topologia*tiempoEsperaM*frecuencia

def distribucionDemanda(r, t, model= None):
    return np.array(matrizDemandaMedia(model))*np.array(probabilidadEleccion(r, t, model))

def pasajerosEstacion(r, t, model= None):
    return distribucionDemanda(r, t, model).sum(axis= 1)

def pasajerosEstaValid(r, t, model= None):
    x = pasajerosEstacion(r, t, model)
    x[x>0] = 1
    # for i in range(x.shape[0]):
    #     if value(x[i]) >= 0.000001:
    #         x[i] = 1
    return x

def pasajerosPuedenAbordar(r, t, model= None):
    '''
        Crea matriz de los pasajeros que pueden abordar, un vector de los que pueden subir y  un vector de capacidades.
    '''
    secuencia = _SECUENCIAS[r][t]-1 # Toma la secuencia utilizara por la ruta r en el trayecto t
    pasajeros = pasajerosEstacion(r, t, model)
    capacidad = np.zeros(shape=(NUMEROESTACIONES)) # Se crea un arreglo de zeros con tamaño igual al numero de estaciones
    puedenSubir = np.zeros(shape=(NUMEROESTACIONES)) # Se crea un arreglo de zeros con tamaño igual al numero de estaciones
    _pasajerosPuedenAbordar = np.zeros(shape=(NUMEROESTACIONES,NUMEROESTACIONES)) # Se crea una matriz cuadrada de zeros con tamaño igual al numero de estaciones
    mTransbordo = transbordos(model)[r,t]
    i = secuencia[0] # Se toma la estación inicial
    capacidad[i] = CAPACIDADBUSES - pasajeros[i] # Se inicializa el arreglo de capacidades
    puedenSubir[i] = CAPACIDADBUSES # Se inicializa el arreglo de puedenSubir
    if puedenSubir[i] >= pasajeros[i]:
        _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t, model)[i,:]
    else:
        _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t, model)[i,:] / (pasajeros[i]*puedenSubir[i])
    if t == 0: # Si el trayecto es de ida
        for iS, i in enumerate(secuencia[1:]):

            valido = pasajerosEstaValid(r, t, model)[i]
            anterior = secuencia[iS]

            pasajerosSuma = _pasajerosPuedenAbordar[:i,i].sum()
            pasajerosTransbordo = 0
            if np.in1d(i+1, mTransbordo):
                mTransbordoB = mTransbordo == i+1
                pasajerosTransbordo = _pasajerosPuedenAbordar[mTransbordoB].sum()

            if capacidad[anterior] > round(pasajeros[i]):
                capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma + pasajerosTransbordo
            else:
                capacidad[i] = 0

            if capacidad[anterior] > 0:
                puedenSubir[i] = (capacidad[anterior] + pasajerosSuma + pasajerosTransbordo)*valido
            else:
                puedenSubir[i] = (pasajerosSuma + pasajerosTransbordo)*valido
            if round(puedenSubir[i]) >= pasajeros[i]:
                _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r, t, model)[i,:]
            else:
                _pasajerosPuedenAbordar[i,:] = (distribucionDemanda(r, t, model)[i,:]/pasajeros[i])*puedenSubir[i]
            # print _MEJOR_SECUENCIA[r][i-1][i]
    else: # Si el trayecto es de Vuelta
        if r == 2 and t == 1: # Si es un final fantasma

            puedAbordI               = pasajerosPuedenAbordar(r, 0, model)
            pasajerosPuedenAbordarI  = puedAbordI[0]
            capacidadI               = puedAbordI[2]#[_SECUENCIAS[r][0][-1]-1]
            # puedenSubirI             = puedAbordI[1]#[:_SECUENCIAS[r][0][-1]-1,secuencia[1]]
            secuenciaI               = _SECUENCIAS[r][0]-1
            anterior                 = secuenciaI[-1]
            mTransbordoI             = transbordos(model)[r,0]

            pasajerosSuma = 0
            for x in secuenciaI:
                    pasajerosSuma += pasajerosPuedenAbordarI[x,i]

            if capacidad[anterior] > 0:
                puedenSubir[i] = capacidadI[anterior] + pasajerosSuma
            else:
                puedenSubir[i] = pasajerosSuma

            if capacidad[anterior] > round(pasajeros[i]):
                capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma
            else:
                capacidad[i] = 0
            # print puedenSubir[i]
            if round(puedenSubir[i]) >= pasajeros[i]:
                _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t, model)[i,:]
            else:
                _pasajerosPuedenAbordar[i,:] = (distribucionDemanda(r,t, model)[i,:]/pasajeros[i])*puedenSubir[i]

            for iS, i in enumerate(secuencia[1:]): # iS -> Contador, i -> Estacion secuencia
                valido = pasajerosEstaValid(r, t, model)[i]
                anterior = secuencia[iS]
                pasajerosSuma  = 0
                pasajerosSumaI = 0
                if np.in1d(i+1, secuenciaI):
                    for x in secuenciaI[i:]:
                        pasajerosSumaI += pasajerosPuedenAbordarI[x,i]
                else:
                    for x in secuenciaI:
                        pasajerosSumaI += pasajerosPuedenAbordarI[x,i]

                for x in secuencia[:iS+1]:
                    pasajerosSuma += _pasajerosPuedenAbordar[x,i]

                pasajerosTransbordo = 0
                if np.in1d(i+1, mTransbordo) or np.in1d(i+1, mTransbordoI):
                    mTransbordoB = mTransbordo == i+1
                    mTransbordoBI = mTransbordoI > 0 # mTransbordo == i+1 Temporalmente > 0 por error de minimizacion en excel
                    pasajerosTransbordo = _pasajerosPuedenAbordar[mTransbordoB].sum() + pasajerosPuedenAbordarI[mTransbordoBI].sum()

                if capacidad[anterior] > 0:
                    puedenSubir[i] = (capacidadI[anterior] + pasajerosSuma + pasajerosSumaI + pasajerosTransbordo)*valido
                else:
                    puedenSubir[i] = (pasajerosSuma +  pasajerosSumaI + pasajerosTransbordo)*valido

                if capacidad[anterior] > round(pasajeros[i]):
                    capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma + pasajerosSumaI + pasajerosTransbordo

                if round(puedenSubir[i]) >= pasajeros[i]:
                    _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t, model)[i,:]
                else:
                    _pasajerosPuedenAbordar[i,:] = (distribucionDemanda(r,t, model)[i,:]/pasajeros[i])*puedenSubir[i]
        else:
            for iS, i in enumerate(secuencia[1:]):

                valido = pasajerosEstaValid(r, t, model)[i]
                anterior = secuencia[iS]
                pasajerosSuma = 0#_pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i].sum()
                # pasajerosSuma = _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i].sum()
                for x in secuencia[:iS+1]:
                    pasajerosSuma += _pasajerosPuedenAbordar[x,i]

                pasajerosTransbordo = 0
                if np.in1d(i+1, mTransbordo):
                    mTransbordoB = mTransbordo == i+1
                    pasajerosTransbordo = _pasajerosPuedenAbordar[mTransbordoB].sum()

                if capacidad[anterior] > round(pasajeros[i]):
                    capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma + pasajerosTransbordo
                else:
                    capacidad[i] = 0

                if capacidad[anterior] > 0:
                    puedenSubir[i] = (capacidad[anterior] + pasajerosSuma + pasajerosTransbordo)*valido
                else:
                    puedenSubir[i] = (pasajerosSuma + pasajerosTransbordo)*valido
                    # print i,anterior, puedenSubir[i], _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i]
                if round(puedenSubir[i]) >= pasajeros[i]:
                    _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t, model)[i,:]
                else:
                    _pasajerosPuedenAbordar[i,:] = (distribucionDemanda(r,t, model)[i,:]/pasajeros[i])*puedenSubir[i]
    # print np.around(puedenSubir, decimals= 0)
    # print capacidad
    # print np.rint(pasajeros)
    return [_pasajerosPuedenAbordar, puedenSubir, capacidad]


def tiempoEsperaEstaciones(r, t, model= None):
    return pasajerosPuedenAbordar(r,t,model)[0]*TIEMPOABORDAR

def tiempoAcumuladoBajada(r, t, model= None):
    tiempoEspera  = tiempoEsperaEstaciones(r,t, model)
    mTransbordo   = transbordos(model)[r,t]
    tiempoEsperaI = 0
    suma = np.zeros(shape=(NUMEROESTACIONES))
    _tiempoBajada = np.zeros(shape=(NUMEROESTACIONES,NUMEROESTACIONES))
    secuencia = _SECUENCIAS[r][t]-1
    for i, e in enumerate(secuencia):
        if t == 0:
            suma[e] = tiempoEspera[:e,e].sum()
        else:
            suma[e] = tiempoEspera[secuencia[:i],e].sum()
            if r==2:
                tiempoEsperaI = tiempoEsperaEstaciones(r,0, model)
                secuenciaI = _SECUENCIAS[r][0]-1
                if np.in1d(e, secuenciaI):
                    suma[e] += tiempoEsperaI[secuenciaI[e:],e].sum() # Revisar
                else:
                    suma[e] += tiempoEsperaI[secuenciaI,e].sum()
        if np.in1d(e+1, mTransbordo):
            mTransbordoB = mTransbordo == e+1
            suma[e] += tiempoEspera[mTransbordoB].sum()
            if r==2:
                suma[e] += tiempoEsperaI[mTransbordoB].sum()
        if i>0 and t==0:
            _tiempoBajada[e,secuencia[i-1]] = suma[e]

    if t == 0:
        for iS, i in enumerate(secuencia):
            for j in range(iS+1,len(secuencia)):
                _tiempoBajada[secuencia[j],i] = _tiempoBajada[secuencia[j-1],i] + suma[secuencia[j]]
        _tiempoBajada = np.transpose(_tiempoBajada)
    else:
        for iS, i in enumerate(secuencia):
            for j in range(iS+1,len(secuencia)):
                _tiempoBajada[i,secuencia[j]] = _tiempoBajada[i,secuencia[j-1]] + suma[secuencia[j]]
    return _tiempoBajada

def tiempoAcumuladoSubida(r, t, model= None):
    tiempoEspera = tiempoEsperaEstaciones(r,t, model)
    suma = tiempoEspera.sum(axis=1)
    _tiempoSubida = np.zeros(shape=(NUMEROESTACIONES,NUMEROESTACIONES))
    np.fill_diagonal(_tiempoSubida,suma)
    secuencia = _SECUENCIAS[r][t] -1
    if t == 0:
        for iS, i in enumerate(secuencia):
            for j in range(iS+1,len(secuencia)):
                _tiempoSubida[secuencia[j],i] = _tiempoSubida[secuencia[j-1],i] + suma[secuencia[j]]
        _tiempoSubida = np.transpose(_tiempoSubida)
    else:
        for iS, i in enumerate(secuencia):
            for j in range(iS+1,len(secuencia)):
                _tiempoSubida[i,secuencia[j]] = _tiempoSubida[i,secuencia[j-1]] + suma[secuencia[j]]
    return _tiempoSubida

def tiempoViajePromedio(r, t, model= None):
    '''
    Matriz tiempo de viaje promedio
    '''
    # print value(FrecuenciasOptimas[0])
    tiempoEntreEstacionesM = _TIEMPO_ENTRE_ESTACIONES[r]
    tiempoEsperaPromedioM  = tiempoEsperaPromedio(t, model)
    tiempoAcumuladoSubidaM = tiempoAcumuladoSubida(r,t, model)
    tiempoAcumuladoBajadaM = tiempoAcumuladoBajada(r,t, model)
    _tiempoViajePromedio = np.zeros(shape=(NUMEROESTACIONES, NUMEROESTACIONES))
    secuencia = _SECUENCIAS[r][t]-1
    for i, ei in enumerate(secuencia):
        for ej in secuencia[i:]:
            _tiempoViajePromedio[ei,ej] = tiempoEntreEstacionesM[ei,ej] + tiempoEsperaPromedioM[ei,ej] + tiempoAcumuladoSubidaM[ei,ej] + tiempoAcumuladoBajadaM[ei,ej]
    # print _tiempoViajePromedio.sum(), model[0].value
    return _tiempoViajePromedio

# print np.around(tiempoViajePromedio(2,1), decimals = 1)
# print np.around(tiempoViajePromedio(2,1).sum(axis=0), decimals = 1)

def pasajerosEspera2Viaje(r,t, model= None):
    return distribucionDemanda(r,t, model) - pasajerosPuedenAbordar(r,t, model)[0]

# print np.around(pasajerosEspera2Viaje(2,1), decimals=1)
# print np.around(pasajerosEspera2Viaje(2,1).sum(), decimals=1)

def tiempoEsperaPor2Bus(t, model= None):
    return tiempoEsperaPromedio(t, model) + tiempoEsperaMaximo(t, model)

# print np.around(tiempoEsperaPor2Bus(1), decimals=2)

def tiempoEsperarPor2Viaje(r,t, model= None):
    pasajerosEspera2ViajeB = pasajerosEspera2Viaje(r,t, model)>0
    # pasajerosE2Vmat = pasajerosEspera2Viaje(r,t, model)
    # pasajerosEspera2ViajeB = np.zeros((NUMEROESTACIONES, NUMEROESTACIONES), dtype=bool)
    # for i in range(pasajerosE2Vmat.shape[0]):
    #     for j in range(pasajerosE2Vmat.shape[1]):
    #         if pasajerosE2Vmat[i,j] > 0:
    #             pasajerosEspera2ViajeB[i,j] = True

    _tiempoEsperarPor2Viaje = np.where(pasajerosEspera2ViajeB, tiempoEsperaPor2Bus(t, model), 0)
    return _tiempoEsperarPor2Viaje
# print np.around(tiempoEsperarPor2Viaje(2,1), decimals=1)

def frecuenciaTotal(t, model= None):
    _frecuenciaTotal = np.zeros(shape=(NUMEROESTACIONES, NUMEROESTACIONES))
    if model:
        for r, f in enumerate(model):
            _frecuenciaTotal += np.where(_TOPOLOGIA[r][t]>0, model[r], 0)#value(f), 0)
    else:
        for r, f in enumerate(FrecuenciasOptimas):
            _frecuenciaTotal += np.where(_TOPOLOGIA[r][t]>0, f, 0)#value(f), 0)
    return _frecuenciaTotal

# print np.around(frecuenciaTotal(1), decimals=2)

def funcionCalidad(t, model= None):
    return np.array(frecuenciaTotal(t, model))*np.array(tiempoEsperaPromedio(t, model))

# print np.around(funcionCalidad(1), decimals=2)

def serviciosRequeridos(r,t, model= None):
    return distribucionDemanda(r,t, model)/CAPACIDADBUSES

# print np.around(serviciosRequeridos(1,0), decimals=2)

def flujoAsignado(t, model= None):
    _flujoAsignado = np.zeros(shape=(NUMEROESTACIONES, NUMEROESTACIONES))
    for r in range(NUMERORUTAS):
        _flujoAsignado += np.where(_TOPOLOGIA[r][t]>0, serviciosRequeridos( r,t, model), 0)
    # print FrecuenciasOptimas
    return _flujoAsignado


def intervalosTiemposEntreSalidas():
    return 1/np.array(FrecuenciasOptimas)

def tiempoViajePromedioSinEsperaSB(r,t, model=None):
    '''
    Matriz tiempo de viaje promedio
    '''
    # print value(FrecuenciasOptimas[0])
    tiempoEntreEstacionesM = _TIEMPO_ENTRE_ESTACIONES[r]
    tiempoAcumuladoSubidaM = tiempoAcumuladoSubida(r,t, model)
    tiempoAcumuladoBajadaM = tiempoAcumuladoBajada(r,t, model)
    _tiempoViajePromedio = np.zeros(shape=(NUMEROESTACIONES, NUMEROESTACIONES))
    secuencia = _SECUENCIAS[r][t]-1
    for i, ei in enumerate(secuencia):
        for ej in secuencia[i:]:
            _tiempoViajePromedio[ei,ej] = tiempoEntreEstacionesM[ei,ej] + tiempoAcumuladoSubidaM[ei,ej] + tiempoAcumuladoBajadaM[ei,ej]
    # print _tiempoViajePromedio.sum(), model[0].value
    return _tiempoViajePromedio

def tiempoViajePromedioSinEspera(r,t, model=None):
    '''
    Matriz tiempo de viaje promedio
    '''
    # print value(FrecuenciasOptimas[0])
    tiempoEntreEstacionesM = _TIEMPO_ENTRE_ESTACIONES[r]
    _tiempoViajePromedio = np.zeros(shape=(NUMEROESTACIONES, NUMEROESTACIONES))
    secuencia = _SECUENCIAS[r][t]-1
    for i, ei in enumerate(secuencia):
        for ej in secuencia[i:]:
            _tiempoViajePromedio[ei,ej] = tiempoEntreEstacionesM[ei,ej]
    # print _tiempoViajePromedio.sum(), model[0].value
    return _tiempoViajePromedio
import datetime

def convertHour(horas = None, hora = None):
    if horas:
        horasD = []
        for i, x in enumerate(horas):
            horasD.append(str(datetime.timedelta(seconds= int(round(((x*24)*60)*60)))))
        # return np.vectorize(str(datetime.timedelta(minutes=x)))
        return np.array(horasD)
    elif hora:
        horaStr = str(datetime.timedelta(seconds= int(round(((hora*24)*60)*60))))
        if len(horaStr) == 7:
            horaStr = "0" + horaStr
        return horaStr


def horaInicioServicios(r):
    intervalosPeriodosRutas = intervalosTiemposEntreSalidas()[r]/(24*60)
    tiempoInicio = HORAINICIO/24
    tiempoFinal = HORAFIN/24
    # minutosTotales = (HORAINICIO - HORAFIN)*60 # Los convertimos en minutos
    horas = np.arange(tiempoInicio, tiempoFinal, intervalosPeriodosRutas)
    horasD = []
    # f = np.vectorize(convertHour)
    # result_array = f(horas)
    for i, x in enumerate(horas):
        horasD.append(str(datetime.timedelta(seconds= int(round(((x*24)*60)*60)))))
    # return np.array(horasD)
    return horas

def horaEstaciones(r,t, idT):
    horaInicio = horaInicioServicios(r)
    secuencia = _SECUENCIAS[r][t] -1
    tiempoSalida = tiempoViajePromedioSinEsperaSB(r,t)[secuencia[0],secuencia] / (24*60)
    tiempoLlegada = np.zeros(len(secuencia))
    # tiempoLlegada[1:] = tiempoSalida[:-1] + tiempoViajePromedioSinEspera(r,t)[secuencia[0],secuencia[1:]] / (24*60)
    for i in range(1,len(tiempoLlegada)):
        tiempoLlegada[i] = tiempoSalida[i-1] + tiempoViajePromedioSinEspera(r,t)[secuencia[i-1],secuencia[i]] / (24*60)
    _horaEstaciones = []
    for horaI in horaInicio[:12]:
        # _horaEstacionesLlegada = convertHour(horaI + tiempoLlegada)
        _horaEstacionesLlegada = (horaI + tiempoLlegada)
        # _horaEstacionesSalida = convertHour(horaI + tiempoSalida)
        _horaEstacionesSalida = (horaI + tiempoSalida)
        estacionInicio = np.zeros(len(secuencia), dtype=bool)
        estacionInicio[0] = True
        estacionFinal = np.zeros(len(secuencia), dtype=bool)
        estacionFinal[-1] = True
        idTrayecto = np.empty(len(secuencia))
        idTrayecto.fill(idT)
        _horaEstaciones.append(zip(_horaEstacionesLlegada, _horaEstacionesSalida, estacionInicio, estacionFinal, idTrayecto, secuencia))
    dtype = [('horaLlegada', float), ('horaSalida', float),('estacionInicio', bool), ('estacionFinal', bool),('idTrayecto', int), ('secuencia', int)]
    _horaEstaciones = np.array(_horaEstaciones, dtype)
    return _horaEstaciones


def horasRuta(r):
    horas = []
    rutaT = _TRAYECTOS[r]
    for t, value in rutaT.iteritems():
        if value == 'Ida':
            # horas.append(horaEstaciones(r,0,t))
            for horaE in horaEstaciones(r,0,t):
                horas.append((horaE[0]['horaLlegada'], horaE[-1]['horaSalida'], horaE[0]['idTrayecto']))
        else:
            for horaE in horaEstaciones(r,1,t):
                horas.append((horaE[0]['horaLlegada'], horaE[-1]['horaSalida'], horaE[0]['idTrayecto']))
    dtype= [('horaInicial', float), ('horaFinal', float), ('idTrayecto', int)]
    horas = np.array(horas, dtype)
    # print horas.shape, r, horas
    # horas = horas.reshape(rows*columns,horas.shape[2])
    return horas

def serviciosRuta(r, horas = None):
    if horas == None:
        horas = horasRuta(r)
    horasDict = []
    for i,hora in enumerate(horas):
        horasDict.append((i, hora['horaInicial'], hora['idTrayecto']))
    dtype = [('id', int),('horaLlegada', float), ('idTrayecto', int)]
    horasDictArray = np.array(horasDict, dtype)
    horasDictArray.sort(order='horaLlegada')
    pilaSalida = []
    servicios = []
    pilaSalida.append((0,horas[horasDictArray[0][0]]['horaFinal'], horasDictArray[0][2]))
    servicios.append((0, horasDictArray[0][0], horasDictArray[0][1], horasDictArray[0][2]))
    i = 1
    for x in horasDictArray[1:]:
        '''
        x[0] = id    x[1] = horaLlegada    x[2] = idTrayecto
        '''
        # pilaSalida.append((i,horas['horaFinal'][x[0]][-1], x[2]))
        typeD = [('servicio', int),('horaSalida', float), ('idTrayecto', int)]
        pilaSalidaArray = np.array(pilaSalida, typeD)
        pilaSalidaArray.sort(order='horaSalida')
        pilaTrayecto = pilaSalidaArray[pilaSalidaArray['idTrayecto'] != x[2]]
        # if pilaSalidaArray[0]['horaSalida'] < x[1]:
        if pilaTrayecto[0]['horaSalida'] < x[1]:
            servicios.append((pilaTrayecto[0]['servicio'], x[0], x[1], x[2]))
            del pilaSalida[pilaTrayecto[0]['servicio']]
            # pilaSalida.insert(pilaSalidaArray[0]['servicio'],(pilaSalidaArray[0]['servicio'], horas[:]['horaSalida'][x[0]][-1],x[2]))
            pilaSalida.insert(pilaTrayecto[0]['servicio'],(pilaTrayecto[0]['servicio'], horas[x[0]]['horaFinal'],x[2]))
        else:
            pilaSalida.append((i,horas[x[0]]['horaFinal'], x[2]))
            servicios.append((i, x[0], x[1], x[2]))
            i+=1
    # dtype = [('servicio', int), ('id', int), ('horaLlegada', float), ('idTrayecto', int)]
    return np.array(servicios)

def jsonFile():
    estructura = []
    tray = 0
    horaAnt = []
    for r, rutaT in enumerate(_TRAYECTOS):
        for t, value in rutaT.iteritems():
            estructura.append({'idtrayecto':t})
            serviciosEst = []
            if value == 'Ida':
                horas = horaEstaciones(r,0,t)
                horaAnt = horas
            else:
                horas = horaEstaciones(r,1,t)
            # print serviciosRuta(0)
            _serviciosRuta = serviciosRuta(r)
            _serviciosRutaB = _serviciosRuta[_serviciosRuta[:,-1]==t]
            for i, servicio in enumerate(_serviciosRutaB):
                horarios = {}
                serviciosDict = {'idservicio':int(servicio[0])+1}
                if value == 'Ida':
                    idLinea = servicio[1]
                else:
                    idLinea = servicio[1] - len(horaAnt)
                for i, hora in enumerate(horas[idLinea]):
                    # print hora
                    estacionesDict = {}
                    estacionesDict["idestacion"] = hora['secuencia']+1
                    estacionesDict["horallegada"] = convertHour(hora = hora['horaLlegada'])
                    estacionesDict["horasalida"] = convertHour(hora = hora["horaSalida"])
                    estacionesDict["estacioninicial"] = 'true' if hora["estacionInicio"] else 'false'
                    estacionesDict["estacionfinal"] = 'true' if hora["estacionFinal"] else 'false'
                    horarios[str(i)] = estacionesDict
                serviciosDict["horarios"] = horarios
                serviciosDict["orden"] = i
                serviciosEst.append(serviciosDict)
            estructura[tray]['servicios']= serviciosEst
            tray+=1
    out_file = open("horarios.json","w")
    json.dump(estructura,out_file, indent=4, sort_keys=True, separators=(',', ': '))
    out_file.close()
# jsonFile()
# print convertHour(hora= 0.2666)
serv =  serviciosRuta(1)#[serviciosRuta(1)[:,-1] == 3]
# serv.sort(order = 'servicio')
print serv[np.lexsort((serv[:,2], serv[:,0]))]
# print np.around(flujoAsignado(1), decimals=2)

# tiempoViajePromedioTot(1, 1)
# a = np.arange(12).reshape(4,3)
# print "numpy", a.sum(axis=0)

# print _PROPORCIONES, _PROPORCIONES.shape, type(_PROPORCIONES)
# print np.sum(_PROPORCIONES)


# print tiempoEsperaPromedio(0)
# sumaTop = _TOPOLOGIA[0][0].sum(axis = 1)
# for x in range(len(sumaTop)):
#   if sumaTop[x] == 0:
#     print x+1

# tiempoEsperaMaximo(1)

# print np.around(tiempoEsperaMaximo(0) + tiempoEsperaMaximo(1), decimals = 2)
# print np.around(tiempoEsperaPromedio(0), decimals = 2)
# print _TOPOLOGIA[1][1]

# print np.around(pasajerosPuedenAbordar(0, 1)[0], decimals= 1)
# print np.around(pasajerosPuedenAbordar(0, 1)[1], decimals= 1)
# print pasajerosPuedenAbordar(0,0)
# print tiempoEntreEstaciones()[0]

# print transbordos()[0,1]
# print transbordos()[2,0]
# print transbordos()[2,1]
# print transbordoE(2)
# print transbordos()[0,0]
# print _SECUENCIAS[1][1]

# pasajerosPuedenAbordar(1,0)
# print _TOPOLOGIA[1][2], _TOPOLOGIA[1][2].shape
# print np.sum(_TOPOLOGIA[1][2])

# print np.around(tiempoEsperaEstaciones(2,0), decimals= 3)
# print np.around(tiempoAcumuladoSubida(2,0), decimals =2)
# print np.around(tiempoAcumuladoBajada(2,0), decimals=1)

model = AbstractModel() # Se crea el modelo abstracto

model.numR = Param(within = NonNegativeIntegers) # Numero total de Rutas
model.estaciones = Param(within = NonNegativeIntegers) #Numero de Estaciones

model.r = RangeSet(0,model.numR-1) # Rutas
model.t = RangeSet(0,1) # Trayectos
model.I = RangeSet(1,model.estaciones) # Estaciones Filas
model.J = RangeSet(1,model.estaciones) # Estaciones Columnas

model.costoRuta = Param(model.r)

model.frecuenciaOptima = Var(model.r, domain=NonNegativeReals, initialize= 0.10, bounds=(0.066, 70))


# def tiempoViajePromedioModel(model, r, t):
#     return tiempoViajePromedio(r,t,model.frecuenciaOptima).sum()
# model.tiempoViajePromedioS = Param(model.r, model.t, initialize=tiempoViajePromedioModel)

# def tiempoEsperaPor2ViajeModel(model, r, t):
#     return tiempoEsperarPor2Viaje(r,t,model.frecuenciaOptima).sum()
# model.tiempoEsperaPor2ViajeS = Param(model.r, model.t, initialize=tiempoEsperaPor2ViajeModel)

def obj_expression(model):
    # global FrecuenciasOptimas
    # FrecuenciasOptimas = model.frecuenciaOptima
    # print model.frecuenciaOptima[0].value
    # tiempoViajePromedioS = 0
    # tiempoEsperaPor2ViajeS = 0
    # x = model.frecuenciaOptima
    # print type(model.frecuenciaOptima[0])
    # x = [model.frecuenciaOptima[0], model.frecuenciaOptima[1], model.frecuenciaOptima[2]]
    # for r in model.r:
    #     for t in model.t:
    #         tiempoViajePromedioS += tiempoViajePromedio(r,t,model).sum()
    #         tiempoEsperaPor2ViajeS += tiempoEsperarPor2Viaje(r,t, model).sum()
    # return (tiempoViajePromedioS + (tiempoEsperaPor2ViajeS*TIEMPOESPERA2BUS))*FACTORPASAJERO + summation(model.costoRuta, model.frecuenciaOptima)*FACTOROPERADEOR
    # return (sum(model.tiempoViajePromedioS[r,t] for r in model.r for t  in model.t) + (sum(model.tiempoEsperaPor2ViajeS[r,t] for r in model.r for t in  model.t))*TIEMPOESPERA2BUS)*FACTORPASAJERO + summation(model.costoRuta, model.frecuenciaOptima)*FACTOROPERADEOR
    obj1 = (sum(tiempoViajePromedio(r,t,model.frecuenciaOptima).sum() for r in model.r for t  in model.t) + (sum(tiempoEsperarPor2Viaje(r,t,model.frecuenciaOptima).sum() for r in model.r for t in  model.t))*TIEMPOESPERA2BUS)*FACTORPASAJERO
    obj2 = summation(model.costoRuta, model.frecuenciaOptima)*FACTOROPERADEOR
    return obj1 + obj2

model.OBJ = Objective(rule= obj_expression, sense=minimize)

def quality_constraint_rule(model, t, i):
    # rule = flujoAsignado(t-1).sum(axis=0) <= funcionCalidad(t-1).sum(axis=0)
    # return rule.all() == True
    return (None, flujoAsignado(t,model.frecuenciaOptima).sum(axis=0)[i-1], funcionCalidad(t,model.frecuenciaOptima).sum(axis=0)[i-1])
    # return (None, sum(model.distribucionServicios[r, j, t] for j, t in zip(model.J, model.trayecto)), sum(model.F1[r, j, t] for j, t in zip(model.I, model.trayecto)))

model.qualityConstraint = Constraint(model.t, model.I, rule=quality_constraint_rule)

# instance = model.create('modeloOptimizacionPyomo.dat')
# instance.pprint()

# def frequency_constraint_rule(model, r):
#     return (0.066, model.frecuenciaOptima[r], None)
# model.frequencyConstraint = Constraint(model.r, rule=frequency_constraint_rule)

# options = Options()
# options.solver = 'ipopt'
# options.quiet = True

# instance = model.create('modeloOptimizacionPyomo.dat')

# results, opt = \
# scripting.util.apply_optimizer(options, instance)
# instance.load(results)
# print " ", str(instance.sv.value).rjust(10),str(instance.cb.value).rjust(15)

# print (sum(tiempoViajePromedio(r,t).sum() for r in range(NUMERORUTAS) for t  in range(1)) + (sum(tiempoEsperarPor2Viaje(r,t).sum() for r in range(NUMERORUTAS) for t  in range(1)))*TIEMPOESPERA2BUS)*FACTORPASAJERO + (5000*0.066)*3#sum(5000*FrecuenciasOptimas[r] for r in range(NUMERORUTAS))*FACTOROPERADEOR
# def scipyObjective(x):
#     global FrecuenciasOptimas
#     FrecuenciasOptimas = [x[0], x[1], x[2]]
#     return (sum(tiempoViajePromedio(r,t).sum() for r in range(NUMERORUTAS) for t  in range(1)) + (sum(tiempoEsperarPor2Viaje(r,t).sum() for r in range(NUMERORUTAS) for t  in range(1)))*TIEMPOESPERA2BUS)*FACTORPASAJERO + sum(5000*FrecuenciasOptimas[r] for r in range(NUMERORUTAS))*FACTOROPERADEOR
# class MyBounds(object):
#     def __init__(self, xmax=[10,10,10], xmin=[0.066,0.066, 0.066] ):
#         self.xmax = np.array(xmax)
#         self.xmin = np.array(xmin)
#     def __call__(self, **kwargs):
#         x = kwargs["x_new"]
#         tmax = bool(np.all(x <= self.xmax))
#         tmin = bool(np.all(x >= self.xmin))
#         return tmax and tmin

# minimizer_kwargs = {"method": "BFGS"}
# mybounds = MyBounds()
# x0 = [0.8,0.8,0.8]
# result = basinhopping(scipyObjective, x0, minimizer_kwargs=minimizer_kwargs, niter=10, accept_test=mybounds)

# print("global minimum: x = %.4f, f(x0) = %.4f" % (ret.x, ret.fun))

