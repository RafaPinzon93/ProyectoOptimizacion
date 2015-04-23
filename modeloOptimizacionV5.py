# -*- coding: utf-8 -*-
from __future__ import division
import numpy as np
import MySQLdb
import json
import datetime
import copy_reg
import types

from scipy import optimize

from pyevolve import G1DList, GSimpleGA, Selectors
from pyevolve import Initializators, Mutators, Consts

import inspect, os, sys


np.set_printoptions(threshold=np.nan)
np.set_printoptions(linewidth=200)
oldSettings = np.seterr(divide='ignore', invalid='ignore')
np.seterr(**oldSettings)

def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

class OptimizacionFrecuencias(object):
    """
    Clase donde estan las funciones requeridas y las variables para optimizar las frecuencias

    Parametros
    ----------
        - numeroDemanda: Numero de demanda con la que se llenara la matriz de demanda.
        - factorPasajero: Factor de peso del pasajero.
        - factorOperador: Factor de peso del operador.
        - capacidadBuses: Capacidad total de los buses.
        - tiempoAbordar: Tiempo promedio para abordar los Buses.
        - tiempoEspera2Bus: Tiempo promedio espera de segundo Bus.
        - horaInicio: Hora de inicio de servicios.
        - horaFin: Hora de fin de servicios.
        - numeroRutas: Numero de Rutas.
        - numeroEstacionesC: Numero de Estaciones.
        - frecuenciasOptimas: Lista con el valor de la frecuencia optima para cada ruta.
        - finTrayecto: Lista con las estaciones finales disponibles de todas las rutas.

    """
    def __init__(self, numeroDemanda = 2, factorPasajero = 100, factorOperador = 100,
                 capacidadBuses = 150, tiempoAbordar = 1/60.0, tiempoEspera2Bus = 1,
                 horaInicio = 5, horaFin = 23, numeroRutas = 3, numeroEstacionesC = 15,
                 frecuenciasOptimas = [0.588608646066, 0.064516141848, 0.487587969109],
                 finTrayecto = [11,0], transbordosM = None):

        self.FACTORPASAJERO = factorPasajero  # Factor de peso del pasajero
        self.FACTOROPERADEOR = factorOperador  # Factor de peso del operador
        self.CAPACIDADBUSES  = capacidadBuses # Capacidad total de los buses
        self.TIEMPOABORDAR = tiempoAbordar
        self.TIEMPOESPERA2BUS = tiempoEspera2Bus
        # self.NUMERODEMANDA = 12
        self.NUMERODEMANDA = numeroDemanda

        self.HORAINICIO = horaInicio
        self.HORAFIN = horaFin

        self.NUMERORUTAS = numeroRutas
        self.NUMEROESTACIONES = numeroEstacionesC
        
        self.FrecuenciasOptimas = frecuenciasOptimas

        
        _TIEMPO_ENTRE_ESTACIONES1 = np.array([[ 0, 2, 4, 6, 6, 8, 8,10,10,12,14,16,12,14,16],
                                              [ 2, 0, 2, 4, 4, 6, 6, 8, 8,10,12,14,10,12,14],
                                              [ 4, 2, 0, 2, 2, 4, 4, 6, 6, 8,10,12, 8,10,12],
                                              [18,14,14, 0,12, 2,10, 4, 8, 6, 8,10, 6, 8,10],
                                              [ 6, 4, 2, 4, 0, 6, 2, 8, 4, 6, 8,10,10,10,12],
                                              [14,12,10,12,10, 0, 8, 2, 6, 4, 6, 8, 4, 6, 8],
                                              [ 8, 6, 4, 6, 2, 8, 0,10, 2, 4, 6, 8,12, 8,10],
                                              [12,10, 8,10, 8,12, 6, 0, 4, 2, 4, 6, 2, 4, 6],
                                              [10, 8, 6, 8, 4,10, 2,12, 0, 2, 4, 6,14, 6, 8],
                                              [12,10, 8,10, 6,12, 4,14, 2, 0, 2, 4,16, 4, 6],
                                              [14,12,10,12, 8,14, 6,16, 4, 2, 0, 2,18, 2, 4],
                                              [16,14,12,14,10,16, 8,18, 6, 4, 2, 0,20, 4, 6],
                                              [10, 8, 6, 8, 8,10,10, 2,12,14,16,18, 0, 2, 4],
                                              [ 8, 6, 4, 6, 6, 8, 8,10,10,12,14,16,12, 0, 2],
                                              [ 6, 4, 2, 4, 4, 6, 6, 8, 8,10,12,14,10,12, 0]])
        _TIEMPO_ENTRE_ESTACIONES2 = np.array([[ 0, 2, 4, 6, 6, 8, 8,10,10,12,14,16,12,14,16],
                                              [ 2, 0, 2, 4, 4, 6, 6, 8, 8,10,12,14,10,12,14],
                                              [ 4, 2, 0, 2, 2, 4, 4, 6, 6, 8,10,12, 8,10,12],
                                              [18,16,12, 0,12, 2,10, 4, 8, 6, 8,10, 6, 8,10],
                                              [ 6, 4, 2, 4, 0, 6, 2, 8, 4, 6, 8,10,10,12,14],
                                              [16,14,12,14,10, 0, 8, 2, 6, 4, 6, 8, 4, 6, 8],
                                              [ 8, 6, 4, 6, 2, 8, 0,10, 2, 4, 6, 8,12, 8,10],
                                              [14,12,10,12, 8,14, 6, 0, 4, 2, 4, 6, 2, 4, 6],
                                              [10, 8, 6, 8, 4,10, 2,12, 0, 2, 4, 6,14, 6, 8],
                                              [12,10, 8,10, 6,12, 4,14, 2, 0, 2, 4,16, 4, 6],
                                              [10, 8, 6, 8, 8,10, 6,12, 4, 2, 0, 2,14, 2, 4],
                                              [12,10, 8,10,10,12, 8,14, 6, 4, 2, 0,16, 4, 6],
                                              [10, 8, 6, 8, 8,10,10, 2,12,14,16,18, 0, 2, 4],
                                              [ 8, 6, 4, 6, 6, 8, 8,10,10,12,14,16,12, 0, 2],
                                              [ 6, 4, 2, 4, 4, 6, 6, 8, 8,10,12,14,10,12, 0]])
        _TIEMPO_ENTRE_ESTACIONES3 = np.array([[ 0, 2, 4, 6, 6, 8, 8,10,10,12,14,16,12,14,16],
                                              [ 2, 0, 2, 4, 4, 6, 6, 8, 8,10,12,14,10,12,14],
                                              [ 4, 2, 0, 2, 2, 4, 4, 6, 6, 8,10,12, 8,10,12],
                                              [16,14,12, 0,14, 2,16, 4,18, 6, 8,10, 6, 8,10],
                                              [ 6, 4, 2, 4, 0, 6, 2, 8, 4, 6, 8,10,10,12,14],
                                              [14,12,10,12,12, 0,14, 2,16, 4, 6, 8, 4, 6, 8],
                                              [ 8, 6, 4, 6, 2, 8, 0,10, 2, 4, 6, 8,12, 8,10],
                                              [12,10, 8,10,10,12,12, 0,14, 2, 4, 6, 2, 4, 6],
                                              [10, 8, 6, 8, 4,10, 2,12, 0, 2, 4, 6,14, 6, 8],
                                              [12,10, 8,10, 6,12, 4,14, 2, 0, 2, 4,16, 4, 6],
                                              [10, 8, 6, 8, 8,10, 6,12, 4, 2, 0, 2,14, 2, 4],
                                              [12,10, 8,10,10,12, 8,14, 6, 4, 2, 0,16, 4, 6],
                                              [10, 8, 6, 8, 8,10,10,12,12,14,16,18, 0, 2, 4],
                                              [ 8, 6, 4, 6, 6, 8, 8,10,10,12,14,16,12, 0, 2],
                                              [ 6, 4, 2, 4, 4, 6, 6, 8, 8,10,12,14,10,12, 0]])

        self._TIEMPO_ENTRE_ESTACIONES = [_TIEMPO_ENTRE_ESTACIONES1, _TIEMPO_ENTRE_ESTACIONES2, _TIEMPO_ENTRE_ESTACIONES3]

        tiempoTrayectoIda = [[2.4339788732394365, 3.265845070422535, 3.0809859154929575, 0.9242957746478873, 1.1399647887323943, 1.8177816901408448, 0.8626760563380281, 1.2632042253521125, 0.7702464788732394, 1.3248239436619715, 0.8318661971830986, 2.403169014084507, 2.834507042253521, 0.8318661971830986, 3.820422535211267, 1.3556338028169013, 1.2015845070422535, 1.1707746478873238, 1.509683098591549, 2.7112676056338025],
                            [2.689964157706094, 3.6093189964157717, 3.4050179211469542, 1.0215053763440864, 1.2598566308243733, 2.1111111111111116, 1.191756272401434, 1.3279569892473122, 0.9534050179211473, 1.6003584229390686, 1.3279569892473122, 1.9408602150537637, 1.2939068100358426, 0.9193548387096778, 1.8387096774193556, 4.222222222222223, 1.4982078853046599, 1.3279569892473122, 1.2939068100358426, 1.6684587813620078, 2.9964157706093197],
                            [2.7869742198100407, 3.7394843962008144, 3.5278154681139755, 1.0583446404341927, 1.3052917232021708, 2.187245590230665, 1.2347354138398914, 1.3758480325644504, 0.9877883310719133, 1.6580732700135683, 1.3758480325644504, 2.010854816824966, 1.3405698778833108, 0.9525101763907734, 0.9877883310719133]]
                             
        tiempoTrayectoVuelta = [[2.1874999999999996, 1.4788732394366195, 1.1091549295774645, 1.232394366197183, 1.3864436619718308, 3.7896126760563376, 0.8626760563380281, 2.7728873239436616, 2.15669014084507, 0.8626760563380281, 1.2015845070422535, 0.9242957746478873, 1.294014084507042, 0.7394366197183098, 1.8485915492957745, 1.232394366197183, 0.8318661971830986, 2.7112676056338025, 2.988556338028168, 2.834507042253521],
                               [2.4175627240143376, 1.634408602150538, 1.2258064516129035, 1.3620071684587818, 1.5322580645161297, 4.42652329749104, 1.7706093189964165, 2.043010752688173, 1.0555555555555558, 1.3620071684587818, 1.191756272401434, 1.5322580645161297, 1.2939068100358426, 1.9408602150537637, 1.3620071684587818, 0.9193548387096778, 2.9964157706093197, 3.3028673835125457, 3.132616487455198],
                               [0.7055630936227951, 1.8344640434192672, 2.1166892808683855, 1.0936227951153326, 1.4111261872455902, 1.2347354138398914, 1.587516960651289, 1.3405698778833108, 2.010854816824966, 1.4111261872455902, 0.9525101763907734, 3.104477611940298, 3.421981004070556, 3.245590230664858]]

        self._TiempoDirectoTrayectos = [tiempoTrayectoIda, tiempoTrayectoVuelta]

        
        #Topologias por rutas y trayectos, teniendo en cuenta viajes 'indirectos'
        _TOPOLOGIA1 = np.array([[0,1,1,0,1,0,1,0,1,1,1,1,0,0,0],
                                [0,0,1,0,1,0,1,0,1,1,1,1,0,0,0],
                                [0,0,0,0,1,0,1,0,1,1,1,1,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,1,0,1,1,1,1,0,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,1,1,1,1,0,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,1,1,1,0,1,1],
                                [0,0,0,0,0,0,0,0,0,0,1,1,0,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
        _TOPOLOGIA2 = np.array([[0,1,1,1,0,1,0,1,0,1,1,1,0,0,0],
                                [0,0,1,1,0,1,0,1,0,1,1,1,0,0,0],
                                [0,0,0,1,0,1,0,1,0,1,1,1,0,0,0],
                                [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,1,0,1,1,1,1,1,1,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,1,0,1,0,1,1,1,1,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,1,1,0,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
        _TOPOLOGIA3 = np.array([[0,1,1,1,0,1,0,1,0,0,0,0,1,1,1],
                                [0,0,1,1,0,1,0,1,0,0,0,0,1,1,1],
                                [0,0,0,1,0,1,0,1,0,0,0,0,1,1,1],
                                [1,1,1,0,0,1,0,1,0,0,0,0,1,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,0,0,0,1,0,0,0,0,1,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,0,1,0,0,0,0,0,0,1,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
        _TOPOLOGIA4 = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,0,1,0,1,0,0,0,0,1,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,1,1,0,1,0,0,0,0,1,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,1,1,1,1,0,0,0,0,1,0,0],
                                [1,1,1,1,1,1,1,1,1,0,0,0,1,0,0],
                                [1,1,1,1,1,1,1,1,1,1,0,0,1,0,0],
                                [1,1,1,1,1,1,1,1,1,1,1,0,1,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
        _TOPOLOGIA5 = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,0,1,0,1,0,0,0,0,1,1,1],
                                [1,1,1,1,0,1,0,1,0,0,1,0,1,1,1],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
                                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0]])
        _TOPOLOGIA6 = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                [1,1,1,1,1,1,1,1,1,1,1,1,0,1,1],
                                [1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
                                [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0]])

        self._TOPOLOGIA = [[_TOPOLOGIA1, _TOPOLOGIA4],
                      [_TOPOLOGIA2, _TOPOLOGIA5],
                      [_TOPOLOGIA3, _TOPOLOGIA6]]

        # Se obtiene de base de datos
        self._TRAYECTOS = [{1:'Ida',2:'Vuelta'},{3:'Ida',4:'Vuelta'},{5:'Ida',6:'Vuelta'}]


        
        _SECUENCIA1 = np.array([1, 2, 3, 5, 7, 9, 10, 11, 12])
        _SECUENCIA4 = np.array([12, 11, 10, 9, 7, 5, 3, 2, 1])
        _SECUENCIA2 = np.array([1, 2, 3, 4, 6, 8, 10, 11, 12])
        _SECUENCIA5 = np.array([12, 11, 14, 15, 3, 2, 1])
        _SECUENCIA3 = np.array([1, 2, 3, 4, 6, 8, 13])
        _SECUENCIA6 = np.array([13, 14, 15, 3, 2, 1])

        self._SECUENCIAS = [[_SECUENCIA1, _SECUENCIA4],
                       [_SECUENCIA2, _SECUENCIA5],
                       [_SECUENCIA3, _SECUENCIA6]
        ]



        if transbordosM is not None:
            self._TRANSBORDOS = transbordosM
        else:
            self._TRANSBORDOS = self.transbordos()

        # self.TRANSBORDO = None # Variable para hacer dp cuando se calculan los self.transbordos().

        self.EstacionesBaseDatosDict = None

        self.FinTrayectoArray = finTrayecto

        # self.EsRutaFantasma = [[False, False],
        #                   [False, False],
        #                   [False, True]
        #                  ]

        self.EsRutaFantasma = self.esRutaFantasmaFun()
        
        self._PROPORCIONES = np.array([[0,0.1,0.15,0.4,0.4,0.7,0.4,0.7,0.4,0.7,0.4,0.4,0.7,0.7,0.7],
                                  [0.1,0,0.1,0.1,0.2,0.4,0.4,0.7,0.4,0.7,0.4,0.4,0.7,0.7,0.7],
                                  [0.1,0.1,0,0.1,0.1,0.4,0.3,0.4,0.4,0.7,0.4,0.4,0.7,0.7,0.7],
                                  [0.2,0.1,0.1,0,0.2,0.1,0.2,0.2,0.2,0.5,0.4,0.4,0.7,0.7,0.7],
                                  [0.2,0.2,0.2,0.7,0,0.5,0.1,0.7,0.1,0.2,0.4,0.4,0.5,0.5,0.5],
                                  [0.2,0.2,0.1,0.1,0.3,0,0.3,0.1,0.3,0.2,0.3,0.3,0.4,0.5,0.5],
                                  [0.2,0.2,0.2,0.7,0.1,0.7,0,0.7,0.4,0.7,0.5,0.5,0.7,0.7,0.7],
                                  [0.2,0.2,0.2,0.1,0.3,0.2,0.7,0,0.4,0.1,0.4,0.4,0.1,0.4,0.4],
                                  [0.2,0.2,0.2,0.2,0.2,0.7,0.1,0.7,0,0.1,0.2,0.3,0.6,0.6,0.6],
                                  [0.2,0.2,0.2,0.7,0.2,0.7,0.2,0.5,0.1,0,0.1,0.2,0.5,0.6,0.6],
                                  [0.2,0.2,0.2,0.7,0.3,0.7,0.4,0.5,0.2,0.1,0,0.1,0.8,0.8,0.8],
                                  [0.2,0.2,0.3,0.7,0.4,0.7,0.5,0.5,0.3,0.2,0.1,0,0.8,0.8,0.8],
                                  [0.2,0.2,0.2,0.3,0.4,0.4,0.4,0.5,0.5,0.4,0.4,0.3,0,0.1,0.2],
                                  [0.2,0.2,0.2,0.2,0.4,0.4,0.4,0.5,0.5,0.4,0.4,0.6,0.2,0,0.1],
                                  [0.2,0.2,0.2,0.2,0.4,0.4,0.4,0.5,0.5,0.4,0.4,0.6,0.6,0.1,0]])

        # print self._PROPORCIONES.sum(axis=0)
        # Valores posibles de frecuencias, que van desde un periodo
        # de 3 minutos a 15.5, con intervalos de 0.5 minutos
        # Obteniendo un vector de posibles frecuencias con 25 valores
        self.ValoresFrecuencias = 1/np.arange(3,16,0.5)

        self.COSTOS = [5000,5000,5000] # Costos de cada Ruta
        self.dbr = None

    def cambiarVariablesOptimizacion(self, demanda = None, factorPasajero = None, factorOperador = None, 
                                     capacidadBuses = None, tiempoAbordar = None, tiempoEspera2Bus = None):
        '''
            Cambia las variables dependientes de la optimizacion, solo cambia las que son pasadas

            Parametros
            ----------
                - demanda = int
                - factorPasajero: int
                - factorOperador: int
                - capacidadBuses: int
                - tiempoAbordar: int
                - tiempoEspera2Bus: int
            Return
            ------
                None
        '''
        if demanda:
            self.NUMERODEMANDA = demanda
        if factorPasajero:
            self.FACTORPASAJERO = factorPasajero
        if factorOperador:
            self.FACTOROPERADEOR = factorOperador
        if capacidadBuses:
            self.CAPACIDADBUSES = capacidadBuses
        if tiempoAbordar:
            self.TIEMPOABORDAR = tiempoAbordar
        if tiempoEspera2Bus:
            self.TIEMPOESPERA2BUS = tiempoEspera2Bus

    def cambiarVariablesJSON(self, horaInicio = None, horaFin = None):
        '''
            Cambia las variables dependientes de generar las tablas horarias en el archivo JSON,
            solo cambia las que son pasadas

            Parametros
            ----------
                - horaInicio = int
                - horaFin = int
            Return
            ------
                None
        '''
        if horaInicio:
            self.HORAINICIO = horaInicio
        if horaFin:
            self.HORAFIN = horaFin
       

    def obtenerDatosBase(self, db_host = 'admin.megaruta.co', usuario ='rutamega_eqopt', clave = 'eedd8ae977b7f997ce92aa1b0', base_de_datos ='rutamega_principal'):
        '''
            Obtiene las variables principales para realizar las tablas horarias como son:
                - Matrices de Transbordos: matricesTransbordo
                - Matriz de Proporciones: matProporcion
                - Diccionario de Estaciones: estacionDictInv {estacionOrden: idEstacionDB,...}
                    Ej: {1: 38L, 2: 39L, 3: 36L, 4: 35L, 5: 34L, 6: 33L, 7: 10L, 8: 9L, 9: 8L...}
                }
                - Matrices Secuencias: matrizSecuencia. Esta siempre va ir ordenada en cada ruta 
                                       primero el trayecto ida y luego el de vuelta.
                - Lista de Diccionario de Trayectos: trayectosList
                    Ej: [{1: 'Ida', 2: 'Vuelta'}, {3: 'Ida', 4: 'Vuelta'}, {5: 'Vuelta', 6: 'Ida'}] 
                - Es Ruta Fantasma: EsRutaFantasma
                - Estaciones de Fin de Trayectos: self.FinTrayectoArray
                - Numero de Estaciones: numEstaciones
                - Numero de Rutas: numRutas
            Opcionales
                - Matrices de Tiempos: matricesTiempo

            Parametros
            ----------
                - db_host = Host de la Base de Datos
                - usuario = Usuario de la Base de Datos
                - clave   = Clave de la Base de Datos
                - base_de_datos = Nombre de la Base de Datos

            Return
            ------
                Vacio. Solo cambia matrices del programa.
        '''

        self.dbr = MySQLdb.connect(host=db_host, user=usuario, passwd=clave,db=base_de_datos)
        cursor= self.dbr.cursor() 
        query_quotes =  "SET sql_mode='ANSI_QUOTES'" # para que acepte tablas con "caracteres especiales"
        cursor.execute(query_quotes)
        sql = '''SELECT * FROM "estacion-matrices"'''
        sqlRutas = '''SELECT distinct idruta FROM "estacion-matrices";''' #Se puede sacar de IdTrayectos
        sqlEstaciones = ''' SELECT distinct estaciones  From(SELECT distinct idestacionorigen as estaciones
                            FROM "estacion-matrices"
                            union all SELECT distinct idestaciondestino FROM "estacion-matrices") estaciones'''
        sqlIdTrayectos = '''SELECT f.idtrayecto, b.idruta, f.sentidotrayecto FROM (SELECT idruta FROM "estacion-matrices" GROUP BY idruta)b
                            LEFT JOIN trayecto f ON b.idruta = f.idruta;'''
        sqlSecuencias = ''' SELECT te.idtrayecto, te.idestacion, te.ordentrayectoestacion
                            FROM "trayecto-estacion" te,
                            (SELECT distinct estaciones
                            From(SELECT distinct idestacionorigen as estaciones FROM "estacion-matrices"
                            union all SELECT distinct idestaciondestino FROM "estacion-matrices") estaciones) em
                            WHERE em.estaciones = te.idestacion and te.estadotrayectoestacion = 'Activo'
                            ORDER BY te.idtrayecto, te.ordentrayectoestacion;
                        '''
        sqlFinTrayecto = '''SELECT idestacion, fintrayecto FROM estacion where fintrayecto = 1; '''
        try:
            cursor.execute(sql)
            # Obtenemos todos los registros en una lista de listas
            resultados = cursor.fetchall()
            cursor.execute(sqlRutas)
            rutas = cursor.fetchall()
            cursor.execute(sqlEstaciones)
            estaciones = cursor.fetchall()
            cursor.execute(sqlIdTrayectos)
            idTrayectos = cursor.fetchall()
            cursor.execute(sqlSecuencias)
            secuencias = cursor.fetchall()
            cursor.execute(sqlFinTrayecto)
            # Contiene las estaciones finales de trayectos, sin incluir fantasmas
            finTrayecto = cursor.fetchall() 
        except:
           print "Error: No se pudo obtener los datos"

        numEstaciones = len(estaciones)
        numRutas = len(rutas)
        matricesTiempo = []
        matricesTransbordo = []
        matDemanda = np.zeros((numEstaciones, numEstaciones))
        matProporcion = np.zeros((numEstaciones, numEstaciones))
        estacionesDict = {}

        iR = 0

        idTrayectosNP = np.array(idTrayectos)
        trayectosDict = {}
        for tray in idTrayectosNP:
            trayectosDict[tray[0]] = tray[2]
        for ruta in rutas:
            instTransRuta = []
            for trayecto in idTrayectosNP[idTrayectosNP[:,1] == str(ruta[0]),0]:
                matTransbordo = np.zeros((numEstaciones, numEstaciones))
                idTrayecto = resultados[iR][6] 
                for fila in range(numEstaciones):
                    for columna in range(numEstaciones):
                        if fila!=columna:
                            # print numEstaciones*ruta + iR
                            registro = resultados[iR]
                            # matTiempo[fila,columna] = registro[4]
                            matTransbordo[fila,columna] = registro[7]
                            if registro[8]:
                                matProporcion[fila,columna] = registro[8]
                            # if registro[3]:
                                # matDemanda[fila,columna] = registro[3]
                            # if registro[8]:
                                # matProporcion[fila,columna] = registro[8]
                            estacionesDict[registro[2]]= columna+1
                            iR +=1
                matTransbordoT = np.zeros((numEstaciones, numEstaciones))
                for i in estacionesDict:
                    matTransbordoT[matTransbordo == i] = estacionesDict[i]

                # Mientras arreglan self.transbordos en base de Datos
                # if trayectosDict[str(idTrayecto)] == 'Ida':
                #     instTransRuta.insert(0, matTransbordoT)
                # else:
                #     instTransRuta.append(matTransbordoT)
                instTransRuta.append(matTransbordoT)

            matricesTransbordo.append(instTransRuta)

        secuenciasNP = np.array(secuencias)

        matrizSecuencia = []
        trayectosList = []
        for i, ruta in enumerate(rutas):
            trayectos = {}
            secuenciaList2 = []
            for trayecto in idTrayectosNP[idTrayectosNP[:,1].astype(int)  == ruta]:
                # Se crea un diccionario solo con el id del trayecto y su valor
                # ej: trayecto [1, 3, vuelta] :: [idtrayecto, idruta, sentido]
                nuevaSecuencia = secuenciasNP[secuenciasNP[:,0]== int(trayecto[0])]
                trayectos[int(trayecto[0])] = trayecto[2]

                secuenciaList = []
                for i, elemento in enumerate(nuevaSecuencia):
                    secuenciaList.append(estacionesDict[elemento[1]])

                if trayecto[2] == 'Ida':
                    secuenciaList2.insert(0, np.array(secuenciaList))
                else:
                    secuenciaList2.append(np.array(secuenciaList))

            matrizSecuencia.append(secuenciaList2)
            trayectosList.append(trayectos) # Se añaden los trayectos de la ruta

        estacionDictInv= {}
        for estacionBase, estacionMod in estacionesDict.iteritems():
            estacionDictInv[estacionMod] = estacionBase

        self.FinTrayectoArray = []
        for estacion in finTrayecto:
            self.FinTrayectoArray.append(estacionesDict[estacion[0]]-1)
        # print self.FinTrayectoArray

        self.EsRutaFantasma = []
        for ruta in matrizSecuencia:
            rutaF = [False]
            secuencia = ruta[0]
            if secuencia[-1] -1 in self.FinTrayectoArray:
                rutaF.append(False)
            else:
                rutaF.append(True)
            self.EsRutaFantasma.append(rutaF)
        # print self.EsRutaFantasma

        # print estacionDictInv

        self.EstacionesBaseDatosDict = estacionDictInv
        # print json.dumps(estacionesDict, sort_keys = True) 
        self.NUMEROESTACIONES = numEstaciones
        self.NUMERORUTAS      = numRutas
        self._TRANSBORDOS     = matricesTransbordo
        self._SECUENCIAS      = matrizSecuencia
        self._TRAYECTOS       = trayectosList
        self._PROPORCIONES    = matProporcion

    # print self.EstacionesBaseDatosDict
    def esRutaFantasmaFun(self):
        self.EsRutaFantasma = []
        for ruta in self._SECUENCIAS:
            rutaF = [False]
            secuencia = ruta[0]
            if secuencia[-1] -1 in self.FinTrayectoArray:
                rutaF.append(False)
            else:
                rutaF.append(True)
            self.EsRutaFantasma.append(rutaF)
        return self.EsRutaFantasma

    def generarCSV(self):
        for ruta in range(self.NUMERORUTAS):
            np.savetxt("archivos/TiempoEntreEstaciones.csv", self._TIEMPO_ENTRE_ESTACIONES[ruta], delimiter=",", fmt = "%10.5f")
            for trayecto in [0,1]:
                if trayecto == 0:
                    np.savetxt("archivos/Secuencia"+str(ruta+1)+"Ida.csv", self._SECUENCIAS[ruta][trayecto], delimiter=",", fmt = "%10.5f")
                    np.savetxt("archivos/Transbordos"+str(ruta+1)+"Ida.csv", self._TRANSBORDOS[ruta][trayecto], delimiter=",", fmt = "%10.5f")
                    np.savetxt("archivos/Topologia"+str(ruta+1)+"Ida.csv", self._TOPOLOGIA[ruta][trayecto], delimiter=",", fmt = "%10.5f")
                else:
                    np.savetxt("archivos/Secuencia"+str(ruta+1)+"Vuelta.csv", self._SECUENCIAS[ruta][trayecto], delimiter=",", fmt = "%10.5f")
                    np.savetxt("archivos/Transbordos"+str(ruta+1)+"Vuelta.csv", self._TRANSBORDOS[ruta][trayecto], delimiter=",", fmt = "%10.5f")
                    np.savetxt("archivos/Topologia"+str(ruta+1)+"Vuelta.csv", self._TOPOLOGIA[ruta][trayecto], delimiter=",", fmt = "%10.5f")
        np.savetxt("archivos/Proporciones.csv", self._PROPORCIONES, delimiter=",", fmt = "%10.5f")

    def tiempoTrayectosDirectos(self, trayectosValue):
        '''
            Devuelve la matriz de tiempo trayectos directos tiempoTrayectos[indiceTrayecto][indiceRuta][fila, columna]

            Parametros
            ----------
            - trayectosValue: matriz que contiene la secuencia del trayecto de las rutas. 
                Ej: [...,[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [16, 17, 18, 19, 20, 21, 22, 23, 24, 6, 5, 4, 3, 2, 1]]] 
                Se muestra solo las secuencias de la ruta 3 trayecto vuelta del modelo de 40 estaciones

            Return
            ------
            - tiempoTrayectos: matriz donde se encuentran los tiempos directos de cada trayecto de cada ruta
                [indiceTrayecto][indiceRuta][np.array(NUMEROESTACIONES,NUMEROESTACIONES)]

        '''
        tiemposTrayectos = []
        for indexT, trayectoValue in enumerate(trayectosValue):
            trayectoVect = []
            for indexR, ruta in enumerate(trayectoValue):
                tiempo = np.zeros((self.NUMEROESTACIONES, self.NUMEROESTACIONES))
                for i, index in enumerate(ruta[:-1]):
                    siguiente = ruta[i+1]
                    tiempo[index, siguiente] = self._TiempoDirectoTrayectos[indexT][indexR][i]
                    # tiemposTrayectos[indexT][indexR][index, siguiente] = self._TiempoDirectoTrayectos[indexT][indexR][i]
                trayectoVect.append(tiempo)
            tiemposTrayectos.append(trayectoVect)
                    

        for indexT, trayectoValue in enumerate(trayectosValue):
            for indexR, ruta in enumerate(trayectoValue):
                for k in range(1,len(ruta[:-1])):
                    for i, sec in enumerate(ruta[:-1]):
                        if i+k <= len(ruta)-2:
                            siguiente = ruta[i+k]
                            if siguiente != ruta[-1]:
                                j = ruta[i+k+1]
                                tiemposTrayectos[indexT][indexR][sec,j] = tiemposTrayectos[indexT][indexR][sec,siguiente]\
                                 + tiemposTrayectos[indexT][indexR][siguiente, j]
        return tiemposTrayectos

    def tiempoTrayectosTransbordo(self, trayectosValue):
        '''
            Devuelve la matriz de tiempo trayectos contando self.transbordos tiempoTrayectos[indiceTrayecto][indiceRuta][fila, columna]

            Parametros
            ----------
            - trayectosValue: matriz que contiene la secuencia del trayecto de las rutas. 
                Ej: [...,[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [16, 17, 18, 19, 20, 21, 22, 23, 24, 6, 5, 4, 3, 2, 1]]] 
                Se muestra solo las secuencias de la ruta 3 trayecto vuelta del modelo de 40 estaciones

            Return
            ------
            - tiempoTrayectos: matriz donde se encuentran los tiempos de cada trayecto de cada ruta con los self.transbordos
                [indiceTrayecto][indiceRuta][np.array(NUMEROESTACIONES,NUMEROESTACIONES)]

        '''
        tiemposTrayectos = self.tiempoTrayectosDirectos(trayectosValue)
        for indR, ruta in enumerate(self._TRANSBORDOS):
            if not(trayectosValue[0][indR][-1] in self.FinTrayectoArray):
                fantasma = True
            else:
                fantasma = False
            for indT, matriz in enumerate(ruta):
                indicesNonZero = np.nonzero(matriz)
                for i in range(len(indicesNonZero[0])):
                    estacionTransbordo = matriz[indicesNonZero[0][i],indicesNonZero[1][i]] -1
                    if fantasma:
                        if estacionTransbordo in trayectosValue[indT][indR][trayectosValue[indT][indR].index(indicesNonZero[0][i]):]:
                            tiempoInicioTransbordo = tiemposTrayectos[indT][indR][indicesNonZero[0][i], estacionTransbordo]
                        else:
                            # Si no se encuentra la Estacion de Transbordo en la secuencia, se sumará el tiempo de ir hasta la
                            # estación final y luego la del trayecto de vuelta hasta la de transbordo
                            tiempoInicioTransbordo = tiemposTrayectos[0][indR][indicesNonZero[0][i], trayectosValue[0][indR][-1]] \
                            + tiemposTrayectos[1][indR][trayectosValue[1][indR][0], estacionTransbordo]

                    else:
                        tiempoInicioTransbordo = tiemposTrayectos[indT][indR][indicesNonZero[0][i], estacionTransbordo]
                    tiempo = None
                    for indT2, rutaTrayecto in enumerate(trayectosValue):
                        for indR2, trayecto in enumerate(rutaTrayecto):
                            if estacionTransbordo in trayecto:
                                if indicesNonZero[1][i] in trayecto[np.where(trayecto==estacionTransbordo)[0]:]: 
                                    if fantasma:
                                        sumaTiempos = (tiempoInicioTransbordo + 
                                        tiemposTrayectos[indT][indR][estacionTransbordo, indicesNonZero[1][i]]) 
                                        tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]] =(
                                            sumaTiempos)
                                    else:
                                        sumaTiempos = (tiempoInicioTransbordo + 
                                        tiemposTrayectos[indT2][indR2][estacionTransbordo, indicesNonZero[1][i]]) 
                                        if tiempo == None: # Si es el primero en encontrarlo
                                            tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]] =(
                                            sumaTiempos)
                                            tiempo = tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]]
                                        elif tiempo > sumaTiempos:
                                            tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]] =(
                                            sumaTiempos)
                                            tiempo = tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]]
                                elif fantasma:
                                    if indicesNonZero[1][i] in trayectosValue[1][indR2]:
                                        sumaTiempos = (tiempoInicioTransbordo + 
                                        tiemposTrayectos[indT2][indR2][estacionTransbordo, trayectosValue[indT2][indR2][-1]] +
                                        tiemposTrayectos[1][indR2][trayectosValue[1][indR][0], indicesNonZero[1][i]]) 
                                        if tiempo == None: # Si es el primero en encontrarlo
                                            tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]] =(
                                            sumaTiempos)
                                            tiempo = tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]]
                                        elif tiempo > sumaTiempos:
                                            tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]] =(
                                            sumaTiempos)
                                            tiempo = tiemposTrayectos[indT][indR][indicesNonZero[0][i], indicesNonZero[1][i]]
        return tiemposTrayectos

    def tiempoTrayectosRutas(self, tiemposTrayectos):
        '''
            Devuelve la matriz de tiempo trayectos contando self.transbordos tiempoTrayectos[indiceTrayecto][indiceRuta][fila, columna]

            Parametros
            ----------
                - tiempoTrayectos:    

            Return
            ------

        '''
        tiempoRutas = []
        for indR in range(self.NUMERORUTAS):
            tiempoRutas.append(tiemposTrayectos[0][indR] + tiemposTrayectos[1][indR])
        return tiempoRutas

    def obtenerTopologias(self, tiemposTrayectos):
        '''
            Crea las matrices de Topologias a traves de las matrices de tiempo

            Parametros
            ----------
                - tiempoTrayectos: 
        '''
        matricesTopologia = []
        for indexT, tiempo in enumerate(tiemposTrayectos):
            trayecto = []
            for i, ruta in enumerate(tiempo):
                topologia = np.zeros((self.NUMEROESTACIONES, self.NUMEROESTACIONES))
                topologia[ruta>0] = 1
                # if indexT == 0:
                    # np.savetxt("tiemposRuta"+str(i+1)+"IdaV2.csv", ruta, delimiter=",", fmt = "%10.5f")
                    # np.savetxt("topologiaRuta"+str(i+1)+"IdaV2.csv", topologia, delimiter=",", fmt = "%d")
                # else:
                    # np.savetxt("tiemposRuta"+str(i+1)+"VueltaV2.csv", ruta, delimiter=",", fmt = "%10.5f")
                    # np.savetxt("topologiaRuta"+str(i+1)+"VueltaV2.csv", topologia, delimiter=",", fmt = "%d")
                trayecto.append(topologia)
            matricesTopologia.append(trayecto)

        matricesTopologia = zip(*matricesTopologia)
        return matricesTopologia

    def numeroEstaciones(self):
        "Devuelve la cantidad de estaciones totales, para generar rango de matrices"
        for ruta in self._SECUENCIAS:
            for secuencia in ruta:
                maximo = secuencia.max()
                if maximo > self.NUMEROESTACIONES:
                    self.NUMEROESTACIONES = maximo
        return self.NUMEROESTACIONES
    # self.numeroEstaciones()

    def tiempoEntreEstaciones(self):
        "Crea las matrices de Tiempo Entre Estaciones, solo se toman en cuenta las directas"
        _tiempoEntreEstaciones = []
        for ruta in self._SECUENCIAS:
            _tiempoEntreEstacionesT = np.zeros(shape=(self.NUMEROESTACIONES,self.NUMEROESTACIONES))
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
        return np.array(_tiempoEntreEstaciones)

    # print self.tiempoEntreEstaciones()

    def mejoresSecuencias(self):
        '''
        Devuelve una matriz con las mejores secuencias para ir de una estación a otra
        (algoritmo de fuerza bruta, se puede optimizar con programacion dinámica)
        '''
        _mejoresSecuencias = []
        _tiempoEntreEstaciones = self.tiempoEntreEstaciones()
        for ind in range(self.NUMEROESTACIONES):
            fila = []
            for indj in range(self.NUMEROESTACIONES):
                minimo = 200
                _mejorSecuencia = []
                for ruta in _tiempoEntreEstaciones:
                    tiempo = ruta[ind,indj]
                    if tiempo != 0 and tiempo <= minimo:
                        minimo = tiempo
                        _mejorSecuencia = [ind+1, indj+1]
                if indj == ind:
                    _mejorSecuencia = [ind+1, indj+1]
                fila.append(_mejorSecuencia)
            _mejoresSecuencias.append(fila)
        for i, fila in enumerate(_mejoresSecuencias):
            for j, secuencia in enumerate(fila):
                if len(secuencia) == 0:
                    minimo = 200
                    for indRuta1, ruta1 in enumerate(self._SECUENCIAS):
                        # rutaN = []
                        # trayectoN = []
                        for trayecto in ruta1:
                            secuenciaN = trayecto-1
                            if j in secuenciaN:
                                r = np.array(range(len(secuenciaN==j)))
                                index = int(r[secuenciaN==j])
                                for estacionI in secuenciaN[:index]: # Estación intermedia
                                    minimoN = _tiempoEntreEstaciones[indRuta1][estacionI, j]
                                    for indRuta2, ruta2 in enumerate(self._SECUENCIAS):
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

        # return np.array(_mejoresSecuencias)
        return _mejoresSecuencias
    # print self.mejoresSecuencias()

    def transbordos(self):
        '''
        Devuelve las matrices de self.transbordos de acuerdo a la matriz de mejores secuencias
        Se implementa DP, con la variable de self.TRANSBORDO
        '''
        # global self.TRANSBORDO
        # if self.TRANSBORDO == None: # Si no se han asignado self.transbordos
            # Se toman las mejores secuencias (utilizando rutas más cortas)
        _mejoresSecuenciasT = self.mejoresSecuencias()
        _mejoresSecuenciasN = []
        for ir ,ruta in enumerate(self._SECUENCIAS):
            r = []
            for it, trayecto in enumerate(ruta):
                tr = np.zeros(shape=(self.NUMEROESTACIONES,self.NUMEROESTACIONES))
                if ir == 2 and it == 1: # Si es estación fantasma
                    # Se concatenan las dos secuencias, la de trayecto ida y la de vuelta.
                    sec = np.concatenate((ruta[0]-1,ruta[1]-1))
                else: # Si es cualquier estación normal, se asigna el trayecto actual
                    sec = trayecto-1
                # print sec
                for i, act in enumerate(sec):
                    for j in range(self.NUMEROESTACIONES):
                        if len(_mejoresSecuenciasT[act][j])>=3 and _mejoresSecuenciasT[act][j][1] != 13:
                            estaTrans = _mejoresSecuenciasT[act][j][1] # Estación de transbordo
                            # Si la estación de transbordo está más adelante en la matriz trayecto
                            # Se le asigna esta estación de transbordo.
                            if np.in1d(estaTrans, sec[i:]+1):
                                tr[act,j] = estaTrans
                r.append(tr)
            _mejoresSecuenciasN.append(np.array(r))

            # self.TRANSBORDO = np.array(_mejoresSecuenciasN)

        # return self.TRANSBORDO
        return np.array(_mejoresSecuenciasN)


    def tiempoEsperaMaximo(self, t):
        "Devuelve matriz de Tiempo de Espera Maximo para el trayecto 't'"
        suma = np.zeros(shape=(self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        # if model!=None:
        #     for r in range(len(model)):

        #         for i in range(suma.shape[0]):
        #             for j in range(suma.shape[1]):
        #                 suma[i,j] += self._TOPOLOGIA[r][t][i,j]*model[r]
        # else:
        for r in range(len(self.FrecuenciasOptimas)):
            if r == 0:
                suma = self._TOPOLOGIA[r][t]*self.FrecuenciasOptimas[r]
            else:
                suma += self._TOPOLOGIA[r][t]*self.FrecuenciasOptimas[r]
        with np.errstate(divide='ignore'):
            result = 1/suma
        result[np.isinf(result)] = 0

        return np.array(result)
        # return np.around(result, decimals = 2)

    def topologiaTot(self):
        '''
        Topologia sin trayectos
        '''
        _MatrizTopologia = []
        for x in self._TOPOLOGIA:
            _MatrizTopologia.append(x[0] + x[1])
        return _MatrizTopologia

    def tiempoEsperaMaximoTot(self):
        "Devuelve matriz de Tiemo de Espera Máximo total para los dos trayectos"
        suma = np.zeros(shape=(self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        topologiaTotV = self.topologiaTot()
        # if model!=None:
        #     for r in range(len(model)):#self.FrecuenciasOptimas)):
        #         # suma += topologiaTotV[r]*value(model[r])
        #         for i in range(suma.shape[0]):
        #             for j in range(suma.shape[1]):
        #                 suma[i,j] += topologiaTotV[r][i,j]*model[r]
        # else:
        for r in range(len(self.FrecuenciasOptimas)):
            if r == 0:
                suma = topologiaTotV[r]*self.FrecuenciasOptimas[r]#value(self.FrecuenciasOptimas[r]))
            else:
                suma += topologiaTotV[r]*self.FrecuenciasOptimas[r]#value(self.FrecuenciasOptimas[r]))

        with np.errstate(divide='ignore'):
            result = 1/suma

        # for i in range(result.shape[0]):
        #     for j in range(result.shape[1]):
        #         topologia1 = 0
        #         topologia2 = 0
        #         for r in range(len(self.FrecuenciasOptimas)):
        #             secuencia = _MEJOR_SECUENCIA[r][i][j]
        #             if len(secuencia)== 3:
        #                 topologia1 += topologiaTotV[r][secuencia[0]-1,secuencia[1]-1]*self.FrecuenciasOptimas[r]
        #                 topologia2 += topologiaTotV[r][secuencia[1]-1,secuencia[2]-1]*self.FrecuenciasOptimas[r]
        #                 if r == 2:
        #                     result[i,j] = (1/topologia1) + (1/topologia2)

        result[np.isinf(result)] = 0
        return result
        #return np.around(result, decimals = 2)



    def demandaMediaConstante(self, x):
        _Demanda = np.zeros(shape= (self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        _Demanda.fill(x)
        np.fill_diagonal(_Demanda,[0]*self.NUMEROESTACIONES)
        return _Demanda

    # print self.demandaMediaConstante(3)

    def tiempoEsperaPromedio(self, t):
        "Devuelve matriz de Tiempo de Espera Promedio para cada trayecto 't'"
        return np.array(self.tiempoEsperaMaximo(t)/2)

    # print np.around(self.tiempoEsperaPromedio(1), decimals = 2)

    def tiempoEsperaPromedioTot(self):
        "Devuelve matriz de Tiempo de Espera Promedio total"
        return np.array(self.tiempoEsperaMaximoTot()/2)



    def matrizDemandaMedia(self):
        "Devuelve matriz de Demanda Media, "
        # arrayDemandaMedia = np.array(_DEMANDA_MEDIA)
        arrayDemandaMedia = self.demandaMediaConstante(self.NUMERODEMANDA)
        a = 0.4*self.tiempoEsperaPromedioTot()*arrayDemandaMedia
        return np.array((a + arrayDemandaMedia) * (self._PROPORCIONES))

    # print np.around(self.matrizDemandaMedia(), decimals = 2)


    # matrizProbabilidadEleccionDP = np.empty((2,3,25))
    # matrizProbabilidadEleccionDP.fill(-1)
    # print matrizProbabilidadEleccionDP[0,0]

    def probabilidadEleccion(self, r, t):
        "Devuelve matriz de probabilidad de Elección para el trayecto 't' de la ruta 'r'"
        topologia = self._TOPOLOGIA[r][t]
        # if model!=None:
        #     frecuencia = model[r]#self.FrecuenciasOptimas[r]
        # else:
        frecuencia = self.FrecuenciasOptimas[r]
        # Se convierte del tipo array para que la multiplicación no sea matricial
        tiempoEsperaM = np.array(self.tiempoEsperaMaximo(t))
        return np.array(topologia*tiempoEsperaM*frecuencia)

    # print np.around(self.probabilidadEleccion(0,0), decimals = 2)

    def distribucionDemanda(self, r, t):
        "Devuelve matriz de Distribucion de Demanda para el trayecto 't' de la ruta 'r'"
        return self.matrizDemandaMedia()*self.probabilidadEleccion(r, t)

    # print np.around(self.distribucionDemanda(0,0), decimals= 2)

    def pasajerosEstacion(self, r, t):
        "Devuelve arreglo de pasajeros en estación para el trayecto 't' de la ruta 'r'"
        return self.distribucionDemanda(r, t).sum(axis= 1)

    def pasajerosEstacionValida(self, r, t):
        '''
        Devuelve una arreglo binario, en donde haya más de un pasajero en la estación se marca 1
        para el trayecto 't' de la ruta 'r'
        '''
        x = self.pasajerosEstacion(r, t)
        x[x>0] = 1
        # for i in range(x.shape[0]):
        #     if value(x[i]) >= 0.000001:
        #         x[i] = 1
        return x

    def pasajerosPuedenAbordar(self, r, t):
        '''
            Crea matriz de los pasajeros que pueden abordar, un vector de los que pueden subir
            y  un vector de capacidades para el trayecto 't' de la ruta 'r'.
        '''
        # Toma la secuencia utilizara por la ruta r en el trayecto t
        secuencia = self._SECUENCIAS[r][t]-1
        pasajeros = self.pasajerosEstacion(r, t)
        # Se crea un arreglo de zeros con tamaño igual al numero de estaciones
        capacidad = np.zeros(shape=(self.NUMEROESTACIONES))
        # Se crea un arreglo de zeros con tamaño igual al numero de estaciones
        puedenSubir = np.zeros(shape=(self.NUMEROESTACIONES))
         # Se crea una matriz cuadrada de zeros con tamaño igual al numero de estaciones
        _pasajerosPuedenAbordar = np.zeros(shape=(self.NUMEROESTACIONES,self.NUMEROESTACIONES))
        mTransbordo = self._TRANSBORDOS[r][t]
        i = secuencia[0] # Se toma la estación inicial
        capacidad[i] = self.CAPACIDADBUSES - pasajeros[i] # Se inicializa el arreglo de capacidades
        puedenSubir[i] = self.CAPACIDADBUSES # Se inicializa el arreglo de puedenSubir
        if puedenSubir[i] >= pasajeros[i]:
            _pasajerosPuedenAbordar[i,:] = self.distribucionDemanda(r,t)[i,:]
        else:
            _pasajerosPuedenAbordar[i,:] = self.distribucionDemanda(r,t)[i,:] / (pasajeros[i]*puedenSubir[i])
        if t == 0: # Si el trayecto es de ida
            for iS, i in enumerate(secuencia[1:]):

                valido = self.pasajerosEstacionValida(r, t)[i]
                anterior = secuencia[iS]

                pasajerosSuma = _pasajerosPuedenAbordar[:i,i].sum()
                pasajerosTransbordo = 0
                if np.in1d(i+1, mTransbordo):
                    mTransbordoB = mTransbordo == i+1
                    pasajerosTransbordo = _pasajerosPuedenAbordar[mTransbordoB].sum()

                if capacidad[anterior] > pasajeros[i]:
                    capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma + pasajerosTransbordo
                else:
                    capacidad[i] = 0

                if capacidad[anterior] > 0:
                    puedenSubir[i] = (capacidad[anterior] + pasajerosSuma + pasajerosTransbordo)*valido
                else:
                    puedenSubir[i] = (pasajerosSuma + pasajerosTransbordo)*valido
                # if round(puedenSubir[i]) >= pasajeros[i]:
                if puedenSubir[i] >= pasajeros[i]:
                    _pasajerosPuedenAbordar[i,:] = self.distribucionDemanda(r, t)[i,:]
                else:
                    _pasajerosPuedenAbordar[i,:] = (self.distribucionDemanda(r, t)[i,:]/pasajeros[i])*puedenSubir[i]
                # print _MEJOR_SECUENCIA[r][i-1][i]
        else: # Si el trayecto es de Vuelta
            # if r == 2 and t == 1: # Si es un final fantasma
            if self.EsRutaFantasma[r][t]:
                puedAbordI               = self.pasajerosPuedenAbordar(r, 0) 
                # Pasajeros que pueden abordar ida
                pasajerosPuedenAbordarI  = puedAbordI[0]
                # Capacidad que pueden abordar ida
                capacidadI               = puedAbordI[2]#[self._SECUENCIAS[r][0][-1]-1]
                # puedenSubirI             = puedAbordI[1]#[:self._SECUENCIAS[r][0][-1]-1,secuencia[1]]
                secuenciaI               = self._SECUENCIAS[r][0]-1 # Secuencia ida
                anterior                 = secuenciaI[-1]
                mTransbordoI          = self._TRANSBORDOS[r][0]# Transbordo ida

                pasajerosSuma = 0
                for x in secuenciaI:
                        pasajerosSuma += pasajerosPuedenAbordarI[x,i]

                if capacidad[anterior] > 0:
                    puedenSubir[i] = capacidadI[anterior] + pasajerosSuma
                else:
                    puedenSubir[i] = pasajerosSuma

                if capacidad[anterior] > pasajeros[i]:
                    capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma
                else:
                    capacidad[i] = 0
                # print puedenSubir[i]
                if puedenSubir[i] >= pasajeros[i]:
                    _pasajerosPuedenAbordar[i,:] = self.distribucionDemanda(r,t)[i,:]
                else:
                    _pasajerosPuedenAbordar[i,:] = (self.distribucionDemanda(r,t)[i,:]/pasajeros[i])*puedenSubir[i]

                for iS, i in enumerate(secuencia[1:]): # iS -> Contador, i -> Estacion secuencia
                    valido = self.pasajerosEstacionValida(r, t)[i]
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

                    if capacidad[anterior] > pasajeros[i]:
                        capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma + pasajerosSumaI + pasajerosTransbordo

                    if puedenSubir[i] >= pasajeros[i]:
                        _pasajerosPuedenAbordar[i,:] = self.distribucionDemanda(r,t)[i,:]
                    else:
                        _pasajerosPuedenAbordar[i,:] = (self.distribucionDemanda(r,t)[i,:]/pasajeros[i])*puedenSubir[i]
            else:
                for iS, i in enumerate(secuencia[1:]):

                    valido = self.pasajerosEstacionValida(r, t)[i]
                    anterior = secuencia[iS]
                    pasajerosSuma = 0#_pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i].sum()
                    # pasajerosSuma = _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i].sum()
                    for x in secuencia[:iS+1]:
                        pasajerosSuma += _pasajerosPuedenAbordar[x,i]

                    pasajerosTransbordo = 0
                    if np.in1d(i+1, mTransbordo):
                        mTransbordoB = mTransbordo == i+1
                        pasajerosTransbordo = _pasajerosPuedenAbordar[mTransbordoB].sum()

                    if capacidad[anterior] > pasajeros[i]:
                        capacidad[i] = capacidad[anterior] - pasajeros[i] + pasajerosSuma + pasajerosTransbordo
                    else:
                        capacidad[i] = 0

                    if capacidad[anterior] > 0:
                        puedenSubir[i] = (capacidad[anterior] + pasajerosSuma + pasajerosTransbordo)*valido
                    else:
                        puedenSubir[i] = (pasajerosSuma + pasajerosTransbordo)*valido
                        # print i,anterior, puedenSubir[i], _pasajerosPuedenAbordar[i-len(_pasajerosPuedenAbordar):,i]
                    if puedenSubir[i] >= pasajeros[i]:
                        _pasajerosPuedenAbordar[i,:] = self.distribucionDemanda(r,t)[i,:]
                    else:
                        _pasajerosPuedenAbordar[i,:] = (self.distribucionDemanda(r,t)[i,:]/pasajeros[i])*puedenSubir[i]
        # print np.around(puedenSubir, decimals= 0)
        # print capacidad
        # print np.rint(pasajeros)
        return [_pasajerosPuedenAbordar, puedenSubir, capacidad]
    # psPA = self.pasajerosPuedenAbordar(0,0)
    # print np.around(psPA[0], decimals=2) , psPA[1], psPA[2]


    def tiempoEsperaEstaciones(self, r, t):
        "Devuelve matriz de tiempo de Espera entre Estaciones para el trayecto 't' de la ruta 'r'"
        return self.pasajerosPuedenAbordar(r,t)[0]*self.TIEMPOABORDAR

    # print np.around(self.tiempoEsperaEstaciones(0, 0), decimals =3)
    # print np.around(self.tiempoEsperaEstaciones(0, 0).sum(axis=1), decimals =2)

    def tiempoAcumuladoBajada(self, r, t):
        "Devuelve matriz de tiempo Acumulado de Bajada para el trayecto 't' de la ruta 'r'"
        tiempoEspera  = self.tiempoEsperaEstaciones(r,t)
        mTransbordo = self._TRANSBORDOS[r][t]
        tiempoEsperaI = 0
        suma = np.zeros(shape=(self.NUMEROESTACIONES))
        _tiempoBajada = np.zeros(shape=(self.NUMEROESTACIONES,self.NUMEROESTACIONES))
        secuencia = self._SECUENCIAS[r][t]-1
        for i, e in enumerate(secuencia):
            if t == 0:
                suma[e] = tiempoEspera[:e,e].sum()
            else:
                suma[e] = tiempoEspera[secuencia[:i],e].sum()
                if r==2:
                    tiempoEsperaI = self.tiempoEsperaEstaciones(r,0)
                    secuenciaI = self._SECUENCIAS[r][0]-1
                    if np.in1d(e, secuenciaI):
                        suma[e] += tiempoEsperaI[secuenciaI[e:],e].sum() # Revisar
                    else:
                        suma[e] += tiempoEsperaI[secuenciaI,e].sum()
            if np.in1d(e+1, mTransbordo):
                mTransbordoB = mTransbordo == e+1
                # print e+1
                # print mTransbordoB
                suma[e] += tiempoEspera[mTransbordoB].sum()
                if r==2:
                    tiempoEsperaI = self.tiempoEsperaEstaciones(r,0)
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

    # print self.tiempoAcumuladoBajada(2,0)
    def tiempoAcumuladoSubida(self, r, t):
        "Devuelve matriz de tiempo Acumulado de Subida para el trayecto 't' de la ruta 'r'"
        tiempoEspera = self.tiempoEsperaEstaciones(r,t)
        suma = tiempoEspera.sum(axis=1)
        _tiempoSubida = np.zeros(shape=(self.NUMEROESTACIONES,self.NUMEROESTACIONES))
        np.fill_diagonal(_tiempoSubida,suma)
        secuencia = self._SECUENCIAS[r][t] -1
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

    # print np.around(self.tiempoAcumuladoSubida(0, 0), decimals = 2)

    def tiempoViajePromedio(self, r, t):
        '''
        Devuelve Matriz tiempo de viaje promedio para el trayecto 't' de la ruta 'r'
        '''
        # print value(self.FrecuenciasOptimas[0])
        tiempoEntreEstacionesM = self._TIEMPO_ENTRE_ESTACIONES[r]
        tiempoEsperaPromedioM  = self.tiempoEsperaPromedio(t)
        tiempoAcumuladoSubidaM = self.tiempoAcumuladoSubida(r,t)
        tiempoAcumuladoBajadaM = self.tiempoAcumuladoBajada(r,t)
        # print tiempoEsperaPromedioM
        # print tiempoAcumuladoSubidaM
        # print tiempoAcumuladoBajadaM
        _tiempoViajePromedio = np.zeros(shape=(self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        secuencia = self._SECUENCIAS[r][t]-1
        for i, ei in enumerate(secuencia):
            for ej in secuencia[i:]:
                _tiempoViajePromedio[ei,ej] = tiempoEntreEstacionesM[ei,ej] + tiempoEsperaPromedioM[ei,ej] + \
                tiempoAcumuladoSubidaM[ei,ej] + tiempoAcumuladoBajadaM[ei,ej]
        # print _tiempoViajePromedio.sum(), model[0].value
        return _tiempoViajePromedio

    # print np.around(self.tiempoViajePromedio(2,1), decimals = 2)
    # print np.around(self.tiempoViajePromedio(1,0).sum(axis=0), decimals = 2)

    def pasajerosEspera2Viaje(self,r,t):
        '''
        Devuelve matriz de tiempo de espera de los pasajeros
        para el segundo viaje para el trayecto 't' de la ruta 'r'
        '''
        return self.distribucionDemanda(r,t) - self.pasajerosPuedenAbordar(r,t)[0]

    # print np.around(self.pasajerosEspera2Viaje(2,1), decimals=1)
    # print np.around(self.pasajerosEspera2Viaje(2,1).sum(), decimals=1)

    def tiempoEsperaPor2Bus(self, t):
        "Devuelve matriz de tiempo de espera por el segundo bus para el trayecto 't'"
        return self.tiempoEsperaPromedio(t) + self.tiempoEsperaMaximo(t)

    # print np.around(self.tiempoEsperaPor2Bus(1), decimals=2)

    def tiempoEsperarPor2Viaje(self,r,t):
        '''
        Devuelve matriz de tiempo de espera para el
        segundo viaje para el trayecto 't' de la ruta 'r'
        '''
        pasajerosEspera2ViajeB = self.pasajerosEspera2Viaje(r,t)>0
        # pasajerosE2Vmat = self.pasajerosEspera2Viaje(r,t, model)
        # pasajerosEspera2ViajeB = np.zeros((self.NUMEROESTACIONES, self.NUMEROESTACIONES), dtype=bool)
        # for i in range(pasajerosE2Vmat.shape[0]):
        #     for j in range(pasajerosE2Vmat.shape[1]):
        #         if pasajerosE2Vmat[i,j] > 0:
        #             pasajerosEspera2ViajeB[i,j] = True

        _tiempoEsperarPor2Viaje = np.where(pasajerosEspera2ViajeB, self.tiempoEsperaPor2Bus(t), 0)
        return _tiempoEsperarPor2Viaje
    # print np.around(self.tiempoEsperarPor2Viaje(2,1), decimals=1)

    def frecuenciaTotal(self,t):
        "Devuelve matriz de Frecuencia Total para el segundo viaje para el trayecto 't'"
        _frecuenciaTotal = np.zeros(shape=(self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        # if model:
        #     for r, f in enumerate(model):
        #         _frecuenciaTotal += np.where(self._TOPOLOGIA[r][t]>0, model[r], 0)#value(f), 0)
        # else:
        for r, f in enumerate(self.FrecuenciasOptimas):
            _frecuenciaTotal += np.where(self._TOPOLOGIA[r][t]>0, f, 0)#value(f), 0)
        return _frecuenciaTotal

    # print np.around(self.frecuenciaTotal(1), decimals=2)

    def funcionCalidad(self,t):
        '''
        Devuelve matriz de Funcion de Calidad para el segundo viaje para el trayecto 't'

        Parametros
        ----------
            - t: trayecto donde "0" es ida y "1" es vuelta

        Return
        ------
            - matriz(self.NUMEROESTACIONES, self.NUMEROESTACIONES)

        '''
        return self.frecuenciaTotal(t)*self.tiempoEsperaPromedio(t)

    # print np.around(self.funcionCalidad(1), decimals=2)

    def serviciosRequeridos(self,r,t):
        '''
        Devuelve matriz de Servicios Requeridos para el
        segundo viaje para el trayecto 't' de la ruta 'r'
        '''
        return self.distribucionDemanda(r,t)/self.CAPACIDADBUSES

    # print np.around(self.serviciosRequeridos(1,0), decimals=2)

    def flujoAsignado(self,t):
        '''
        Devuelve matriz de Flujo Asignado para el segundo viaje de todas las rutas en el trayecto trayecto 't'

        Parametros
        ----------
            - t: trayecto donde "0" es ida y "1" es vuelta

        Return
        ------
            - _flujoAsignado: matriz(self.NUMEROESTACIONES, self.NUMEROESTACIONES)

        '''
        _flujoAsignado = np.zeros(shape=(self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        for r in range(self.NUMERORUTAS):
            _flujoAsignado += np.where(self._TOPOLOGIA[r][t]>0, self.serviciosRequeridos(r,t), 0)
        # print self.FrecuenciasOptimas
        return _flujoAsignado


    def intervalosTiemposEntreSalidas(self):
        "Devuelve los periodos de salida de las rutas"
        return 1/np.array(self.FrecuenciasOptimas)

    def tiempoViajePromedioSinEsperaSB(self,r,t):
        '''
        Matriz tiempo de viaje promedio
        '''
        # print value(self.FrecuenciasOptimas[0])
        tiempoEntreEstacionesM = self._TIEMPO_ENTRE_ESTACIONES[r]
        tiempoAcumuladoSubidaM = self.tiempoAcumuladoSubida(r,t)
        tiempoAcumuladoBajadaM = self.tiempoAcumuladoBajada(r,t)
        _tiempoViajePromedio = np.zeros(shape=(self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        secuencia = self._SECUENCIAS[r][t]-1
        for i, ei in enumerate(secuencia):
            for ej in secuencia[i:]:
                _tiempoViajePromedio[ei,ej] = tiempoEntreEstacionesM[ei,ej] + tiempoAcumuladoSubidaM[ei,ej] + tiempoAcumuladoBajadaM[ei,ej]
        # print _tiempoViajePromedio.sum(), model[0].value
        return _tiempoViajePromedio

    def tiempoViajePromedioSinEspera(self,r,t):
        '''
        Matriz tiempo de viaje promedio
        '''
        # print value(self.FrecuenciasOptimas[0])
        tiempoEntreEstacionesM = self._TIEMPO_ENTRE_ESTACIONES[r]
        _tiempoViajePromedio = np.zeros(shape=(self.NUMEROESTACIONES, self.NUMEROESTACIONES))
        secuencia = self._SECUENCIAS[r][t]-1
        for i, ei in enumerate(secuencia):
            for ej in secuencia[i:]:
                _tiempoViajePromedio[ei,ej] = tiempoEntreEstacionesM[ei,ej]
        # print _tiempoViajePromedio.sum(), model[0].value
        return _tiempoViajePromedio
    

    def convertHour(self, horas = None, hora = None):
        '''
        horas/hora es una variable que viene en segundos, esta Función
        transforma los segundos en la clase delta.timedelta y los devuelve
        como string
        '''
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


    def horaInicioServicios(self,r):
        '''
        Devuelve un arreglo con las horas de inicio de cada servicio en la Ruta 'r'
        '''
        intervalosPeriodosRutas = self.intervalosTiemposEntreSalidas()[r]/(24*60)
        tiempoInicio = self.HORAINICIO/24
        tiempoFinal = self.HORAFIN/24
        # minutosTotales = (self.HORAINICIO - self.HORAFIN)*60 # Los convertimos en minutos
        horas = np.arange(tiempoInicio, tiempoFinal, intervalosPeriodosRutas)

        # horasD = []
        # for i, x in enumerate(horas):
        #     horasD.append(str(datetime.timedelta(seconds= int(round(((x*24)*60)*60)))))
        # return np.array(horasD)

        return horas

    def horaEstaciones(self,r,t, idT):
        '''
        Devuelve la linea del servicio,
        es decir para cada estación tiene: la hora de llegada, la hora de salida,
        dos booleanos que indican si es una estación de inicio o estación final,
        el id del trayecto y la secuencia

        Parametros
        ----------
            - r: Indice de Ruta
            - t: Indice de Trayecto
            - idT: id del Trayecto

        Return
        ------
            - _horaEstaciones: matriz que contiene
                               [[   * _horaEstacionesLlegada,
                                    * _horaEstacionesSalida,
                                    * estacionInicio,
                                    * estacionFinal,
                                    * idTrayecto,
                                    * secuencia ], ...]

        '''
        horaInicio = self.horaInicioServicios(r)
        secuencia = self._SECUENCIAS[r][t] -1
        tiempoSalida = self.tiempoViajePromedioSinEsperaSB(r,t)[secuencia[0],secuencia] / (24*60)
        tiempoLlegada = np.zeros(len(secuencia))
        # tiempoLlegada[1:] = tiempoSalida[:-1] + self.tiempoViajePromedioSinEspera(r,t)[secuencia[0],secuencia[1:]] / (24*60)
        for i in range(1,len(tiempoLlegada)):
            tiempoLlegada[i] = tiempoSalida[i-1] + self.tiempoViajePromedioSinEspera(r,t)[secuencia[i-1],secuencia[i]] / (24*60)
        _horaEstaciones = []
        for horaI in horaInicio:
            # _horaEstacionesLlegada = self.convertHour(horaI + tiempoLlegada)
            _horaEstacionesLlegada = (horaI + tiempoLlegada)
            # _horaEstacionesSalida = self.convertHour(horaI + tiempoSalida)
            _horaEstacionesSalida = (horaI + tiempoSalida)
            estacionInicio = np.zeros(len(secuencia), dtype=bool)
            estacionInicio[0] = True
            estacionFinal = np.zeros(len(secuencia), dtype=bool)
            estacionFinal[-1] = True
            idTrayecto = np.empty(len(secuencia))
            idTrayecto.fill(idT)
            _horaEstaciones.append(zip(_horaEstacionesLlegada, _horaEstacionesSalida, estacionInicio, estacionFinal, idTrayecto, secuencia))
        dtype = [('horaLlegada', float), ('horaSalida', float),('estacionInicio', bool), 
                 ('estacionFinal', bool),('idTrayecto', int), ('secuencia', int)]
        _horaEstaciones = np.array(_horaEstaciones, dtype)
        return _horaEstaciones


    def horasRuta(self,r):
        '''
        Devuelve una lista que contiene la hora inicial,
        la hora final y el id del trayecto para la ruta "r"
        '''
        horas = []
        rutaT = self._TRAYECTOS[r]
        horasIda = []
        horasVuelta = []
        for t, value in rutaT.iteritems():
            if value == 'Ida':
                # horas.append(self.horaEstaciones(r,0,t))
                for horaE in self.horaEstaciones(r,0,t):
                    horasIda.append((horaE[0]['horaLlegada'], horaE[-1]['horaSalida'], horaE[0]['idTrayecto']))
            else:
                for horaE in self.horaEstaciones(r,1,t):
                    horasVuelta.append((horaE[0]['horaLlegada'], horaE[-1]['horaSalida'], horaE[0]['idTrayecto']))
        horas = horasIda + horasVuelta
        dtype= [('horaInicial', float), ('horaFinal', float), ('idTrayecto', int)]
        horas = np.array(horas, dtype)
        # print horas.shape, r, horas
        # horas = horas.reshape(rows*columns,horas.shape[2])
        return horas

    def serviciosRuta(self,r, horas = None):
        '''
            Función que recibe la ruta para la cual se van a sacar los servicios
            Los servicios son la identificación de un determinado bus que recorre la ruta

            Parametros
            ----------
                - r: indice de Ruta. Ej: 0 --> Ruta 1
                - horas: Arreglo con hora inicial y final de la ruta

            Return
            ------
                - servicios: 

        '''
        if horas == None:
            horas = self.horasRuta(r)
        horasDict = []
        tray = self._TRAYECTOS[r]
        tIda = None
        tVuelta = None
        for key, value in tray.items():
            if value == 'Ida':
                tIda = key
            else:
                tVuelta = key
        for ind ,hora in enumerate(horas):
            horasDict.append((ind , hora['horaInicial'], hora['idTrayecto']))
        dtype = [('id', int),('horaLlegada', float), ('idTrayecto', int)]
        horasDictArray = np.array(horasDict, dtype)
        horasDictArray.sort(order='horaLlegada')
        pilaSalida = []
        servicios = []
        pilaSalida.append((0,horas[horasDictArray[0][0]]['horaFinal'], horasDictArray[0][2]))
        servicios.append((0, horasDictArray[0][0], horasDictArray[0][1], horasDictArray[0][2]))
        serv  = 1
        flag = True
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
            if pilaTrayecto[0]['horaSalida'] < x[1] and flag:
                serviciosV = np.array(servicios)
                serviciosAdicionales = serviciosV[serviciosV[:,-1]==tVuelta]
                for ind in reversed(serviciosAdicionales):
                    servicios.insert(0, (ind[0], -1.0, 0.0, tIda))
                servicios.append((pilaTrayecto[0]['servicio'], x[0], x[1], x[2]))
                del pilaSalida[pilaTrayecto[0]['servicio']]
                # pilaSalida.insert(pilaSalidaArray[0]['servicio'],(pilaSalidaArray[0]['servicio'], horas[:]['horaSalida'][x[0]][-1],x[2]))
                pilaSalida.insert(pilaTrayecto[0]['servicio'],(pilaTrayecto[0]['servicio'], horas[x[0]]['horaFinal'],x[2]))
                flag = False
            elif pilaTrayecto[0]['horaSalida'] < x[1]:
                servicios.append((pilaTrayecto[0]['servicio'], x[0], x[1], x[2]))
                del pilaSalida[pilaTrayecto[0]['servicio']]
                # pilaSalida.insert(pilaSalidaArray[0]['servicio'],(pilaSalidaArray[0]['servicio'], horas[:]['horaSalida'][x[0]][-1],x[2]))
                pilaSalida.insert(pilaTrayecto[0]['servicio'],(pilaTrayecto[0]['servicio'], horas[x[0]]['horaFinal'],x[2]))
            else:
                pilaSalida.append((serv , horas[x[0]]['horaFinal'] , x[2]))
                servicios.append((serv , x[0], x[1], x[2]))
                serv +=1
        # print len(servicios)
        numeroServA = len(serviciosAdicionales)
        serviciosIda = np.array(servicios)
        serviciosIda = serviciosIda[serviciosIda[:,-1]==tIda]
        for serv in serviciosIda[-numeroServA:]:
            servicios.append((serv[0], -1.0, 1.0, tVuelta))
        # print len(servicios)

        # dtype = [('servicio', int), ('id', int), ('horaLlegada', float), ('idTrayecto', int)]
        return np.array(servicios)

    def serviciosOrdenados(self,r, t):
        "Recibe los servicios, y los devuelve con orden respecto a los servicios"
        serv = self.serviciosRuta(r)
        serv = serv[serv[:,-1]==t]
        _serviciosOrdenados = serv[np.lexsort((serv[:,2], serv[:,0]))]
        arrayServ = []
        length = 0
        for i in range(int(_serviciosOrdenados[:,0].max())+1):
            subArray = _serviciosOrdenados[_serviciosOrdenados[:,0] == i]
            lengthA = len(subArray)
            arrayServ.append(subArray)
            if length < lengthA:
                length = lengthA
        newArray = np.empty_like(serv)
        ind = 0
        for i in range(length):
            for e in arrayServ:
                if i < len(e):
                    newArray[ind] = e[i]
                    ind += 1
                # print e[i]
        return np.array(newArray)
        # return 0


    def jsonFile(self, direccion = None, nombreArchivoS = None, nombreProgramacion= None):
        '''
            Genera el archivo "horarios-NOMBREARCHIVOFUENTE-.json" con la estructura v3
            requerida por SingleClick

            Parametros
            ----------
                - direccion = String. Contiene la direccion de la carpeta donde se va a generar el JSON
                                      Si se deja como vacio la direccion por defecto sera:
                                        "/var/www/html/Archivos/Optimizacion/Programacion/"
                - nombreArchivoS = String. Contiene el nombre del archivo para ser generado. Si se deja
                                           Vacio el nombre por defecto sera el nombre de este archivo.
                                           "modeloOptimizacionV5"

        '''
        estructura = []
        tray = 0
        # horaAnt = None
        # print self._TRAYECTOS
        # _serviciosRuta = None
        for r, rutaT in enumerate(self._TRAYECTOS):
            _serviciosRuta = self.serviciosRuta(r)
            horaAnt = None
            for t, value in rutaT.iteritems():
                estructura.append({'idtrayecto':t})
                serviciosEst = []
                if value == 'Ida':
                    horas = self.horaEstaciones(r,0,t)
                    horaAnt = horas
                else:
                    if horaAnt == None:
                        for key, valueD in self._TRAYECTOS[r].iteritems():
                            if valueD == 'Ida':
                                horaAnt = self.horaEstaciones(r,0,key)
                    horas = self.horaEstaciones(r,1,t)
                # print self.serviciosRuta(0)
                # _serviciosRuta = self.serviciosOrdenados(r, t)
                _serviciosRutaB = _serviciosRuta[_serviciosRuta[:,-1]==t]
                for i, servicio in enumerate(_serviciosRutaB):
                # for i, servicio in enumerate(_serviciosRuta):
                    horarios = {}
                    # horarios = []
                    serviciosDict = {'idservicio':int(servicio[0])+1}
                    if servicio[1] != -1:
                        if value == 'Ida':
                            idLinea = servicio[1]
                        else:
                            idLinea = servicio[1] - len(horaAnt)
                        for j, hora in enumerate(horas[idLinea]):
                            # print hora
                            estacionesDict = {}
                            if self.EstacionesBaseDatosDict:
                                estacionesDict["idestacion"] = self.EstacionesBaseDatosDict[hora['secuencia']+1]
                            else:
                                estacionesDict["idestacion"] = hora['secuencia']+1
                            estacionesDict["horallegada"] = self.convertHour(hora = hora['horaLlegada'])
                            estacionesDict["horasalida"] = self.convertHour(hora = hora["horaSalida"])
                            estacionesDict["estacioninicial"] = 'true' if hora["estacionInicio"] else 'false'
                            estacionesDict["estacionfinal"] = 'true' if hora["estacionFinal"] else 'false'
                            horarios[str(j)] = estacionesDict
                            # horarios.append(str(j) +" "+str(estacionesDict))
                    serviciosDict["horarios"] = horarios
                    serviciosDict["orden"] = i+1
                    serviciosEst.append(serviciosDict)
                estructura[tray]['servicios']= serviciosEst
                tray+=1
        path = inspect.getfile(inspect.currentframe()) 
        nombreArchivoExt = os.path.basename(path)
        nombreArchivo, extension = os.path.splitext(nombreArchivoExt)
        if direccion is None:
            out_file = open("/var/www/html/Archivos/Optimizacion/Programacion/"+nombreArchivoS+".json","w")
        else:
            if nombreArchivoS is None:
                out_file = open(direccion+"/"+nombreArchivo+".json","w")
            else:
                out_file = open(direccion+"/"+nombreArchivoS+".json","w")

        # out_file = open("/etc/optimizacion/archivos/horariosOpt.json","w")
        # out_file = open("/var/www/html/Archivos/Optimizacion/horariosOpt.json","w")
        json.dump(estructura,out_file, indent=4, sort_keys=True, separators=(',', ': '))
        self.generarRegistroBD(nombreArchivoS, nombreProgramacion)
        out_file.close()

    def generarRegistroBD(self, nombreArchivoS, nombreProgramacion):
        '''
            Genera registro de la generacion de optimizacion de frecuencias en la base de datos.
            Sera guardada en la tabla "programacion-optimizacion" con el:
                - nombreprogramacionoptimizacion
                - archivoprogramacionoptimizacion
                - fechacreacion
                - fechamodificacion

            Parametros
            ----------
                - nombreArchivoS: String, nombre del archivo generado.
                - nombreProgramacion: String, nombre de la programacion.
        '''
        cursor = self.dbr.cursor() 
        query_quotes =  "SET sql_mode='ANSI_QUOTES'" # para que acepte tablas con "caracteres especiales"
        cursor.execute(query_quotes)

        sqlCheckNombre = '''SELECT nombreprogramacionoptimizacion FROM "programacion-optimizacion" where 
                           LOWER(nombreprogramacionoptimizacion) = '%s'; ''' %nombreProgramacion.lower()
        cursor.execute(sqlCheckNombre)
        checkNombre = cursor.fetchall()

        fecha = datetime.datetime.now().date()
        nombreArchivo = nombreArchivoS + ".json"
        if len(checkNombre) == 0:
            sqlNuevoRegistro = """INSERT INTO "programacion-optimizacion" (nombreprogramacionoptimizacion,
                 archivoprogramacionoptimizacion, fechacreacion, fechamodificacion, enejecucion)
                 VALUES ('%s', '%s', NOW(), NOW(), 'No')"""%(nombreProgramacion, nombreArchivo)
                 # VALUES ('%s', '%s', NOW(), NOW())"""%(nombreProgramacion, nombreArchivo)
            try:
               # Ejecutamos el comando
               cursor.execute(sqlNuevoRegistro)
               # Efectuamos los cambios en la base de datos
               self.dbr.commit()
            except:
               # Si se genero algún error revertamos la operación
               self.dbr.rollback()
               print "datos no validos"
        else:
            sqlModificacionRegistro = """UPDATE "programacion-optimizacion" 
            SET fechamodificacion= NOW(), archivoprogramacionoptimizacion='%s', enejecucion = 'No'
            WHERE LOWER(nombreprogramacionoptimizacion) = '%s' """ % (nombreArchivo, nombreProgramacion.lower())

            try:
               # Ejecutamos el comando
               cursor.execute(sqlModificacionRegistro)
               # Efectuamos los cambios en la base de datos
               self.dbr.commit()
            except:
               # Si se genero algún error revertamos la operación
               self.dbr.rollback()
               print "datos no validos"
        self.dbr.close()

    def objFunctionGenetic(self, frecuencias):
        '''
        Función objetivo utilizada en el algoritmo Genético,
        Que devuelve el valor de la función sin escalamiento

        Parametros
        ----------
            - frecuencias: Lista de tipo int, que contiene los indices
                           de la lista "self.ValoresFrecuencias".
        Return
        ------
            - (obj1 + obj2)*penalty: Devuelve el valor de la funcion objetivo total,
                                     Que es la suma de la funcion objetivo de los pasajeros "obj1"
                                     mas la suma de la funcion objetivo del operador "obj2"
                                     esto multiplicado por una penalidad.
        '''
        # global self.FrecuenciasOptimas
        penalty = 1
        for i, x in enumerate(frecuencias):
            self.FrecuenciasOptimas[i] = self.ValoresFrecuencias[x]
            # self.FrecuenciasOptimas[i] = x

        lenf = len(self.FrecuenciasOptimas)
        obj1 = (sum(self.tiempoViajePromedio(r,t).sum() for r in range(lenf) for t in  [0,1]) +
                (sum(self.tiempoEsperarPor2Viaje(r,t).sum() for r in range(lenf) 
                 for t in  [0,1]))*self.TIEMPOESPERA2BUS)*self.FACTORPASAJERO
        obj2 = sum(self.COSTOS[r]* self.FrecuenciasOptimas[r] for r in range(lenf))*self.FACTOROPERADEOR

        # rule = self.flujoAsignado().sum(axis=0) <= self.funcionCalidad().sum(axis=0)
        # Restriccion, se agrega penalidad a objetivo si no se cumple
        if not((self.flujoAsignado(0) <= self.funcionCalidad(0)).all() and (self.flujoAsignado(1) <= self.funcionCalidad(1)).all()):
            penalty = 100
        # vecO[frecuencias]
        return (obj1 + obj2)*penalty

    def objFunction(self, frecuencias):
        '''
        Devuelve el valor de la funcion Funcion objetivo utilizada en el algoritmo Nelder-Mead,
        ya que se utilizan los valores de las Frecuencias Optimas obtenidas por el algoritmo. 
        Se requiere separar las funciones objetivo ya que la variacion y tipo de el parametro "frecuencias"
        es diferente.


        Parametros
        ----------
            - frecuencias: Lista de tipo float, que contiene las frecuencias
                           actuales.
        Return
        ------
            - (obj1 + obj2)*penalty: Devuelve el valor de la funcion objetivo total,
                                     Que es la suma de la funcion objetivo de los pasajeros "obj1"
                                     mas la suma de la funcion objetivo del operador "obj2"
                                     esto multiplicado por una penalidad.

        '''
        # global self.FrecuenciasOptimas
        penalty = 1

        for i, x in enumerate(frecuencias):
            # self.FrecuenciasOptimas[i] = self.ValoresFrecuencias[x]
            if x < self.ValoresFrecuencias[-1]:
                penalty = 1000
                self.FrecuenciasOptimas[i] = self.ValoresFrecuencias[-1]
            else:
                self.FrecuenciasOptimas[i] = x
        lenf = len(self.FrecuenciasOptimas)
        obj1 = (sum(self.tiempoViajePromedio(r,t).sum() for r in range(lenf) for t in  [0,1]) +
                (sum(self.tiempoEsperarPor2Viaje(r,t).sum() for r in range(lenf) for t in  [0,1]))*self.TIEMPOESPERA2BUS)*self.FACTORPASAJERO
        obj2 = sum(self.COSTOS[r]* self.FrecuenciasOptimas[r] for r in range(lenf))*self.FACTOROPERADEOR

        if not((self.flujoAsignado(0) <= self.funcionCalidad(0)).all() and (self.flujoAsignado(1) <= self.funcionCalidad(1)).all()):
            penalty = 100
        # vecO[frecuencias]
        return (obj1 + obj2)*penalty

    def objFunctionList(self, frecuencias = None):
        '''
        Funcion objetivo utilizada en el algoritmo Nelder-Mead,
        ya que se utilizan los valores de las Frecuencias Optimas
        obtenidas por el algoritmo

        frecuencias: Lista de tipo float, que contiene las frecuencias
        optimas
        '''
        # global self.FrecuenciasOptimas

        if frecuencias != None:
            for i, x in enumerate(frecuencias):
                # self.FrecuenciasOptimas[i] = self.ValoresFrecuencias[x]
                self.FrecuenciasOptimas[i] = x

        lenf = len(self.FrecuenciasOptimas)
        obj1 = (sum(self.tiempoViajePromedio(r,t).sum() for r in range(lenf) for t in  [0,1]) +
                (sum(self.tiempoEsperarPor2Viaje(r,t).sum() for r in range(lenf) for t in  [0,1]))*self.TIEMPOESPERA2BUS)*self.FACTORPASAJERO
        obj2 = sum(self.COSTOS[r]* self.FrecuenciasOptimas[r] for r in range(lenf))*self.FACTOROPERADEOR

        # vecO[frecuencias]
        return [obj1, obj2]

    def gradf(self, frecuencias):
        '''
        Calcula la gradiente de la función objetivo a través de numpy
        '''
        # global self.FrecuenciasOptimas

        for i, x in enumerate(frecuencias):
            # self.FrecuenciasOptimas[i] = self.ValoresFrecuencias[x]
            self.FrecuenciasOptimas[i] = x
        arrayT = []
        for r in range(len(frecuencias)):
            obj1 = (sum(self.tiempoViajePromedio(r,t).sum() for t in  [0,1]) +
                sum(self.tiempoEsperarPor2Viaje(r,t).sum() for t in  [0,1])*self.TIEMPOESPERA2BUS)*self.FACTORPASAJERO
            obj2 = self.COSTOS[r]* frecuencias[r]*self.FACTOROPERADEOR
            arrayT.append(obj1+ obj2)
        arrayN = np.array(arrayT)
        arrayG = np.gradient(arrayN)
        return arrayG


    # Genome instance
    def optGAPyevolve(self, multiProcessing= False):
        '''
        Implementación de Algoritmo Genético, a través de la librería pyevolve.
        Devuelve la lista con las frecuencias óptimas para cada ruta
        '''
        # Crea una lista del tamaño del Numero de Rutas
        genome = G1DList.G1DList(len(self.FrecuenciasOptimas))
        # parametros que varían de 0 a 24 que son los indices de los valores
        genome.setParams(rangemin=0, rangemax=25)
        genome.initializator.set(Initializators.G1DListInitializatorInteger)
        genome.mutator.set(Mutators.G1DListMutatorIntegerRange)

        # The evaluator function (objective function)
        genome.evaluator.set(self.objFunctionGenetic)

        # Genetic Algorithm Instance
        ga = GSimpleGA.GSimpleGA(genome)

        if multiProcessing:
            ga.setMultiProcessing()

        ga.selector.set(Selectors.GRankSelector)
        # ga.selector.set(Selectors.GTournamentSelector)
        # csv_adapter = DBFileCSV(identify="run1", filename="stats.csv")
        # ga.setDBAdapter(csv_adapter)
        ga.setMinimax(Consts.minimaxType["minimize"])
        ga.setGenerations(20)
        ga.setMutationRate(0.1)
        # ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)

        # print Initializators.G1DListInitializatorReal
        # Do the evolution, with stats dump
        # frequency of 10 generations
        ga.evolve(freq_stats=5)

        # # Best individual
        best = ga.bestIndividual()
        # print best
        # print [self.ValoresFrecuencias[x] for x in best.genomeList]
        frecuencias = np.copy(self.FrecuenciasOptimas)
        for i, g in enumerate(best.genomeList):
            frecuencias[i] = self.ValoresFrecuencias[g]

        print "\nFuncion objetivo Genetico: %.2f"% (best.score,), \
        ", Frecuencias: ", np.around(frecuencias, decimals = 4)

        objetivos = self.objFunctionList(frecuencias)
        print "Objetivo Pasajeros: " + str(objetivos[0])+" Objetivo Operador: " + str(objetivos[1])
        return frecuencias

    def optNelderMead(self, multiProcessing = False):
        '''
        Función que cambia las variables de las self.FrecuenciasOptimas # global
        utilizando el algoritmo Nelder-Mead de la librería SciPy
        Nelder-Mead: nonlinear optimization technique
        '''
        # global self.FrecuenciasOptimas
        x0 = np.array(self.optGAPyevolve(multiProcessing))

        # x0 = np.asarray((0.18, 0.11, 0.12))
        # resultado = optimize.minimize(self.objFunction, x0, method = 'Nelder-Mead',
        #                options={'disp': False})
        resultado = optimize.fmin(self.objFunction, x0)
        print "\nFuncion Objetivo Nelder-Mead: %.2f"%(self.objFunction(resultado)),
        print ', Frecuencias : ', #np.around(resultado.x, decimals= 4)
        self.FrecuenciasOptimas = resultado
        # frecuencias = []
        for i, x in enumerate(resultado):
            # self.FrecuenciasOptimas[i] = x
            # frecuencias.append(x)
            print x,
        # self.FrecuenciasOptimas = frecuencias

        objetivos = self.objFunctionList(self.FrecuenciasOptimas)
        print "\nObjetivo Pasajeros: " + str(objetivos[0])+" Objetivo Operador: " + str(objetivos[1])

    def trayectosValueF(self, secuencias):
        '''
            Transpone la matriz de secuencias y pasa de indices iniciando en 1 a 0
            ej: [[1,2,3,10,15],...] ---> [[0,1,2,9,14],...]

            Parametros
            ----------
                - secuencias: Matriz que contiene las secuencias de cada ruta
                              [[ida,vuelta], # Ruta 1
                                ...        , # Ruta n
                              ]
            Return
            ------
                - trayectosValue: Matriz transpuesta de secuencias
                                  [[ruta 1,...,ruta n], # Trayecto 1
                                    ...               , # Trayecto 2
                                  ]
                              
        '''
        trayectosValue = map(list, zip(*secuencias))
        for tray in range(len(trayectosValue)):
            for ruta in range(len(trayectosValue[0])):
                trayectosValue[tray][ruta] = list(trayectosValue[tray][ruta] -1)
        return trayectosValue

    def calcularTopologiaTiempo(self):
        '''
            Cambia las matrices de self._TIEMPO_ENTRE_ESTACIONES y self._TOPOLOGIA, de acuerdo a las 
            self._SECUENCIAS establecidas 

            Parametros
            ----------
                None

            Return
            ------
                - trayectosValue: Matriz transpuesta de secuencias
                                  [[ruta 1,...,ruta n], # Trayecto 1
                                    ...               , # Trayecto 2
                                  ]
        '''
        # global self._TIEMPO_ENTRE_ESTACIONES
        # global self._TOPOLOGIA
        trayectosValue = self.trayectosValueF(self._SECUENCIAS)
        tiemposTrayectos = self.tiempoTrayectosTransbordo(trayectosValue)
        self._TIEMPO_ENTRE_ESTACIONES = self.tiempoTrayectosRutas(tiemposTrayectos)
        self._TOPOLOGIA = self.obtenerTopologias(self._TIEMPO_ENTRE_ESTACIONES)

#Se ejecuta la optimización con Algorítmos Geneticos y luego el NelderMead

if __name__ == "__main__":
    optimizacionF = OptimizacionFrecuencias(numeroDemanda = 2)
    optimizacionF.obtenerDatosBase( 
        db_host =  'localhost',
        usuario = 'optimizacion',
        clave =  'fdoq9zSyfSlMsyW9wGkh',
        base_de_datos = 'rutamega_principal',
    )
    # optimizacionF.obtenerDatosBase()
    # optimizacionF.generarCSV()
    optimizacionF.calcularTopologiaTiempo()
    # print optimizacionF._TRANSBORDOS
    optimizacionF.optNelderMead(multiProcessing = True)
  
    print "\nFactor Operador: ", optimizacionF.FACTOROPERADEOR, " Factor Pasajero: ", optimizacionF.FACTORPASAJERO
    print "Demanda: ", optimizacionF.NUMERODEMANDA, " Costos: ", optimizacionF.COSTOS

    # Se ejecuta la función que genera el archivo JSON, se toma el primer parametro como el nombre de archivo.
    # Ejemplo: > python modeloOptimizacionV5.py horariosOpt. El nombre del archivo seria horariosOpt.json
    optimizacionF.jsonFile(nombreArchivoS = sys.argv[1], nombreProgramacion = sys.argv[2])

