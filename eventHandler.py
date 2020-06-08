import os
from watchdog.events import PatternMatchingEventHandler
import queue
import time
import threading
import detect

exitFlag = 0
threadList = ["One"]
queueLock = threading.Lock()
workQueue = queue.Queue(10)
threads = []
threadID = 1


class ImagesEventHandler(PatternMatchingEventHandler):

    def __init__(self, iou, confidence, names, create_csv):
        self.eventIou = iou
        self.eventConfidence = confidence
        self.eventNames = names
        self.eventCreateCsv = create_csv
        PatternMatchingEventHandler.__init__(self, patterns=['*.jpg', '*.mp4'],
                                             ignore_directories=True, case_sensitive=False)

        thread = Mythread(threadID, "Analyse", workQueue, self.eventIou, self.eventConfidence, self.eventNames,
                          self.eventCreateCsv)
        thread.start()
        threads.append(thread)

    def on_created(self, event):
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


class Mythread(threading.Thread):
    def __init__(self, thread_id, name, q, iou, confidence, names, create_csv):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.q = q
        self.iou = iou
        self.confidence = confidence
        self.names = names
        self.createCsv = create_csv

    def run(self):
        print("Starting " + self.name)
        process_data(self.name, self.q, self.iou, self.confidence, self.names, self.createCsv)
        print("Exiting " + self.name)


def process_data(thread_name, q, iou, confidence, names, create_csv):
    while not exitFlag:
        queueLock.acquire()
        print(".....Polling.....")
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            print("%s processing %s" % (thread_name, data))
            file_end = (os.path.splitext(os.path.basename(data))[1])
            print(file_end)
            save_loc = os.path.dirname(data)
            print(save_loc)

            save_loc = save_loc + r"\saved"
            save_loc = os.path.abspath(save_loc)

            data_list = []
            data_list.insert(0, data)
            base_name = os.path.basename(data)
            print(base_name)

            if file_end.lower() == ".mp4" and "_analysed" not in base_name:
                try:
                    os.mkdir(save_loc)
                except OSError as error:
                    print(error)
                try:
                    print("Starting video analysis...")
                    detect.main("video", data_list, save_loc, iou,
                                confidence, names, create_csv)
                    print("Video analysis ended successfully")
                except Exception as err:
                    print("Error in video analysis")
                    print(err)

            elif file_end.lower() == ".jpg" and "_analysed" not in base_name:
                try:
                    os.mkdir(save_loc)
                except OSError as error:
                    print(error)
                try:
                    print("Starting Image analysis...")
                    detect.main("images", data_list, save_loc, iou,
                                confidence, names, create_csv)
                    print("Image analysis ended successfully")
                except Exception as err:
                    print("Error in image analysis")
                    print(err)
        else:
            queueLock.release()
        time.sleep(1)
    print("EXITING ANALYSE THREAD")


def stop_threading():
    global exitFlag
    exitFlag = 1
    for t in threads:
        t.join()
    print(threads)


def lower_exit_flag():
    global exitFlag
    exitFlag = 0
