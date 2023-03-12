
import popchat
import config
import server
import functions
import subprocess
#import traceback
import importlib
import time
import sys
import os
import pyttsx3
from PyQt6.QtWidgets import QApplication,  QWidget, QPlainTextEdit, QMainWindow, QPushButton, QTextEdit, QRadioButton, QButtonGroup, QHBoxLayout, QVBoxLayout, QListWidget, QLineEdit, QLabel, QListWidgetItem, QStatusBar
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QPainter, QColor, QTextFormat, QFontDatabase, QTextCursor
from PyQt6.QtCore import QRect, pyqtSlot, Qt, QThread, QTimer
import re
xfile=''
otext=''
engine=''
error = ''
otext_proof=''
class LineNumberArea(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, parent=editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        QPlainTextEdit.__init__(self, parent)
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
#        self.setGeometry(25,35,450,300)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(0, 0, 0))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber();
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(255,255,0))
                painter.drawText(0, top, self.lineNumberArea.width(),
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def lineNumberAreaWidth(self):
        digits = len(str(self.blockCount()))
        space = 50 #+ self.fontMetrics().width('9')*digits
        return space

    def keyPressEvent(self, event):
        if event.key() == 16777217: # Tab Key
            self.insertPlainText(" " * 4)
            return
        elif event.key() == 16777219: # Backspace Key
            try:
              if self.toPlainText()[self.textCursor().position() - 4: self.textCursor().position()] == " " * 4:
                self.textCursor().deletePreviousChar()
                self.textCursor().deletePreviousChar()
                self.textCursor().deletePreviousChar()
                self.textCursor().deletePreviousChar()
                return
            except Exception as err:
                pass
        elif event.key() == 16777220: # Enter Key
            cursor = self.textCursor()
            current_line = cursor.block().text()
            indent = 0
            for char in current_line:
                if char == " ":
                    indent += 1
                else:
                    break
            if current_line.strip() and current_line.strip()[-1] == ":":
                self.insertPlainText("\n" + " " * (indent + 4))
                return
            elif indent >= 4:
                self.insertPlainText("\n" + " " * indent)
                return
        super().keyPressEvent(event)
    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    @pyqtSlot(int)
    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0);

    @pyqtSlot()
    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(255,0,0).lighter(130)
            selection.format.setBackground(lineColor)
            #selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            #print(dir(QTextFormat.lengthProperty))
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    @pyqtSlot(QRect, int)
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
class StandardItem(QListWidgetItem):
    def __init__(self, txt='',  color=QColor(0, 0, 0)):
        super().__init__()

        self.setForeground(color)
        self.setText(txt)
class Highlighter(QSyntaxHighlighter):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._mapping = {}

	def add_mapping(self, pattern, pattern_format):
		self._mapping[pattern] = pattern_format

	def highlightBlock(self, text_block):
		for pattern, fmt in self._mapping.items():
			for match in re.finditer(pattern, text_block):
				start, end = match.span()
				self.setFormat(start, end-start, fmt)

