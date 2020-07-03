import os
from watchdog.events import PatternMatchingEventHandler
import queue
import time
import threading
import detect
from tkinter import *

exitFlag = 0
threadList = ["One"]
queueLock = threading.Lock()
workQueue = queue.Queue(50)
threads = []
queueCheck = []
threadID = 1
video_extensions = [".mp4", ".mov", ".avi", ".flv", ".mkv", ".webm", ".wmv", ".gif"]
image_extensions = [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".tga", ".webp"]
patterns = ["*.mp4", "*.mov", "*.avi", "*.flv", "*.mkv", "*.webm", "*.wmv", ".gif", "*.jpg", "*.jpeg", "*.png",
            "*.tiff",
            "*.tif", "*.bmp", "*.tga", "*.webp"]


class ImagesEventHandler(PatternMatchingEventHandler):

    def __init__(self, iou, confidence, names, create_csv, save_loc):
        self.eventIou = iou
        self.eventConfidence = confidence
        self.eventNames = names
        self.eventCreateCsv = create_csv
        self.eventSaveLoc = save_loc
        PatternMatchingEventHandler.__init__(self, patterns=patterns,
                                             ignore_directories=True, case_sensitive=False)

        thread = Mythread(threadID, "Analyse", workQueue, self.eventIou, self.eventConfidence, self.eventNames,
                          self.eventCreateCsv, self.eventSaveLoc)
        thread.start()
        threads.append(thread)

    def on_created(self, event):

        base_name = os.path.basename(event.src_path)
        if "_analysed" not in base_name:
            file_size = -1
            while file_size != os.path.getsize(event.src_path):
                file_size = os.path.getsize(event.src_path)
            print("Watchdog received created event - % s." % event.src_path)
            if event.src_path not in queueCheck:
                queueCheck.append(event.src_path)
                queueLock.acquire()
                workQueue.put(event.src_path)
                queueLock.release()
            else:
                print("Already in queue")
        else:
            print("Skipping already analysed file")

    def on_deleted(self, event):
        print("Watchdog received deleted event - % s." % event.src_path)

    # def dispatch(self, event):
    #    print("dispatch")

    def on_modified(self, event):

        base_name = os.path.basename(event.src_path)
        if "_analysed" not in base_name:
            file_size = -1
            while file_size != os.path.getsize(event.src_path):
                file_size = os.path.getsize(event.src_path)
            print("Watchdog received modified event - % s." % event.src_path)

            if event.src_path not in queueCheck:
                queueCheck.append(event.src_path)
                queueLock.acquire()
                workQueue.put(event.src_path)
                queueLock.release()
            else:
                print("Already in queue")
        else:
            print("Skipping already analysed file")


class Mythread(threading.Thread):
    def __init__(self, thread_id, name, q, iou, confidence, names, create_csv, save_loc):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.q = q
        self.iou = iou
        self.confidence = confidence
        self.names = names
        self.createCsv = create_csv
        self.save_loc = save_loc

    def run(self):
        print("Starting " + self.name)
        process_data(self.name, self.q, self.iou, self.confidence, self.names, self.createCsv, self.save_loc)
        print("Exiting " + self.name)


def process_data(thread_name, q, iou, confidence, names, create_csv, save_location):
    root = Tk()
    root.title("Polling UI")
    root.protocol("WM_DELETE_WINDOW", disable_event)
    txt = Text(root, height=20, width=70)
    vsb = Scrollbar(root, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    txt.pack(side="left", fill="both", expand=True)
    root.update()
    while not exitFlag:
        queueLock.acquire()
        print(".....Polling.....")
        append_text(txt, root, ".....Polling.....")
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            append_text(txt, root, "Watchdog received event - % s." % data)
            print("%s processing %s" % (thread_name, data))
            append_text(txt, root, "%s processing %s" % (thread_name, data))
            file_end = (os.path.splitext(os.path.basename(data))[1])
            print(file_end)
            append_text(txt, root, file_end)

            #save_loc = os.path.dirname(data)
            #print(save_loc)

            append_text(txt, root, save_location)

            save_location = save_location + r"\analysed"
            save_location = os.path.abspath(save_location)
            print(save_location)

            data_list = []
            data_list.insert(0, data)

            # if file_end.lower() == ".mp4":
            if file_end.lower() in video_extensions:
                try:
                    os.mkdir(save_location)
                except FileExistsError as error:
                    print(error)
                    append_text(txt, root, "Saved folder already exists")

                try:
                    print("Starting video analysis...")
                    append_text(txt, root, "Starting video analysis...")
                    detect.main("video", data_list, save_location, iou,
                                confidence, names, create_csv)
                    print("Video analysis ended successfully")
                    append_text(txt, root, "Video analysis ended successfully")
                except Exception as err:
                    print("Error in video analysis")
                    print(err)
                    append_text(txt, root, "Error in video analysis")
                    append_text(txt, root, err)
            # elif file_end.lower() == ".jpg":
            elif file_end.lower() in image_extensions:
                try:
                    os.mkdir(save_location)
                except FileExistsError as error:
                    print(error)
                    append_text(txt, root, "Saved folder already exists")
                try:
                    print("Starting Image analysis...")
                    append_text(txt, root, "Starting Image analysis...")
                    detect.main("images", data_list, save_location, iou,
                                confidence, names, create_csv)
                    print("Image analysis ended successfully")
                    append_text(txt, root, "Image analysis ended successfully")
                except Exception as err:
                    print("Error in image analysis")
                    append_text(txt, root, "Error in video analysis")
                    print(err)
                    append_text(txt, root, err)

            queueLock.acquire()
            queueCheck.remove(data)
            print(queueCheck)
            queueLock.release()
        else:
            queueLock.release()
        time.sleep(0.5)
    print("EXITING ANALYSE THREAD")
    append_text(txt, root, "EXITING ANALYSE THREAD")


def stop_threading():
    global exitFlag
    queueCheck.clear()
    exitFlag = 1
    for t in threads:
        t.join()
    print(threads)


def lower_exit_flag():
    global exitFlag
    exitFlag = 0


def disable_event():
    pass


def append_text(text, root, append_string):
    text.insert(END, "\n" + str(append_string))
    text.see(END)
    root.update()
