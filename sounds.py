from numpy import ndarray
from enum import Enum
import wave

import numpy


class NChannels(Enum):
    MONO = 1
    STEREO = 2


class SampWidth(Enum):
    BYTE = 1
    WORD = 2
    DWORD = 4

    @property
    def used_int(self):
        if   self == SampWidth.BYTE:  return '<i1'
        elif self == SampWidth.WORD:  return '<i2'
        else:                         return '<i4'


class Channel(Enum):
    LEFT = 0
    RIGHT = 1


FRAMERATE: int = 44100
class Sound:
    def __init__(self, nchannels: NChannels, samp_width: SampWidth, nframes: int, framerate: int = FRAMERATE):
        self.nchannels, self.samp_width, self.framerate = nchannels, samp_width, framerate
        self.data = ndarray((nframes, nchannels.value), float)
        self.amplitude = 2 ** (samp_width.value * 8 - 1)

    def __setitem__(self, i: int, value):
        self.data[i] = value

    def __getitem__(self, i: int):
        return self.data[i]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def save(self, file: str):
        with wave.open(file, 'wb') as w:
            w.setnchannels(self.nchannels.value)
            w.setsampwidth(self.samp_width.value)
            w.setframerate(self.framerate)
            w.setnframes(len(self))
            w.setcomptype('NONE', 'not compressed')
            int_data = (numpy.round(self.data - 1) + 1).astype(self.samp_width.used_int)
            w.writeframes(int_data.tobytes())

    def merge_channels(self, sound, for_channel: Channel = Channel.RIGHT):
        assert self.nchannels == sound.nchannels == NChannels.MONO
        assert len(self) == len(sound)
        self.nchannels = NChannels.STEREO
        array = ndarray((len(self), 2), float)
        if for_channel == Channel.LEFT:
            for i in range(len(sound)):
                array[i] = sound[i][0], self[i][0]
        else:
            for i in range(len(sound)):
                array[i] = self[i][0], sound[i][0]
        self.data = array
