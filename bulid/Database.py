# import tracemalloc
# tracemalloc.start()

import sys
import os
import pymysql
import cv2
from math import ceil
from numpy import rot90
from threading import Thread
from time import sleep
from webbrowser import open_new_tab
from configparser import ConfigParser
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QTransform
from PyQt5.uic import loadUi

toNone = lambda x : None if x == 'None' else x
toBool = lambda x : True if x == 'True' else False
product_key = 'XBQ9-W836-5QWRT-S9YQP'

def threaded_video_capture(obj):
	try:
		video_capture = cv2.VideoCapture(0)
		click_count = 1
		while True:
			try:
				ret, real_image = video_capture.read()
				if obj.capture_on_video:
					obj.capture_on_video = False
					folder = obj.data_directory + os.sep + obj.image_label + os.sep
					while True:
						file = 'image-%04d.jpg' % click_count
						if not os.path.exists(folder + file):
							cv2.imwrite( folder + file, real_image )
							obj.click_count_video.setText(str(click_count) + ' Clicks')
							obj.file_name.setText(obj.image_label + os.sep + file)
							break
						click_count = click_count + 1

				if (not obj.video) or (obj.video == 0):
					break

				image = MainApp.get_cv_to_pixmap(obj, real_image)
				MainApp.display_cv_image(obj, image)
			except:
				video_capture.release()
				print("Error on Video Capture -_- -_- -_-")
		video_capture.release()
		obj.display.setPixmap(obj.sponsor)
		print("Camera Closed ~^_^~")
	except:
		pass

class About(QDialog):
	def __init__(self):
		super(About, self).__init__()
		loadUi('ui/about.ui', self)
		self.move(150, 100)
		self.show()

class Copyright(QDialog):
	"""docstring for Copyright"""
	def __init__(self):
		super(Copyright, self).__init__()
		loadUi('ui/copyrigth_notice.ui', self)
		self.move(150, 100)
		self.show()

class Documentatin(QDialog):
	"""docstring for Documentatin"""
	def __init__(self):
		super(Documentatin, self).__init__()
		loadUi('ui/documentatin.ui', self)
		self.move(150, 100)
		self.show()
		self.link_btn.clicked.connect(self.open_url)

	def open_url(self):
		open_new_tab("https://www.bit.ly/2jkaf4qt")


