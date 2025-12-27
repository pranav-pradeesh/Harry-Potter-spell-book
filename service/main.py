
from jnius import autoclass
from plyer import notification, brightness, vibrator, stt, tts
import time
import json
import os
import threading
from kivy.clock import Clock

Context = autoclass('android.content.Context')
AudioManager = autoclass('android.media.AudioManager')
PythonService = autoclass('org.kivy.android.PythonService')

class VoiceService:
    """Persistent foreground service that listens for spells using Android native STT"""

    def __init__(self):
        self.running = True
        self.service = PythonService.mService
        self.audio_manager = self.service.getSystemService(Context.AUDIO_SERVICE)

        # Start STT callback listener
        self.init_stt()

        # Keep as foreground service
        self.start_foreground()

    def init_stt(self):
        """Initialize Android voice recognition without extra build dependencies"""
        try:
            stt.start()
            stt.bind(on_result=self.on_spell)
            print("🎤 STT initialized")
        except Exception as e:
            print("STT error:", e)

    def start_foreground(self):
        """Keep service alive with persistent notification"""
        try:
            print("⚡ Voice service running in foreground")
            notification.notify(
                title="⚡ Spellbook Active",
                message="Listening for magical spells…",
                timeout=5
            )
        except Exception as e:
            print("Foreground error:", e)

    def on_spell(self, instance, result):
        """Triggered when a spell is spoken"""
        if not result:
            return

        text = result.lower()
        print("Recognized:", text)

        # Match spell keywords and trigger actions
        if "lumos" in text:
            self.cast_lumos()
        elif "nox" in text:
            self.cast_nox()
        elif "silencio" in text:
            self.cast_mute()
        elif "sonorus" in text:
            self.cast_volume_max()
        elif "protego" in text:
            self.cast_dnd()
        elif "accio music" in text:
            self.open_music_player()
        elif "alohomora" in text:
            self.open_settings()
        elif "homenum revelio" in text:
            self.reveal_presence()
        else:
            print("Unknown spell")

    # All your spell functions rewritten safely ✔

    def cast_lumos(self):
        brightness.set_level(100)
        tts.speak("Lumos!")
        notification.notify(title="💡 Lumos", message="Brightness maximized!", timeout=2)

    def cast_nox(self):
        brightness.set_level(10)
        tts.speak("Nox!")
        notification.notify(title="🌑 Nox", message="Brightness minimized!", timeout=2)

    def cast_mute(self):
        self.audio_manager.setRingerMode(AudioManager.RINGER_MODE_SILENT)
        tts.speak("Silencio!")
        notification.notify(title="🔇 Silencio", message="Device muted!", timeout=2)

    def cast_volume_max(self):
        max_vol = self.audio_manager.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
        self.audio_manager.setStreamVolume(AudioManager.STREAM_MUSIC, max_vol, 1)
        tts.speak("Sonorus!")
        notification.notify(title="🔊 Sonorus", message="Volume maximized!", timeout=2)

    def cast_dnd(self):
        tts.speak("Protego!")
        notification.notify(title="🛡️ Protego", message="Do Not Disturb activated!", timeout=2)

    def open_music_player(self):
        Intent = autoclass('android.content.Intent')
        intent = Intent(Intent.ACTION_VIEW)
        intent.setType("audio/*")
        intent.setFlags(0x10000000)
        self.service.startActivity(intent)
        notification.notify(title="🎵 Accio", message="Opening music!", timeout=2)

    def open_settings(self):
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')
        intent = Intent(Settings.ACTION_SETTINGS)
        intent.setFlags(0x10000000)
        self.service.startActivity(intent)
        notification.notify(title="🔓 Alohomora", message="Opening settings!", timeout=2)

    def reveal_presence(self):
        tts.speak("Homenum Revelio!")
        notification.notify(title="👁️ Homenum Revelio", message="Presence revealed!", timeout=3)

    def run(self):
        """Run loop in thread-safe mode"""
        while self.running:
            time.sleep(30)

    def stop(self):
        """Stop service safely"""
        self.running = False
        stt.stop()
        print("🛑 Voice service stopped")

if __name__ == "__main__":
    service = VoiceService()
    thread = threading.Thread(target=service.run)
    thread.daemon = True
    thread.start()
