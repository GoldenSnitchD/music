import numpy
if __name__ == '__main__':
    from sounds import NChannels, SampWidth, FRAMERATE, Sound
else:
    from music import NChannels, SampWidth, FRAMERATE, Sound

tone_list = ['A', '♯A', 'B', 'C', '♯C', 'D', '♯D', 'E', 'F', '♯F', 'G', '♯G']
tone_dict = {'A': 0, 'B': 2, 'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2}
sharp_flat = {'♯': +1, '♭': -1, '𝄪': +2, '𝄫': -2, '♮': 0}


class Pitch:
    def __init__(self, value, octave: int = 0):
        if type(value) == int:
            self.diff = value
        elif type(value) == str:
            self.diff = tone_dict[value[-1]]
            if len(value) == 2:
                self.diff += sharp_flat[value[0]]
        elif value is None:
            self.diff = self.frequency = None
            return
        self.diff += octave * 12
        self.frequency = 440 * 2 ** (self.diff / 12.0)

    def __eq__(self, other) -> bool:
        return self.diff == other.diff

REST = Pitch(None)


def sine_wave(period: float, φ: float, n: int) -> numpy.ndarray:
    """
    Return a 1D `numpy.ndarray` of `n` `float`s, which collects a sine wave of referred `period`, `φ`.
    """
    from math import sin, cos, pi
    ω = pi * 2 / period
    array = numpy.ndarray(n, float)
    for x in range(n):
        phase = (x * ω + φ) % (pi * 2)
        array[x] = cos(phase - pi / 2) if pi / 4 <= phase % pi < pi * 3 / 4 else sin(phase)
    return array


class Note:
    def __init__(self, pitch: Pitch, volume: float, secs: float):
        self.pitch = pitch
        self.volume = volume
        self.secs = secs
        self.frequency = self.pitch.frequency

    def pure_sound(self, nchannels: NChannels, samp_width: SampWidth, framerate: int = FRAMERATE, φ: float = 0.0) -> Sound:
        sound = Sound(nchannels, samp_width, round(
            self.secs * framerate), framerate)

        if self.pitch == REST:

            return sound

        collection = sine_wave(framerate / self.frequency, φ, len(sound))
        for i in range(len(sound)):
            for j in range(nchannels.value):
                sound.data[i][j] = collection[i]
        sound.data *= sound.amplitude * self.volume
        sound.data -= 0.5
        return sound


if __name__ == '__main__':
    C, G = Note(Pitch('C'), 1.0, 1.0), Note(Pitch('G'), 1.0, 1.0)
    sound = C.pure_sound(NChannels.MONO, SampWidth.WORD)
    sound.merge_channels(G.pure_sound(NChannels.MONO, SampWidth.WORD))
    sound.save('double_tone.wav')
