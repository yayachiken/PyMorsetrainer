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
import functools
from threading import Thread
import random
from PyQt5.Qt import Qt, QSettings
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QMainWindow,
    QAction,
    QTextEdit,
    QLineEdit,
    QLabel,
    QGridLayout,
    qApp,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QDialog,
    QSizePolicy,
    QToolButton,
)

from pymorsetrainer.morselib import MorsePlayer, MorseCode
from pymorsetrainer.distance import global_matching, levenshtein

KOCH_LETTERS = "KMURESNAPTLWI.JZ=FOY,VG5/Q92H38B?47C1D60X"


class MainWindow(QMainWindow):
    def __init__(self):
        self.settings = QSettings("yayachiken", "PyMorsetrainer")
        if not self.settings.allKeys():
            print("Initializing application settings...")
            self.settings.setValue("currentLesson", "1")
            self.settings.setValue("wpm", "20")
            self.settings.setValue("effectiveWpm", "15")
            self.settings.setValue("frequency", "800")
            self.settings.setValue("duration", "60")

        self.requireNewExercise = False
        self.mp = None
        self.lessonButtons = []
        self.debug = False

        super().__init__()
        self.initUI()
        self.generateExercise()

    def initUI(self):
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.receivedTextEdit = QTextEdit()
        self.receivedTextEdit.setAcceptRichText(False)
        monospaceFont = QFont("Monospace")
        monospaceFont.setStyleHint(QFont.Monospace)
        self.receivedTextEdit.setFont(monospaceFont)

        playExerciseButton = QPushButton("Play exercise text")
        playExerciseButton.clicked.connect(self.playExercise)

        stopButton = QPushButton("Stop playing")
        stopButton.clicked.connect(self.stopPlaying)

        validateButton = QPushButton("Check input / Generate next exercise")
        validateButton.clicked.connect(self.checkInput)

        self.wpmLineEdit = QLineEdit(self.settings.value("wpm"))
        self.wpmLineEdit.textChanged.connect(
            functools.partial(self.saveChangedText, self.wpmLineEdit, "wpm")
        )
        wpmLabel = QLabel("WPM")

        self.ewpmLineEdit = QLineEdit(self.settings.value("effectiveWpm"))
        self.ewpmLineEdit.textChanged.connect(
            functools.partial(self.saveChangedText, self.ewpmLineEdit, "effectiveWpm")
        )
        ewpmLabel = QLabel("effective WPM")

        self.freqLineEdit = QLineEdit(self.settings.value("frequency"))
        self.freqLineEdit.textChanged.connect(
            functools.partial(self.saveChangedText, self.freqLineEdit, "frequency")
        )
        freqLabel = QLabel("Frequency (Hz)")

        self.durationLineEdit = QLineEdit(self.settings.value("duration"))
        self.durationLineEdit.textChanged.connect(
            functools.partial(self.saveChangedText, self.durationLineEdit, "duration")
        )
        durationLabel = QLabel("Duration (seconds)")

        self.lessonGrid = QGridLayout()

        lessonCombo = QComboBox()
        lessonCombo.setStyleSheet("combobox-popup: 0;")
        lessonCombo.addItem("1 - K M")
        for lesson in range(2, len(KOCH_LETTERS)):
            lessonCombo.addItem(str(lesson) + " - " + KOCH_LETTERS[lesson])
        lessonCombo.setCurrentIndex(int(self.settings.value("currentLesson")) - 1)
        lessonCombo.currentIndexChanged.connect(self.newLessonSelected)

        lessonIdLabel = QLabel("Lesson:")

        lessonBox = QHBoxLayout()
        lessonBox.addWidget(lessonIdLabel)
        lessonBox.addWidget(lessonCombo)
        lessonBox.addStretch(-1)

        self.createLessonLetterButtons(self.lessonGrid)

        mainLayout = QVBoxLayout()

        inputAndParameters = QHBoxLayout()
        parameterField = QVBoxLayout()
        inputAndParameters.addWidget(self.receivedTextEdit, stretch=1)
        self.receivedTextEdit.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        )
        inputAndParameters.addLayout(parameterField, stretch=0)

        parameterField.addWidget(playExerciseButton)
        parameterField.addWidget(stopButton)
        parameterField.addWidget(validateButton)

        parameterGrid = QGridLayout()
        parameterGrid.addWidget(self.wpmLineEdit, 0, 0)
        parameterGrid.addWidget(wpmLabel, 0, 1)
        parameterGrid.addWidget(self.ewpmLineEdit, 1, 0)
        parameterGrid.addWidget(ewpmLabel, 1, 1)
        parameterGrid.addWidget(self.freqLineEdit, 2, 0)
        parameterGrid.addWidget(freqLabel, 2, 1)
        parameterGrid.addWidget(self.durationLineEdit, 3, 0)
        parameterGrid.addWidget(durationLabel, 3, 1)
        parameterField.addLayout(parameterGrid)
        parameterField.insertSpacing(-1, 15)
        parameterField.addLayout(lessonBox)
        parameterField.insertStretch(-1)

        mainLayout.addLayout(inputAndParameters)
        mainLayout.addLayout(self.lessonGrid)

        self.centralWidget.setLayout(mainLayout)

        self.setWindowTitle("PyMorsetrainer")
        self.show()

    def closeEvent(self, event):
        self.stopPlaying()

    def createLessonLetterButtons(self, parentGrid):
        newButtonCount = int(self.settings.value("currentLesson")) + 1
        oldButtonCount = len(self.lessonButtons)

        if oldButtonCount > newButtonCount:
            for button in self.lessonButtons[newButtonCount:]:
                parentGrid.removeWidget(button)
                button.deleteLater()
            self.lessonButtons = self.lessonButtons[:newButtonCount]
        else:
            for idx, letter in enumerate(KOCH_LETTERS[oldButtonCount:newButtonCount]):
                idx = idx + oldButtonCount
                button = QToolButton()
                button.setText(letter)
                button.clicked.connect(functools.partial(self.playMorse, letter))
                buttonPolicy = QSizePolicy(
                    QSizePolicy.Minimum, QSizePolicy.Fixed, QSizePolicy.PushButton
                )
                buttonPolicy.setHorizontalStretch(0)
                button.setSizePolicy(buttonPolicy)
                button.setMinimumWidth(5)
                parentGrid.addWidget(button, 1 + int(idx / 12), int(idx % 12))
                self.lessonButtons.append(button)

    def playMorse(self, text):
        if self.mp is not None:
            self.mp.shutdown()
        wpm = int(self.settings.value("wpm"))
        effectiveWpm = int(self.settings.value("effectiveWpm"))
        frequency = int(self.settings.value("frequency"))
        self.mp = MorsePlayer(text, wpm, effectiveWpm, frequency)
        self.mp.start()

    def playExercise(self):
        if self.requireNewExercise == True:
            self.generateExercise()
        self.playMorse(self.morse_solution)

    def stopPlaying(self):
        if self.mp is not None:
            self.mp.shutdown()

    def newLessonSelected(self, comboId):
        newLesson = comboId + 1
        self.settings.setValue("currentLesson", newLesson)
        self.createLessonLetterButtons(self.lessonGrid)
        self.requireNewExercise = True

    def generateExercise(self):
        lesson = int(self.settings.value("currentLesson"))
        letters = KOCH_LETTERS[: lesson + 1]
        wpm = int(self.wpmLineEdit.text())
        effectiveWpm = int(self.ewpmLineEdit.text())
        frequency = int(self.freqLineEdit.text())
        duration = int(self.durationLineEdit.text())

        mc = MorseCode("")

        while mc.tally_length_in_seconds(wpm, effectiveWpm) < duration:
            new_word = ""
            for _ in range(0, 5):
                new_word += random.choice(letters)
            mc.set_morse_text(mc.get_morse_text() + " " + new_word)
        self.requireNewExercise = False
        self.morse_solution = mc.get_morse_text()
        if self.debug:
            print(self.morse_solution)

    def checkInput(self):
        self.evalWindow = EvaluationWindow(
            self.receivedTextEdit.toPlainText().upper(), self.morse_solution
        )
        self.evalWindow.setModal(True)
        self.evalWindow.show()
        self.requireNewExercise = True
        self.receivedTextEdit.clear()

    def saveChangedText(self, inputField, settingName):
        self.settings.setValue(settingName, inputField.text())

    def enableDebugMode():
        self.debug = True


