
import popchat
#import popchat_t1
#import popchat_t2
#import popchat_t3
import config
#import config_tmp
#import config_tmp0
#import config_tmp1
import server
#import server_tmp
import functions
#import functions_tmp
#import functions_tmp0
#import functions_tmp1
import subprocess
#import subprocess as sbp1
#import subprocess as sbp2
#import subprocess as sbp3
import importlib
import time
import sys
import os
import pyttsx3
from PyQt6.QtWidgets import QApplication,  QWidget, QPlainTextEdit, QMainWindow, QPushButton, QTextEdit, QRadioButton, QButtonGroup, QHBoxLayout, QVBoxLayout, QListWidget, QLineEdit, QLabel
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QPainter, QColor, QTextFormat
from PyQt6.QtCore import QRect, pyqtSlot, Qt, QThread, QTimer

xfile=''
otext=''
engine=''
error = ''
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
        space = 35 #+ self.fontMetrics().width('9')*digits
        return space

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
class Window_dev(QMainWindow):

    def __init__(self):
        super(Window_dev, self).__init__()

        self.initUI()

    def initUI(self):
        global xfile
        layout1 = QHBoxLayout()

        layout2 = QHBoxLayout()
        layout3 = QVBoxLayout()
        layout4 = QVBoxLayout()
        layout5 = QHBoxLayout()
        layout6 = QHBoxLayout()
        widget = QWidget()
        self.setCentralWidget(widget)
        self.filelist = QListWidget(self)
        self.filelist.currentTextChanged.connect(self.text_changed)
        self.filelist.setFixedWidth(80)
        self.filelist.addItems(['popchat'])
        self.filelist.addItems(['config'])
        self.filelist.addItems(['functions'])
        self.filelist.addItems(['server'])
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
        self.etext = CodeEditor(self)

        new_font = QFont("Courier", 8)
        self.etext.setFont(new_font)
        text=open('popchat.py').read()
        self.etext.setPlainText(text)
        self.thread()
        layout2.addWidget(self.filelist)
        layout2.addWidget(self.etext)
        layout2.addLayout( layout4 )
        layout3.addLayout( layout1 )
        layout3.addLayout( layout2 )
        layout3.addWidget(self.stext)
        widget = QWidget()
        widget.setLayout(layout3)
        self.setCentralWidget(widget)
        self.setGeometry(25, 45, 900, 600)
        self.setWindowTitle('System IDE')
        xfile = 'popchat.py'
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)

        self.show()

    def showTime(self):
        global error
        if error != '':
            self.stext.setPlainText(str(error))
            error = ''
    def text_changed(self, s):
        global xfile
        self.pb6.setVisible(False)
        if s == 'readme':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('read_me.txt').read()
            self.etext.setPlainText(text)
            xfile='read_me.txt'
            self.pb6.setVisible(True)
        elif s == 'protocol':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('protocol.txt').read()
            self.etext.setPlainText(text)
            xfile='protocol.txt'
            self.pb6.setVisible(True)
        elif s == 'planner':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('planner.txt').read()
            self.etext.setPlainText(text)
            xfile='planner.txt'
            self.pb6.setVisible(True)
        elif s == 'config':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('config.py').read()
            self.etext.setPlainText(text)
            xfile='config.py'
        elif s == 'protocol':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('protocol.txt').read()
            self.etext.setPlainText(text)
            xfile='protocol.txt'
        elif s == 'functions':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('functions.py').read()
            self.etext.setPlainText(text)
            xfile='functions.py'
        elif s == 'server':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('server.py').read()
            self.etext.setPlainText(text)
            xfile='server.py'
        elif s == 'popchat':
            new_font = QFont("Courier", 8)
            self.etext.setFont(new_font)
            text=open('popchat.py').read()
            self.etext.setPlainText(text)
            xfile='popchat.py'
    def val_changed(self, s):
        pass
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
        if xfile=='server.py':
            comd = 'self.setGeometry(450, 270, 350, 400)\n'
            prog=open('server.py').read()
            prog1 = prog.split('self.setGeometry(25, 45, 350, 400)\n')
            prog = prog1[0] + comd + prog1[1]
            ff = open('server_tmp.py', 'w')
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
           comd = 'self.setGeometry(10, 35, 420, 540)\n'
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
           comd = 'self.setGeometry(432, 35, 420, 540)\n'
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
           comd = 'self.setGeometry(853, 35, 420, 540)\n'
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

#           importlib.reload(popchat_t3)
#           importlib.reload(functions_tmp1)
#           importlib.reload(config_tmp1)
           try:
              self.worker4 = WorkerThread4()
              self.worker4.start()
           except Exception as err:
              self.stext.setPlainText(str(err))
           time.sleep(1)
           comd = 'self.setGeometry(450, 270, 350, 400)\n'
           prog=open('server.py').read()
           prog1 = prog.split('self.setGeometry(25, 45, 350, 400)\n')
           prog = prog1[0] + comd + prog1[1]
           ff = open('server_tmp.py', 'w')
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
          print(vfile)
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
                importlib.reload(popchat)
                importlib.reload(server)
                importlib.reload(config)
                importlib.reload(functions)
                #self.mdiwindow = popchat.MainW()
                #self.mdiwindow.show()
          else:
              otext=self.etext.toPlainText()
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

class WorkerThread1(QThread):
   def run(self):
       global error
       try:
           os.system("python server_tmp.py")
       except Exception as err:
           error=str(err)

class WorkerThread2(QThread):
   def run(self):
       global error
       try:
           os.system("python popchat_t1.py")
       except Exception as err:
           error=str(err)

class WorkerThread3(QThread):
   def run(self):
       global error
       try:
           os.system("python popchat_t2.py")
       except Exception as err:
           error=str(err)
class WorkerThread4(QThread):
   def run(self):
       global error
       try:
           os.system("python popchat_t3.py")
       except Exception as err:
           error=str(err)
def main():

    app = QApplication(sys.argv)
    ex = Window_dev()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
