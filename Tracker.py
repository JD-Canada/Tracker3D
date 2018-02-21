
#imports
import sys
import os
import time
from glob import glob

#from PyQt5.QtGui import *
#from PyQt5.QtCore import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox


import cv2
import numpy as np
import pandas as pd
from distutils.dir_util import copy_tree
import csv
import DLT

from PyQt5 import QtCore
from PyQt5 import QtGui
import tracker_ui
import videoTracking
#import calibration
import postProcessing2D
import postProcessing3D

import matplotlib
matplotlib.style.use('seaborn-darkgrid')
import matplotlib.pyplot as plt
plt.rc('font', family='serif') 
plt.rc('font', serif='Times New Roman') 


from matplotlib.backends.backend_qt4agg \
import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QtWidgets.QMainWindow, tracker_ui.Ui_MainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('dice.png'))
        self.setWindowTitle("Tracker3D")
        self.setGeometry(300, 200, 700, 500)
        self.path=os.path.dirname(os.path.realpath(__file__))
        
        #intial values
        self.tracks=[]
        
        #global lists        
        self.cal2DFiles=[]
        self.cal3DFiles=[]
        self.reconstruct3D=[]
        self.tracks2DInsts=[]
        self.trackList=[]
        self.master_calList=[]
        self.three_dee=[]

        #project setup / calibration
        self.chooseProjectPath_b.clicked.connect(self.get_project_path)
        self.loadCal3D_b.clicked.connect(self.loadCal3D)
        self.removeCal3D_b.clicked.connect(self.removeCal3D)  
   
        #track
        self.trkTrack_B.clicked.connect(self.trackVideo)
        self.trkLoad_B.clicked.connect(self.videoOpen)
        self.trkPreview_B.clicked.connect(self.previewVideo)
        self.selectStartStop_b.clicked.connect(self.selectVideoBounds)

        self.gaussSlider.valueChanged.connect(self.gaussSliderChange)
        self.medianSlider.valueChanged.connect(self.medianSliderChange)
        self.kernelSlider.valueChanged.connect(self.kernelSliderChange)

        #post-process
        self.ppFileOpen_B.clicked.connect(self.open_CSV_tracks)
        self.ppClearList_B.clicked.connect(self.clean_CSV_tracks)
        self.ppBlank_B.clicked.connect(self.blankRows)
        self.ppUndo_B.clicked.connect(self.changesUndo)
        
        self.csvList_LW.doubleClicked.connect(self.selectTrack)
        self.tracks3D_LW.doubleClicked.connect(self.select_3D_track)
        self.calView1_3D_select_B.clicked.connect(self.calView1_3D_select)
        self.calView2_3D_select_B.clicked.connect(self.calView2_3D_select)        
        self.addView_3D_b.clicked.connect(self.addTrack3D)
        self.clear_reconst3D_LW_b.clicked.connect(self.clear_reconst3D_LW)
        self.reconstruct_3D_b.clicked.connect(self.reconstruct_3D)
        self.cleartracks3DLW_b.clicked.connect(self.clean_3D_tracks)

    #Video functionality
    def videoOpen(self): 
        try:
            fileobj=QFileDialog.getOpenFileName(self,"Video file", self.path,filter="Video Files( *.mp4 *.h264)")
            self.pathLabel.setText(str(fileobj[0]))
            self.video=fileobj[0]
            self.tracking=videoTracking.VideoTracking(self)
        except AttributeError:
            self.errMessage="Project path not specified."
            self.errorTitle="Please specify a project path ..."
            self.errorMsg()            

    def previewVideo(self):
        self.tracking.preview() 
        
    def selectVideoBounds(self):
        self.tracking.selectVideoBounds()

    def trackVideo(self):
        self.tracking.trackVideo()
    
    #calibration functionality
    def loadCal3D(self):
        
        try:
            self.cal3DFilesTemp = QFileDialog.getOpenFileNames(self,"CSV files", self.path, filter="Text Files (*.csv)")[0]
            self.cal3DFiles = self.cal3DFiles+self.cal3DFilesTemp
            self.cal3D_LW1.clear()
            self.cal3D_LW2.clear()
    
            for i in range(len(self.cal3DFiles)):
                print(i)
                self.cal3D_LW1.addItem(os.path.split(os.path.abspath(self.cal3DFiles[i]))[1])
                self.cal3D_LW2.addItem(os.path.split(os.path.abspath(self.cal3DFiles[i]))[1])
        except AttributeError:
            self.errMessage="Project path not specified."
            self.errorTitle="Please specify a project path ..."
            self.errorMsg()            
               
    def removeCal3D(self):
        self.cal3DFiles=[]
        self.cal3D_LW1.clear()
        self.cal3D_LW2.clear() 
        
    def calView1_3D_select(self):
        view = 1
        self.tracks2DInsts[self.csvList_LW.currentRow()].define_calibration(view)

    def calView2_3D_select(self):
        view = 2
        self.tracks2DInsts[self.csvList_LW.currentRow()].define_calibration(view)

    def selectTrack(self):
        try:
            self.tracks2DInsts[self.csvList_LW.currentRow()].plot_pixel_coordinates()
        except IndexError:
            pass

    def select_3D_track(self):
        try:
            print("sometime")
        except IndexError:
            pass

    def addTrack3D(self):
        
        self.reconstruct3D.append(self.tracks2DInsts[self.csvList_LW.currentRow()])
        
        print(len(self.reconstruct3D))

        if len(self.reconstruct3D) > 2:
            self.errMessage="Only two views allowed for 3D reconstruction."
            self.errorTitle="Trying to add too many views!"
            self.errorMsg()
            return 
            
        self.reconstruct3D_LW.addItem(self.tracks2DInsts[self.csvList_LW.currentRow()].filename)

    def clear_reconst3D_LW(self):
        self.reconstruct3D_LW.clear()
        self.reconstruct3D=[]

    def reconstruct_3D(self):
        try:
            self.threeDee_temp=postProcessing3D.postProcessing3D(self)
            self.three_dee.append(self.threeDee_temp)
            self.tracks3D_LW.clear()
            
            for i in range(len(self.three_dee)): 
                self.useless_path, self.basename=os.path.split(os.path.abspath(self.three_dee[i].three_dee_name))
                self.filename=os.path.splitext(self.basename)[0]
                self.tracks3D_LW.addItem(self.filename)        
        except AttributeError:
            self.errMessage="One or both files has not been attributed a calibration"
            self.errorTitle="Please specify calibrations ..."
            self.errorMsg()    
            
    def open_CSV_tracks(self):

        self.tempTracks = QFileDialog.getOpenFileNames(self,"CSV files", self.path, filter="Text Files (*.csv)")[0]
        self.tracks=self.tracks+self.tempTracks
        
        if self.tracks2DInsts:
            print("True")
            self.nmb_tracks=len(self.tracks2DInsts)
            self.newTracks2DInsts=[postProcessing2D.postProcessing2D(self.tempTracks[i],self) for i in range(len(self.tempTracks))]
            self.tracks2DInsts=self.tracks2DInsts+self.newTracks2DInsts

            for i in range(len(self.tracks2DInsts)): 

                if i+1 <= self.nmb_tracks:
                    continue
                else:
                    print("In")
                    self.useless_path, self.basename=os.path.split(os.path.abspath(self.tracks2DInsts[i].fileobj))
                    self.filename=os.path.splitext(self.basename)[0]
                    self.csvList_LW.addItem(self.filename)
        else:
            self.tracks2DInsts=[postProcessing2D.postProcessing2D(self.tempTracks[i],self) for i in range(len(self.tempTracks))]
            self.nmb_tracks=len(self.tracks2DInsts)
            print("False")
            for i in range(len(self.tracks2DInsts)): 

                    self.useless_path, self.basename=os.path.split(os.path.abspath(self.tracks2DInsts[i].fileobj))
                    self.filename=os.path.splitext(self.basename)[0]
                    self.csvList_LW.addItem(self.filename)
            
    def clean_CSV_tracks(self):
        self.tracks=[]
        self.tracks2DInsts=[]
        self.pp_TV.clearSpans()
        self.csvList_LW.clear()
        self.reconstruct3D_LW.clear() 
        self.reconstruct3D=[]         

    def clean_3D_tracks(self):
        self.tracks3D=[]
        self.tracks3D_LW.clear()

       
    def blankRows(self):
        self.tracks2DInsts[self.csvList_LW.currentRow()].blankRows()
