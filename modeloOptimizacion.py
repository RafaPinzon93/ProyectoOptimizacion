# -*- coding: utf-8 -*-
from __future__ import division
from coopr.pyomo import *
import numpy as np

np.set_printoptions(linewidth=200)

FACTORPASAJERO  = 10  # Factor de peso del pasajero
FACTOROPERADEOR = 20  # Factor de peso del operador
CAPACIDADBUSES  = 150 # Capacidad total de los buses
_tiempoViajePromedio = [[[[1,2],[3,4]]]]

frecuenciaOptima1 = 0.19370
frecuenciaOptima2 = 0.15703
frecuenciaOptima3 = 0.19119
FrecuenciasOptimas = [frecuenciaOptima1, frecuenciaOptima2, frecuenciaOptima3]

_TIEMPO_ENTRE_ESTACIONES1 = np.mat('0,2,4,6,6,8,8,10,10,12,14,16,12,14,16; 2,0,2,4,4,6,6,8,8,10,12,14,10,12,14; 4,2,0,2,2,4,4,6,6,8,10,12,8,10,12; 18,14,14,0,12,2,10,4,8,6,8,10,6,8,10;6,4,2,4,0,6,2,8,4,6,8,10,10,10,12;14,12,10,12,10,0,8,2,6,4,6,8,4,6,8;8,6,4,6,2,8,0,10,2,4,6,8,12,8,10;12,10,8,10,8,12,6,0,4,2,4,6,2,4,6;10,8,6,8,4,10,2,12,0,2,4,6,14,6,8;12,10,8,10,6,12,4,14,2,0,2,4,16,4,6;14,12,10,12,8,14,6,16,4,2,0,2,18,2,4;16,14,12,14,10,16,8,18,6,4,2,0,20,4,6;10,8,6,8,8,10,10,2,12,14,16,18,0,2,4;8,6,4,6,6,8,8,10,10,12,14,16,12,0,2;6,4,2,4,4,6,6,8,8,10,12,14,10,12,0')
_TIEMPO_ENTRE_ESTACIONES2 = np.mat('0  ,2  ,4  ,6  ,6  ,8  ,8  ,10 ,10 ,12 ,14 ,16 ,12 ,14 ,16 ;2,0,2,4,4,6,6,8,8,10,12,14,10,12,14;4,2,0,2,2,4,4,6,6,8,10,12,8,10,12;18,16,12,0,12,2,10,4,8,6,8,10,6,8,10;6,4,2,4,0,6,2,8,4,6,8,10,10,12,14;16,14,12,14,10,0,8,2,6,4,6,8,4,6,8;8,6,4,6,2,8,0,10,2,4,6,8,12,8,10;14,12,10,12,8,14,6,0,4,2,4,6,2,4,6;10,8,6,8,4,10,2,12,0,2,4,6,14,6,8;12,10,8,10,6,12,4,14,2,0,2,4,16,4,6;10,8,6,8,8,10,6,12,4,2,0,2,14,2,4;12,10,8,10,10,12,8,14,6,4,2,0,16,4,6;10,8,6,8,8,10,10,2,12,14,16,18,0,2,4;8,6,4,6,6,8,8,10,10,12,14,16,12,0,2;6,4,2,4,4,6,6,8,8,10,12,14,10,12,0')
_TIEMPO_ENTRE_ESTACIONES3 = np.mat('0,2,4,6,6,8,8,10,10,12,14,16,12,14,16;2,0,2,4,4,6,6,8,8,10,12,14,10,12,14;4,2,0,2,2,4,4,6,6,8,10,12,8,10,12;16,14,12,0,14,2,16,4,18,6,8,10,6,8,10;6,4,2,4,0,6,2,8,4,6,8,10,10,12,14;14,12,10,12,12,0,14,2,16,4,6,8,4,6,8;8,6,4,6,2,8,0,10,2,4,6,8,12,8,10;12,10,8,10,10,12,6,0,4,2,4,6,2,4,6;10,8,6,8,4,10,2,12,0,2,4,6,14,6,8;12,10,8,10,6,12,4,14,2,0,2,4,16,4,6;10,8,6,8,8,10,6,12,4,2,0,2,14,2,4;12,10,8,10,10,12,8,14,6,4,2,0,16,4,6;10,8,6,8,8,10,10,2,12,14,16,18,0,2,4;8,6,4,6,6,8,8,10,10,12,14,16,12,0,2;6,4,2,4,4,6,6,8,8,10,12,14,10,12,0')
_TIEMPO_ENTRE_ESTACIONES = [_TIEMPO_ENTRE_ESTACIONES1, _TIEMPO_ENTRE_ESTACIONES2, _TIEMPO_ENTRE_ESTACIONES3]