class Window_dev(QMainWindow):

    def __init__(self):
        super(Window_dev, self).__init__()

        self.initUI()

    def initUI(self):
        global xfile
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.setFixedHeight(30)
        self.lbl_con = QLabel(self)
        self.statusBar.addPermanentWidget(self.lbl_con)
        self.lbl_con.move(30, 40)
        self.lbl_con.setFixedHeight(30)
        layout1 = QHBoxLayout()

        layout2 = QHBoxLayout()
        layout3 = QVBoxLayout()
        layout4 = QVBoxLayout()
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()
        layout7 = QVBoxLayout()
        widget = QWidget()
        self.setCentralWidget(widget)
        self.filelist = QListWidget(self)
        #self.filelist.currentTextChanged.connect(self.text_changed)
        self.filelist.itemClicked.connect(self.text_changed)
        self.filelist.setFixedWidth(80)
        self.filelist.addItems(['popchat'])
        self.filelist.addItems(['config'])
        self.filelist.addItems(['functions'])

        self.filelist.addItem( StandardItem("server", color=QColor(50, 0, 255)) )
        self.filelist.addItem( StandardItem("config", color=QColor(50, 0, 255)) )
        self.filelist.addItem( StandardItem("functions", color=QColor(50, 0, 255)) )
        self.filelist.addItems(['readme'])
        self.filelist.addItems(['protocol'])
        self.filelist.addItems(['planner'])

        self.varlist = QListWidget(self)
        self.varlist.currentTextChanged.connect(self.val_changed)
        self.varlist.setFixedWidth(150)
        pb1 = QPushButton('Check Syntax', self)
        pb1.clicked.connect(self.onClick_pb1)
        pb2 = QPushButton('Recompile', self)
        pb2.clicked.connect(self.onClick_pb2)
        pb3 = QPushButton('Test', self)
        pb3.clicked.connect(self.onClick_pb3)
        pb4 = QPushButton('Add', self)
        pb4.clicked.connect(self.onClick_pb4)
        pb5 = QPushButton('Debug', self)
        pb5.clicked.connect(self.onClick_pb5)
        pb4.setFixedWidth(30)
        self.pb6 = QPushButton('Read Aloud!', self)
        self.pb6.clicked.connect(self.onClick_pb6)
        self.pb6.setVisible(False)
        self.txtvar = QLineEdit('', self)
        self.txtvar.setPlaceholderText("Enter VariableName Here")
        self.txtvar.setFixedWidth(115)
        layout5.addWidget(self.txtvar)
        layout5.addWidget(pb4)
        lbltmr =  QLabel('Set Stop Time:', self)
        lbltmr.setFixedWidth(75)
        self.txttmr = QLineEdit('', self)
        self.txttmr.setFixedWidth(70)
        layout6.addWidget(lbltmr)
        layout6.addWidget(self.txttmr)
        self.stext = QTextEdit(self)
        pb7 = QPushButton('Read', self)
        pb7.clicked.connect(self.onClick_pb7)
        pb7.setFixedWidth(80)
        self.sproof = QTextEdit(self)
        self.sproof.setFixedWidth(80)
        self.stext.setStyleSheet('QTextEdit {background-color: white; color: black;}')
        self.stext.setFixedHeight(40)
        layout1.addWidget(pb1)
        layout1.addWidget(pb2)
        layout1.addWidget(pb3)
        layout1.addWidget(pb5)
        layout1.addWidget(self.pb6)
        layout4.addLayout(layout5)
        layout4.addLayout(layout6)
        layout4.addWidget(self.varlist)
        self.etext1 = QTextEdit(self)
        self.etext = CodeEditor(self)
        self.etext.cursorPositionChanged.connect(self.update_cursor_loc)
        new_font = QFont("Courier", 12)
        self.etext.setFont(new_font)
        self.etext1.setFont(new_font)
        self.etext1.setVisible(False)
        new_font = QFont("Courier", 6)
        self.sproof.setFont(new_font)
        text=open('popchat.py').read()
        self.etext.setPlainText(text)
        self.thread()
        layout7.addWidget(self.filelist)
        layout7.addWidget(pb7)
        layout7.addWidget(self.sproof)
        layout2.addLayout( layout7 )
        layout2.addWidget(self.etext)
        layout2.addWidget(self.etext1)
        layout2.addLayout( layout4 )
        layout3.addLayout( layout1 )
        layout3.addLayout( layout2 )
        layout3.addWidget(self.stext)
        widget = QWidget()
        widget.setLayout(layout3)
        self.setCentralWidget(widget)
        self.setGeometry(25, 45, 1200, 800)
        self.setWindowTitle('System IDE')
        xfile = 'popchat.py'
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.highlighter = Highlighter()
        self.setUpEditor()
        self.show()
    def update_cursor_loc(self):
        cursor = self.etext.textCursor()
        row = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.lbl_con.setText('Ln:' + str(row) + ' Col:' + str(column))
    def showTime(self):
        global error
        if error != '':
            self.stext.setPlainText(str(error))
            error = ''
    def text_changed(self, s):
        global xfile
        self.pb6.setVisible(False)
        if s.foreground() != QColor(50, 0, 255):
          if s.text() == 'readme':
            self.etext.setVisible(False)
            self.etext1.setVisible(True)
            new_font = QFont("Courier", 8)
            self.etext1.setFont(new_font)
            text=open('read_me.txt').read()
            self.etext1.setPlainText(text)
            xfile='read_me.txt'
            self.pb6.setVisible(True)
          elif s.text() == 'protocol':
            self.etext.setVisible(False)
            self.etext1.setVisible(True)
            new_font = QFont("Courier", 8)
            self.etext1.setFont(new_font)
            text=open('protocol.txt').read()
            self.etext1.setPlainText(text)
            xfile='protocol.txt'
            self.pb6.setVisible(True)
          elif s.text() == 'planner':
            self.etext.setVisible(False)
            self.etext1.setVisible(True)
            new_font = QFont("Courier", 8)
            self.etext1.setFont(new_font)
            text=open('planner.txt').read()
            self.etext1.setPlainText(text)
            xfile='planner.txt'
            self.pb6.setVisible(True)
          elif s.text() == 'config':
            self.etext.setVisible(True)
            self.etext1.setVisible(False)
            new_font = QFont("Courier", 12)
            self.etext.setFont(new_font)
            text=open('config.py').read()
            self.etext.setPlainText(text)
            xfile='config.py'
          #elif s.text() == 'protocol':
            #new_font = QFont("Courier", 8)
            #self.etext.setFont(new_font)
            #text=open('protocol.txt').read()
            #self.etext.setPlainText(text)
            #xfile='protocol.txt'
          elif s.text() == 'functions':
            self.etext.setVisible(True)
            self.etext1.setVisible(False)
            new_font = QFont("Courier", 12)
            self.etext.setFont(new_font)
            text=open('functions.py').read()
            self.etext.setPlainText(text)
            xfile='functions.py'
          #elif s == 'server':
            #new_font = QFont("Courier", 12)
            #self.etext.setFont(new_font)
            #text=open('server.py').read()
            #self.etext.setPlainText(text)
            #xfile='server\server.py'
          elif s.text() == 'popchat':
            self.etext.setVisible(True)
            self.etext1.setVisible(False)
            new_font = QFont("Courier", 12)
            self.etext.setFont(new_font)
            text=open('popchat.py').read()
            self.etext.setPlainText(text)
            xfile='popchat.py'
        else:
          if s.text() == 'server':
            self.etext.setVisible(True)
            self.etext1.setVisible(False)
            new_font = QFont("Courier", 12)
            self.etext.setFont(new_font)
            text=open(r'server\server.py').read()
            self.etext.setPlainText(text)
            xfile='server\server.py'
          elif s.text() == 'config':
            self.etext.setVisible(True)
            self.etext1.setVisible(False)
            new_font = QFont("Courier", 12)
            self.etext.setFont(new_font)
            text=open(r'server\config.py').read()
            self.etext.setPlainText(text)
            xfile='server\config.py'
          elif s.text() == 'functions':
            self.etext.setVisible(True)
            self.etext1.setVisible(False)  
            new_font = QFont("Courier", 12)
            self.etext.setFont(new_font)
            text=open(r'server\functions.py').read()
            self.etext.setPlainText(text)
            xfile=r'server\functions.py'
    def setUpEditor(self):
    		# define pattern rule #1: highlight class header
    		class_format = QTextCharFormat()
    		class_format.setForeground(QColor(50, 0, 255))
    		#class_format.setFontWeight(QFont.setBold(True))
    		pattern = r'^\s*class\s+\w+\(.*$'
    		self.highlighter.add_mapping(pattern, class_format)

            # pattern #2: function format
    		function_format = QTextCharFormat()
    		function_format.setForeground(QColor(255, 10, 10))
    		function_format.setFontItalic(True)
    		pattern = r'^\s*def\s+\w+\s*\(.*\)\s*:\s*$'
    		self.highlighter.add_mapping(pattern, function_format)


            # pattern 3: import format
    		fnt = QFont("Courier", 12)
    		fnt.setBold(True)

    		import_format = QTextCharFormat()
    		import_format.setFont(fnt)
    		import_format.setForeground(QColor(176,88,0))
    		pattern = r'\bimport\b' # hightlight from the beginning of the text

    		self.highlighter.add_mapping(pattern, import_format)

            # pattern 4: self format
    		self_format = QTextCharFormat()
    		fnt = QFont("Courier", 12)
    		fnt.setBold(True)
    		self_format.setFont(fnt)
    		self_format.setForeground(QColor(225, 102, 213))
    		pattern = r'\bself\b' # hightlight from the beginning of the text

    		self.highlighter.add_mapping(pattern, self_format)

            # pattern 4: print format
    		print_format = QTextCharFormat()
    		fnt = QFont("Courier", 12)
    		fnt.setBold(True)
    		print_format.setFont(fnt)
    		print_format.setForeground(QColor(166, 166, 210))
    		pattern = r'\bprint\b' # hightlight from the beginning of the text

    		self.highlighter.add_mapping(pattern, print_format)


            # pattern 5: if format
    		if_format = QTextCharFormat()
    		#fnt = QFont("Courier", 12)
    		#fnt.setBold(True)
    		if_format.setFont(fnt)
    		if_format.setForeground(QColor(255, 0, 128))
    		pattern = r'\bif\b' # hightlight from the beginning of the text

    		self.highlighter.add_mapping(pattern, if_format)

            # pattern 6: elif format
    		elif_format = QTextCharFormat()
    		#fnt = QFont("Courier", 12)
    		#fnt.setBold(True)
    		elif_format.setFont(fnt)
    		elif_format.setForeground(QColor(255, 0, 128))
    		pattern = r'\belif\b' # hightlight from the beginning of the text


    		self.highlighter.add_mapping(pattern, elif_format)

            # pattern 7: else format
    		else_format = QTextCharFormat()
    		#fnt = QFont("Courier", 12)
    		#fnt.setBold(True)
    		else_format.setFont(fnt)
    		else_format.setForeground(QColor(255, 0, 128))
    		pattern = r'\belse\b' # hightlight from the beginning of the text
    		self.highlighter.add_mapping(pattern, else_format)

            # pattern 8: update format
    		update_format = QTextCharFormat()
    		#fnt = QFont("Courier", 12)
    		#fnt.setBold(True)
    		update_format.setFont(fnt)
    		update_format.setForeground(QColor(0, 204, 102))
    		pattern = r'\bupdate\b' # hightlight from the beginning of the text
    		self.highlighter.add_mapping(pattern, update_format)

            # pattern 9: config format
    		config_format = QTextCharFormat()
    		#fnt = QFont("Courier", 12)
    		#fnt.setBold(True)
    		config_format.setFont(fnt)
    		config_format.setForeground(QColor(45, 134, 242))
    		pattern = r'\bconfig\b' # hightlight from the beginning of the text
    		self.highlighter.add_mapping(pattern, config_format)

            # pattern 9:eqg format
    		eq_format = QTextCharFormat()
    		fnt = QFont("Courier", 14)
    		fnt.setBold(True)
    		eq_format.setFont(fnt)
    		eq_format.setForeground(QColor(207, 159, 255))
    		pattern = r'\b = \b' # hightlight from the beginning of the text
    		self.highlighter.add_mapping(pattern, eq_format)



            # pattern 10: comment format
    		comment_format = QTextCharFormat()
    		comment_format.setForeground(QColor("#e28743"))
    		# pattern = r'^\s*#.*$' # hightlight from the beginning of the line
    		pattern = r'#.*$' # just the text
    		self.highlighter.add_mapping(pattern, comment_format)
    		#font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    		#self.etext.setFont(font)

    		self.highlighter.setDocument(self.etext.document())

    def val_changed(self, s):
        pass

    def onClick_pb7(self):
        global otext_proof
        if self.sproof.toPlainText() != '':
            otext_proof = self.sproof.toPlainText()
            self.worker7 = WorkerThread7()
            self.worker7.start()
            self.sproof.setPlainText('')
    def onClick_pb5(self):
        pass
    def onClick_pb6(self):
        global otext
        otext = self.etext.toPlainText()
        self.worker = WorkerThread()
        self.worker.start()
    def onClick_pb4(self):
        pass
    def onClick_pb3(self):
        global xfile
        if xfile=='server\server.py':
            comd = 'self.setGeometry(650, 270, 350, 400)\n'
            prog=open('server\server.py').read()
            prog1 = prog.split('self.setGeometry(25, 45, 350, 400)\n')
            prog = prog1[0] + comd + prog1[1]
            ff = open('server\server_tmp.py', 'w')
            ff.write(prog)
            ff.close()

