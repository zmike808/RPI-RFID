import sys, serial, threading, random, Queue, time
from PyQt4 import QtGui, QtCore
serialPort = "/dev/ttyACM0"
serialBaud = 9600

## this is the main window class, it handles setting up the widnow and menu bars and maintining a connection with the worker thread. It also has the main widget loded in it
class mainWindow(QtGui.QMainWindow):
	def __init__(self, queue, endcommand):
		super(mainWindow, self).__init__()

		self.queue = queue
		self.endcommand = endcommand

		self.initUI()

	## a function that sets up all of the uo elements needed for the GUI
	def initUI(self):
		self.initMenu()
		self.splitterWidget = mainWidget()
		self.setCentralWidget(self.splitterWidget)
		self.setGeometry(100,100,800,700)
		#self.showWindowTitle('RFID READER SOFTWARE')

	## a function that sets up the menus and menu bars for the application
	def initMenu(self):
		# Exit the program button
		exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit Application')
		exitAction.triggered.connect(self.close)

		openSerialAction = QtGui.QAction(QtGui.QIcon('connect.png'),'Connect Reader',self)
		openSerialAction.setShortcut('Ctrl+R')
		openSerialAction.setStatusTip('Connect the RFID Reader')
		openSerialAction.triggered.connect(self.connectReader)

		self.statusBar()

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAction)
		fileMenu.addAction(openSerialAction)

		toolbar = self.addToolBar('Exit')
		toolbar.addAction(exitAction)
		toolbar.addAction(openSerialAction)

	def connectReader(self):
		# This function will open a window to allow the user to select which serial port the reader is on
		pass

	## This fucntion reads the queue and reacts to the elements it contains
	def readQueue(self):
		while self.queue.qsize():
			try:
				tag = self.queue.get(0)
				self.handleTag(tag)
			except Queue.Empty:
				pass

	## this fucntion handles the tags and how to add them to the database it also handles how to add the tag to the lists contained within
	def handleTag(self,tag):
		item = QtGui.QListWidgetItem("Tag %s" % tag[0:-2])
		self.splitterWidget.tagListWidget.addItem(item)	


class mainWidget(QtGui.QWidget):
	def __init__(self):
		super(mainWidget, self).__init__()
		self.initUI()

	## this function intilizes the UI for the main widget which currently involves seting up two lists that get written to
	def initUI(self):
		hbox = QtGui.QHBoxLayout(self)

		self.tagListWidget = QtGui.QListWidget()
		self.namelistWidget = QtGui.QListWidget()

		splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
		splitter.addWidget(self.tagListWidget)
		splitter.addWidget(self.namelistWidget)

		hbox.addWidget(splitter)
		self.setLayout(hbox)
		QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

	



############################# THREADER PARENT CLASS ############################
# The threader parent class spawns a second thread to pass messages from the   #
# rfid reader over the serial port to a queue which is read by the main qt     #
# thread                                                                       #
################################################################################
class ThreaderParent:
	############################# INIT THREADER PARENT #############################
	# THe initilization function creates the queue, calls the QT main window       #
	# generation class to generate the QT window, and then creates the thread for  #
	# the serial port to read from                                                 #
	################################################################################
	def __init__(self):
		print "WTHAT HE HELL"
		# create a queue for message passing
		self.queue = Queue.Queue()
		print "CREATED QUEUE"
		#instanciate the gui
		self.gui = mainWindow(self.queue, self.endApplication)
		self.gui.show()
		print "CRATED GUI"
		# create a timer to periodicly check the queue to see if it has tags
		self.timer = QtCore.QTimer()
		QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.periodicCall)
		self.timer.start(100)
		print "CRATED TIMER"
		# Create a thread to read the serial port
		self.running = 1
		self.thread = threading.Thread(target=self.workerThread)
		self.thread.start()

	################################# PERIODIC CALL ################################
	# THis function is called periodoicly by the QT timer to tell the Main QT      #
	# Window to read data from the queue and update the display accordingly        #
	################################################################################
	def periodicCall(self):
		self.gui.readQueue()
		if not self.running:
			root.quit()

	################################ END APPLICATION ###############################
	# This function should be called by the QT main window class when the QT       #
	# process ends, it sets the variable running to 0 so that the worker thread    #
	# can quit when the main thread does                                           #
	################################################################################
	def endApplication(self):
		print "ENDING"
		self.running = 0

	################################# WORKER THREAD ################################
	# The worker thread function is the function that is called to run inside the  #
	# spawned thread. It handles reading from the serial connection, if it reads   #
	# a valid tag then it puts it into a queue from wich the main thread can       #
	# handle it                                                                    #
	################################################################################
	def workerThread(self):
		serialConnection = serial.Serial(port=serialPort, baudrate=serialBaud, timeout=0)
		print "STARTING WORKER THREAD"
		while self.running:
			tag = serialConnection.readline()
			if (tag):
				self.queue.put(tag)
				print 'read tag'






## the main function ##
def main():
	app = QtGui.QApplication(sys.argv)
	display = ThreaderParent()
	app.exec_()
	print "DONE"
	#display.thread.terminate()
	display.running = False
	#sys.exit()
	exit()

## run the main function ##
if __name__ == '__main__':
	main()