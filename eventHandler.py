import os
from PIL import Image
from PIL.ImageOps import grayscale
from watchdog.events import PatternMatchingEventHandler


class ImagesEventHandler(PatternMatchingEventHandler):
    # THUMBNAIL_SIZE = (128,128)
    # IMAGES_REGEX = [r".*[^_thumbnail]\.jpg$"]

    def __init__(self):
        # super().__init__(self, patterns=['*.jpg'],ignore_directories=True, case_sensitive=False)
        PatternMatchingEventHandler.__init__(self, patterns=['*.jpg'],
                                             ignore_directories=True, case_sensitive=False)

    def on_created(self, event):
        # self.process(event)
        file_size = -1
        while file_size != os.path.getsize(event.src_path):
            file_size = os.path.getsize(event.src_path)
        print("Watchdog received created event - % s." % event.src_path)

    def on_deleted(self, event):
        print("deleted")

    # def dispatch(self, event):
    #    print("dispatch")

    def on_modified(self, event):
        print("modified")

    def process(self, event):
        filename, ext = os.path.splitext(event.src_path)
        filename = f"{filename}_thumbnail.jpg"

        image = Image.open(event.src_path)
        image = grayscale(image)
        image.thumbnail(self.THUMBNAIL_SIZE)
        image.save(filename)
