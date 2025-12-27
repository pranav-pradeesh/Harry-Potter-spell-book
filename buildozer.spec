[app]
title = Harry Potter Spellbook
package.name = hpspellbook
package.domain = org.magicspells
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,json
version = 1.0.0

# ✅ Only Android-compatible dependencies
requirements = python3,kivy==2.3.0,plyer,pyjnius

orientation = portrait
fullscreen = 0

# Permissions kept as you need background/overlay services ✔
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE,MODIFY_AUDIO_SETTINGS,FOREGROUND_SERVICE,ACCESS_NOTIFICATION_POLICY,WRITE_SETTINGS,SYSTEM_ALERT_WINDOW,WAKE_LOCK,RECEIVE_BOOT_COMPLETED,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS

services = VoiceService:service/main.py:foreground

android.api = 33
android.minapi = 21
android.ndk = 25b
android.private_storage = True
android.accept_sdk_license = True

android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.release_artifact = apk
android.debug_artifact = apk

[app:service]
title = Voice Recognition Service
author = Magic Spells
description = Background voice recognition for spell casting

[buildozer]
log_level = 2
warn_on_root = 1