class MainApp(QMainWindow):
	def __init__(self):

		config = ConfigParser()
		config.read('config.ini')

		self.input_key = config['SECURITY']['hashkey']
		self.video = False
		self.server_ip = config['DATABASE']['server_ip']
		self.server_user = config['DATABASE']['server_user']
		self.server_password = config['DATABASE']['server_password']
		self.database_name = config['DATABASE']['database_name']

		self.data_directory = config['DATA']['data_directory']
		self.output_directory = config['DATA']['output_directory']
		self.click_size = toNone(config['IMAGE']['click_size'])
		self.image_label = config['DATA']['image_label']

		self.capture_on_video = False
		self.face_on_video = toBool(config['IMAGE']['face_on_video'])
		self.eye_on_video = toBool(config['IMAGE']['eye_on_video'])
		self.zoom_leval = float(config['IMAGE']['zoom_leval'])

		self.sponsor_poster = config['DATA']['sponsor_poster']
		self.cv_facecascade_file = config['DATA']['cv_facecascade_file']
		self.cv_eyecascade_file = config['DATA']['cv_eyecascade_file']

		self.sponsor = QPixmap(self.sponsor_poster)
		self.sponsor = self.sponsor.scaled(870, 640, QtCore.Qt.KeepAspectRatio)

		self.faceCascade = cv2.CascadeClassifier(self.cv_facecascade_file)
		self.eyeCascade = cv2.CascadeClassifier(self.cv_eyecascade_file)

		self.connection = None

		super(MainApp, self).__init__()
		loadUi('ui/capture_tool.ui', self)
		self.move(50, 0)
		self.show()

		self.display.setPixmap(self.sponsor)
		self.display.setAlignment (QtCore.Qt.AlignCenter)

		if self.input_key != product_key:
			key, okPressed = QInputDialog.getText(self, "Security Checkup", "Wrong access key please enter a valid access key:", QLineEdit.Normal, "XBQ9-W836-5QWRT-S9YQP")
			if okPressed:
				if key != product_key:
					self.event_exit()
					exit()
			else:
				self.event_exit()
				exit()

		self.capture.clicked.connect(self.setVideoCapture)
		self.crop_image_btn.clicked.connect(self.cropImage)
		self.cropall_image_btn.clicked.connect(self.cropAll)
		self.next_img.clicked.connect(self.nextImage)
		self.back_img.clicked.connect(self.prevImage)
		self.output_dir.clicked.connect(self.setOutputDir)
		self.data_dir.clicked.connect(self.setDataDir)
		self.load_dir.clicked.connect(self.loadImageData)
		self.loaded_label.clicked.connect(self.unloadImageData)

		self.checkBoxFace.clicked.connect(self.faceDetectSwitech)
		self.checkBoxEye.clicked.connect(self.eyeDetectSwitech)

		self.actionExit.triggered.connect(self.event_exit)
		self.actionOpen.triggered.connect(self.camera_on)
		self.actionClose.triggered.connect(self.camera_off)
		self.actionNext_Image.triggered.connect(self.nextImage)
		self.actionBack_Image.triggered.connect(self.prevImage)

		self.actionIP_Address.triggered.connect(self.setIP)
		self.actionUser.triggered.connect(self.setUser)
		self.actionPassword.triggered.connect(self.setPassword)
		self.actionDatabase_Name.triggered.connect(self.setDatabase)
		self.actionConnect.triggered.connect(self.db_connect)
		self.actionDisconnect.triggered.connect(self.db_disconnect)
		self.actionUpload_To_Database.triggered.connect(self.upload_to_db)

		self.actionSet_Lable.triggered.connect(self.setImageLabel)
		self.actionOrignal_Size.triggered.connect(self.setImageSize)
		self.actionData_Directory.triggered.connect(self.setDataDir)
		self.actionOutput_Directory.triggered.connect(self.setOutputDir)

		self.actionCapture.triggered.connect(self.setVideoCapture)
		self.actionCrop_2.triggered.connect(self.cropImage)
		self.actionCrop_All_2.triggered.connect(self.cropAll)
		self.actionLoad_Data.triggered.connect(self.loadImageData)
		self.actionUnload_Data.triggered.connect(self.unloadImageData)

		self.actionAbout.triggered.connect(self.about_us)
		# self.actionCopyright_Notice.triggered.connect(self.copyrigth_notice)
		self.actionCite.triggered.connect(self.download_cite)
		self.actionDocumentatin.triggered.connect(self.documentatin_menu)

		self.horizontalScroll.valueChanged.connect(self.todo)
		self.verticalScroll.valueChanged.connect(self.todo)
		self.zoom.valueChanged.connect(self.setZoomLeval)

		self.click_count_video.setText("0 Clicks")
		self.image_counting.setText("0/0")
		self.file_name.setText(" ")

		self.load_query = []
		self.load_query_count = None

	def todo(self):
		print("TODO: Task is not assigned.")

	def about_us(self):
		dialog = About()
		dialog.exec_()

	def copyrigth_notice(self):
		dialog = Copyright()
		dialog.exec_()

	def download_cite(self):
		open_new_tab("http://bit.ly/2jkaf4qt")
	def documentatin_menu(self):
		dialog = Documentatin()
		dialog.exec_()

	def cropAll(self):
		if self.load_query_count != None:
			for i in range(len(self.load_query)):
				self.load_query_count = i
				self.cropImage()
			QMessageBox.information(self, "Information", "All croping done.", QMessageBox.Yes)
		else:
			QMessageBox.information(self, "Information", "Please open a folder.", QMessageBox.Yes)

	def cropImage(self,):
		if self.load_query_count != None:
			image_file_path = self.load_query[self.load_query_count]
			image_file_name = os.path.basename(self.load_query[self.load_query_count]).split('.')[0]
			real_image = cv2.imread(image_file_path)
			gray = cv2.cvtColor(real_image, cv2.COLOR_BGR2GRAY)
			faces = self.faceCascade.detectMultiScale(
				gray,
				scaleFactor=1.1,
				minNeighbors=5,
				minSize=(30, 30),
				flags=cv2.CASCADE_SCALE_IMAGE
			)
			i = 0
			output_path = os.path.join(self.output_directory, self.image_label)
			if not os.path.exists(output_path):
				os.makedirs(output_path)
			for (x, y, w, h) in faces:
				face = real_image[y:y+h, x:x+w]
				save_file = os.path.join(output_path, (image_file_name+"-face-%02d" % i) + ".jpg")
				face = cv2.resize(face, (64, 64))
				cv2.imwrite(save_file, face)
		else:
			QMessageBox.information(self, "Information", "Please open a folder.", QMessageBox.Yes)

	def nextImage(self):
		if self.load_query_count != None:
			if self.load_query_count != len(self.load_query)-1:
				self.load_query_count = self.load_query_count + 1
			self.__image_load(self.load_query_count)
		else:
			QMessageBox.information(self, "Information", "Please open a folder.", QMessageBox.Yes)

	def prevImage(self):
		if self.load_query_count != None:
			if self.load_query_count != 0:
				self.load_query_count = self.load_query_count - 1
			self.__image_load(self.load_query_count)
		else:
			QMessageBox.information(self, "Information", "Please open a folder.", QMessageBox.Yes)

	def __image_load(self, index):
		real_image = cv2.imread(self.load_query[index])
		image = MainApp.get_cv_to_pixmap(self, real_image)
		MainApp.display_cv_image(self, image)
		self.click_count_video.setText("%d Image Found" % len(self.load_query))
		self.image_counting.setText("%d / %d" % (index+1, len(self.load_query)))
		self.file_name.setText(self.load_query[0][-25:])

	def unloadImageData(self):
		self.loaded_label.setStyleSheet('background:rgb(227, 227, 227);color:rgb(255, 255, 255);padding:2px;border-radius:5px;')
		self.load_query_count = None
		self.display.setPixmap(self.sponsor)

	def loadImageData(self):
		if not self.video:
			self.loaded_label.setStyleSheet('background:rgb(255, 48, 12);color:rgb(255, 255, 255);padding:2px;border-radius:5px;')
			self.load_query = []
			for r, d, f in os.walk(self.data_directory + os.sep + self.image_label):
				for file in f:
					if '.jpg' or '.png' in file:
						self.load_query.append(os.path.join(r, file))
			self.load_query_count = None if len(self.load_query) == 0 else 0
			if self.load_query_count != None:
				self.__image_load(0)

	def setZoomLeval(self):
		try:
			val = self.zoom.value()
			self.zoom_leval = 0.5 + (val/100)
			if val > 45 and val < 55:
				self.zoom_leval = 1.0
		except:
			self.zoom_leval = 1.0
		self.zoom_leval_display.setText("%.2f X" % self.zoom_leval)
		if self.load_query_count != None:
			self.__image_load(self.load_query_count)

	def faceDetectSwitech(self):
		if self.checkBoxFace.isChecked():
			self.face_on_video = True
		else:
			self.face_on_video = False
		if self.load_query_count != None:
			self.__image_load(self.load_query_count)


	def eyeDetectSwitech(self):
		if self.checkBoxEye.isChecked():
			self.eye_on_video = True
		else:
			self.eye_on_video = False
		if self.load_query_count != None:
			self.__image_load(self.load_query_count)

	def setDataDir(self):
		self.data_directory = QFileDialog.getExistingDirectory(self, "Data Directory", "")
		if not os.path.exists(self.data_directory):
			os.makedirs(self.data_directory)
		print(self.data_directory)

	def setOutputDir(self):
		self.output_directory = QFileDialog.getExistingDirectory(self, "Output Directory", "")
		if not os.path.exists(self.output_directory):
			os.makedirs(self.output_directory)
		print(self.output_directory)

	def camera_on(self):
		if self.load_query_count == None:
			self.load_query_count = None
			self.click_count_video.setText(" ")
			self.image_counting.setText(" ")
			self.file_name.setText(" ")

			if not self.video:
				msg = QMessageBox.information(self, "Information", "Opening Camera\nMake sure to close the camera !!!\nPress CTRL+X or 'C' to close the camera.", QMessageBox.Yes | QMessageBox.No)
				if msg == QMessageBox.Yes:
					self.video = True
					thread = Thread(target = threaded_video_capture, args = (self,))
					thread.start()
			else:
				print("Already Open")
		else:
			QMessageBox.information(self, "Information", "Please close data folder.", QMessageBox.Yes)

	def setVideoCapture(self):
		if self.video:
			self.capture_on_video = True
		else:
			QMessageBox.information(self, "Information", "Please open an active webcam.", QMessageBox.Yes)

	def setImageSize(self, ratio=None):
		self.click_size = ratio

	def camera_off(self):
		self.video = False
		
		# cu_mem, peak_mem = tracemalloc.get_traced_memory()
		# print("Current: %f MB, Peak %f MB" % (cu_mem/(1024*1024), peak_mem/(1024*1024)))

	def setImageLabel(self):
		i, okPressed = QInputDialog.getText(self, "Image Label", "Label for clicked images:", QLineEdit.Normal, self.image_label)
		if okPressed:
			self.image_label = i.lower()
		if not os.path.exists(self.data_directory + os.sep + self.image_label):
			os.makedirs(self.data_directory + os.sep + self.image_label)
		if not os.path.exists(self.output_directory + os.sep + self.image_label):
			os.makedirs(self.output_directory + os.sep + self.image_label)

	def setUser(self):
		i, okPressed = QInputDialog.getText(self, "Database Configration", "Remote Server user-name:", QLineEdit.Normal, self.server_user)
		if okPressed:
			self.server_user = i

	def setPassword(self):
		i, okPressed = QInputDialog.getText(self, "Database Configration","Remote Server Password:", QLineEdit.Normal, self.server_password)
		if okPressed:
			self.server_password = i

	def setDatabase(self):
		i, okPressed = QInputDialog.getText(self, "Database Configration","Database name in Remote Server:", QLineEdit.Normal, self.database_name)
		if okPressed:
			self.database_name = i

	def setIP(self):
		i, okPressed = QInputDialog.getText(self, "Database Configration","Remote Server IP Address:", QLineEdit.Normal, self.server_ip)
		if okPressed:
			self.server_ip = i

	def event_exit(self,):
		self.camera_off()
		self.db_disconnect()
		self.close()

	def db_connect(self):
		try:
			self.connection = pymysql.connect(host=self.server_ip,
							user=self.server_user,
							password=self.server_password,
							db='humoface',
							charset='utf8mb4',
							cursorclass=pymysql.cursors.DictCursor)
		except Exception as e:
			QMessageBox.information(self, "Critical Error", "Unable to stablish connection.", QMessageBox.Yes)

	def db_disconnect(self):
		if self.connection:
			self.connection.close()
			self.connection = None

	def upload_to_db(self):
		if self.connection:
			try:
				with self.connection.cursor() as cursor:

					sql = "INSERT INTO face (`label`, `image`) VALUES (%s, %s)"
					cursor.execute(sql, (self.image_label, 'binary-image-data'))
				self.connection.commit()
				# with connection.cursor() as cursor:
				# 	sql = "SELECT * FROM `face` WHERE `label`=%s"
				# 	cursor.execute(sql, ('webmaster@python.org',))
				# 	results = cursor.fetchall()
				# 	for result in results:
				# 		print(result)
			except Exception as e:
				QMessageBox.information(self, "Critical Error", "One Image not Uploaded.", QMessageBox.Yes)
		else:
			QMessageBox.information(self, "Critical Error", "Database not connected.", QMessageBox.Yes)

	@staticmethod
	def get_cv_to_pixmap(obj, real_image):
		if (not obj.face_on_video) and (not obj.eye_on_video):
			height, width, _ = real_image.shape
			if height > width:
				real_image = rot90(real_image)
				height, width, _ = real_image.shape
				resized_image = cv2.resize(real_image, (ceil(870*obj.zoom_leval),
					ceil(640*obj.zoom_leval*(height/width)))) 
			else:
				resized_image = cv2.resize(real_image, (ceil(870*obj.zoom_leval), ceil(640*obj.zoom_leval)))

		else:
			resized_image = cv2.resize(real_image, (ceil(870*obj.zoom_leval), ceil(640*obj.zoom_leval))) 
		
		image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
		gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
		if obj.face_on_video:
			faces = obj.faceCascade.detectMultiScale(
				gray,
				scaleFactor=1.1,
				minNeighbors=5,
				minSize=(30, 30),
				flags=cv2.CASCADE_SCALE_IMAGE
			)
			for (x, y, w, h) in faces:
				cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
		if obj.eye_on_video:
			eyes = obj.eyeCascade.detectMultiScale(
				gray,
				scaleFactor=1.1,
				minNeighbors=5,
				minSize=(30, 30),
				flags=cv2.CASCADE_SCALE_IMAGE
			)
			for (x, y, w, h) in eyes:
				cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
		return image

	@staticmethod
	def display_cv_image(obj, image):
		height, width, channel = image.shape
		bytesPerLine = 3 * width
		qImg = QImage(image.copy(), width, height, bytesPerLine, QImage.Format_RGB888)
		pixmap = QPixmap(qImg)
		obj.display.setPixmap(pixmap)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainApp()

	# cu_mem, peak_mem = tracemalloc.get_traced_memory()
	# print("Current: %f MB, Peak %f MB" % (cu_mem/(1024*1024), peak_mem/(1024*1024)))

	sys.exit(app.exec_())
