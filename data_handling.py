# -*- coding: utf-8 -*-
"""Data_Handling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/rickituri98/Fault_Classifier_CNN/blob/master/Data_Handling.ipynb

# Data Handling - Fault Events from IEEE 13 Node Test Feeder

## Files import from GitHub Repository
"""

#!npx degit rickituri98/Fault_Classifier_CNN -f

"""Modules import and functions initialization"""

import os
import copy
import sys
from comtrade import Comtrade
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import interactive
import time
import pandas as pd
import seaborn as sns
import scipy.io as sio
from IPython.display import display
import pywt
import scipy.stats
import datetime as dt
from collections import defaultdict, Counter
from scipy.signal import find_peaks
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def import_files(path):
  dir_list = sorted(os.listdir(path)) # lista de señales en comtrade
  tupfiles = list() # lista de pares de archivos cfg y dat
  l = np.arange(0, len(dir_list), 2)
  recorders = list()
  for i in l:
    (cfg, dat) = (dir_list[i], dir_list[i+1])
    tupfiles.append((cfg, dat))
    record = Comtrade()
    recorders.append(record)
  return tupfiles, recorders

def creacion_dic(dic,valores,string):
  pos = string.find("/")
  if string[pos-1]=='A':
    dic['A']= np.array(valores)
  if string[pos-1]=='B':
    dic['B']= np.array(valores)
  if string[pos-1]=='C':
    dic['C']= np.array(valores)

def get_XY(path,tupfile, record):
  record.load(path+tupfile[0])
  num_sig = record.analog_count
  timesec = np.array(record.time)
  samples =record.total_samples
  dic1=dict.fromkeys(['A','B','C'],np.zeros(samples))
  dic1['time']=timesec
  dic2=dict.fromkeys(['A','B','C'],np.zeros(samples))
  dic2['time']=timesec
  dic3=dict.fromkeys(['A','B','C'],np.zeros(samples))
  dic3['time']=timesec
  dic4=dict.fromkeys(['A','B','C'],np.zeros(samples))
  dic4['time']=timesec
  for k in range(0, num_sig):
    string = record.analog_channel_ids[k]
    if string.startswith('LC684-652A'):
      creacion_dic(dic1,record.analog[k],string)
    elif string.startswith('LC692-675'):
      creacion_dic(dic2,record.analog[k],string)
    elif string.startswith('LOHL632-633'):
      creacion_dic(dic3,record.analog[k],string)
    elif string.startswith('LOHL645-646'):
      creacion_dic(dic4,record.analog[k],string)
  list_dic=[dic1,dic2,dic3,dic4]
  return list_dic

def fill_Siglist(lista, sublista):
  lista.append(sublista[0])
  lista.append(sublista[1])
  lista.append(sublista[2])
  lista.append(sublista[3])

