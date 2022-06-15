#!/usr/bin/env python3

import argparse, os, glob

import numpy as np
from skimage.io import imread
from skimage.transform import resize
from skimage.color import rgb2gray
from scipy.io import wavfile


class Image2Sound():
    
    def __init__(
        self,
        power=6,
        freq_lim=(500,2500),
        duration=1,
    ):
        self.power = power
        self.size = 2**power
        self.freq_lim = freq_lim
        self.sps = 2*freq_lim[1]
        self.duration = duration
        
        self.points = _generate_hilbert_points(self.power)
        
    def get_audio_from_path(self, path, output_dir=None):
        audio = _generate_audio_from_path(path, self.size, self.points, self.freq_lim, self.duration, self.sps)
        if output_path: 
            filename = os.path.splitext(os.path.split(self.path)[-1])[0]
            wavfile.write(os.path.join(output_dir, filename+'.wav'), self.sps, audio.astype(np.dtype('i2')))
        return audio
    
    def get_audio(self, img, output_file=None):
        audio = _generate_audio(img, self.size, self.points, self.freq_lim, self.duration, self.sps)
        if output_file: wavfile.write(output_file, self.sps, audio.astype(np.dtype('i2')))
        return audio

class ImageList2SoundList(Image2Sound):
    
    def __init__(
        self,
        dir_path,
        power=6,
        freq_lim=(500,2500),
        duration=1,
    ):
        self.dir_path = dir_path
        self.paths = glob.glob(os.path.join(dir_path, '*.png'))
        self.power = power
        self.size = 2**power
        self.freq_lim = freq_lim
        self.sps = 2*freq_lim[1]
        self.duration = duration
        
        self.points = _generate_hilbert_points(self.power)
    
    def get_audio_list(self, output_dir=None):
        audio_list = []
        for i,file in enumerate(self.paths):
            audio = _generate_audio(file, self.size, self.points, self.freq_lim, self.duration, self.sps)
            audio_list.append(audio)
            if output_dir: 
                filename = os.path.splitext(os.path.split(file)[-1])[0]
                wavfile.write(os.path.join(output_dir, filename+'.wav'), self.sps, audio.astype(np.dtype('i2')))
        return audio_list
    
    
    
def _parse_args():
    parser = argparse.ArgumentParser(description='Take in a video and generate a sound file')
    parser.add_argument('path', type=str, help='local path to video or directory of .pngs')
    parser.add_argument('--power', type=int, default=6, help='exponent of two to determine video dimension')
    parser.add_argument('--freq-min', type=int, default=500, help='lower bound of output frequency')
    parser.add_argument('--freq-max', type=int, default=2500, help='upper bound of output frequency')
    parser.add_argument('--fps', type=int, default=5, help='frames per second of output video')
    
    args = parser.parse_args()
    return args

def _generate_hilbert_points(power):
    """ Generates a sequence of points that fill pixelated space 
    smoothly using a (pseudo-) Hilbert curve. The power of the Hilbert curve 
    is the order of the pseudo-hilbert curve; higher power, higher resolution.

    This uses a Lindenmayer System (or Rewrite System) that acts like it is doing
    turtle graphics.

    More details on this method can be found at: https://en.wikipedia.org/wiki/Hilbert_curve
    """

    sequence = ['A']
    n = int(power)

    for _ in range(n):
        new_sequence = []
        for item in sequence:
            if item=='A':
                new_sequence.extend(['+', 'B', 'F', '-', 'A', 'F', 'A', '-', 'F', 'B', '+'])
            elif item=='B':
                new_sequence.extend(['-', 'A', 'F', '+', 'B', 'F', 'B', '+', 'F', 'A', '-'])
            else:
                new_sequence.append(item)
        sequence = new_sequence
    for i,item in enumerate(sequence):
        if item=='A' or item=='B':
            del sequence[i]
    for i,item in enumerate(sequence):
        try:
            if item=='+' and sequence[i-1]=='-':
                del sequence[i]
                del sequence[i-1]
            elif item=='-' and sequence[i-1]=='+':
                del sequence[i]
                del sequence[i-1]
        except IndexError:
            continue

    points = [(0,0)]
    angle = 0
    for item in sequence:
        if item=='F':
            new_point = (points[-1][0] + np.cos(angle), points[-1][1] + np.sin(angle))
            points.append(new_point)
        elif item=='+':
            angle+=np.pi/2
        elif item=='-':
            angle-=np.pi/2
    points = np.round(np.array(points)).astype('int')
    return points


def _generate_audio(img, size, points, freq_lim, duration, sps):
    """Generates audio file from an image and a (pseudo-) Hilbert curve.
    The image is first made grayscale, then pixels are mapped from 2D pixel space to 1D
    frequency space along the Hilbert curve. The brightness of the pixel is mapped to 
    the amplitude of that pixel's frequency.
    """
    
    # Resize image
    img = resize(img, (size, size, 3))

    # Convert 2D image to 1D frequency
    amplitudes = np.array([rgb2gray(img[points[i,0], points[i,1]]) for i in range(len(points))], dtype='float32')
    frequencies = np.linspace(freq_lim[0], freq_lim[1], len(amplitudes), dtype='float32')
    
    # Convert 1D frequency to 1D time (adding sines)
    t = np.linspace(0,duration,sps, dtype='float32')
    total = np.zeros(sps, dtype='float32')
    for i,freq in enumerate(frequencies):
        total += amplitudes[i]*np.sin(2*np.pi*freq*(t-np.random.random()))
    total *= 100
    return total

def _generate_audio_from_path(file, size, points, freq_lim, duration, sps):
    """Wrapper for if image is from file
    """
    img = imread(file)
    return _generate_audio(img, size, points, freq_lim, duration, sps)

    
if __name__ == '__main__':
    
    # Argument parsing
    args = _parse_args()
    points = _generate_hilbert_points(args.power)
    sps = args.freq_max*2
    cwd = os.getcwd()
    if os.path.isdir(args.path):
        for file in glob.glob(os.path.join(args.path, '*.png')):
            audio = _generate_audio_from_path(file, 2**args.power, points, (args.freq_min, args.freq_max), 1, sps)
            filename = os.path.splitext(os.path.split(file)[-1])[0]
            print('Writing %s' % filename)
            wavfile.write(os.path.join(cwd, 'audio', filename+'.wav'), sps, audio.astype(np.dtype('i2')))