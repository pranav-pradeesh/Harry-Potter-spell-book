"""
Harry Potter Spell Control App - Complete APK Ready Version
With Overlay Animations and Persistent Background Service
Build with: buildozer android debug
"""

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
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, Line, Rectangle
from plyer import tts, notification, brightness, vibrator
import json
import os
import threading
import random

if platform == 'android':
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android.permissions import request_permissions, Permission, check_permission
    from android.runnable import run_on_ui_thread
    from android import mActivity
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    Settings = autoclass('android.provider.Settings')
    AudioManager = autoclass('android.media.AudioManager')
    Context = autoclass('android.content.Context')
    Build = autoclass('android.os.Build')
    PythonService = autoclass('org.kivy.android.PythonService')
    WindowManager = autoclass('android.view.WindowManager')
    PixelFormat = autoclass('android.graphics.PixelFormat')
    Gravity = autoclass('android.view.Gravity')
    Color_Android = autoclass('android.graphics.Color')
    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    View = autoclass('android.view.View')
    PowerManager = autoclass('android.os.PowerManager')

# Harry Potter color scheme
HP_COLORS = {
    'gold': (0.85, 0.65, 0.13, 1),
    'maroon': (0.5, 0.0, 0.13, 1),
    'dark_red': (0.4, 0.0, 0.1, 1),
    'dark_bg': (0.1, 0.08, 0.08, 1),
    'parchment': (0.96, 0.87, 0.7, 1),
    'dark_gold': (0.6, 0.4, 0.08, 1),
    'light_gold': (1, 0.84, 0.0, 1)
}


class SpellAnimation(FloatLayout):
    """Overlay animation widget for spell casting"""
    
    def __init__(self, spell_name, icon, animation_type='lumos', **kwargs):
        super().__init__(**kwargs)
        self.spell_name = spell_name
        self.icon = icon
        self.animation_type = animation_type
        self.size_hint = (1, 1)
        
        # Semi-transparent background
        with self.canvas.before:
            Color(0, 0, 0, 0.3)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Create animation based on type
        self.create_animation()
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def create_animation(self):
        """Create spell-specific animation"""
        center_x = Window.width / 2
        center_y = Window.height / 2
        
        if self.animation_type in ['lumos', 'nox']:
            self.create_light_animation(center_x, center_y)
        elif self.animation_type in ['silencio', 'sonorus']:
            self.create_sound_wave_animation(center_x, center_y)
        elif self.animation_type == 'protego':
            self.create_shield_animation(center_x, center_y)
        elif self.animation_type == 'stupefy':
            self.create_lightning_animation(center_x, center_y)
        else:
            self.create_magic_circle_animation(center_x, center_y)
        
        # Spell name label
        self.spell_label = Label(
            text=f'{self.icon}\n{self.spell_name}',
            font_size='48sp',
            bold=True,
            color=HP_COLORS['light_gold'],
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            opacity=0
        )
        self.add_widget(self.spell_label)
        
        # Animate label
        anim = Animation(opacity=1, duration=0.3) + Animation(opacity=1, duration=1.5) + Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *x: Clock.schedule_once(lambda dt: self.parent.remove_widget(self) if self.parent else None, 0))
        anim.start(self.spell_label)
    
    def create_light_animation(self, cx, cy):
        """Lumos/Nox light burst animation"""
        for i in range(20):
            angle = random.uniform(0, 360)
            distance = random.uniform(50, 300)
            
            light = Widget()
            light.size = (15, 15)
            light.pos = (cx - 7.5, cy - 7.5)
            
            with light.canvas:
                Color(1, 1, 0.8, 0.8)
                Ellipse(pos=light.pos, size=light.size)
            
            self.add_widget(light)
            
            # Animate outward
            end_x = cx + distance * random.uniform(0.5, 1.5)
            end_y = cy + distance * random.uniform(0.5, 1.5)
            
            anim = Animation(
                x=end_x - 7.5,
                y=end_y - 7.5,
                opacity=0,
                duration=random.uniform(0.8, 1.5)
            )
            anim.start(light)
    
    def create_sound_wave_animation(self, cx, cy):
        """Sound wave ripple animation"""
        for i in range(5):
            wave = Widget()
            wave.size = (50, 50)
            wave.pos = (cx - 25, cy - 25)
            
            with wave.canvas:
                Color(0.3, 0.6, 0.9, 0.7)
                Line(circle=(cx, cy, 25), width=3)
            
            self.add_widget(wave)
            
            # Expand and fade
            anim = Animation(
                size=(400, 400),
                pos=(cx - 200, cy - 200),
                opacity=0,
                duration=1.2
            )
            Clock.schedule_once(lambda dt, w=wave: anim.start(w), i * 0.2)
    
    def create_shield_animation(self, cx, cy):
        """Protego shield animation"""
        shield = Widget()
        shield.size = (300, 300)
        shield.pos = (cx - 150, cy - 150)
        shield.opacity = 0
        
        with shield.canvas:
            Color(0.3, 0.5, 0.9, 0.6)
            Ellipse(pos=shield.pos, size=shield.size)
            Color(0.5, 0.7, 1, 0.8)
            Line(ellipse=(shield.x, shield.y, shield.width, shield.height), width=4)
        
        self.add_widget(shield)
        
        # Pulse animation
        anim = (
            Animation(opacity=1, duration=0.2) +
            Animation(size=(320, 320), pos=(cx - 160, cy - 160), duration=0.3) +
            Animation(size=(300, 300), pos=(cx - 150, cy - 150), duration=0.3) +
            Animation(opacity=0, duration=0.5)
        )
        anim.start(shield)
    
    def create_lightning_animation(self, cx, cy):
        """Stupefy lightning bolt animation"""
        for i in range(8):
            bolt = Widget()
            
            # Random lightning path
            points = [cx, cy]
            curr_x, curr_y = cx, cy
            
            for j in range(5):
                curr_x += random.uniform(-40, 40)
                curr_y += random.uniform(30, 80)
                points.extend([curr_x, curr_y])
            
            with bolt.canvas:
                Color(1, 1, 0, 0.9)
                Line(points=points, width=3)
            
            self.add_widget(bolt)
            
            # Flash and fade
            anim = Animation(opacity=0, duration=0.4)
            Clock.schedule_once(lambda dt, b=bolt: anim.start(b), i * 0.05)
    
    def create_magic_circle_animation(self, cx, cy):
        """Generic magic circle animation"""
        circle = Widget()
        circle.size = (100, 100)
        circle.pos = (cx - 50, cy - 50)
        circle.opacity = 0
        
        with circle.canvas:
            Color(*HP_COLORS['light_gold'])
            Line(circle=(cx, cy, 50), width=2)
            Line(circle=(cx, cy, 40), width=2)
            
            # Magic symbols
            for angle in range(0, 360, 45):
                x = cx + 45 * (angle % 2 * 0.5 + 0.5)
                y = cy + 45 * ((angle + 90) % 2 * 0.5 + 0.5)
                Ellipse(pos=(x - 3, y - 3), size=(6, 6))
        
        self.add_widget(circle)
        
        # Rotate and fade
        anim = (
            Animation(opacity=1, duration=0.2) +
            Animation(opacity=1, duration=1) +
            Animation(opacity=0, duration=0.3)
        )
        anim.start(circle)


