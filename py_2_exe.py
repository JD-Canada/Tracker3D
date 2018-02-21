# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 08:54:47 2016

@author: Jason
"""

import os
import sys
from PyQt4.QtGui import QFileDialog

ui_filename= sys.argv[1]

os.system('pyinstaller --onedir --onefile --name %s --windowed ".\%s.py"' %(ui_filename, ui_filename))
