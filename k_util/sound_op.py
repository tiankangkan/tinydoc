import os
import time
import platform
import subprocess
import pyaudio
import wave


class SoundUtil(object):
    def __init__(self):
        self.platform = platform.system()
        self.stream = None
        self.wave_file = None
        self.py_audio = None
        pass

    def play_mp3(self, file_path):
        if self.platform == 'Darwin':
            subprocess.call(["afplay", file_path])
        else:
            print 'Not support'

    def start_play_wava(self, file_path, block=True):
        # define callback (2)
        def callback(in_data, frame_count, time_info, status):
            data = self.wave_file.readframes(frame_count)
            return data, pyaudio.paContinue

        self.wave_file = wave.open(file_path, 'rb')

        # instantiate PyAudio (1)
        p = pyaudio.PyAudio()
        self.py_audio = p

        # open stream using callback (3)
        self.stream = p.open(
                format=p.get_format_from_width(self.wave_file.getsampwidth()),
                channels=self.wave_file.getnchannels(),
                rate=self.wave_file.getframerate(),
                output=True, stream_callback=callback)

        # start the stream (4)
        self.stream.start_stream()

        if block:
            while self.stream.is_active():
                time.sleep(0.1)

    def stop_play_wave(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wave_file.close()
        self.py_audio.terminate()

    def start_record_wave(self, file_path, sample_width=2, channels=1, rate=16000):
        # define callback (2)
        def callback(in_data, frame_count, time_info, status):
            data = self.wave_file.writeframes(in_data)
            # print time_info, status
            return data, pyaudio.paContinue

        self.wave_file = wave.open(file_path, 'wb')
        self.wave_file.setnchannels(1)
        self.wave_file.setframerate(16000)
        self.wave_file.setsampwidth(2)

        # instantiate PyAudio (1)
        p = pyaudio.PyAudio()
        self.py_audio = p

        # open stream using callback (3)
        self.stream = p.open(format=p.get_format_from_width(sample_width), channels=channels, rate=rate,
                             input=True, stream_callback=callback)

        # start the stream (4)
        self.stream.start_stream()

    def stop_record_wave(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wave_file.close()
        self.py_audio.terminate()


if __name__ == '__main__':
    s = SoundUtil()
    # s.start_play_wava('/Users/kangtian/Documents/Master/talker/record_2.wav')
    s.start_record_wave(file_path='/Users/kangtian/Documents/Master/talker/record_3.wav')
    time.sleep(6)
    s.stop_record_wave()
    # time.sleep(6)