class PermissionScreen(Screen):
    """Permission request screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        with layout.canvas.before:
            Color(*HP_COLORS['dark_bg'])
            self.rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_rect, size=self.update_rect)
        
        content = BoxLayout(
            orientation='vertical',
            padding=40,
            spacing=20,
            size_hint=(0.9, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Title
        title = Label(
            text='⚡ SPELLBOOK PERMISSIONS ⚡',
            font_size='28sp',
            bold=True,
            color=HP_COLORS['light_gold'],
            size_hint_y=0.15
        )
        
        # Description
        desc = Label(
            text='To cast spells even with your wand holstered,\nthis app requires the following permissions:',
            font_size='16sp',
            color=HP_COLORS['parchment'],
            size_hint_y=0.15,
            halign='center'
        )
        
        # Permissions list
        perms_text = (
            '🎤 Microphone - To hear your incantations\n\n'
            '📱 Display Over Apps - To show spell effects\n\n'
            '🔋 Battery Optimization - To keep service alive\n\n'
            '💾 Storage - To save your custom spells\n\n'
            '🔊 Audio Settings - To control volume\n\n'
            '📳 Vibration - For haptic feedback'
        )
        
        perms_label = Label(
            text=perms_text,
            font_size='14sp',
            color=HP_COLORS['parchment'],
            size_hint_y=0.5,
            halign='left',
            valign='top'
        )
        perms_label.bind(size=perms_label.setter('text_size'))
        
        # Grant button
        grant_btn = Button(
            text='⚡ GRANT PERMISSIONS ⚡',
            size_hint_y=0.15,
            background_color=HP_COLORS['dark_gold'],
            color=HP_COLORS['light_gold'],
            font_size='18sp',
            bold=True
        )
        grant_btn.bind(on_press=self.request_all_permissions)
        
        # Skip button
        skip_btn = Button(
            text='Continue without all permissions',
            size_hint_y=0.1,
            background_color=(0.3, 0.3, 0.3, 1),
            font_size='14sp'
        )
        skip_btn.bind(on_press=self.skip_permissions)
        
        content.add_widget(title)
        content.add_widget(desc)
        content.add_widget(perms_label)
        content.add_widget(grant_btn)
        content.add_widget(skip_btn)
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def update_rect(self, *args):
        self.rect.pos = self.args[0].pos
        self.rect.size = self.args[0].size
    
    def request_all_permissions(self, instance):
        """Request all necessary permissions"""
        if platform == 'android':
            # Request standard permissions
            permissions = [
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.VIBRATE,
                Permission.MODIFY_AUDIO_SETTINGS,
                Permission.FOREGROUND_SERVICE,
                Permission.ACCESS_NOTIFICATION_POLICY,
                Permission.WAKE_LOCK,
                Permission.RECEIVE_BOOT_COMPLETED
            ]
            
            request_permissions(permissions)
            
            # Request overlay permission
            Clock.schedule_once(lambda dt: self.request_overlay_permission(), 0.5)
            
            # Request battery optimization exemption
            Clock.schedule_once(lambda dt: self.request_battery_optimization(), 1.0)
        
        # Wait a bit then continue
        Clock.schedule_once(lambda dt: self.continue_to_app(), 2.0)
    
    def request_overlay_permission(self):
        """Request display over other apps permission"""
        if platform == 'android':
            try:
                if Build.VERSION.SDK_INT >= 23:
                    if not Settings.canDrawOverlays(PythonActivity.mActivity):
                        intent = Intent(
                            Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse(f"package:{PythonActivity.mActivity.getPackageName()}")
                        )
                        PythonActivity.mActivity.startActivity(intent)
                        
                        notification.notify(
                            title='Permission Required',
                            message='Please enable "Display over other apps"',
                            timeout=5
                        )
            except Exception as e:
                print(f"Overlay permission error: {e}")
    
    def request_battery_optimization(self):
        """Request to disable battery optimization"""
        if platform == 'android':
            try:
                if Build.VERSION.SDK_INT >= 23:
                    intent = Intent()
                    pm = PythonActivity.mActivity.getSystemService(Context.POWER_SERVICE)
                    package_name = PythonActivity.mActivity.getPackageName()
                    
                    if not pm.isIgnoringBatteryOptimizations(package_name):
                        intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                        intent.setData(Uri.parse(f"package:{package_name}"))
                        PythonActivity.mActivity.startActivity(intent)
                        
                        notification.notify(
                            title='Battery Optimization',
                            message='Please allow unrestricted battery usage',
                            timeout=5
                        )
            except Exception as e:
                print(f"Battery optimization error: {e}")
    
    def skip_permissions(self, instance):
        """Skip permission screen"""
        notification.notify(
            title='Warning',
            message='Some features may not work without permissions',
            timeout=3
        )
        self.continue_to_app()
    
    def continue_to_app(self):
        """Continue to main app"""
        self.manager.current = 'main'


class SpellDatabase:
    """Manages spell storage and retrieval"""
    
    def __init__(self):
        self.db_path = self.get_storage_path()
        self.spells = self.load_spells()
    
    def get_storage_path(self):
        """Get appropriate storage path for platform"""
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                path = app_storage_path()
                return os.path.join(path, 'spells.json')
            except:
                return '/data/data/org.magicspells.hpspellbook/files/spells.json'
        else:
            return 'spells.json'
    
    def load_spells(self):
        """Load spells from storage"""
        default_spells = {
            'Light Spells': {
                'Lumos': {
                    'description': 'Illuminate surroundings',
                    'action': 'brightness_max',
                    'icon': '💡',
                    'animation': 'lumos'
                },
                'Nox': {
                    'description': 'Extinguish light',
                    'action': 'brightness_min',
                    'icon': '🌑',
                    'animation': 'nox'
                }
            },
            'Sound Spells': {
                'Silencio': {
                    'description': 'Silence all sounds',
                    'action': 'mute',
                    'icon': '🔇',
                    'animation': 'silencio'
                },
                'Sonorus': {
                    'description': 'Amplify voice/sound',
                    'action': 'volume_max',
                    'icon': '🔊',
                    'animation': 'sonorus'
                }
            },
            'Utility Spells': {
                'Alohomora': {
                    'description': 'Unlock doors',
                    'action': 'open_settings',
                    'icon': '🔓',
                    'animation': 'magic'
                },
                'Accio Music': {
                    'description': 'Summon music',
                    'action': 'open_music',
                    'icon': '🎵',
                    'animation': 'magic'
                },
                'Accio': {
                    'description': 'Summon search results',
                    'action': 'web_search',
                    'icon': '🔍',
                    'animation': 'magic'
                }
            },
            'Protection Spells': {
                'Protego': {
                    'description': 'Shield charm',
                    'action': 'dnd_mode',
                    'icon': '🛡️',
                    'animation': 'protego'
                },
                'Stupefy': {
                    'description': 'Stun/Lock device',
                    'action': 'vibrate_lock',
                    'icon': '⚡',
                    'animation': 'stupefy'
                }
            },
            'Detection Spells': {
                'Homenum Revelio': {
                    'description': 'Reveal presence',
                    'action': 'show_notification',
                    'icon': '👁️',
                    'animation': 'magic'
                }
            }
        }
        
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    loaded = json.load(f)
                    # Ensure animation field exists for all spells
                    for category in loaded:
                        for spell in loaded[category]:
                            if 'animation' not in loaded[category][spell]:
                                loaded[category][spell]['animation'] = 'magic'
                    return loaded
            except:
                return default_spells
        return default_spells
    
    def save_spells(self):
        """Save spells to storage"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump(self.spells, f, indent=2)
        except Exception as e:
            print(f"Error saving spells: {e}")
    
    def add_spell(self, category, name, description, action, icon='✨', animation='magic'):
        """Add a new spell"""
        if category not in self.spells:
            self.spells[category] = {}
        
        self.spells[category][name] = {
            'description': description,
            'action': action,
            'icon': icon,
            'animation': animation
        }
        self.save_spells()
    
    def search_spells(self, query):
        """Search for spells"""
        results = {}
        query = query.lower()
        
        for category, spells in self.spells.items():
            for spell_name, spell_data in spells.items():
                if (query in spell_name.lower() or 
                    query in spell_data['description'].lower()):
                    if category not in results:
                        results[category] = {}
                    results[category][spell_name] = spell_data
        
        return results


