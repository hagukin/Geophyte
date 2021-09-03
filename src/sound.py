import time
import wave
import pyaudio
import threading
import inspect
import ctypes

from collections import deque
from typing import Any, Optional


def _async_raise(tid, exctype):
    """
    raises the exception, performs cleanup if needed
    Args:
        tid:
            thread's id
        exctype:
            Exception object. Must not be an instance.
    """
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # if res is not 0,something has gone horribly wrong
        # you should call it again with exc=NULL to revert the effect
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class SoundThread(threading.Thread):
    """Thread object that handles all audio-related tasks."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        # target function of the thread class
        try:
            super().run()
            # print(f"SOUND::SoundThread running")
        except Exception as e:
            print(f"FATAL ERROR::an error occurred during running SoundThread - {e}")
        finally:
            # print(f"SOUND::SoundThread stopped")
            pass

    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.is_alive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        raise AssertionError("could not determine the thread's id")

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def terminate(self):
        """
        raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)
        """
        self.raise_exc(SystemExit)

    def kill(self) -> None:
        """Terminate and join this thread."""
        self.terminate()
        self.join(1) # timeout = 1 sec


class SoundManager():
    """
    Handles all sound-related tasks.

    NOTE: Due to GIL, current structure requires no lock.
    """
    __SLEEP_TIME = 0.0167  # 1/60 sec

    def __init__(self) -> None:
        # Iniitalization
        global sound_queue
        global bgm
        global bgs
        sound_queue = deque()
        bgm = set()
        bgs = set()

        self.threads = {}

        self.p = pyaudio.PyAudio()
        self.chunk = 1024 # bytes to read per write loop

    def __del__(self) -> None:
        try:
            self.p.terminate()
        except Exception as e:
            print(f"ERROR::error during SoundManager deletion - {e}")

    def update(self) -> None:
        """
        Main method of the sound manager.
        update() is called each frame (not game loop)
        """
        while True:
            if bgm:
                self.__play_bgm()
            if bgs:
                self.__play_bgs()
            while sound_queue:
                self.__play_queue()
            time.sleep(SoundManager.__SLEEP_TIME) # check every 1/60 sec for sound update

    def __play_queue(self) -> None:
        """
        Do not directly call this method outside of run()
        """
        snd = sound_queue.pop()
        th = SoundThread(target=self.play_sound, args=(snd,))
        th.daemon = True
        th.start()

    def __play_bgm(self) -> None:
        """
        Do not directly call this method outside of run()
        """
        snd = bgm.pop()
        th = SoundThread(target=self.play_sound, args=(snd,True))
        th.daemon = True
        self.threads["bgm"] = th
        th.start()

    def __play_bgs(self) -> None:
        """
        Do not directly call this method outside of run()
        """
        snd = bgs.pop()
        th = SoundThread(target=self.play_sound, args=(snd,True))
        th.daemon = True
        self.threads["bgs"] = th
        th.start()

    def add_sound_queue(self, directory: str=None, file: Any=None) -> None:
        sound_queue.append(directory)

    def change_bgm(self, directory: str=None) -> None:
        if bgm:
            print("Warning::BGM deque should be empty.")
            bgm.clear()
        if "bgm" in self.threads.keys():
            if self.threads["bgm"]:
                self.threads["bgm"].terminate() # Stopping the previous thread
        bgm.add(directory) # will be played in next .run()

    def change_bgs(self, directory: str=None) -> None:
        if bgs:
            print("Warning::BGS deque should be empty.")
            bgs.clear()
        if "bgs" in self.threads.keys():
            if self.threads["bgs"]:
                self.threads["bgs"].terminate() # Stopping the previous thread
        bgs.add(directory)  # will be played in next .run()

    def play_sound(self, directory: str=None, loop: bool=False) -> None:
        """
        Play sound of given directory.
        """
        playing = True
        while playing:
            f = wave.open(directory, "rb")
            stream = self.p.open(format=self.p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)

            data = f.readframes(self.chunk)

            while data:
                stream.write(data)
                data = f.readframes(self.chunk)

            if not loop:
                stream.stop_stream()
                stream.close()
                playing = False



