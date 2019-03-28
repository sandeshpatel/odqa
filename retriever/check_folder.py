import pyinotify

wm = pyinotify.WatchManager()

mask =pyinotify.IN_CREATE  # watched events

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print ("Creating:", event.pathname)

print("startingloop")
handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch('questions', mask, rec=True)
notifier.loop()