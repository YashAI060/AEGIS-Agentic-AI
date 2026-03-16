import psutil
import time
import datetime
import threading

class SystemMonitor(threading.Thread):
    def __init__(self, speak_callback, is_busy_callback):
        super().__init__()
        self.speak = speak_callback
        self.is_busy = is_busy_callback
        self.daemon = True # When main program closes, this thread will also die

        # Trackers (So AEGIS doesn't annoy by speaking repeatedly)
        self.battery_warned_low = False
        self.battery_warned_full = False
        self.cpu_high_count = 0
        self.start_time = time.time()
        self.late_night_warned = False

    def run(self):
        """This function will always run in the background"""
        while True:
            time.sleep(60) # Checks every 60 seconds

            if self.is_busy():
                continue # If you are talking to AEGIS, it will wait

            self.check_battery()
            self.check_cpu()
            self.check_screen_time()
            self.check_time()

    def check_battery(self):
        battery = psutil.sensors_battery()
        if not battery: return

        percent = battery.percent
        plugged = battery.power_plugged

        # 1. Low Battery (< 20%)
        if percent <= 20 and not plugged and not self.battery_warned_low:
            self.speak(f"Sir, battery is critically low at {percent} percent. Please plug in the charger.")
            self.battery_warned_low = True
            self.battery_warned_full = False

        # 2. Full Battery (100%)
        elif percent == 100 and plugged and not self.battery_warned_full:
            self.speak("Sir, battery is fully charged. You can unplug the charger to prevent battery degradation.")
            self.battery_warned_full = True
            self.battery_warned_low = False

        # Reset warnings if battery is in normal range
        elif 20 < percent < 100:
            self.battery_warned_low = False
            self.battery_warned_full = False

    def check_cpu(self):
        usage = psutil.cpu_percent(interval=1)
        if usage > 90:
            self.cpu_high_count += 1
        else:
            self.cpu_high_count = 0

        # If CPU is above 90% for 2 minutes consecutively
        if self.cpu_high_count >= 2:
            self.speak("Sir, CPU usage has been critically high for 2 minutes. Should I close heavy background applications?")
            self.cpu_high_count = -10 # Will not annoy again for the next 10 minutes

    def check_screen_time(self):
        elapsed_minutes = (time.time() - self.start_time) / 60
        # If 2 hours (120 mins) have passed
        if elapsed_minutes >= 120:
            self.speak("Sir, you have been working continuously for 2 hours. Please take a 5-minute break and drink some water.")
            self.start_time = time.time() # Timer reset

    def check_time(self):
        now = datetime.datetime.now()
        # At 2 AM (Will speak once between 2:00 AM and 2:05 AM)
        if now.hour == 2 and now.minute < 5 and not self.late_night_warned:
            self.speak("Sir, it is 2 AM. I suggest you wrap up your work and get some sleep.")
            self.late_night_warned = True
        elif now.hour == 8: # Will reset tracker at 8 AM
            self.late_night_warned = False