#Topologias por rutas y trayectos, teniendo en cuenta viajes 'indirectos'
_TOPOLOGIA1 = np.mat('0,1,1,0,1,0,1,0,1,1,1,1,0,0,0;0,0,1,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,1,0,1,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,1,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,1,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA2 = np.mat('0,1,1,1,0,1,0,1,0,1,1,1,0,0,0;0,0,1,1,0,1,0,1,0,1,1,1,0,0,0;0,0,0,1,0,1,0,1,0,1,1,1,0,0,0;0,0,0,0,1,1,1,1,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,1,0,1,1,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,1,0,1,0,1,1,1,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,1,1,0,1,1;0,0,0,0,0,0,0,0,0,0,0,1,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA3 = np.mat('0,1,1,1,0,1,0,1,0,0,0,0,1,1,1;0,0,1,1,0,1,0,1,0,0,0,0,1,1,1;0,0,0,1,0,1,0,1,0,0,0,0,1,1,1;1,1,1,0,1,1,1,1,1,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,0,1,1,1,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,0,1,0,0,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA4 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,1,0,1,0,0,0,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,0,1,0,0,0,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,0,0,0,0,1,0,0;1,1,1,1,1,1,1,1,1,0,0,0,1,0,0;1,1,1,1,1,1,1,1,1,1,0,0,1,0,0;1,1,1,1,1,1,1,1,1,1,1,0,1,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
_TOPOLOGIA5 = np.mat('0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,0,1,0,1,0,0,0,0,1,1,1;1,1,1,1,0,1,0,1,0,0,1,0,1,1,1;0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;1,1,1,1,1,1,1,1,1,1,1,1,1,0,0;1,1,1,1,1,1,1,1,1,1,1,1,1,1,0')
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

NUMEROESTACIONES = 0

_DEMANDA_MEDIA = np.mat('''0 ,15,15,15,15,15,15,15,15,15,15,15,15,15,15;
                           15,0 ,15,15,15,15,15,15,15,15,15,15,15,15,15;
                           15,15,0 ,15,15,15,15,15,15,15,15,15,15,15,15;
                           15,15,15,0 ,15,15,15,15,15,15,15,15,15,15,15;
                           15,15,15,15,0 ,15,15,15,15,15,15,15,15,15,15;
                           15,15,15,15,15,0 ,15,15,15,15,15,15,15,15,15;
                           15,15,15,15,15,15,0 ,15,15,15,15,15,15,15,15;
                           15,15,15,15,15,15,15,0 ,15,15,15,15,15,15,15;
                           15,15,15,15,15,15,15,15,0 ,15,15,15,15,15,15;
                           15,15,15,15,15,15,15,15,15,0 ,15,15,15,15,15;
                           15,15,15,15,15,15,15,15,15,15,0 ,15,15,15,15;
                           15,15,15,15,15,15,15,15,15,15,15,0 ,15,15,15;
                           15,15,15,15,15,15,15,15,15,15,15,15,0 ,15,15;
                           15,15,15,15,15,15,15,15,15,15,15,15,15,0 ,15;
                           15,15,15,15,15,15,15,15,15,15,15,15,15,15,0 ''')

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
# _tiempoViajePromedioN = np.matrix('1,2;3,4')
# _tiempoViajePromedioN1 = np.matrix('1,2;3,4'),,,,,,,,,,,,,,;
# _tiempoViajePromedioN2 = np.matrix('1,2;3,4')15,15,15,15,15,15,15,15,15,15,15,15,15,15,15;
# _tiempoViajePromedioN3 = np.matrix('1,2;3,4')
# _tiempoViajePromedioN4 = np.matrix('1,2;3,4')
# _tiempoViajePromedioN5 = np.matrix('1,2;3,4')
# rtMatrix = [[_tiempoViajePromedioN,_tiempoViajePromedioN1,_tiempoViajePromedioN2],[_tiempoViajePromedioN3, _tiempoViajePromedioN4, _tiempoViajePromedioN5]]


# model = AbstractModel() # Se crea el modelo abstracto

# model.numR = Param(within = NonNegativeIntegers) # Numero total de Rutas
# model.estaciones = Param(within = NonNegativeIntegers) #Numero de Estaciones

# model.r = RangeSet(1,model.numR) # Rutas
# model.t = RangeSet(1,2) # Trayectos
# model.I = RangeSet(1,model.estaciones) # Estaciones Filas
# model.J = RangeSet(1,model.estaciones) # Estaciones Columnas



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
                    _mejorSecuencia = [i, j]
            if j == i:
                _mejorSecuencia = [i, j]
            fila.append(_mejorSecuencia)
        _mejoresSecuencias.append(fila)

    return _mejoresSecuencias




def tiempoViajePromedioTot(r, t):
    '''
    Suma de la matriz tiempo de viaje promedio
    ''' 
    result = 0
    r = r-1
    t = t-1
    for i in _tiempoViajePromedio[r][t]:
        for j in i:
            # tiempoEntreEstaciones(r)
            result += j
    print result

def tiempoViajePromedioMat(r):
    pass

def tiempoEsperaMaximo(t):
    for r in range(len(FrecuenciasOptimas)):
        if r == 0:
            suma = (_TOPOLOGIA[r][t]*FrecuenciasOptimas[r])
        else:
            suma += (_TOPOLOGIA[r][t]*FrecuenciasOptimas[r])
    result = 1/suma
    result[np.isinf(result)] = 0

    # print result
    return result
    # return np.around(result, decimals = 2)

def tiempoEsperaMaximoTot():
    topologiaTotV = topologiaTot()
    for r in range(len(FrecuenciasOptimas)):
        if r == 0:
            suma = (topologiaTotV[r]*FrecuenciasOptimas[r])
        else:
            suma += (topologiaTotV[r]*FrecuenciasOptimas[r])

    result = 1/suma
    
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            topologia1 = 0
            topologia2 = 0
            for r in range(len(FrecuenciasOptimas)):
                secuencia = _MEJOR_SECUENCIA[r][i][j]
                if len(secuencia)== 3:
                    topologia1 += topologiaTotV[r][secuencia[0]-1,secuencia[1]-1]*FrecuenciasOptimas[r]
                    topologia2 += topologiaTotV[r][secuencia[1]-1,secuencia[2]-1]*FrecuenciasOptimas[r]
                    if r == 2:
                        result[i,j] = (1/topologia1) + (1/topologia2)
                        
    result[np.isinf(result)] = 0
    return result
    #return np.around(result, decimals = 2)

def tiempoEsperaPromedio(t):
    return tiempoEsperaMaximo(t)/2

def tiempoEsperaPromedioTot():
    return tiempoEsperaMaximoTot()/2

def tiempoAcumuladoSubida(r, t):
    pass

def tiempoEsperaEstaciones(r, t):
    pass



def matrizDemandaMedia():
    a = 0.4*np.array(tiempoEsperaPromedioTot())*np.array(_DEMANDA_MEDIA)
    return (a + np.array(_DEMANDA_MEDIA)) * np.array(_PROPORCIONES)

def topologiaTot():
    '''
    Topologia sin trayectos
    '''
    _MatrizTopologia = []
    for x in _TOPOLOGIA:
        _MatrizTopologia.append(x[0] + x[1])
    return _MatrizTopologia

def probabilidadEleccion(r, t):
    topologia = np.array(_TOPOLOGIA[r][t])
    frecuencia = FrecuenciasOptimas[r]
    tiempoEsperaM = np.array(tiempoEsperaMaximo(t))
    return topologia*tiempoEsperaM*frecuencia

def distribucionDemanda(r, t):
    return np.array(matrizDemandaMedia())*np.array(probabilidadEleccion(r, t))

def pasajerosEstacion(r, t):
    return distribucionDemanda(r, t).sum(axis= 1)

def pasajerosEstaValid(r, t):
    x = pasajerosEstacion(r, t)
    x[x>0] = 1
    return x

def pasajerosPuedenAbordar(r, t):
    '''
        Crea matriz de los pasajeros que pueden abordar
    '''
    secuencia = _SECUENCIAS[r][t] # Toma la secuencia utilizara por la ruta r en el trayecto t
    pasajeros = pasajerosEstacion(r, t) 
    capacidad = np.zeros(shape=(NUMEROESTACIONES)) # Se crea un arreglo de zeros con tamaño igual al numero de estaciones
    puedenSubir = np.zeros(shape=(NUMEROESTACIONES)) # Se crea un arreglo de zeros con tamaño igual al numero de estaciones
    _pasajerosPuedenAbordar = np.zeros(shape=(NUMEROESTACIONES,NUMEROESTACIONES)) # Se crea una matriz cuadrada de zeros con tamaño igual al numero de estaciones 
    i = secuencia[0]-1 # Se toma la estación inicial
    capacidad[i] = CAPACIDADBUSES - pasajeros[i] # Se inicializa el arreglo de capacidades
    puedenSubir[i] = CAPACIDADBUSES # Se inicializa el arreglo de puedenSubir
    if puedenSubir[i] >= pasajeros[i]:
        _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t)[i,:] 
    else:
        _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t)[i,:] / (pasajeros[i]*puedenSubir[i])
    if t == 0: # Si el trayecto es de ida
        for i, iS in zip(secuencia[1:]-1, range(len(secuencia[1:]-1))):
            valido = pasajerosEstaValid(r, t)[i] 
            anterior = secuencia[iS]-1
            if capacidad[anterior] >= round(pasajeros[i]):
                capacidad[i] = capacidad[anterior] - pasajeros[i] + _pasajerosPuedenAbordar[:i,i].sum()
            else: 
                capacidad[i] = 0

            if capacidad[anterior] > 0:
                puedenSubir[i] = (capacidad[anterior] + _pasajerosPuedenAbordar[:i,i].sum())*valido
            else:
                puedenSubir[i] = _pasajerosPuedenAbordar[:i,i].sum()*valido
            if round(puedenSubir[i]) >= pasajeros[i]:
                _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t)[i,:]
            else:
                _pasajerosPuedenAbordar[i,:] = (distribucionDemanda(r,t)[i,:]/pasajeros[i])*puedenSubir[i]
            # print _MEJOR_SECUENCIA[r][i-1][i]
    else: # Si el trayecto es de Vuelta
        for i, iS in zip(secuencia[1:]-1, range(len(secuencia[1:]-1))):
            valido = pasajerosEstaValid(r, t)[i] 
            anterior = secuencia[iS]-1
            if capacidad[anterior] >= round(pasajeros[i]):
                capacidad[i] = capacidad[anterior] - pasajeros[i] + _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i].sum()
            else: 
                capacidad[i] = 0

            if capacidad[anterior] > 0:
                puedenSubir[i] = (capacidad[anterior] + _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i].sum())*valido
            else:
                puedenSubir[i] = _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i].sum()*valido
                print i,anterior, puedenSubir[i], _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i]
            if round(puedenSubir[i]) >= pasajeros[i]:
                _pasajerosPuedenAbordar[i,:] = distribucionDemanda(r,t)[i,:]
            else:
                _pasajerosPuedenAbordar[i,:] = (distribucionDemanda(r,t)[i,:]/pasajeros[i])*puedenSubir[i]   
    # print np.around(puedenSubir, decimals= 1)
    # print capacidad
    # print np.rint(pasajeros)
    return _pasajerosPuedenAbordar

    

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
# print np.around(tiempoEsperaMaximo(0), decimals = 2)

# print np.around(pasajerosPuedenAbordar(1, 1), decimals= 1)
# print pasajerosPuedenAbordar(0,0)


print mejoresSecuencias()

# pasajerosPuedenAbordar(1,0)
# print _TOPOLOGIA[1][2], _TOPOLOGIA[1][2].shape
# print np.sum(_TOPOLOGIA[1][2])
