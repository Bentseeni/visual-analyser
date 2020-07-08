import sys
import time

from watchdog.observers import Observer

import eventHandler


class ImagesWatcher:
    """
    Watchdog observer
    """
    def __init__(self, src_path, iou, confidence, names, create_csv, save_loc):
        eventHandler.lower_exit_flag()
        self.__src_path = src_path
        self.__event_handler = eventHandler.ImagesEventHandler(iou, confidence, names, create_csv, save_loc)
        self.__event_observer = Observer()

    def run(self):
        self.start()
        # try:
        #    while True:
        #        time.sleep(1)
        #        print("----")
        # except KeyboardInterrupt:
        #    self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()
        print("polling stopped")
        eventHandler.stop_threading()

    def __schedule(self):
        self.__event_observer.schedule(self.__event_handler, self.__src_path, recursive=True)


if __name__ == "__main__":
    src_path = r"C:\Users\Matias\PycharmProjects\Test\testfolder"
    ImagesWatcher(src_path).run()