#        self.trackList[listindex].blankRows(self.pp_TV.selectionModel().selectedRows())
        
    def changesUndo(self):
        self.tracks2DInsts[self.csvList_LW.currentRow()]=postProcessing2D.postProcessing2D(self.tracks[self.csvList_LW.currentRow()],self)
        self.tracks2DInsts[self.csvList_LW.currentRow()].plot_pixel_coordinates()
       
    def get_project_path(self):
        self.path=QFileDialog.getExistingDirectory(self,"Choose project folder", "C:\\Users\\tempo\\Desktop\\Trial_1")
        self.active_path_label.setText(self.path)

                        


    def gaussSliderChange(self):
        self.gaussValueLabel.setText(str(self.gaussSlider.value()))

    def medianSliderChange(self):
        self.medianValueLabel.setText(str(self.medianSlider.value()))

    def kernelSliderChange(self):
        self.kernelValueLabel.setText(str(self.kernelSlider.value()))

    def cleanup(self):
        
       msg = QMessageBox()
       msg.setIcon(QMessageBox.Information)
    
       msg.setText("Are you sure? This will erase all the tracks with the *_treated.csv, *.png, *_Stitch.csv extensions from the active folder!")
       #msg.setInformativeText("This is additional information")
       msg.setWindowTitle("WARNING!")
       #msg.setDetailedText("The details are as follows:")
       msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
       retval = msg.exec_()
       
#       print "value of pressed message box button:", retval

       if retval==1024:
#            for fl in glob("%s\\*_orig.csv" %self.path):
#                os.remove(fl)
            for fl in glob("%s\\*_treated.csv" %self.path):
                os.remove(fl)
            for fl in glob("%s\\Stitch.csv" %self.path):
                os.remove(fl)
            for fl in glob("%s\\*.png" %self.path):
                os.remove(fl)
            
            self.pp_TV.clearSpans()
            del self.trackList[:]
            self.csvList_LW.clear()
            self.ppFileLoaded_L.clear()
            self.trackPlot_L.setText("Trace will appear when a trajectory file is selected ...")

    def errorMsg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(self.errMessage)
        msg.setWindowTitle(self.errorTitle)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()        


class calibration:
    
    def __init__(self,filename):
        
        self.filename=filename
        self.path, self.basename=os.path.split(os.path.abspath(self.filename))
        self.calfilename=os.path.splitext(self.basename)[0]
               
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
    

#if __name__ == "__main__":
#    def run_app():
#        app = QtWidgets.QApplication(sys.argv)
#        mainWin = MainWindow()
#        mainWin.show()
#        app.exec_()
#    run_app()

        
app = QtWidgets.QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
form = MainWindow()
form.show()
app.exec_()