#            importlib.reload(server_tmp)
            try:
              self.worker1 = WorkerThread1()
              self.worker1.start()
            except Exception as err:
              self.stext.setPlainText(str(err))

        elif xfile=='popchat.py':
           comcon = 'import config_tmp as config\n'
           comfunc = 'import functions_tmp as update\n'
           comd = 'self.setGeometry(10, 35, 620, 700)\n'
           prog=open('popchat.py').read()
           prog1 = prog.split('#<<0>>\n')
           prog = prog1[0] + comd + prog1[1]
           ff = open('popchat_t1.py', 'w')
           ff.write(prog)
           ff.close()

           prog1 = prog.split('import config\n')
           prog = prog1[0] + comcon + prog1[1]
           ff = open('popchat_t1.py', 'w')
           ff.write(prog)
           ff.close()

           prog1 = prog.split('import functions as update\n')
           prog = prog1[0] + comfunc + prog1[1]
           ff = open('popchat_t1.py', 'w')
           ff.write(prog)
           ff.close()

           prog=open('functions.py').read()
           prog1 = prog.split('import config\n')
           prog = prog1[0] + comcon + prog1[1]
           ff = open('functions_tmp.py', 'w')
           ff.write(prog)
           ff.close()

           prog=open('config.py').read()
           ff = open('config_tmp.py', 'w')
           ff.write(prog)
           ff.close()
