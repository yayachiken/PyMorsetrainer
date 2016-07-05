#!/usr/bin/env python

"""
(C) 2016 David Kolossa

This file is part of PyMorsetrainer.

PyMorsetrainer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyMorsetrainer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyMorsetrainer.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from threading import Thread
import random
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QAction, QTextEdit, QLineEdit, QLabel, QGridLayout, qApp, QPushButton, QHBoxLayout, QVBoxLayout,  QComboBox

from morselib import MorsePlayer, MorseCode
from distance import global_matching, levenshtein

KOCH_LETTERS = "KMURESNAPTLWI.JZ=FOY,VG5/Q92H38B?47C1D60X"

class MainWindow(QMainWindow):
    def __init__(self):
        self.lesson = 1
        self.requireNewExercise = False
        self.mp = None
        self.thread = None
        super().__init__()
        self.initUI()
        self.generateExercise()
        
    def initUI(self):
        
        self.centralWidget = QWidget()

        self.receivedTextEdit = QTextEdit()  
        monospaceFont = QFont("Monospace")
        monospaceFont.setStyleHint(QFont.Monospace)
        self.receivedTextEdit.setCurrentFont(monospaceFont)
        
        playExerciseButton = QPushButton("Play exercise text")
        playExerciseButton.clicked.connect(self.playExercise)
        stopButton = QPushButton("Stop playing")
        stopButton.clicked.connect(self.stopPlaying)
        validateButton = QPushButton("Check input / Generate next exercise")
        validateButton.clicked.connect(self.checkInput)
        self.wpmLineEdit = QLineEdit("20")
        wpmLabel = QLabel("WPM")
        self.ewpmLineEdit = QLineEdit("12")
        ewpmLabel = QLabel("effective WPM")
        self.freqLineEdit = QLineEdit("800")
        freqLabel = QLabel("Frequency (Hz)")
        self.durationLineEdit = QLineEdit("1")
        durationLabel = QLabel("Duration (min)")
        
        lessonGrid = QGridLayout()
        lessonCombo = QComboBox()
        lessonCombo.addItem("1 - K M")
        for lesson in range(2, len(KOCH_LETTERS)):
            lessonCombo.addItem(str(lesson) + " - " + KOCH_LETTERS[lesson])
        lessonCombo.currentIndexChanged.connect(self.newLessonSelected)
        
        
        self.lessonLabel = QLabel(' '.join(KOCH_LETTERS[:self.lesson+1]))
        lessonGrid.addWidget(lessonCombo, 1, 1, 1, 1)
        lessonGrid.addWidget(self.lessonLabel, 1, 2, 1, 1)
        
        
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.receivedTextEdit, 1, 1, 7, 1)
        grid.addWidget(playExerciseButton, 1, 2, 1, 2)
        grid.addWidget(stopButton, 2, 2, 1, 2)
        grid.addWidget(validateButton, 3, 2, 1, 2)
        grid.addWidget(self.wpmLineEdit, 4, 2)
        grid.addWidget(wpmLabel, 4, 3)
        grid.addWidget(self.ewpmLineEdit, 5, 2)
        grid.addWidget(ewpmLabel, 5, 3)
        grid.addWidget(self.freqLineEdit, 6, 2)
        grid.addWidget(freqLabel, 6, 3)
        grid.addWidget(self.durationLineEdit, 7, 2)
        grid.addWidget(durationLabel, 7, 3)
        grid.addLayout(lessonGrid, 8, 1, 1, 3)
        
        

        self.centralWidget.setLayout(grid)
        self.setCentralWidget(self.centralWidget)
        
        
        self.setWindowTitle('PyMorsetrainer')
        self.show()
        
        
    def playExercise(self):
        if self.requireNewExercise == True:
            self.generateExercise()
        wpm = int(self.wpmLineEdit.text())
        effectiveWpm = int(self.ewpmLineEdit.text())
        frequency = int(self.freqLineEdit.text())
        self.mp = MorsePlayer(self.morse_solution, wpm, effectiveWpm, frequency)
        self.mp.start()
    
    def stopPlaying(self):
        if self.mp is not None:
            self.mp.shutdown()
    
    def newLessonSelected(self, comboId):
        self.lesson = comboId+1
        self.lessonLabel.setText(' '.join(KOCH_LETTERS[:self.lesson+1]))
        self.requireNewExercise = True
        
    def generateExercise(self):
        letters = KOCH_LETTERS[:self.lesson+1]
        wpm = int(self.wpmLineEdit.text())
        effectiveWpm = int(self.ewpmLineEdit.text())
        frequency = int(self.freqLineEdit.text())
        duration = int(self.durationLineEdit.text())
        
        mc = MorseCode("")
        
        while mc.tally_length_in_seconds(wpm, effectiveWpm) < duration * 60:
            new_word = ""
            for _ in range(0, 5):
                new_word += (random.choice(letters))
            mc.set_morse_text(mc.get_morse_text() + " " + new_word)
        self.requireNewExercise = False
        self.morse_solution = mc.get_morse_text()
        print(self.morse_solution)
        
    def checkInput(self):
        self.evalWindow = EvaluationWindow(self.receivedTextEdit.toPlainText().upper(), self.morse_solution)
        self.evalWindow.show()
        self.requireNewExercise = True
        self.receivedTextEdit.clear()
        
        
        
class EvaluationWindow(QWidget):
    def __init__(self, inputText, solutionText):
        self.inputText = inputText
        self.solutionText = solutionText
        super(EvaluationWindow, self).__init__()
        self.initUI()
        
    def initUI(self):
        inputGroups = self.inputText.split()
        solutionGroups = self.solutionText.split()
        numLetters = 0.0
        numErrors = 0.0
        comparisonText = "<pre>SENT \t RECEIVED<br/>"
        for idx, _ in enumerate(solutionGroups):
            numLetters += len(solutionGroups[idx])
            try:
                numErrors += levenshtein(solutionGroups[idx], inputGroups[idx])
                _, solutionMatched, inputMatched = global_matching(solutionGroups[idx], inputGroups[idx])
                colorSolution = ""
                colorInput = ""
                for idx, _ in enumerate(solutionMatched):
                    if solutionMatched[idx] == inputMatched[idx]:
                        colorSolution += "<span style='color: green'>" + solutionMatched[idx] + "</span>"
                        colorInput += "<span style='color: green'>" + inputMatched[idx] + "</span>"
                    else:
                        colorSolution += "<span style='color: red'>" + solutionMatched[idx] + "</span>"
                        colorInput += "<span style='color: red'>" + inputMatched[idx] + "</span>"
                        
                comparisonText += ("\n" + colorSolution + " \t " + colorInput + "<br/>")
            except(IndexError):
                numErrors += len(solutionGroups[idx])
        percentage = numErrors / numLetters * 100.0
        solutionLabel = QLabel(comparisonText + "</pre>")
        errorLabel = QLabel("Error count (Levenshtein): %02.2f%%" % percentage)
        layout = QVBoxLayout()
        layout.addWidget(solutionLabel)
        layout.addWidget(errorLabel)
        if percentage < 10.0:
            successLabel = QLabel("Error rate lower than 10%! <br/> Proceed to next lesson!")
            layout.addWidget(successLabel)
        self.setLayout(layout)
        self.setWindowTitle('Evaluation')
            
        
                



        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