class SpellController:
    """Executes spell actions"""
    
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
    
    def execute(self, action, spell_name='', spell_data=None):
        """Execute a spell action with animation"""
        # Show overlay animation
        if spell_data:
            self.app.show_spell_animation(
                spell_name,
                spell_data.get('icon', '✨'),
                spell_data.get('animation', 'magic')
            )
        
        # Execute action
        if action in self.actions:
            return self.actions[action](spell_name)
        return "Action not found"
    
    def brightness_max(self, spell):
        try:
            brightness.set_level(100)
            notification.notify(title=f"{spell}!", message="Maximum brightness", timeout=2)
            return f"{spell} cast successfully!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def brightness_min(self, spell):
        try:
            brightness.set_level(10)
            notification.notify(title=f"{spell}", message="Minimum brightness", timeout=2)
            return f"{spell} cast successfully!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def mute(self, spell):
        try:
            if platform == 'android':
                activity = PythonActivity.mActivity
                audio = activity.getSystemService(Context.AUDIO_SERVICE)
                audio.setRingerMode(AudioManager.RINGER_MODE_SILENT)
            notification.notify(title=f"{spell}!", message="Device muted", timeout=2)
            return f"{spell} - silence achieved!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def volume_max(self, spell):
        try:
            if platform == 'android':
                activity = PythonActivity.mActivity
                audio = activity.getSystemService(Context.AUDIO_SERVICE)
                max_vol = audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
                audio.setStreamVolume(AudioManager.STREAM_MUSIC, max_vol, AudioManager.FLAG_SHOW_UI)
            notification.notify(title=f"{spell}!", message="Volume maximized", timeout=2)
            return f"{spell} - amplified!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def open_settings(self, spell):
        try:
            if platform == 'android':
                intent = Intent(Settings.ACTION_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                PythonActivity.mActivity.startActivity(intent)
            return f"{spell} - unlocked!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def open_music(self, spell):
        try:
            if platform == 'android':
                intent = Intent(Intent.ACTION_VIEW)
                intent.setType("audio/*")
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                PythonActivity.mActivity.startActivity(intent)
            return f"{spell} - music summoned!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def web_search(self, spell):
        try:
            if platform == 'android':
                intent = Intent(Intent.ACTION_WEB_SEARCH)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                PythonActivity.mActivity.startActivity(intent)
            return f"{spell} - searching!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def dnd_mode(self, spell):
        try:
            if platform == 'android':
                intent = Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                PythonActivity.mActivity.startActivity(intent)
            notification.notify(title=f"{spell}!", message="Shield activated", timeout=2)
            return f"{spell} - protected!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def vibrate_lock(self, spell):
        try:
            vibrator.vibrate(0.5)
            notification.notify(title=f"{spell}!", message="Stunned", timeout=2)
            return f"{spell} - device stunned!"
        except Exception as e:
            return f"Failed: {str(e)}"
    
    def show_notification(self, spell):
        try:
            notification.notify(
                title=f"{spell}!",
                message="Presence revealed",
                timeout=3
            )
            return f"{spell} - presence detected!"
        except Exception as e:
            return f"Failed: {str(e)}"


class HPButton(Button):
    """Custom Harry Potter themed button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = HP_COLORS['maroon']
        self.color = HP_COLORS['gold']
        self.font_size = '16sp'
        self.bold = True


class HPLabel(Label):
    """Custom Harry Potter themed label"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = HP_COLORS['parchment']
        self.font_size = '14sp'


class MainScreen(Screen):
    """Main spell listing screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        layout.canvas.before.clear()
        
        # Background
        from kivy.graphics import Color, Rectangle
        with layout.canvas.before:
            Color(*HP_COLORS['dark_bg'])
            self.rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_rect, size=self.update_rect)
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            pos_hint={'top': 1},
            padding=[10, 10]
        )
        
        title = Label(
            text='⚡ SPELLBOOK ⚡',
            font_size='28sp',
            bold=True,
            color=HP_COLORS['light_gold'],
            size_hint=(0.6, 1)
        )
        
        search_btn = HPButton(
            text='🔍',
            size_hint=(0.2, 1)
        )
        search_btn.bind(on_press=self.goto_search)
        
        add_btn = HPButton(
            text='➕',
            size_hint=(0.2, 1),
            background_color=HP_COLORS['dark_gold']
        )
        add_btn.bind(on_press=self.goto_add_spell)
        
        header.add_widget(title)
        header.add_widget(search_btn)
        header.add_widget(add_btn)
        
        # Scroll view for spells
        scroll = ScrollView(
            size_hint=(1, 0.8),
            pos_hint={'top': 0.9}
        )
        
        self.spell_container = GridLayout(
            cols=1,
            spacing=10,
            padding=[10, 10],
            size_hint_y=None
        )
        self.spell_container.bind(minimum_height=self.spell_container.setter('height'))
        
        scroll.add_widget(self.spell_container)
        
        # Bottom controls
        bottom = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            pos_hint={'y': 0},
            padding=[10, 5],
            spacing=10
        )
        
        self.listen_btn = HPButton(
            text='🎤 Start Listening',
            background_color=HP_COLORS['dark_red']
        )
        self.listen_btn.bind(on_press=self.toggle_listening)
        
        settings_btn = HPButton(
            text='⚙️',
            size_hint=(0.2, 1)
        )
        
        bottom.add_widget(self.listen_btn)
        bottom.add_widget(settings_btn)
        
        layout.add_widget(header)
        layout.add_widget(scroll)
        layout.add_widget(bottom)
        
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def on_enter(self):
        """Refresh spell list when entering screen"""
        if self.app:
            self.refresh_spells()
    
    def refresh_spells(self):
        """Refresh the spell list"""
        self.spell_container.clear_widgets()
        
        for category, spells in self.app.spell_db.spells.items():
            # Category header
            cat_label = Label(
                text=f'\n═══ {category.upper()} ═══',
                font_size='20sp',
                bold=True,
                color=HP_COLORS['light_gold'],
                size_hint_y=None,
                height=60
            )
            self.spell_container.add_widget(cat_label)
            
            # Spells in category
            for spell_name, spell_data in spells.items():
                spell_btn = self.create_spell_button(spell_name, spell_data, category)
                self.spell_container.add_widget(spell_btn)
    
    def create_spell_button(self, name, data, category):
        """Create a spell button"""
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=80,
            padding=[5, 5]
        )
        
        # Main spell button
        spell_btn = HPButton(
            text=f"{data['icon']} {name}\n{data['description']}",
            size_hint=(0.85, 1)
        )
        spell_btn.bind(on_press=lambda x: self.cast_spell(name, data))
        
        # Delete button
        del_btn = Button(
            text='🗑️',
            size_hint=(0.15, 1),
            background_color=(0.6, 0.2, 0.2, 1)
        )
        del_btn.bind(on_press=lambda x: self.delete_spell(category, name))
        
        btn_layout.add_widget(spell_btn)
        btn_layout.add_widget(del_btn)
        
        return btn_layout
    
    def cast_spell(self, name, data):
        """Cast a spell"""
        result = self.app.controller.execute(data['action'], name, data)
        try:
            tts.speak(result)
        except:
            pass
        
        notification.notify(
            title=f"{data['icon']} {name}",
            message=result,
            timeout=3
        )
    
    def delete_spell(self, category, spell_name):
        """Delete a spell"""
        if category in self.app.spell_db.spells:
            if spell_name in self.app.spell_db.spells[category]:
                del self.app.spell_db.spells[category][spell_name]
                if not self.app.spell_db.spells[category]:
                    del self.app.spell_db.spells[category]
                self.app.spell_db.save_spells()
                self.refresh_spells()
    
    def goto_search(self, instance):
        self.manager.current = 'search'
    
    def goto_add_spell(self, instance):
        self.manager.current = 'add_spell'
    
    def toggle_listening(self, instance):
        if self.app.listening:
            self.app.stop_listening()
            self.listen_btn.text = '🎤 Start Listening'
            self.listen_btn.background_color = HP_COLORS['dark_red']
        else:
            self.app.start_listening()
            self.listen_btn.text = '🛑 Stop Listening'
            self.listen_btn.background_color = (0.2, 0.6, 0.2, 1)


class SearchScreen(Screen):
    """Search spells screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        with layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*HP_COLORS['dark_bg'])
            self.rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_rect, size=self.update_rect)
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            pos_hint={'top': 1},
            padding=[10, 10]
        )
        
        back_btn = HPButton(text='← Back', size_hint=(0.3, 1))
        back_btn.bind(on_press=self.go_back)
        
        title = Label(
            text='🔍 SEARCH SPELLS',
            font_size='24sp',
            bold=True,
            color=HP_COLORS['light_gold'],
            size_hint=(0.7, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        # Search input
        search_box = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'top': 0.9},
            padding=[10, 5],
            spacing=10
        )
        
        self.search_input = TextInput(
            hint_text='Enter spell name or description...',
            multiline=False,
            size_hint=(0.8, 1),
            background_color=HP_COLORS['parchment'],
            foreground_color=(0, 0, 0, 1)
        )
        self.search_input.bind(text=self.on_search)
        
        search_btn = HPButton(text='Search', size_hint=(0.2, 1))
        search_btn.bind(on_press=lambda x: self.on_search(None, self.search_input.text))
        
        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        
        # Results
        scroll = ScrollView(
            size_hint=(1, 0.82),
            pos_hint={'top': 0.82}
        )
        
        self.results_container = GridLayout(
            cols=1,
            spacing=10,
            padding=[10, 10],
            size_hint_y=None
        )
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        
        scroll.add_widget(self.results_container)
        
        layout.add_widget(header)
        layout.add_widget(search_box)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def on_search(self, instance, text):
        """Search for spells"""
        self.results_container.clear_widgets()
        
        if not text or len(text) < 2:
            return
        
        results = self.app.spell_db.search_spells(text)
        
        if not results:
            no_result = HPLabel(
                text='No spells found',
                size_hint_y=None,
                height=50
            )
            self.results_container.add_widget(no_result)
            return
        
        for category, spells in results.items():
            cat_label = Label(
                text=f'\n{category}',
                font_size='18sp',
                bold=True,
                color=HP_COLORS['gold'],
                size_hint_y=None,
                height=50
            )
            self.results_container.add_widget(cat_label)
            
            for spell_name, spell_data in spells.items():
                spell_btn = HPButton(
                    text=f"{spell_data['icon']} {spell_name}\n{spell_data['description']}",
                    size_hint_y=None,
                    height=70
                )
                spell_btn.bind(on_press=lambda x, n=spell_name, d=spell_data: self.cast_spell(n, d))
                self.results_container.add_widget(spell_btn)
    
    def cast_spell(self, name, data):
        result = self.app.controller.execute(data['action'], name, data)
        try:
            tts.speak(result)
        except:
            pass
    
    def go_back(self, instance):
        self.manager.current = 'main'