#           importlib.reload(functions_tmp)
#           importlib.reload(config_tmp)
#           importlib.reload(popchat_t1)
           try:
              self.worker2 = WorkerThread2()
              self.worker2.start()
           except Exception as err:
              self.stext.setPlainText(str(err))
           time.sleep(1)
           comcon = 'import config_tmp0 as config\n'
           comfunc = 'import functions_tmp0 as update\n'
           comd = 'self.setGeometry(632, 35, 620, 700)\n'
           prog=open('popchat.py').read()
           prog1 = prog.split('#<<0>>\n')
           prog = prog1[0] + comd + prog1[1]
           ff = open('popchat_t2.py', 'w')
           ff.write(prog)
           ff.close()

           prog1 = prog.split('import config\n')
           prog = prog1[0] + comcon + prog1[1]
           ff = open('popchat_t2.py', 'w')
           ff.write(prog)
           ff.close()

           prog1 = prog.split('import functions as update\n')
           prog = prog1[0] + comfunc + prog1[1]
           ff = open('popchat_t2.py', 'w')
           ff.write(prog)
           ff.close()

           prog=open('functions.py').read()
           prog1 = prog.split('import config\n')
           prog = prog1[0] + comcon + prog1[1]
           ff = open('functions_tmp0.py', 'w')
           ff.write(prog)
           ff.close()

           prog=open('config.py').read()
           ff = open('config_tmp0.py', 'w')
           ff.write(prog)
           ff.close()

