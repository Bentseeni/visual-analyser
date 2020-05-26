import os
from tkinter import *
from tkinter import filedialog as fd
import load_weights
import threading
import pathlib
import detect
import watcher


class UI(Frame):
    dlg = os.getcwd()
    saveLocation = os.getcwd()
    weightsLocation = "./weights/yolov3.weights"
    classesLocation = "./data/labels/coco.names"
    isPolling = False


    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("File dialog")
        # self.pack(fill=BOTH, expand=1)

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        fileMenu.add_command(label="Select weights", command=self.selectWeights)
        fileMenu.add_command(label="Select classes", command=self.selectClasses)
        menubar.add_cascade(label="File", menu=fileMenu)

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

        self.openButton = Button(self.parent, text="Open file", command=self.onOpen)
        self.openButton.grid(row=0, column=1)

        self.saveButton = Button(self.parent, text="Save location", command=self.selectSaveLocation)
        self.saveButton.grid(row=1, column=1)

        self.weightsFileButton = Button(self.parent, text="Weights location", command=self.selectWeights)
        self.weightsFileButton.grid(row=2, column=1)

        self.classesFileButton = Button(self.parent, text="Classes location", command=self.selectClasses)
        self.classesFileButton.grid(row=3, column=1)

        # iou & confidence
        # select .weights & select classes .names
        self.iouEntry = Entry(self.parent, width=5)
        self.iouEntry.grid(row=5, column=0, sticky=E)
        self.iouEntry.insert(0, "0.5")

        self.confidenceEntry = Entry(self.parent, width=5, text=0.5)
        self.confidenceEntry.grid(row=6, column=0, sticky=E)
        self.confidenceEntry.insert(0, "0.5")

        self.loadWeightsButton = Button(self.parent, text="Load Weights", command=self.threadStartWeights)
        self.loadWeightsButton.grid(row=4, column=0)

        self.analyseButton = Button(self.parent, text="Analyse", command=self.startAnalyse)
        self.analyseButton.grid(row=7, column=0)

        self.pollingButton = Button(self.parent, text="Start polling", command=self.startPolling)
        self.pollingButton.grid(row=8, column=1)

        self.iouLbl = Label(self.parent, text="iou")
        self.iouLbl.grid(row=5, column=1)

        self.confidenceLbl = Label(self.parent, text="confidence")
        self.confidenceLbl.grid(row=6, column=1)

        self.txt = Text(self.parent, height=10, width=35)
        self.txt.grid(row=8, column=0, sticky=W, pady=5)

    # self.txt = Text(self.parent)
    # self.txt.grid(column=0,row=0)
    # self.txt.pack(fill=BOTH, expand=1)

    # self.lbl = Label(self, text="asd").grid(row=1,column=0)
    # self.lbl.grid(column=1,row=0)
    # self.lbl.pack(fill=BOTH, expand=1)

    def onOpen(self):
        ftypes = [('Video', '*.mp4'), ('Images', '*.jpg')]
        # dlg = tkFileDialog.Open(self, filetypes = ftypes)
        self.dlg = fd.askopenfilenames(filetypes=ftypes)
        # fl = dlg.show()
        print(self.dlg)
        if self.dlg == "":
            self.dlg = os.getcwd()

        # if type(self.dlg) is not tuple:
        #    print(pathlib.Path(self.dlg).suffix)

        # if self.dlg == '':
        #   self.dlg = os.getcwd()
        #    print(self.dlg)
        # self.txt.insert(END, dlg)
        # self.lbl['text'] = dlg
        self.openFileEntry.delete(0, END)
        self.openFileEntry.insert(0, self.dlg)

    # if dlg != '':
    # dlg = os.getcwd()
    # text = self.readFile(dlg)
    #  print(text)
    # self.txt.insert(END, dlg)

    def readFile(self, filename):
        f = open(filename, "r")
        text = f.read()
        return text

    def selectWeights(self):
        ftypes = [('Weights', '*.weights')]
        self.weightsLocation = fd.askopenfilename(filetypes=ftypes)
        if self.weightsLocation == "":
            self.weightsLocation = "./weights/yolov3.weights"
        self.weightsFileEntry.delete(0, END)
        self.weightsFileEntry.insert(0, self.weightsLocation)
        print(self.weightsLocation)

    def selectClasses(self):
        ftypes = [('Classes', '*.names')]
        self.classesLocation = fd.askopenfilename(filetypes=ftypes)
        if self.classesLocation == "":
            self.classesLocation = "./data/labels/coco.names"
        self.classesFileEntry.delete(0, END)
        self.classesFileEntry.insert(0, self.classesLocation)
        print(self.classesLocation)

    def selectSaveLocation(self):
        self.saveLocation = fd.askdirectory()
        if self.saveLocation == "":
            self.saveLocation = os.getcwd()
        self.saveFileEntry.delete(0, END)
        self.saveFileEntry.insert(0, self.saveLocation)
        print(self.saveLocation)

    def startPolling(self):
        if self.isPolling == False:
            self.pollingButton['text'] = "Stop polling"
            self.appendText("Polling started")
            self.isPolling = True
            #self.pollingWatcher = watcher.ImagesWatcher(self.saveFileEntry.get(), float(self.iouEntry.get()),
            #                                            float(self.confidenceEntry.get()), self.classesLocation)
            #self.pollingWatcher.run()


            pollingThread = threading.Thread(target=self.startPollingThread)
            pollingThread.start()
        elif self.isPolling == True:
            self.pollingButton['text'] = "Start polling"
            self.appendText("Polling stopped")
            self.isPolling = False
            self.pollingWatcher.stop()


    def startPollingThread(self):

        namespath = self.classesLocation
        try:
            namespathfile = open("namespath.txt")
            namespath = namespathfile.read()
            namespathfile.close()
        except Exception:
            self.txt.insert(END, "\nCouldn't read namespath.txt, using default .names")

        self.pollingWatcher = watcher.ImagesWatcher(self.saveFileEntry.get(), float(self.iouEntry.get()),
                                                    float(self.confidenceEntry.get()), namespath)
        self.pollingWatcher.run()

    def startAnalyse(self):
        print(self.dlg)
        # dlg_extension = os.path.splitext(self.dlg)[1]
        # print(dlg_extension)
        # if pathlib.Path(self.dlg).suffix == '.jpg':
        #    print(pathlib.Path(self.dlg).suffix)

        if pathlib.Path(self.dlg[0]).suffix.lower() == ".mp4":
            print(pathlib.Path(self.dlg[0]).suffix)
            # detect.main("video", self.dlg, self.saveLocation, float(self.iouEntry.get()),
            # float(self.confidenceEntry.get()))
            analyseThreadVideo = threading.Thread(target=self.analyseVideo)
            analyseThreadVideo.start()


        elif pathlib.Path(self.dlg[0]).suffix.lower() == ".jpg":
            print(pathlib.Path(self.dlg[0]).suffix)
            analyseThreadImages = threading.Thread(target=self.analyseImages)
            analyseThreadImages.start()

            # detect.main("images", self.dlg, self.saveLocation, float(self.iouEntry.get()),
            #           float(self.confidenceEntry.get()))

        # float(self.iouEntry.get())
        # float(self.confidenceEntry.get())
    def appendText(self, string):
        self.txt.insert(END, "\n" + string)

    def threadStartWeights(self):

        if self.classesFileEntry.get() == "" or self.weightsFileEntry.get() == "":
            print("no selected classes or weights")
            self.txt.insert(END, "\nno selected classes or weights")

            return
        else:
            t = threading.Thread(target=self.startLoadWeights)
            t.start()

    def startLoadWeights(self):
        try:
            self.txt.insert(END, "\nLoading weights...")
            load_weights.main(weights_file=self.weightsFileEntry.get(), class_names_file=self.classesFileEntry.get())
            namespathfile = open("namespath.txt", "w")
            namespathfile.write(self.classesFileEntry.get())
            namespathfile.close()
            self.txt.insert(END, "\nWeights loaded")
        except Exception as err:
            self.txt.insert(END, "\nerror loading weights")
            self.txt.insert(END, err)

    def analyseImages(self):
        namespath = self.classesLocation
        try:
            namespathfile = open("namespath.txt")
            namespath = namespathfile.read()
            namespathfile.close()
        except Exception:
            self.txt.insert(END, "\nCouldn't read namespath.txt, using default .names")

        try:
            self.txt.insert(END, "\nStarting image analysis...")
            detect.main("images", self.dlg, self.saveLocation, float(self.iouEntry.get()),
                        float(self.confidenceEntry.get()), namespath)
            self.txt.insert(END, "\nImage analysis ended successfully")
        except Exception as err:
            self.txt.insert(END, "\nerror in image analysis")
            self.txt.insert(END, err)

    def analyseVideo(self):
        namespath = self.classesLocation
        try:
            namespathfile = open("namespath.txt")
            namespath = namespathfile.read()
            namespathfile.close()
        except Exception:
            self.txt.insert(END, "\nCouldn't read namespath.txt, using default .names")

        try:
            self.txt.insert(END, "\nStarting video analysis...")
            detect.main("video", self.dlg, self.saveLocation, float(self.iouEntry.get()),
                        float(self.confidenceEntry.get()), namespath)
            self.txt.insert(END, "\nVideo analysis ended successfully")
        except Exception as err:
            self.txt.insert(END, "\nerror in video analysis")
            self.txt.insert(END, err)


def main():
    root = Tk()
    ui = UI(root)
    root.geometry("400x450+300+300")
    root.mainloop()



if __name__ == '__main__':
    main()