class AddSpellScreen(Screen):
    """Add new spell screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        with layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*HP_COLORS['dark_bg'])
            self.rect = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self.update_rect, size=self.update_rect)
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            pos_hint={'top': 1},
            padding=[10, 10]
        )
        
        back_btn = HPButton(text='← Back', size_hint=(0.3, 1))
        back_btn.bind(on_press=self.go_back)
        
        title = Label(
            text='✨ CREATE SPELL',
            font_size='24sp',
            bold=True,
            color=HP_COLORS['light_gold'],
            size_hint=(0.7, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(title)
        
        # Form
        form_scroll = ScrollView(
            size_hint=(1, 0.8),
            pos_hint={'top': 0.9}
        )
        
        form = GridLayout(
            cols=1,
            spacing=15,
            padding=[20, 20],
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter('height'))
        
        # Category
        form.add_widget(HPLabel(text='Category:', size_hint_y=None, height=30))
        self.category_spinner = Spinner(
            text='Select Category',
            values=['Light Spells', 'Sound Spells', 'Utility Spells', 
                    'Protection Spells', 'Detection Spells', 'Custom'],
            size_hint_y=None,
            height=44,
            background_color=HP_COLORS['parchment'],
            color=(0, 0, 0, 1)
        )
        form.add_widget(self.category_spinner)
        
        # Custom category input
        self.custom_category = TextInput(
            hint_text='Enter custom category name...',
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=HP_COLORS['parchment'],
            foreground_color=(0, 0, 0, 1)
        )
        form.add_widget(self.custom_category)
        
        # Spell name
        form.add_widget(HPLabel(text='Spell Name:', size_hint_y=None, height=30))
        self.spell_name = TextInput(
            hint_text='e.g., Expecto Patronum',
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=HP_COLORS['parchment'],
            foreground_color=(0, 0, 0, 1)
        )
        form.add_widget(self.spell_name)
        
        # Description
        form.add_widget(HPLabel(text='Description:', size_hint_y=None, height=30))
        self.description = TextInput(
            hint_text='What does this spell do?',
            multiline=True,
            size_hint_y=None,
            height=80,
            background_color=HP_COLORS['parchment'],
            foreground_color=(0, 0, 0, 1)
        )
        form.add_widget(self.description)
        
        # Action
        form.add_widget(HPLabel(text='Action:', size_hint_y=None, height=30))
        self.action_spinner = Spinner(
            text='Select Action',
            values=['brightness_max', 'brightness_min', 'mute', 'volume_max',
                    'open_settings', 'open_music', 'web_search', 'dnd_mode',
                    'vibrate_lock', 'show_notification'],
            size_hint_y=None,
            height=44,
            background_color=HP_COLORS['parchment'],
            color=(0, 0, 0, 1)
        )
        form.add_widget(self.action_spinner)
        
        # Animation type
        form.add_widget(HPLabel(text='Animation:', size_hint_y=None, height=30))
        self.animation_spinner = Spinner(
            text='Select Animation',
            values=['magic', 'lumos', 'nox', 'silencio', 'sonorus', 'protego', 'stupefy'],
            size_hint_y=None,
            height=44,
            background_color=HP_COLORS['parchment'],
            color=(0, 0, 0, 1)
        )
        form.add_widget(self.animation_spinner)
        
        # Icon
        form.add_widget(HPLabel(text='Icon (emoji):', size_hint_y=None, height=30))
        self.icon = TextInput(
            hint_text='✨',
            multiline=False,
            size_hint_y=None,
            height=44,
            background_color=HP_COLORS['parchment'],
            foreground_color=(0, 0, 0, 1)
        )
        form.add_widget(self.icon)
        
        # Save button
        save_btn = HPButton(
            text='⚡ Create Spell ⚡',
            size_hint_y=None,
            height=60,
            background_color=HP_COLORS['dark_gold']
        )
        save_btn.bind(on_press=self.save_spell)
        form.add_widget(save_btn)
        
        form_scroll.add_widget(form)
        
        layout.add_widget(header)
        layout.add_widget(form_scroll)
        
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def save_spell(self, instance):
        """Save the new spell"""
        category = self.category_spinner.text
        if category == 'Custom' and self.custom_category.text:
            category = self.custom_category.text
        elif category == 'Select Category':
            self.show_error('Please select a category')
            return
        
        name = self.spell_name.text.strip()
        if not name:
            self.show_error('Please enter a spell name')
            return
        
        description = self.description.text.strip()
        if not description:
            self.show_error('Please enter a description')
            return
        
        action = self.action_spinner.text
        if action == 'Select Action':
            self.show_error('Please select an action')
            return
        
        animation = self.animation_spinner.text
        if animation == 'Select Animation':
            animation = 'magic'
        
        icon = self.icon.text.strip() or '✨'
        
        # Save spell
        self.app.spell_db.add_spell(category, name, description, action, icon, animation)
        
        # Show success
        notification.notify(
            title='Spell Created!',
            message=f'{name} has been added to your spellbook',
            timeout=3
        )
        
        # Clear form
        self.spell_name.text = ''
        self.description.text = ''
        self.icon.text = ''
        
        # Go back
        self.manager.current = 'main'
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'main'


class SpellbookApp(App):
    """Main application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spell_db = SpellDatabase()
        self.controller = SpellController(self)
        self.listening = False
        self.listen_thread = None
        self.overlay_layer = None
    
    def build(self):
        Window.clearcolor = HP_COLORS['dark_bg']
        
        # Main container with overlay support
        self.root_layout = FloatLayout()
        
        # Screen manager
        sm = ScreenManager(transition=FadeTransition())
        
        # Create screens
        perm = PermissionScreen(name='permissions')
        perm.app = self
        
        main = MainScreen(name='main')
        main.app = self
        
        search = SearchScreen(name='search')
        search.app = self
        
        add_spell = AddSpellScreen(name='add_spell')
        add_spell.app = self
        
        sm.add_widget(perm)
        sm.add_widget(main)
        sm.add_widget(search)
        sm.add_widget(add_spell)
        
        self.root_layout.add_widget(sm)
        
        return self.root_layout
    
    def on_start(self):
        """Start on permission screen"""
        # Check if we need to show permissions
        if platform == 'android':
            # Always show permission screen on first run
            self.root.children[0].current = 'permissions'
        else:
            self.root.children[0].current = 'main'
        
        # Start background service
        Clock.schedule_once(lambda dt: self.start_background_service(), 2)
    
    def start_background_service(self):
        """Start background service for voice recognition"""
        if platform == 'android':
            try:
                from android import mActivity
                from jnius import autoclass
                
                service = autoclass('org.kivy.android.PythonService')
                mActivity.start_service(
                    title='Spellbook Service',
                    description='Listening for magical commands',
                    arg=''
                )
                
                notification.notify(
                    title='⚡ Spellbook Active',
                    message='Background service started',
                    timeout=3
                )
            except Exception as e:
                print(f"Could not start background service: {e}")
    
    def show_spell_animation(self, spell_name, icon, animation_type):
        """Show overlay animation for spell"""
        try:
            # Create animation overlay
            anim = SpellAnimation(spell_name, icon, animation_type)
            self.root_layout.add_widget(anim)
            
            # Remove after animation completes
            Clock.schedule_once(lambda dt: self.root_layout.remove_widget(anim), 2.5)
        except Exception as e:
            print(f"Animation error: {e}")
    
    def start_listening(self):
        """Start voice recognition"""
        self.listening = True
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()
        
        notification.notify(
            title='🎤 Listening',
            message='Say a spell name to cast it',
            timeout=2
        )
    
    def stop_listening(self):
        """Stop voice recognition"""
        self.listening = False
        
        notification.notify(
            title='🛑 Stopped',
            message='Voice recognition disabled',
            timeout=2
        )
    
    def listen_loop(self):
        """Continuous voice recognition loop"""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 4000
            recognizer.dynamic_energy_threshold = True
            
            while self.listening:
                try:
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        
                        try:
                            text = recognizer.recognize_google(audio).lower()
                            Clock.schedule_once(lambda dt: self.process_voice_command(text), 0)
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError:
                            pass
                except Exception as e:
                    print(f"Listening error: {e}")
                    if self.listening:
                        import time
                        time.sleep(1)
        except ImportError:
            Clock.schedule_once(
                lambda dt: notification.notify(
                    title='Error',
                    message='SpeechRecognition not installed',
                    timeout=3
                ),
                0
            )
    
    def process_voice_command(self, text):
        """Process recognized voice command"""
        # Search for matching spell
        matched = False
        
        for category, spells in self.spell_db.spells.items():
            for spell_name, spell_data in spells.items():
                if spell_name.lower() in text:
                    result = self.controller.execute(spell_data['action'], spell_name, spell_data)
                    
                    notification.notify(
                        title=f"{spell_data['icon']} {spell_name}",
                        message=result,
                        timeout=3
                    )
                    
                    try:
                        tts.speak(f"{spell_name}. {result}")
                    except:
                        pass
                    
                    matched = True
                    break
            
            if matched:
                break
        
        if not matched:
            notification.notify(
                title='Unknown Spell',
                message=f'"{text}" not found in spellbook',
                timeout=2
            )


if __name__ == '__main__':
    SpellbookApp().run()