#           importlib.reload(popchat_t2)
#           importlib.reload(functions_tmp0)
#           importlib.reload(config_tmp0)

           try:
              self.worker3 = WorkerThread3()
              self.worker3.start()
           except Exception as err:
              self.stext.setPlainText(str(err))
           time.sleep(1)
           comd = 'self.setGeometry(1255, 35, 620, 700)\n'
           prog=open('popchat.py').read()
           prog1 = prog.split('#<<0>>\n')
           prog = prog1[0] + comd + prog1[1]
           ff = open('popchat_t3.py', 'w')
           ff.write(prog)
           ff.close()

           prog=open('functions.py').read()
           ff = open('functions_tmp1.py', 'w')
           ff.write(prog)
           ff.close()

           prog=open('config.py').read()
           ff = open('config_tmp1.py', 'w')
           ff.write(prog)
           ff.close()


           try:
              self.worker4 = WorkerThread4()
              self.worker4.start()
           except Exception as err:
              self.stext.setPlainText(str(err))
           time.sleep(1)
           comd = 'self.setGeometry(1400, 770, 450, 270)\n'
           prog=open('server\server.py').read()
           prog1 = prog.split('self.setGeometry(25, 45, 350, 400)\n')
           prog = prog1[0] + comd + prog1[1]
           ff = open('server\server_tmp.py', 'w')
           ff.write(prog)
           ff.close()

