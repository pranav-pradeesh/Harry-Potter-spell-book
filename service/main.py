"""
Background Service for Harry Potter Spellbook
This runs independently and PERSISTS even when app is removed from recents
Save this as: service/main.py
"""

import time
import json
import os
from jnius import autoclass, cast
from plyer import notification, brightness, vibrator

# Android services
PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
Intent = autoclass('android.content.Intent')
PendingIntent = autoclass('android.app.PendingIntent')
AndroidString = autoclass('java.lang.String')
NotificationBuilder = autoclass('android.app.Notification$Builder')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
AudioManager = autoclass('android.media.AudioManager')
Settings = autoclass('android.provider.Settings')
Uri = autoclass('android.net.Uri')
Build = autoclass('android.os.Build')
PowerManager = autoclass('android.os.PowerManager')
WakeLock = autoclass('android.os.PowerManager$WakeLock')


class PersistentVoiceService:
    """Persistent background service that survives app closure"""
    
    def __init__(self):
        self.running = True
        self.service = PythonService.mService
        self.wake_lock = None
        
        # Set service to restart if killed
        self.service.setAutoRestartService(True)
        
        # Acquire wake lock to keep service alive
        self.acquire_wake_lock()
        
        # Setup as foreground service (required for Android 8+)
        self.setup_foreground_service()
    
    def acquire_wake_lock(self):
        """Acquire partial wake lock to keep service running"""
        try:
            pm = self.service.getSystemService(Context.POWER_SERVICE)
            self.wake_lock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "Spellbook::VoiceRecognition"
            )
            self.wake_lock.acquire()
            print("Wake lock acquired")
        except Exception as e:
            print(f"Wake lock error: {e}")
    
    def setup_foreground_service(self):
        """Setup as foreground service with persistent notification"""
        try:
            channel_id = "spellbook_persistent"
            
            # Create notification channel (Android 8.0+)
            if Build.VERSION.SDK_INT >= 26:
                channel = NotificationChannel(
                    channel_id,
                    AndroidString("Spellbook Voice Service"),
                    NotificationManager.IMPORTANCE_LOW
                )
                channel.setDescription(AndroidString("Listening for magical commands"))
                
                notification_service = self.service.getSystemService(
                    Context.NOTIFICATION_SERVICE
                )
                notification_service.createNotificationChannel(channel)
            
            # Create intent to open app when notification is tapped
            app_context = self.service.getApplication().getApplicationContext()
            package_name = app_context.getPackageName()
            
            launch_intent = app_context.getPackageManager().getLaunchIntentForPackage(package_name)
            if launch_intent:
                launch_intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)
                
                pending_intent = PendingIntent.getActivity(
                    app_context,
                    0,
                    launch_intent,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
                )
            else:
                pending_intent = None
            
            # Create notification
            notification_builder = NotificationBuilder(app_context, channel_id)
            notification_builder.setContentTitle(AndroidString("⚡ Spellbook Active"))
            notification_builder.setContentText(AndroidString("Listening for spells... Say 'Lumos', 'Silencio', etc."))
            notification_builder.setSmallIcon(app_context.getApplicationInfo().icon)
            notification_builder.setOngoing(True)  # Make notification persistent
            notification_builder.setPriority(NotificationBuilder.PRIORITY_LOW)
            
            if pending_intent:
                notification_builder.setContentIntent(pending_intent)
            
            # Build notification
            notification_obj = notification_builder.build()
            
            # Start as foreground service (ID must be > 0)
            self.service.startForeground(1001, notification_obj)
            
            print("Foreground service started")
            
        except Exception as e:
            print(f"Foreground service setup error: {e}")
    
    def load_spell_database(self):
        """Load spell database from storage"""
        try:
            # Try multiple storage locations
            possible_paths = [
                '/data/data/org.magicspells.hpspellbook/files/spells.json',
                '/storage/emulated/0/Android/data/org.magicspells.hpspellbook/files/spells.json',
                '/sdcard/spellbook/spells.json'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return json.load(f)
            
            # Return default spells if file not found
            return self.get_default_spells()
            
        except Exception as e:
            print(f"Error loading spells: {e}")
            return self.get_default_spells()
    
    def get_default_spells(self):
        """Return default spell database"""
        return {
            'Light Spells': {
                'Lumos': {'action': 'brightness_max', 'icon': '💡'},
                'Nox': {'action': 'brightness_min', 'icon': '🌑'}
            },
            'Sound Spells': {
                'Silencio': {'action': 'mute', 'icon': '🔇'},
                'Sonorus': {'action': 'volume_max', 'icon': '🔊'}
            },
            'Utility Spells': {
                'Alohomora': {'action': 'open_settings', 'icon': '🔓'},
                'Accio Music': {'action': 'open_music', 'icon': '🎵'},
                'Accio': {'action': 'web_search', 'icon': '🔍'}
            },
            'Protection Spells': {
                'Protego': {'action': 'dnd_mode', 'icon': '🛡️'},
                'Stupefy': {'action': 'vibrate_lock', 'icon': '⚡'}
            },
            'Detection Spells': {
                'Homenum Revelio': {'action': 'show_notification', 'icon': '👁️'}
            }
        }
    
    def run(self):
        """Main service loop - runs continuously"""
        print("=== Spellbook Service Starting ===")
        
        # Load spell database
        spells_db = self.load_spell_database()
        print(f"Loaded {len(spells_db)} spell categories")
        
        # Show startup notification
        notification.notify(
            title="⚡ Spellbook Service Active",
            message="Voice recognition running in background",
            timeout=3
        )
        
        # Try to initialize speech recognition
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 3000
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8
            
            print("Speech recognition initialized")
            
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while self.running:
                try:
                    with sr.Microphone() as source:
                        # Adjust for ambient noise
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        
                        # Listen for audio
                        audio = recognizer.listen(
                            source,
                            timeout=10,
                            phrase_time_limit=5
                        )
                        
                        try:
                            # Recognize speech
                            text = recognizer.recognize_google(audio).lower()
                            print(f"Recognized: {text}")
                            
                            # Reset error counter on success
                            consecutive_errors = 0
                            
                            # Process spell
                            self.process_spell(text, spells_db)
                            
                        except sr.UnknownValueError:
                            # Speech was unintelligible - this is normal
                            pass
                        
                        except sr.RequestError as e:
                            consecutive_errors += 1
                            print(f"Recognition error: {e}")
                            
                            if consecutive_errors >= max_consecutive_errors:
                                notification.notify(
                                    title="Service Warning",
                                    message="Speech recognition having issues. Check internet connection.",
                                    timeout=5
                                )
                                consecutive_errors = 0
                                time.sleep(5)
                
                except Exception as e:
                    consecutive_errors += 1
                    print(f"Service error: {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        # Too many errors, wait longer
                        time.sleep(10)
                        consecutive_errors = 0
                    else:
                        time.sleep(2)
        
        except ImportError:
            # Speech recognition not available
            print("SpeechRecognition not installed")
            notification.notify(
                title="Service Error",
                message="Speech recognition library not available",
                timeout=5
            )
            
            # Keep service alive anyway
            while self.running:
                time.sleep(30)
        
        finally:
            # Release wake lock on exit
            if self.wake_lock and self.wake_lock.isHeld():
                self.wake_lock.release()
    
    def process_spell(self, text, spells_db):
        """Process recognized spell command"""
        matched = False
        
        # Search for matching spell
        for category, spells in spells_db.items():
            for spell_name, spell_data in spells.items():
                if spell_name.lower() in text:
                    print(f"Casting spell: {spell_name}")
                    self.execute_spell(spell_name, spell_data)
                    matched = True
                    break
            
            if matched:
                break
        
        if not matched:
            print(f"Unknown spell: {text}")
    
    def execute_spell(self, spell_name, spell_data):
        """Execute spell action"""
        action = spell_data.get('action', '')
        icon = spell_data.get('icon', '✨')
        
        try:
            if action == 'brightness_max':
                brightness.set_level(100)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Maximum brightness activated",
                    timeout=2
                )
            
            elif action == 'brightness_min':
                brightness.set_level(10)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Minimum brightness activated",
                    timeout=2
                )
            
            elif action == 'mute':
                audio = self.service.getSystemService(Context.AUDIO_SERVICE)
                audio.setRingerMode(AudioManager.RINGER_MODE_SILENT)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Device muted",
                    timeout=2
                )
            
            elif action == 'volume_max':
                audio = self.service.getSystemService(Context.AUDIO_SERVICE)
                max_vol = audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
                audio.setStreamVolume(
                    AudioManager.STREAM_MUSIC,
                    max_vol,
                    AudioManager.FLAG_SHOW_UI
                )
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Volume maximized",
                    timeout=2
                )
            
            elif action == 'vibrate_lock':
                vibrator.vibrate(0.5)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Device stunned",
                    timeout=2
                )
            
            elif action == 'show_notification':
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Presence revealed",
                    timeout=3
                )
            
            elif action == 'open_settings':
                intent = Intent(Settings.ACTION_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                self.service.startActivity(intent)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Opening settings",
                    timeout=2
                )
            
            elif action == 'open_music':
                intent = Intent(Intent.ACTION_VIEW)
                intent.setType("audio/*")
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                self.service.startActivity(intent)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Music summoned",
                    timeout=2
                )
            
            elif action == 'web_search':
                intent = Intent(Intent.ACTION_WEB_SEARCH)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                self.service.startActivity(intent)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Searching the web",
                    timeout=2
                )
            
            elif action == 'dnd_mode':
                intent = Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS)
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                self.service.startActivity(intent)
                notification.notify(
                    title=f"{icon} {spell_name}",
                    message="Shield charm activated",
                    timeout=2
                )
            
            print(f"Spell {spell_name} executed successfully")
            
        except Exception as e:
            print(f"Error executing spell {spell_name}: {e}")
            notification.notify(
                title="Spell Failed",
                message=f"Could not cast {spell_name}",
                timeout=2
            )
    
    def stop(self):
        """Stop the service"""
        self.running = False
        
        # Release wake lock
        if self.wake_lock and self.wake_lock.isHeld():
            self.wake_lock.release()
        
        # Stop foreground service
        try:
            self.service.stopForeground(True)
        except:
            pass


# Service entry point
if __name__ == '__main__':
    print("=== Initializing Spellbook Service ===")
    service = PersistentVoiceService()
    
    try:
        service.run()
    except KeyboardInterrupt:
        print("Service stopped by user")
        service.stop()
    except Exception as e:
        print(f"Service crashed: {e}")
        # Try to restart
        time.sleep(5)
        service = PersistentVoiceService()
        service.run()

