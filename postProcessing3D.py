# -*- coding: utf-8 -*-
"""
Created on Tue May 23 14:42:49 2017

@author: dugj2403
"""
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#from PyQt5.QtGui import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from glob import glob
import DLT

import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
        
class postProcessing3D:
    
    def __init__(self,MainWindow):
        
        self.MainWindow = MainWindow
        self.image_points_1 = self.MainWindow.reconstruct3D[0].df[['x_px','y_px']]
        self.three_dee_name=self.MainWindow.reconstruct3D[0].filename
        self.image_points_1 = self.image_points_1.as_matrix(columns=None)
        
        self.image_points_2 = self.MainWindow.reconstruct3D[1].df[['x_px','y_px']]
        self.image_points_2 = self.image_points_2.as_matrix(columns=None)
        
        self.cal_view_1 = self.MainWindow.reconstruct3D[0].calibration
        print(self.cal_view_1)
        self.cal_view_1 = np.asarray(self.cal_view_1)
        print(self.cal_view_1)
        self.cal_view_2 = self.MainWindow.reconstruct3D[1].calibration
        print(self.cal_view_2)
        self.cal_view_2=np.asarray(self.cal_view_2) 
        print(self.cal_view_2)

        self.calibrations=[self.cal_view_1,self.cal_view_2]
        self.image_points_together=[self.image_points_1,self.image_points_2]
        
        self.find_3D_coordinates()
        self.plot_3D_points()
        self.populate_table()
        
    def find_3D_coordinates(self):
        self.nd=3
        self.nc=2 
        self.xyz = np.zeros((len(self.image_points_1), 3))
        for i in range(len(self.image_points_1)):
            self.xyz[i,:] = DLT.DLTrecon(self.nd, self.nc, self.calibrations, [self.image_points_1[i],self.image_points_2[i]])      
        self.xyz = pd.DataFrame(self.xyz, columns=['x', 'y', 'z'])
        
        if self.MainWindow.save_3D_track_cb.isChecked()==True:
            try:
                os.mkdir(self.MainWindow.path+'\\'+'3DTracks')
            except WindowsError:
                pass
            self.xyz.to_csv("%s\\3DTracks\\3D_%s.csv" % (self.MainWindow.path,self.MainWindow.reconstruct3D[0].filename),sep =',', index=False)

    def plot_3D_points(self):

        ax = plt.figure().gca(projection='3d')
        ax.scatter(self.xyz.x, self.xyz.y, self.xyz.z)
        ax.set_xlabel('Distance from start of flume (mm)')
        ax.set_ylabel('Lateral position (mm)')
        ax.set_zlabel('Vertical position (mm)')
        ax.set_xlim(1500, 1000)
        ax.set_ylim(0, 150)
        ax.set_zlim(0, 100)
        plt.show()

    def populate_table(self):
        self.MainWindow.pp_TV.setModel(PandasModel(self.xyz))       


       
class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None