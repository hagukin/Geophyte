import time
import wave, audioop
import pyaudio
import threading
import inspect
import ctypes
import traceback
import random

from collections import deque
from typing import Any, Optional
from biome import Biome


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
            traceback.print_exc()
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

        self.__current_bgm = None # Read-only
        self.__current_bgs = None

        self.master_volume: float = 0.5

        self.sound_db = { # TODO: Add volume - make sound_db value contains directory AND volume.
            "fx_player_hit":("fx\\hit.wav",0.35),
            "fx_player_crit":("fx\\kill.wav",0.35),
            "fx_player_miss":("fx\\miss.wav",0.35),
            "fx_block":("fx\\block.wav",0.5),
            "fx_player_kill":("fx\\crit_hit.wav",0.25),
            "fx_player_death":("fx\\death.wav",0.5),
            "fx_damaged": ("fx\\damaged.wav", 1),
            "fx_damaged2": ("fx\\damaged2.wav", 1),
            "fx_damaged3":("fx\\damaged3.wav", 0.7),
            "fx_damaged4": ("fx\\damaged4.wav", 1),
            "fx_near_death_damage": ("fx\\near_death_damage.wav", 0.5),
            "fx_teleport":("fx\\teleport.wav",1),
            "fx_pickup":("fx\\pickup.wav",0.5),
            "fx_steal": ("fx\\pickup.wav", 0.5),
            "fx_descend":("fx\\descend.wav",0.5),
            "fx_throw":("fx\\throw.wav",0.5),
            "fx_drop":("fx\\drop.wav",0.5),
            "fx_split":("fx\\equip.wav",0.5),
            "fx_equip":("fx\\equip.wav",0.5),
            "fx_unequip":("fx\\equip.wav",0.5),
            "fx_enchant": ("fx\\enchant.wav", 0.9),
            "fx_identify": ("fx\\identify.wav", 0.8),
            "fx_remove_curse": ("fx\\remove_curse.wav", 0.5),
            "fx_quaff":("fx\\quaff.wav",0.8),
            "fx_eat":("fx\\eat.wav",0.5),
            "fx_unlock":("fx\\unlock.wav",0.5),
            "fx_open_door":("fx\\open_door.wav",0.5),
            "fx_door_open_fail":("fx\\door_open_fail.wav",0.5),
            "fx_close_door":("fx\\open_door.wav",0.5), # Same as opening
            "fx_try_break_door":("fx\\try_break_door.wav",0.5),
            "fx_force_open_door":("fx\\force_open_door.wav",0.5),
            "fx_break_door":("fx\\break_door.wav",0.5),
            "fx_explosion":("fx\\explosion.wav",0.35),
            "fx_exp_gain":("fx\\exp_gain.wav",0.5),
            "fx_water_splash":("fx\\water_splash.wav",0.5),
            "fx_water_splash_short":("fx\\water_splash_short.wav",0.5),
            "fx_shatter":("fx\\shatter.wav",0.5),
            "fx_fall_impact":("fx\\low_impact.wav",0.5),
            "fx_burden":("fx\\burden.wav",0.5),
            "fx_cash":("fx\\coin.wav",0.5),
            "fx_book":("fx\\book.wav",0.5),
            "fx_victory":("fx\\victory.wav",0.5),
            "fx_destroy_item":("fx\\destroy_item.wav",0.5),
            "fx_ui_warning":("fx\\ui_warning.wav",0.5),
            "fx_ui_negative": ("fx\\ui_negative.wav",0.5),
            "fx_ui_positive":("fx\\ui_positive.wav",0.5),
            "fx_invalid":("fx\\invalid.wav",0.5),

            "fx_anger": ("fx\\anger.wav", 0.5),
            "fx_roar": ("fx\\roar.wav", 0.8),
            "fx_evil":("fx\\evil.wav",0.5),
            "fx_evil2": ("fx\\evil.wav", 1),
            "fx_collision": ("fx\\collision.wav", 0.5),
            "fx_crack": ("fx\\crack.wav", 0.5),
            "fx_earth_impact": ("fx\\earth_impact.wav", 0.5),
            "fx_electric_impact": ("fx\\electric_impact.wav", 0.5),
            "fx_electric": ("fx\\electric.wav", 0.5),
            "fx_lightning": ("fx\\lightning.wav", 0.9),
            "fx_fire_impact": ("fx\\fire_impact.wav", 0.5),
            "fx_fire_lit": ("fx\\fire_lit.wav", 0.5),
            "fx_fire_lit2": ("fx\\fire_lit2.wav", 0.8),
            "fx_burn": ("fx\\burn.wav", 1),
            "fx_spray": ("fx\\spray.wav", 1),
            "fx_ice_impact": ("fx\\ice_impact.wav", 0.5),
            "fx_credit": ("fx\\credit.wav", 0.5),
            "fx_sonicboom": ("fx\\sonicboom.wav", 0.5),
            "fx_low_impact": ("fx\\low_impact.wav", 0.5),
            "fx_bad_impact": ("fx\\bad_impact.wav", 0.5),
            "fx_magic_applied2": ("fx\\magic_applied2.wav", 0.5),
            "fx_summon": ("fx\\summon.wav", 0.7),
            "fx_magic_applied4": ("fx\\magic_applied4.wav", 0.5),
            "fx_ray": ("fx\\ray.wav", 0.5),
            "fx_magic_mapping": ("fx\\magic_mapping.wav", 0.5),
            "fx_hatred": ("fx\\hatred.wav", 0.5),
            "fx_slow_effect": ("fx\\slow_effect.wav", 0.5),
            "fx_tension_magic_applied": ("fx\\tension_magic_applied.wav", 0.5),
            "fx_heal": ("fx\\heal.wav", 0.5),
            "fx_gain_ability": ("fx\\gain_ability.wav", 0.5),

            "bgm_title_screen":("bgm\\Constellation.wav",0.5),
            "bgm_mystical_beginning":("bgm\\Magical_Travel.wav",0.5),
            "bgm_pianomotive": ("bgm\\Pianomotive.wav", 0.5),
            "bgm_virtual_relaxation": ("bgm\\Virtual_Relaxation.wav", 0.5),
            "bgm_mystic_train": ("bgm\\Mystic_Train.wav", 0.5),

            "bgs_cave":("bgs\\cave.wav",0.5),
        }

        self.update_volume_change()

    @property
    def current_bgm(self) -> str:
        """returns current bgm directory"""
        return self.__current_bgm

    @property
    def current_bgs(self) -> str:
        """returns current bgs directory"""
        return self.__current_bgs

    def update_volume_change(self) -> None:
        """
        Refresh current config volume data to newly updated json.
        """
        from configuration import get_game_config
        self.master_volume = round(get_game_config()["master_volume"] / 100, 2)

    def play_bgm_for_biome(self, biome: Biome) -> None:
        """Is called when engine.game_map changes."""
        if biome.biome_bgm_id == "" or biome.biome_bgm_id == None:
            print(f"SOUND::Biome {biome.biome_id} has no bgm.")
            return
        self.change_bgm(biome.biome_bgm_id, force_change=False)

    def play_bgs_for_biome(self, biome: Biome) -> None:
        """Is called when engine.game_map changes."""
        if biome.biome_bgs_id == "" or biome.biome_bgs_id == None:
            print(f"SOUND::Biome {biome.biome_id} has no bgs.")
            return
        self.change_bgs(biome.biome_bgs_id, force_change=False)

    def get_path_from_id(self, sound_id: str) -> str:
        """Returns directory"""
        return "resources\\sound\\"+self.sound_db[sound_id][0]

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
        self.__current_bgm = snd
        th.start()

    def __play_bgs(self) -> None:
        """
        Do not directly call this method outside of run()
        """
        snd = bgs.pop()
        th = SoundThread(target=self.play_sound, args=(snd,True))
        th.daemon = True
        self.threads["bgs"] = th
        self.__current_bgs = snd
        th.start()

    def add_sound_queue(self, sound_id: str) -> None:
        if sound_id:
            sound_queue.append(sound_id)
        else:
            print("SOUND::ERROR::passed None to add_sound_queue()")

    def add_sound_queue_rand(self, sound_id_prefix: str, sound_index_len: int):
        """
        Choose a random sound id from given prefix and index len.
        e.g. walk.wav, walk2.wav, walk3.wav
        -> sound_id_prefix = walk, sound_index_len = 3
        TODO: implement tile walk fx manager
        """
        f = lambda ind: "" if ind == 1 else str(ind)
        if sound_id_prefix and sound_index_len:
            sound_queue.append(sound_id_prefix + f(random.randint(1,sound_index_len)))
        else:
            print("SOUND::ERROR::passed None to add_sound_queue_rand()")

    def remove_bgm(self) -> None:
        if "bgm" in self.threads.keys():
            self.threads["bgm"].terminate()
        self.__current_bgm = None

    def remove_bgs(self) -> None:
        if "bgs" in self.threads.keys():
            self.threads["bgs"].terminate()
        self.__current_bgm = None

    def change_bgm(self, sound_id: str=None, force_change: bool=False, show_warning: bool=True) -> None:
        """
        Args:
            force_change:
                if True, the function will stop the current bgm and play the given sound even if they are the same.
        """
        if self.current_bgm == sound_id and not force_change:
            if show_warning:
                print(f"SOUND::WARNING::BGM Already set to {sound_id}")
            return None
        if bgm:
            print("WARNING::BGM deque should be empty.")
            bgm.clear()
        if "bgm" in self.threads.keys():
            if self.threads["bgm"]:
                if self.threads["bgm"].is_alive():
                    self.threads["bgm"].terminate() # Stopping the previous thread
        bgm.add(sound_id) # will be played in next .run()

    def change_bgs(self, sound_id: str=None, force_change: bool=False, show_warning: bool=True) -> None:
        """
        Args:
            force_change:
                if True, the function will stop the current bgm and play the given sound even if they are the same.
        """
        if self.current_bgs == sound_id and not force_change:
            if show_warning:
                print(f"SOUND::WARNING::BGS Already set to {sound_id}")
            return None
        if bgs:
            print("Warning::BGS deque should be empty.")
            bgs.clear()
        if "bgs" in self.threads.keys():
            if self.threads["bgs"]:
                if self.threads["bgs"].is_alive():
                    self.threads["bgs"].terminate() # Stopping the previous thread
        bgs.add(sound_id)  # will be played in next .run()

    def change_volume_of_data(self, data, sampwidth, volume: float=1):
        """It is highly recommended not to increase volume over 1."""
        return audioop.mul(data, sampwidth, volume * self.master_volume)

    def play_sound(self, sound_id: str=None, loop: bool=False) -> None:
        """
        Play sound of given directory.
        """
        playing = True
        while playing:
            f = wave.open(self.get_path_from_id(sound_id), "rb")
            sampwidth = f.getsampwidth()
            stream = self.p.open(format=self.p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)

            data = f.readframes(self.chunk)
            data = self.change_volume_of_data(data, sampwidth=sampwidth, volume=self.sound_db[sound_id][1])

            while data:
                stream.write(data)
                data = f.readframes(self.chunk)
                data = self.change_volume_of_data(data, sampwidth=sampwidth, volume=self.sound_db[sound_id][1])

            if not loop:
                stream.stop_stream()
                stream.close()
                playing = False



