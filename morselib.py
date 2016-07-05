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

import math
import numpy
from scipy.signal import butter, lfilter
import pyaudio
from threading import Thread


SAMPLE_RATE = 44100

class MorseCode():
    def __init__(this, morse_text):
        this.morse_text = morse_text
        
        
    def set_morse_text(this, morse_text):
        this.morse_text = morse_text
        
    def get_morse_text(this):
        return this.morse_text
    
    
    def morse_code(self):
        morse_str = ""
        for c in self.morse_text:
            if c == ' ':
                morse_str += "#"
                continue
            
            # The string is actually a flat tree, the morse code is encoded in the
            # tree position of the letter.
            # Some special symbols were removed.
            binary_pos = bin('ETIANMSURWDKGOHVFÜLÄPJBXCYZQÖ 54 3   2  +    16=/     7   8 90            ?_    "  .    @   \'  -        ;!       ,    :'.index(c)+2)
            # Cut away 0b prefix and the first number (tree has two roots)
            codepoint = binary_pos[3:]
            # Convert binary code to morse code (0 = dit, 1 = dah)
            code_str = codepoint.replace("0", ". ").replace("1", "- ")
            morse_str += code_str[:-1] + "/"
        return morse_str
    
    
    def morse_tone(self, wpm, effective_wpm, frequency=800):
        tones = []
        for c in self.morse_code():
            if c == '.':
                tones.append(self.__dit(wpm, frequency))
            if c == '-':
                tones.append(self.__dah(wpm, frequency))
            if c == ' ':
                tones.append(self.__dit_pause(wpm))
            if c == '/':
                tones.append(self.__dah_pause(wpm, effective_wpm))
            if c == '#':
                tones.append(self.__space(wpm, effective_wpm))
        # As a rule of thumb, the bandwidth of a CW signal is 4 * WPM in Hertz
        return self.__lowpass_filter(numpy.concatenate(tones), frequency, cutoff=wpm*4).astype(numpy.float32)
    
    def tally_length_in_seconds(self, wpm, effective_wpm):
        length = 0
        for c in self.morse_code():
            if c == '.':
                length += self.__dit_length(wpm)
            if c == '-':
                length += self.__dah_length(wpm)
            if c == ' ':
                length += self.__dit_pause_length(wpm)
            if c == '/':
                length += self.__dah_pause_length(wpm, effective_wpm)
            if c == '#':
                length += self.__space_length(wpm, effective_wpm)
        return length
    
    """
    Morse code consists of "dits" (short tones), "dahs" (long tones),
    and pauses with varying length.

    Dits and dahs are often expressed by the letters . (dot) and - (dash).

    The lengths are as follows:
    dit:         1 length
    dah:         3 lengths
    dit pause:   1 length    (seperates symbols)
    dah pause:   3 lengths   (seperates letters)
    space:       7 lengths   (seperates words)

    The length of a dit is defined by repeating the standard word "PARIS", and
    counting the number of possible repetitions per minute (words per minute,
    wpm)

    PARIS = .--. .- .-. .. ... (space)
        = 10 dits + 4 dahs + 9 dit pauses + 4 dah pauses + 1 space 
        = 10 * 1 + 4 * 3 + 9 * 1 + 4 * 3 + 1 * 7
        = 22 voiced intervals + 28 silent intervals
        = 50 intervals
    => 1 wpm = 50 dits per minute = 1.2 seconds per dit.

    For didactive reasons, there is a second measure called "effective WPM"
    which lengthens the pauses between letters and words, but not between symbols.

    This so-called Farnsworth timing uses formulae defined as in
    http://www.arrl.org/files/file/Technology/x9004008.pdf
    """
    
    """ Only used in the formula for effective WPM < 18 """
    def __delay_per_character(self, wpm, effective_wpm):
        return (60 * wpm - 37.2 * effective_wpm) / (wpm * effective_wpm)


    def __dit_length(self, wpm):
        return 1.2 / wpm

    def __dah_length(self, wpm):
        return 3 * self.__dit_length(wpm)

    def __dit_pause_length(self, wpm):
        return self.__dit_length(wpm)

    def __dah_pause_length(self, wpm, effective_wpm):
        if effective_wpm >= 18:
            return 3 * self.__dit_length(wpm)
        else:
            return 3 * self.__delay_per_character(wpm, effective_wpm) / 19
        
    def __space_length(self, wpm, effective_wpm):
        if effective_wpm >= 18:
            return 7 * self.__dit_length(wpm)
        else:
            return 7 * self.__delay_per_character(wpm, effective_wpm) / 19


    def __dit(self, wpm, frequency):
        return self.__sine(self.__dit_length(wpm), frequency, SAMPLE_RATE)

    def __dah(self, wpm, frequency):
        return self.__sine(self.__dah_length(wpm), frequency, SAMPLE_RATE)

    def __dit_pause(self, wpm):
        return self.__pause(self.__dit_pause_length(wpm), SAMPLE_RATE)

    def __dah_pause(self, wpm, effective_wpm):
        return self.__pause(self.__dah_pause_length(wpm, effective_wpm), SAMPLE_RATE)

    def __space(self, wpm, effective_wpm):
        return self.__pause(self.__space_length(wpm, effective_wpm), SAMPLE_RATE)
    
    
    """
    Primitives to create sine waves of a certain length
    and pauses.

    Simple band-pass filtering is used to avoid clicks.
    """

    def __butterworth(self, cutoff, frequency):
        lowcut = (frequency - cutoff/2) * 2.0 / SAMPLE_RATE
        highcut = (frequency + cutoff/2) * 2.0 / SAMPLE_RATE
        return butter(1, [lowcut, highcut], btype="band", analog=False)
        
    def __lowpass_filter(self, data, frequency, cutoff=100):
        b, a = self.__butterworth(cutoff, frequency)
        return lfilter(b, a, data)

    def __sine(self, length, frequency, rate=SAMPLE_RATE):
        length = int(length * rate)
        factor = float(frequency) * (math.pi * 2) / rate
        return numpy.sin(numpy.arange(length) * factor)

    def __pause(self, length, rate=SAMPLE_RATE):
        length = int(length * rate)
        return numpy.arange(length) * 0
        
    
        


class MorsePlayer(Thread):
    def __init__(self, morse_text, wpm, effective_wpm, frequency):
        self.p = pyaudio.PyAudio()
        self.morse = MorseCode(morse_text)
        self.wpm = wpm
        self.effective_wpm = effective_wpm
        self.frequency = frequency
        self.shutdownFlag = False
        super(MorsePlayer, self).__init__()
    
    def run(self):
        samples = self.morse.morse_tone(self.wpm, self.effective_wpm, self.frequency)
        stream = self.p.open(format=pyaudio.paFloat32,
                    channels=1, rate=SAMPLE_RATE, output=1)
        chunknum = len(samples) / 1024
        samples = numpy.array_split(samples, chunknum)
        for s in samples:
            if self.shutdownFlag == True:
                stream.close()
                break
            stream.write(s.tostring())

    def shutdown(self):
        self.shutdownFlag = True
        

