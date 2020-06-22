import os
from tkinter import *
from tkinter import filedialog as fd
import load_weights
import threading
import pathlib
import detect
import watcher

import utils
import csv


class UI(Frame):
    dlg = os.getcwd()
    saveLocation = os.getcwd()
    weightsLocation = "./weights/yolov3.weights"
    classesLocation = "./data/labels/coco.names"
    green = "#32a62e"
    video_extensions = [".mp4", ".mov", ".avi", ".flv", ".mkv", ".webm", ".wmv", ".gif"]
    image_extensions = [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".tga", ".webp"]

    isPolling = False

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.parent.title("VA")

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        file_menu = Menu(menubar)
        file_menu.add_command(label="Open", command=self.on_open)
        file_menu.add_command(label="Select weights", command=self.select_weights)
        file_menu.add_command(label="Select classes", command=self.select_classes)
        file_menu.add_command(label="Test", command=self.class_names)
        menubar.add_cascade(label="File", menu=file_menu)

        self.openFileEntry = Entry(self.parent, width=50)
        self.openFileEntry.grid(row=0, column=0)
        self.openFileEntry.insert(0, os.getcwd())

        self.saveFileEntry = Entry(self.parent, width=50)
        self.saveFileEntry.grid(row=1, column=0)
        self.saveFileEntry.insert(0, os.getcwd())

        self.weightsFileEntry = Entry(self.parent, width=50)
        self.weightsFileEntry.grid(row=2, column=0)
        self.weightsFileEntry.insert(0, self.weightsLocation)

        self.classesFileEntry = Entry(self.parent, width=50)
        self.classesFileEntry.grid(row=3, column=0)
        self.classesFileEntry.insert(0, self.classesLocation)

        self.pollingLocationEntry = Entry(self.parent, width=50)
        self.pollingLocationEntry.grid(row=10, column=0, pady=10)
        self.pollingLocationEntry.insert(0, os.getcwd())

        self.openButton = Button(self.parent, text="Open file", command=self.on_open)
        self.openButton.grid(row=0, column=1)

        self.saveButton = Button(self.parent, text="Save location", command=self.select_save_location)
        self.saveButton.grid(row=1, column=1)

        self.weightsFileButton = Button(self.parent, text="Weights location", command=self.select_weights)
        self.weightsFileButton.grid(row=2, column=1)

        self.classesFileButton = Button(self.parent, text="Classes location", command=self.select_classes)
        self.classesFileButton.grid(row=3, column=1)

        self.pollingLocationButton = Button(self.parent, text="Polling location", command=self.select_polling_location)
        self.pollingLocationButton.grid(row=10, column=1)

        self.iouEntry = Entry(self.parent, width=5)
        self.iouEntry.grid(row=5, column=0, sticky=E)
        self.iouEntry.insert(0, "0.5")

        self.confidenceEntry = Entry(self.parent, width=5, text=0.5)
        self.confidenceEntry.grid(row=6, column=0, sticky=E)
        self.confidenceEntry.insert(0, "0.5")

        self.loadWeightsButton = Button(self.parent, text="Load Weights", command=self.thread_start_weights)
        self.loadWeightsButton.grid(row=4, column=0)

        self.analyseButton = Button(self.parent, text="Analyse", command=self.start_analyse, bg=self.green, height=3,
                                    width=20)
        self.analyseButton.grid(row=8, column=0)

        self.pollingButton = Button(self.parent, text="Start polling", command=self.start_polling, bg='#b828ae')
        self.pollingButton.grid(row=11, column=0)

        self.txt = Text(self.parent, height=10, width=35)
        self.txt.grid(row=9, column=0, sticky=W, pady=5)

        self.weightsLocation = self.get_current_weights_path()
        self.classesLocation = self.get_names_path()

        self.weightsLabel = Label(self.parent, text=os.path.basename(self.weightsLocation), width=37)
        self.weightsLabel.grid(row=5, column=0, sticky=W)

        self.classesLabel = Label(self.parent, text=os.path.basename(self.classesLocation), width=37)
        self.classesLabel.grid(row=6, column=0, sticky=W)

        self.iouLbl = Label(self.parent, text="iou")
        self.iouLbl.grid(row=5, column=1)

        self.confidenceLbl = Label(self.parent, text="confidence")
        self.confidenceLbl.grid(row=6, column=1)

        self.createCsv = BooleanVar()
        self.csvCheckButton = Checkbutton(self.parent, text="Create CSV", variable=self.createCsv, onvalue=True,
                                          offvalue=False)
        self.csvCheckButton.grid(row=7, column=0, columnspan=2, sticky=E, padx=30)

    def on_open(self):
        ftypes = [('Video', '*.mp4 *.mov *.avi *.flv *.mkv *.webm *.wmv *.gif'), ('Images', '*.jpg *.jpeg *.png *.tif '
                                                                                            '*.tiff *.bmp *.tga '
                                                                                            '*.webp')]
        self.dlg = fd.askopenfilenames(filetypes=ftypes)
        print(self.dlg)
        if self.dlg == "":
            self.dlg = os.getcwd()

        self.openFileEntry.delete(0, END)
        self.openFileEntry.insert(0, self.dlg)

    def read_file(self, filename):
        f = open(filename, "r")
        text = f.read()
        return text

    def select_weights(self):
        ftypes = [('Weights', '*.weights')]
        self.weightsLocation = fd.askopenfilename(filetypes=ftypes)
        if self.weightsLocation == "":
            self.weightsLocation = "./weights/yolov3.weights"
        self.weightsFileEntry.delete(0, END)
        self.weightsFileEntry.insert(0, self.weightsLocation)
        print(self.weightsLocation)

    def select_classes(self):
        ftypes = [('Classes', '*.names')]
        self.classesLocation = fd.askopenfilename(filetypes=ftypes)
        if self.classesLocation == "":
            self.classesLocation = "./data/labels/coco.names"
        self.classesFileEntry.delete(0, END)
        self.classesFileEntry.insert(0, self.classesLocation)
        print(self.classesLocation)

    def class_names(self):
        class_names = utils.load_class_names(self.classesFileEntry.get())
        class_names.insert(0, "frame")
        print(class_names)
        filename = "test_file.csv"
        print(self.createCsv.get())
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvfile.write("sep=,")
            csvfile.write('\n')
            csvwriter.writerow(class_names)

    def select_save_location(self):
        self.saveLocation = fd.askdirectory()
        if self.saveLocation == "":
            self.saveLocation = os.getcwd()
        self.saveFileEntry.delete(0, END)
        self.saveFileEntry.insert(0, self.saveLocation)
        print(self.saveLocation)

    def select_polling_location(self):
        self.pollingLocation = fd.askdirectory()
        if self.pollingLocation == "":
            self.pollingLocation = os.getcwd()
        self.pollingLocationEntry.delete(0, END)
        self.pollingLocationEntry.insert(0, self.pollingLocation)
        print(self.saveLocation)

    def start_polling(self):
        if not self.isPolling:
            self.pollingButton['text'] = "Stop polling"
            self.pollingButton['bg'] = "red"
            self.append_text("Polling started in location:\n" + self.pollingLocationEntry.get())
            self.isPolling = True
            polling_thread = threading.Thread(target=self.start_polling_thread)
            polling_thread.start()
        elif self.isPolling:
            self.pollingButton['text'] = "Start polling"
            self.pollingButton['bg'] = '#b828ae'
            self.append_text("Polling stopped")
            self.isPolling = False
            self.pollingWatcher.stop()

    def start_polling_thread(self):

        namespath = self.classesLocation
        try:
            namespathfile = open("namespath.txt")
            namespath = namespathfile.read()
            namespathfile.close()
        except Exception:
            self.txt.insert(END, "\nCouldn't read namespath.txt, using default .names")

        self.pollingWatcher = watcher.ImagesWatcher(self.pollingLocationEntry.get(), float(self.iouEntry.get()),
                                                    float(self.confidenceEntry.get()), namespath, self.createCsv.get())
        self.pollingWatcher.run()

    def start_analyse(self):
        print(self.dlg)

        # if pathlib.Path(self.dlg[0]).suffix.lower() == ".mp4":
        if pathlib.Path(self.dlg[0]).suffix.lower() in self.video_extensions:
            print(pathlib.Path(self.dlg[0]).suffix)
            analyse_thread_video = threading.Thread(target=self.analyse_video)
            analyse_thread_video.start()

        # elif pathlib.Path(self.dlg[0]).suffix.lower() == ".jpg":
        elif pathlib.Path(self.dlg[0]).suffix.lower() in self.image_extensions:
            print(pathlib.Path(self.dlg[0]).suffix)
            analyse_thread_images = threading.Thread(target=self.analyse_images)
            analyse_thread_images.start()

    def append_text(self, string):
        self.txt.insert(END, "\n" + string)

    def thread_start_weights(self):

        if self.classesFileEntry.get() == "" or self.weightsFileEntry.get() == "":
            print("no selected classes or weights")
            self.txt.insert(END, "\nno selected classes or weights")

            return
        else:
            t = threading.Thread(target=self.start_load_weights)
            t.start()

    def start_load_weights(self):
        try:
            self.txt.insert(END, "\nLoading weights...")
            load_weights.main(weights_file=self.weightsFileEntry.get(), class_names_file=self.classesFileEntry.get())
            names_path_file = open("namespath.txt", "w")
            names_path_file.write(self.classesFileEntry.get())
            names_path_file.close()
            weights_path_file = open("currentweights.txt", "w")
            weights_path_file.write(self.weightsFileEntry.get())
            weights_path_file.close()
            self.txt.insert(END, "\nWeights loaded")
            self.weightsLabel['text'] = os.path.basename(self.weightsFileEntry.get())
            self.classesLabel['text'] = os.path.basename(self.classesFileEntry.get())
        except Exception as err:
            self.txt.insert(END, "\nerror loading weights")
            self.txt.insert(END, err)

    def analyse_images(self):
        namespath = self.get_names_path()
        try:
            self.txt.insert(END, "\nStarting image analysis...")
            detect.main("images", self.dlg, self.saveLocation, float(self.iouEntry.get()),
                        float(self.confidenceEntry.get()), namespath)
            self.txt.insert(END, "\nImage analysis ended successfully")
        except Exception as err:
            self.txt.insert(END, "\nerror in image analysis")
            self.txt.insert(END, err)

    def analyse_video(self):
        namespath = self.get_names_path()
        try:
            self.txt.insert(END, "\nStarting video analysis...")
            detect.main("video", self.dlg, self.saveLocation, float(self.iouEntry.get()),
                        float(self.confidenceEntry.get()), namespath, self.createCsv.get())
            self.txt.insert(END, "\nVideo analysis ended successfully")
        except Exception as err:
            self.txt.insert(END, "\nerror in video analysis")
            self.txt.insert(END, err)

    def get_names_path(self):
        try:
            names_path_file = open("namespath.txt")
            names_path = names_path_file.read()
            names_path_file.close()
        except Exception:
            self.txt.insert(END, "\nCouldn't read namespath.txt, using default .names")
            names_path = self.classesLocation
        finally:
            return names_path

    def get_current_weights_path(self):
        try:
            current_weights_file = open("currentweights.txt")
            current_weights_path = current_weights_file.read()
            current_weights_file.close()
        except Exception:
            self.txt.insert(END, "\nCouldn't read currentweights.txt")
            current_weights_path = "default/unknown"
        finally:
            return current_weights_path


def main():
    root = Tk()
    ui = UI(root)
    root.geometry("420x500+300+300")
    root.mainloop()


if __name__ == '__main__':
    main()
