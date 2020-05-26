import os
from PIL import Image
from PIL.ImageOps import grayscale
from watchdog.events import PatternMatchingEventHandler
import queue
import time
import threading
import detect
import pathlib

exitFlag = 0
threadList = ["One"]
queueLock = threading.Lock()
workQueue = queue.Queue(10)
threads = []
threadID = 1


class ImagesEventHandler(PatternMatchingEventHandler):
    # THUMBNAIL_SIZE = (128,128)
    # IMAGES_REGEX = [r".*[^_thumbnail]\.jpg$"]

    def __init__(self, iou, confidence, names):

        self.eventIou = iou
        self.eventConfidence = confidence
        self.eventNames = names
        PatternMatchingEventHandler.__init__(self, patterns=['*.jpg','*.mp4'],
                                             ignore_directories=True, case_sensitive=False)

        thread = myThread(threadID, "Analyse", workQueue, self.eventIou, self.eventConfidence, self.eventNames)
        thread.start()
        threads.append(thread)


    def on_created(self, event):
        # self.process(event)
        file_size = -1
        while file_size != os.path.getsize(event.src_path):
            file_size = os.path.getsize(event.src_path)
        print("Watchdog received created event - % s." % event.src_path)
        queueLock.acquire()
        workQueue.put(event.src_path)
        queueLock.release()

    def on_deleted(self, event):
        print("deleted")

    # def dispatch(self, event):
    #    print("dispatch")

    def on_modified(self, event):
        print("modified")




class myThread(threading.Thread):
    def __init__(self, threadID, name, q, iou, confidence, names):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.iou = iou
        self.confidence = confidence
        self.names = names

    def run(self):
        print("Starting " + self.name)
        processData(self.name, self.q, self.iou, self.confidence, self.names)
        print("Exiting " + self.name)


def processData(threadName, q, iou, confidence, names):
    while not exitFlag:
        queueLock.acquire()
        print(".....")
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            print("%s processing %s" % (threadName, data))
            fileEnd = (os.path.splitext(os.path.basename(data))[1])
            print(fileEnd)
            saveLoc = os.path.dirname(data)
            print(saveLoc)
            saveLoc = saveLoc + "\saved"
            saveLoc = os.path.abspath(saveLoc)
            dataList = []
            dataList.insert(0,data)
            baseName = os.path.basename(data)
            print(baseName)



            if fileEnd.lower() == ".mp4" and "_analysed" not in baseName:
                try:
                    print("Starting video analysis...")
                    detect.main("video", dataList, saveLoc, iou,
                                confidence, names)
                    print("Video analysis ended successfully")
                except Exception as err:
                    print("Error in video analysis")
                    print(err)

            elif fileEnd.lower() == ".jpg" and "_analysed" not in baseName:
                try:
                    print("Starting Image analysis...")
                    detect.main("images", dataList, saveLoc, iou,
                                confidence, names)
                    print("Image analysis ended successfully")
                except Exception as err:
                    print("Error in image analysis")
                    print(err)
        else:
            queueLock.release()
        time.sleep(1)
    print("EXITING ANALYSE THREAD")
def stopThreading():
    global exitFlag
    exitFlag = 1
    for t in threads:
        t.join()
    print(threads)
def lowerExitFlag():
    global exitFlag
    exitFlag = 0