#           importlib.reload(server_tmp)
           try:
              self.worker1 = WorkerThread1()
              self.worker1.start()
           except Exception as err:
              self.stext.setPlainText(str(err))
           time.sleep(1)
    def onClick_pb1(self):
          global xfile

          vfile = xfile.split('.')

          if vfile[1] != 'txt':

            nfile = vfile[0] + '_tmp.' + vfile[1]

            otext=self.etext.toPlainText()

            with open(nfile, 'w') as ff:
                ff.write(otext)
            cmdCommand = "python -m py_compile " +  nfile   #specify your cmd command
            process = subprocess.getoutput(cmdCommand.split())

            if process == '':
                self.stext.setPlainText("No error encountered during syntax check!")
            else:
                self.stext.setPlainText(process)

    def onClick_pb2(self):
        global xfile
        vfile = xfile.split('.')
        try:

          if vfile[1] != 'txt':
             nfile = vfile[0] + '_tmp.' + vfile[1]

             otext=self.etext.toPlainText()
             with open(nfile, 'w') as ff:
               ff.write(otext)
             cmdCommand = "python -m py_compile " + nfile   #specify your cmd command
             process = subprocess.getoutput(cmdCommand.split())
             self.stext.setPlainText(process)
             if process == '':
                otext=self.etext.toPlainText()

                with open(xfile, 'w') as ff:
                    ff.write(otext)

          else:
              otext=self.etext1.toPlainText()
              with open(xfile, 'w') as ff:
                    ff.write(otext)
        except Exception as err:
              self.stext.setPlainText(str(err))
              pass

class WorkerThread(QThread):
   def run(self):
       global otext, engine, error
       try:
           engine.endLoop()
       except Exception as err:
           error=err
       try:
           engine = pyttsx3.init()
           engine.setProperty('rate', 120)
           engine.say(otext)
           engine.runAndWait()
       except Exception as err:
            error=str(err)
class WorkerThread7(QThread):
   def run(self):
       global otext_proof, engine, error
       try:
           engine.endLoop()
       except Exception as err:
           error=err
       try:
           engine = pyttsx3.init()
           engine.setProperty('rate', 120)
           engine.say(otext_proof)
           engine.runAndWait()
       except Exception as err:
            error=str(err)
class WorkerThread1(QThread):
   def run(self):
       global error
       try:
           cmdCommand = "python server\server_tmp.py"   #specify your cmd command
           process = subprocess.getoutput(cmdCommand.split())
           error = process
           #os.system("python server_tmp.py")
       except Exception as err:

           error=(str(err))

class WorkerThread2(QThread):
   def run(self):
       global error
       try:
           cmdCommand = "python popchat_t1.py"   #specify your cmd command
           process = subprocess.getoutput(cmdCommand.split())
           error = process
           #os.system("python popchat_t1.py")
       except Exception as err:
           error=str(err)

class WorkerThread3(QThread):
   def run(self):
       global error
       try:
           cmdCommand = "python popchat_t2.py"   #specify your cmd command
           process = subprocess.getoutput(cmdCommand.split())
           error = process
           #os.system("python popchat_t2.py")
       except Exception as err:
           error=str(err)
class WorkerThread4(QThread):
   def run(self):
       global error
       try:
           cmdCommand = "python popchat_t3.py"   #specify your cmd command
           process = subprocess.getoutput(cmdCommand.split())
           error = process
           #os.system("python popchat_t3.py")
       except Exception as err:
           error=str(err)
def main():

    app = QApplication(sys.argv)
    ex = Window_dev()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