def Inputs_Vectors(path, tupfiles, recorders):
  signal_list = list()
  Fault_type_list = list()
  Fault_cat_list = list()

  ph_1, ph_2, ph_2G, ph_3, noF = 0, 1, 2, 3, 4
  for entry in range(len(tupfiles)):
    sub_typeF = list()
    cat_F = list()
    list_sig = get_XY(path,tupfiles[entry], recorders[entry])
    id_f = tupfiles[entry][0]

    if id_f.find("_L692-675_") != -1 or id_f.find("_L632-633_") != -1 or id_f.find("_L671-680_") != -1:

      if id_f.find("Falla_A_") != -1:
        fill_Siglist(signal_list, list_sig)
        sub_typeF.append(np.array([[1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 1]]))
        cat_F.append([ph_1, ph_1, ph_1, noF])
      elif id_f.find("Falla_B_") != -1:
        fill_Siglist(signal_list, list_sig)
        sub_typeF.append(np.array([[0, 0, 0, 0, 1], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0]]))
        cat_F.append([noF, ph_1, ph_1, ph_1])
      elif id_f.find("Falla_C_") != -1:
        fill_Siglist(signal_list, list_sig)
        sub_typeF.append(np.array([[1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0]]))
        cat_F.append([ph_1, ph_1, ph_1, ph_1])
      elif id_f.find("Falla_2F_") != -1:
        if id_f.find("_CA_") != -1:
          fill_Siglist(signal_list, list_sig)
          sub_typeF.append(np.array([[0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0]]))
          cat_F.append([ph_2, ph_2, ph_2, ph_1])
        elif id_f.find("_BC_") != -1:
          fill_Siglist(signal_list, list_sig)
          sub_typeF.append(np.array([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0]]))
          cat_F.append([ph_1, ph_2, ph_2, ph_2])
        elif id_f.find("_AB_") != -1:
          fill_Siglist(signal_list, list_sig)
          sub_typeF.append(np.array([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0]]))
          cat_F.append([ph_1, ph_2, ph_2, ph_1])
      elif id_f.find("Falla_2GF_") != -1:
        if id_f.find("_CA_") != -1:
          fill_Siglist(signal_list, list_sig)
          sub_typeF.append(np.array([[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [1, 0, 0, 0, 0]]))
          cat_F.append([ph_2G, ph_2G, ph_2G, ph_1])
        elif id_f.find("_BC_") != -1:
          fill_Siglist(signal_list, list_sig)
          sub_typeF.append(np.array([[1, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]))
          cat_F.append([ph_1, ph_2G, ph_2G, ph_2G])
        elif id_f.find("_AB_") != -1:
          fill_Siglist(signal_list, list_sig)
          sub_typeF.append(np.array([[1, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [1, 0, 0, 0, 0]]))
          cat_F.append([ph_1, ph_2G, ph_2G, ph_1])
      elif id_f.find("Falla_3F_") != -1:
        fill_Siglist(signal_list, list_sig)
        sub_typeF.append(np.array([[0, 0, 1, 0, 0],[0, 0, 0, 1, 0], [0, 0, 0, 1, 0], [0, 0, 1, 0, 0]]))
        cat_F.append([ph_2G, ph_3, ph_3, ph_2G])

    elif id_f.find("_L684-652_") != -1:
      fill_Siglist(signal_list, list_sig)
      sub_typeF.append(np.array([[1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 1]]))
      cat_F.append([ph_1, ph_1, ph_1, noF])

    else:
      fill_Siglist(signal_list, list_sig)
      sub_typeF.append(np.array([[1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0]]))
      cat_F.append([ph_1, ph_1, ph_1, ph_1])

    Fault_type_list.append(sub_typeF)
    Fault_cat_list.append(cat_F)
  s1 = np.array(Fault_type_list).shape
  s2 = np.array(Fault_cat_list).shape
  Fault_type_list = np.array(Fault_type_list).reshape((s1[0]*s1[2], s1[3]))
  Fault_cat_list = np.array(Fault_cat_list).reshape((s2[0]*s2[2], s2[1]))
  return signal_list, Fault_type_list, Fault_cat_list

def Location_groups(path, tupfiles, recorders):
  L1_list = list() # Eventos Linea 692-675 Bus 692
  L2_list = list() # Eventos Linea 632-633 Bus 632
  L3_list = list() # Eventos Linea 684-652 Bus 684
  L4_list = list() # Eventos Linea 645-646 Bus 645
  cat_fault = list()
  cat_fault3 = list()
  cat_fault4 = list()
  loc_orden = list() # orden de loc
  loc_orden2 = list() # orden de loc
  loc_orden3 = list() # orden de loc
  loc_orden4 = list() # orden de loc
  for entry in range(len(tupfiles)):
    sub_typeF = list()
    list_sig = get_XY(path,tupfiles[entry], recorders[entry])
    id_f = tupfiles[entry][0]
    for loc in ['05', 10, 15, 20, 30, 35, 40, 45, 50, 60, 65, 70, 75, 80, 90, 95]:
      if id_f.find("Falla_A_") != -1:
        if id_f.find("_"+str(loc)+"%_")!=-1:
          L1_list.append(list_sig[1])
          L2_list.append(list_sig[2])
          L3_list.append(list_sig[0])
          loc_orden.append(int(loc))
          cat_fault.append(0)
          cat_fault3.append(0)
      elif id_f.find("Falla_C_") != -1:
        if id_f.find("_"+str(loc)+"%_")!=-1:
          L4_list.append(list_sig[-1])
          cat_fault4.append(0)

      elif id_f.find("Falla_2F_") != -1:
        if id_f.find(str(loc)+"%_")!=-1:
          L1_list.append(list_sig[1])
          L2_list.append(list_sig[2])
          loc_orden2.append(int(loc))
          cat_fault.append(1)

      elif id_f.find("Falla_2GF_") != -1:
        if id_f.find(str(loc)+"%_")!=-1:
          L1_list.append(list_sig[1])
          L2_list.append(list_sig[2])
          loc_orden3.append(int(loc))
          cat_fault.append(2)

      elif id_f.find("Falla_3F_") != -1:
        if id_f.find(str(loc)+"%_")!=-1:
          L1_list.append(list_sig[1])
          L2_list.append(list_sig[2])
          L4_list.append(list_sig[-1])
          loc_orden4.append(int(loc))
          cat_fault.append(3)
          cat_fault4.append(2)


  return L1_list, L2_list, L3_list, L4_list, loc_orden, loc_orden2, loc_orden3, loc_orden4, cat_fault, cat_fault3, cat_fault4

def Sag_curve(line, type_fault):
  ph_3_curve = []
  ph_2_curve = []
  ph_2g_curve = []
  ph_1_curve = []

  for ind in range(len(line)):
    phase_a = line[ind].get("A")
    phase_b = line[ind].get("B")
    phase_c = line[ind].get("C")
    timeset = line[ind].get("time")
    coeffs_a = pywt.wavedec(phase_a, 'bior4.4', level=5)
    coeffs_b = pywt.wavedec(phase_b, 'bior4.4', level=5)
    coeffs_c = pywt.wavedec(phase_c, 'bior4.4', level=5)
    dur_A, mag_A, type_event_A = event_result(coeffs_a[0], timeset)
    dur_B, mag_B, type_event_B = event_result(coeffs_b[0], timeset)
    dur_C, mag_C, type_event_C = event_result(coeffs_c[0], timeset)
    mag_pro = 0

    if type_fault[ind] == 0:

      if mag_A < 0.9 and dur_A != 0 and type_event_A == True and mag_A != 0:
        ph_1_curve.append(mag_A)
      elif mag_B < 0.9 and dur_B != 0 and type_event_B == True and mag_B != 0:
        ph_1_curve.append(mag_B)
      elif mag_C < 0.9 and dur_C != 0 and type_event_C == True and mag_C != 0:

        ph_1_curve.append(mag_C)

    elif type_fault[ind] == 1:
      if mag_A < 0.9 and dur_A != 0 and type_event_A == True and mag_A != 0:
        mag_pro= mag_A
      if mag_B < 0.9 and dur_B != 0 and type_event_B == True and mag_B != 0:
        mag_pro= (mag_pro + mag_B)
      if mag_C < 0.9 and dur_C != 0 and type_event_C == True and mag_C != 0:
        mag_pro= (mag_pro + mag_C)

      ph_2_curve.append(mag_pro/2)


    elif type_fault[ind] == 2:
      if mag_A < 0.9 and dur_A != 0 and type_event_A == True and mag_A != 0:
        mag_pro= mag_A
      if mag_B < 0.9 and dur_B != 0 and type_event_B == True and mag_B != 0:
        mag_pro= (mag_pro + mag_B)
      if mag_C < 0.9 and dur_C != 0 and type_event_C == True and mag_C != 0:
        mag_pro= (mag_pro + mag_C)

      ph_2g_curve.append(mag_pro/2)

    elif type_fault[ind] == 3:
      mag_pro = (mag_A+mag_B+mag_C)/3
      ph_3_curve.append(mag_pro)
  return [np.array(ph_3_curve), np.array(ph_2_curve), np.array(ph_2g_curve), np.array(ph_1_curve)]

def lin_Regression(location_vec, mag_vec):
  x = np.sort(np.array(location_vec)).reshape((len(location_vec),1))
  y = np.sort(mag_vec).reshape((len(mag_vec),1))

  # sckit-learn implementation

  # Model initialization
  regression_model = LinearRegression()
  # Fit the data(train the model)
  regression_model.fit(x, y)
  # Predict
  y_predicted = regression_model.predict(x)

  # model evaluation
  rmse = mean_squared_error(y, y_predicted)
  r2 = r2_score(y, y_predicted)

  ## printing values
  #print('Slope:' ,regression_model.coef_)
  #print('Intercept:', regression_model.intercept_)
  #print('Root mean squared error: ', rmse)
  #print('R2 score: ', r2)

  # plotting values

  # data points
  plt.scatter(x, y, s=10)
  plt.xlabel('% de la línea')
  plt.ylabel('magnitud del sag p.u')
  plt.grid()

  # predicted values
  plt.plot(x, y_predicted, color='r')
  plt.grid()
  plt.xlabel("% de la línea")
  plt.ylabel("magnitud del sag p.u")
  plt.show()
  return x,y_predicted


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

"""##Characteristic curve: Sag magnitude vs Distance (%) """

def get_train_test(y_col, x_col, ratio):
    """
    This method transforms a dataframe into a train and test set, for this you need to specify:
    1. the ratio train : test (usually 0.7)
    2. the column with the Y_values
    """
    mask = np.random.rand(len(y_col)) < ratio
    Y_train = y_col[mask]
    Y_test = y_col[~mask]
    X_train = x_col[mask]
    X_test = x_col[~mask]
    return X_train, Y_train, X_test, Y_test

def Table_Set(X_train, Y_train, X_test, Y_test):
    id_f = ['Fault Type', 'Train Set', 'Test Set', 'Total']
    faults = ['1Ph', '2Ph', '2Ph-to-G', '3Ph', 'None','Total']
    Num_train = [np.count_nonzero(Y_train == 0), np.count_nonzero(Y_train == 1), np.count_nonzero(Y_train == 2), np.count_nonzero(Y_train == 3), np.count_nonzero(Y_train == 4), len(Y_train)]
    Num_test = [np.count_nonzero(Y_test == 0), np.count_nonzero(Y_test == 1), np.count_nonzero(Y_test == 2), np.count_nonzero(Y_test == 3), np.count_nonzero(Y_test == 4), len(Y_test)]
    Total = [Num_train[0]+Num_test[0], Num_train[1]+Num_test[1], Num_train[2]+Num_test[2], Num_train[3]+Num_test[3], Num_train[4]+Num_test[4], Num_train[5]+Num_test[5]]
    data = [id_f] + list(zip(faults, Num_train, Num_test, Total))
    for i, d in enumerate(data):
        line = '|'.join(str(x).ljust(Total[3]) for x in d)
        print(line)
        if i == 0:
            print('-' * len(line))

## Almacenamiento de eventos por tipo de falla para usuarios
def Get_UserTest_Folder(X_testset, Y_testset):
  List_3ph = []
  List_2ph = []
  List_2phG = []
  List_1ph = []
  List_none = []
  for j in range(len(Y_testset)):
    if Y_testset[j][0] == 1:
      List_1ph.append(X_testset[j])
    elif Y_testset[j][1] == 1:
      List_2ph.append(X_testset[j])
    elif Y_testset[j][2] == 1:
      List_2phG.append(X_testset[j])
    elif Y_testset[j][3] == 1:
      List_3ph.append(X_testset[j])
    elif Y_testset[j][4] == 1:
      List_none.append(X_testset[j])
  return List_3ph, List_2ph, List_2phG, List_1ph, List_none

# Conversión a nivel de energía 5 - CORRER SOLO UNA VEZ
def DWT_Level_N(Xset):
    X_lev5 = copy.deepcopy(Xset)
    X_mat = []
    for x in X_lev5:
        for k, v in x.items():
            if k is not "time":
                coeffs = pywt.wavedec(v, 'bior4.4', level=5)
                cA, cD5, cD4, cD3, cD2, cD1 = coeffs
                levels = np.concatenate((cD5, cD4, cD3, cD2, cD1))
                x.update({k:levels})
        x.pop("time")
        m = np.array([x[i] for i in x.keys()])
        X_mat.append(m.T)
    return X_lev5, cA, X_mat
