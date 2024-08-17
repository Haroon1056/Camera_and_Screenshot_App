import sys
import os
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PIL import ImageGrab
import mysql.connector
from datetime import datetime

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        
        # Initialize MySQL connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1056",
            database="ImageDatabase"
        )
        self.cursor = self.db.cursor()

    def initUI(self):
        self.setWindowTitle("Camera and Screenshot App")
        self.setGeometry(100, 100, 800, 600)

        # Create buttons
        self.openCameraButton = QPushButton("Open Camera", self)
        self.openCameraButton.setGeometry(50, 50, 200, 50)
        self.openCameraButton.clicked.connect(self.openCamera)
        
        self.takePictureButton = QPushButton("Take Picture", self)
        self.takePictureButton.setGeometry(50, 120, 200, 50)
        self.takePictureButton.clicked.connect(self.takePicture)
        
        self.savePictureButton = QPushButton("Save Picture", self)
        self.savePictureButton.setGeometry(50, 190, 200, 50)
        self.savePictureButton.clicked.connect(self.savePicture)
        
        self.screenshotButton = QPushButton("Take Screenshot", self)
        self.screenshotButton.setGeometry(50, 260, 200, 50)
        self.screenshotButton.clicked.connect(self.takeScreenshot)
        
        # Create label to display camera feed
        self.cameraLabel = QLabel(self)
        self.cameraLabel.setGeometry(300, 50, 640, 480)
        
        # Timer for camera feed
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        
        # Key press detection
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def openCamera(self):
        self.timer.start(20)
    
    def updateFrame(self):
        ret, frame = self.cap.read()
        if ret:
            self.currentFrame = frame
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
            self.cameraLabel.setPixmap(QtGui.QPixmap.fromImage(convertToQtFormat))
    
    def takePicture(self):
        self.capturedFrame = self.currentFrame
    
    def savePicture(self):
        if hasattr(self, 'capturedFrame'):
            filename = f'captured_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
            filepath = os.path.join(os.getcwd(), filename)
            cv2.imwrite(filepath, self.capturedFrame)
            self.saveToDatabase(filepath)
    
    def takeScreenshot(self):
        screenshot = ImageGrab.grab()
        filename = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        filepath = os.path.join(os.getcwd(), filename)
        screenshot.save(filepath)
        self.saveToDatabase(filepath)
    
    def saveToDatabase(self, filepath):
        query = "INSERT INTO Images (file_path) VALUES (%s)"
        self.cursor.execute(query, (filepath,))
        self.db.commit()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            self.close()
            self.cap.release()
            cv2.destroyAllWindows()

    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = Ui_MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
