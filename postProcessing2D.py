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
import csv

        
class postProcessing2D:
    
    def __init__(self,fileobj,MainWindow):
        
        self.MainWindow=MainWindow
        self.fileobj=fileobj
        self.framerate=int(self.MainWindow.trkFramerate_LE.text())
        self.df=pd.read_csv(self.fileobj)
        
        self.path, self.basename=os.path.split(os.path.abspath(self.fileobj))
        self.filename=os.path.splitext(self.basename)[0]

        self.df.columns= ['Index','Image frame', 'x_px','y_px']
        self.df.drop('Index', axis=1, inplace=True)
        self.df=self.df.replace(0.0, np.nan)
        self.df=self.df.round(0)
           
    def define_calibration(self,view):
        self.view=view
        with open(self.MainWindow.cal3DFiles[self.MainWindow.cal3D_LW2.currentRow()], 'rt') as f:
            reader = csv.reader(f,quoting=csv.QUOTE_NONNUMERIC)
            self.calibration = list(reader)
        self.calibration=self.calibration[0]
        print(self.calibration)
        
#        self.cal_path, self.cal_filename = os.path.split(self.MainWindow.cal3DFiles[self.MainWindow.cal3D_LW2.currentRow()])
#        self.errMessage = "Track %s has been associated with %s calibration file." %(self.filename,self.cal_filename)
#        self.errorTitle= "Calibration succesfully associated!"
#        self.errorMsg()
        self.MainWindow.csvList_LW.item(self.MainWindow.csvList_LW.currentRow()).setBackground(QtCore.Qt.green)

        
    def plot_pixel_coordinates(self):
        
        if self.MainWindow.show2Dplot_B.isChecked()==True:
            self.x='x_px'
            self.y='y_px'
            self.color='Red'
            self.label="pixel coordinates"
            self.MainWindow.pp_TV.setModel(PandasModel(self.df))
            ax=self.df.plot(x=self.x,y=self.y,kind='scatter',color=self.color, figsize=[7,2], label=self.label)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            plt.legend(loc='best',prop={'size':10}, frameon=True, shadow=True, bbox_to_anchor=(1.1, 1.1))
            plt.title('Fish Track', style='italic')
            fig = ax.get_figure()
            plt.show()

    def errorMsg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(self.errMessage)
        msg.setWindowTitle(self.errorTitle)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()        

        
    def blankRows(self):
        self.rowIndices=self.MainWindow.pp_TV.selectionModel().selectedRows()
        for i in range(len(self.rowIndices)):
            self.df.iloc[self.rowIndices[i].row(),1:10]=None 
        self.plot_pixel_coordinates()        
        
    def interpolate(self):
        
        self.df=self.df.drop(['u','v','up','down'],axis=1)
        self.df["Interpolated"]=0
        self.df.ix[self.df['x'].isnull(),'Interpolated']=1
        self.df=self.df.interpolate() 
        self.df['Interpolated_x'] = np.where(self.df['Interpolated'] == 1, self.df['x'],None)
        self.kinematics()
        

            


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