class EvaluationWindow(QDialog):
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
        for idx, _ in enumerate(solutionGroups):
            if idx >= len(inputGroups):
                inputGroups.append("")
            numLetters += len(solutionGroups[idx])
            numErrors += levenshtein(solutionGroups[idx], inputGroups[idx])
        percentage = numErrors / numLetters * 100.0

        solutionLabel = QLabel(
            self.createEvaluationRichText(solutionGroups, inputGroups)
        )
        errorLabel = QLabel("Error count (Levenshtein): %02.2f%%" % percentage)

        layout = QVBoxLayout()
        layout.addWidget(solutionLabel)
        layout.addWidget(errorLabel)

        if percentage < 10.0:
            successLabel = QLabel(
                "Error rate lower than 10%! <br/> Proceed to next lesson!"
            )
            layout.addWidget(successLabel)

        self.setLayout(layout)
        self.setWindowTitle("Evaluation")

    def createEvaluationRichText(self, solutionGroups, inputGroups):
        richText = "<table align='center'><tr><td align='center'><pre>SENT</pre></td><td align='center'><pre>RECEIVED</pre></t></tr>"
        for idx, solutionGroup in enumerate(solutionGroups):
            richText += "<tr>"
            if idx >= len(inputGroups):
                inputGroups.append("")
            _, solutionMatched, inputMatched = global_matching(
                solutionGroups[idx], inputGroups[idx]
            )
            colorSolution, colorInput = "", ""
            for idx, _ in enumerate(solutionMatched):
                if solutionMatched[idx] == inputMatched[idx]:
                    colorSolution += (
                        "<span style='color: green'>" + solutionMatched[idx] + "</span>"
                    )
                    colorInput += (
                        "<span style='color: green'>" + inputMatched[idx] + "</span>"
                    )
                else:
                    colorSolution += (
                        "<span style='color: red'>" + solutionMatched[idx] + "</span>"
                    )
                    colorInput += (
                        "<span style='color: red'>" + inputMatched[idx] + "</span>"
                    )
            richText += (
                "<td align='center'><pre>"
                + colorSolution
                + "</pre></td><td align='center'><pre>"
                + colorInput
                + "</pre></td>"
            )
            richText += "</tr>"
        richText += "</table>"
        return richText
