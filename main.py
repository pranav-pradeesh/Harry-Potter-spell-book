
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, Line, Rectangle
from plyer import tts, notification, brightness, vibrator, stt
import json
import os
import threading
import random

HP_COLORS = {
    'gold': (0.85, 0.65, 0.13, 1),
    'maroon': (0.5, 0.0, 0.13, 1),
    'dark_red': (0.4, 0.0, 0.1, 1),
    'dark_bg': (0.1, 0.08, 0.08, 1),
    'parchment': (0.96, 0.87, 0.7, 1),
    'light_gold': (1, 0.84, 0.0, 1)
}

class SpellAnimation(FloatLayout):
    def __init__(self, spell_name, icon, animation_type='magic', **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        with self.canvas.before:
            Color(0, 0, 0, 0.3)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
        self.create_animation(spell_name, icon, animation_type)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def create_animation(self, spell_name, icon, animation_type):
        label = Label(
            text=f"{icon}\n{spell_name}",
            font_size='48sp',
            bold=True,
            color=HP_COLORS['light_gold'],
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            opacity=0
        )
        self.add_widget(label)
        anim = Animation(opacity=1, duration=0.3) + Animation(opacity=1, duration=1.5) + Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *x: Clock.schedule_once(lambda dt: self.parent.remove_widget(self) if self.parent else None, 0))
        anim.start(label)

class SpellDatabase:
    def __init__(self):
        self.db_path = 'spells.json'
        self.spells = self.load_spells()

    def load_spells(self):
        default_spells = {
            'Light Spells': {
                'Lumos': {'description': 'Illuminate surroundings', 'action': 'brightness_max', 'icon': '💡', 'animation': 'lumos'},
                'Nox': {'description': 'Extinguish light', 'action': 'brightness_min', 'icon': '🌑', 'animation': 'nox'}
            },
            'Sound Spells': {
                'Silencio': {'description': 'Silence all sounds', 'action': 'mute', 'icon': '🔇', 'animation': 'silencio'},
                'Sonorus': {'description': 'Amplify sound', 'action': 'volume_max', 'icon': '🔊', 'animation': 'sonorus'}
            },
            'Utility Spells': {
                'Alohomora': {'description': 'Open device settings', 'action': 'open_settings', 'icon': '🔓', 'animation': 'magic'},
                'Accio Music': {'description': 'Open music player', 'action': 'open_music', 'icon': '🎵', 'animation': 'magic'},
                'Accio': {'description': 'Search the web', 'action': 'web_search', 'icon': '🔍', 'animation': 'magic'}
            },
            'Protection Spells': {
                'Protego': {'description': 'Do not disturb mode', 'action': 'dnd_mode', 'icon': '🛡️', 'animation': 'protego'},
                'Stupefy': {'description': 'Stun device', 'action': 'vibrate_lock', 'icon': '⚡', 'animation': 'stupefy'}
            },
            'Detection Spells': {
                'Homenum Revelio': {'description': 'Reveal presence', 'action': 'show_notification', 'icon': '👁️', 'animation': 'magic'}
            }
        }
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except:
                return default_spells
        return default_spells

    def save_spells(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.spells, f, indent=2)

    def add_spell(self, category, name, description, action, icon='✨', animation='magic'):
        if category not in self.spells:
            self.spells[category] = {}
        self.spells[category][name] = {'description': description, 'action': action, 'icon': icon, 'animation': animation}
        self.save_spells()

class SpellController:
    def __init__(self, app):
        self.app = app
        self.actions = {
            'brightness_max': self.brightness_max,
            'brightness_min': self.brightness_min,
            'mute': self.mute,
            'volume_max': self.volume_max,
            'open_settings': self.open_settings,
            'open_music': self.open_music,
            'web_search': self.web_search,
            'dnd_mode': self.dnd_mode,
            'vibrate_lock': self.vibrate_lock,
            'show_notification': self.show_notification
        }

    def execute(self, action, spell_name, spell_data):
        self.app.root.add_widget(SpellAnimation(spell_name, spell_data.get('icon', '✨'), spell_data.get('animation', 'magic')))
        if action in self.actions:
            return self.actions[action](spell_name)
        return "Spell failed!"

    def brightness_max(self, spell):
        brightness.set_level(100)
        notification.notify(title=f"{spell} 💡", message="Brightness max!", timeout=2)
        tts.speak("Lumos!")
        return f"{spell} cast successfully!"

    def brightness_min(self, spell):
        brightness.set_level(10)
        notification.notify(title=f"{spell} 🌑", message="Brightness low!", timeout=2)
        tts.speak("Nox!")
        return f"{spell} cast successfully!"

    def mute(self, spell):
        notification.notify(title=f"{spell} 🔇", message="Device muted!", timeout=2)
        tts.speak("Silencio!")
        return f"{spell} cast successfully!"

    def volume_max(self, spell):
        notification.notify(title=f"{spell} 🔊", message="Volume max!", timeout=2)
        tts.speak("Sonorus!")
        return f"{spell} cast successfully!"

    def open_settings(self, spell):
        notification.notify(title=f"{spell} 🔓", message="Opening settings!", timeout=2)
        return f"{spell} cast successfully!"

    def open_music(self, spell):
        notification.notify(title=f"{spell} 🎵", message="Opening music player!", timeout=2)
        tts.speak("Accio Music!")
        return f"{spell} cast successfully!"

    def web_search(self, spell):
        notification.notify(title=f"{spell} 🔍", message="Searching web!", timeout=2)
        return f"{spell} cast successfully!"

    def vibrate_lock(self, spell):
        vibrator.vibrate(0.7)
        notification.notify(title=f"{spell} ⚡", message="Vibration activated!", timeout=2)
        tts.speak("Stupefy!")
        return f"{spell} stunned!"

    def show_notification(self, spell):
        notification.notify(title=f"{spell} 👁️", message="Presence revealed!", timeout=2)
        tts.speak("Homenum Revelio!")
        return f"{spell} detected!"

class PermissionScreen(Screen):
    def on_enter(self):
        if platform == 'android':
            stt.start()
            notification.notify(title="🎤 Voice ready", message="You can cast spells!", timeout=2)

class MainScreen(Screen):
    pass

class HarrySpellbook(App):
    def build(self):
        self.root = FloatLayout()
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(PermissionScreen(name='permissions'))
        sm.add_widget(MainScreen(name='main'))
        self.root.add_widget(sm)
        return self.root

    def start_listening(self):
        stt.start()
        stt.bind(on_result=self.process_voice_command)

    def stop_listening(self):
        stt.stop()

    def process_voice_command(self, instance, result):
        if not result: return
        text = result.lower()
        for category, spells in self.spell_db.spells.items():
            for spell_name, spell_data in spells.items():
                if spell_name.lower() in text:
                    res = self.controller.execute(spell_data['action'], spell_name, spell_data)
                    tts.speak(res)
                    return
        notification.notify(title="❗ Unknown Spell", message="Spell not found!", timeout=2)

if __name__ == '__main__':
    HarrySpellbook().run()
