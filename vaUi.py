"""
Project: Object detection with OpenCV, tf and yolov3, Graphical User Interface included

Authors: Matias Röyttä https://github.com/Bentseeni
         Saku Huuha https://github.com/SakuH
         Niko Hämäläinen https://github.com/GitSucks123
         Jere Hannula https://github.com/jersku

Github repository: https://github.com/Bentseeni/visual-analyser
"""
import os
from tkinter import *
from tkinter import filedialog as fd
from tkinter import colorchooser
import tkinter.ttk as ttk
from tkinter.ttk import *
import load_weights
import threading
import pathlib
import detect
import watcher
import utils
import csv
import json


def load_json():
    config_location = 'config.json'

    if os.path.exists(config_location):
        config = json.load(open(config_location))
        return config
    else:
        config = {
            'printClasses': True,
            'printIou': False,
            'printConfidence': False,
            'printNamesPath': False,
            'printWeightsPath': False,
            'createCsv': False,
            'namesPath': './data/labels/coco.names',
            'weightsPath': './weights/yolov3.weights',
            'iou': '0.5',
            'confidence': '0.5',
            'textColorHex': '#FFFFFF',
            'textColorRGB': (255, 255, 255),
            'textStrokeColorHex': '#FF00AF',
            'textStrokeColorRGB': (255, 0, 180)
        }
        json.dump(config, open(config_location, 'w'), sort_keys=True, indent=4)
        return config


class UI(Frame):
    dlg = os.getcwd()
    saveLocation = os.getcwd()
    weightsLocation = "./weights/yolov3.weights"
    classesLocation = "./data/labels/coco.names"
    green = "#32a62e"
    video_extensions = [".mp4", ".mov", ".avi", ".flv", ".mkv", ".webm", ".wmv", ".gif"]
    image_extensions = [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".tga", ".webp"]
    isPolling = False
    analyser_config = load_json()

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.textColorHex = self.analyser_config.get("textColorHex")
        self.textColorRGB = self.analyser_config.get("textColorRGB")
        self.textStrokeColorHex = self.analyser_config.get("textStrokeColorHex")
        self.textStrokeColorRGB = self.analyser_config.get("textStrokeColorRGB")

        self.init_ui()

    def init_ui(self):
        """
        Initialize user interface
        """
        self.parent.title("VA")

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        file_menu = Menu(menubar)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Select weights", command=self.select_weights)
        file_menu.add_command(label="Select classes", command=self.select_classes)
        file_menu.add_command(label="Test", command=self.test)
        menubar.add_cascade(label="File", menu=file_menu)

        self.tabControl = Notebook(self.parent)
        self.tab1 = Frame(self.tabControl)
        self.tab2 = Frame(self.tabControl)
        self.tabControl.add(self.tab1, text="Analyse")
        self.tabControl.add(self.tab2, text="Options")
        self.tabControl.pack(expand=1, fill="both")

        self.openFileEntry = Entry(self.tab1, width=50)
        self.openFileEntry.grid(row=0, column=0, padx=5, pady=5)
        self.openFileEntry.insert(0, os.getcwd())

        self.saveLocationEntry = Entry(self.tab1, width=50)
        self.saveLocationEntry.grid(row=1, column=0, padx=5, pady=5)
        self.saveLocationEntry.insert(0, os.getcwd())

        self.weightsFileEntry = Entry(self.tab1, width=50)
        self.weightsFileEntry.grid(row=2, column=0, padx=5, pady=5)
        self.weightsFileEntry.insert(0, self.weightsLocation)

        self.classesFileEntry = Entry(self.tab1, width=50)
        self.classesFileEntry.grid(row=3, column=0, padx=5, pady=5)
        self.classesFileEntry.insert(0, self.classesLocation)

        self.pollingLocationEntry = Entry(self.tab1, width=50)
        self.pollingLocationEntry.grid(row=10, column=0, pady=10)
        self.pollingLocationEntry.insert(0, os.getcwd())

        self.pollingSaveLocationEntry = Entry(self.tab1, width=50)
        self.pollingSaveLocationEntry.grid(row=12, column=0, pady=5)
        self.pollingSaveLocationEntry.insert(0, os.getcwd())

        self.openButton = Button(self.tab1, text="Open file", command=self.open_file)
        self.openButton.grid(row=0, column=1, padx=5, pady=5)

        self.saveButton = Button(self.tab1, text="Save location",
                                 command=lambda: self.select_folder(self.saveLocationEntry))
        self.saveButton.grid(row=1, column=1, padx=5, pady=5)

        self.weightsFileButton = Button(self.tab1, text="Weights location", command=self.select_weights)
        self.weightsFileButton.grid(row=2, column=1, padx=5, pady=5)

        self.classesFileButton = Button(self.tab1, text="Classes location", command=self.select_classes)
        self.classesFileButton.grid(row=3, column=1, padx=5, pady=5)

        self.pollingLocationButton = Button(self.tab1, text="Polling location",
                                            command=lambda: self.select_folder(self.pollingLocationEntry))
        self.pollingLocationButton.grid(row=10, column=1, padx=5, pady=5)

        self.pollingSaveLocationButton = Button(self.tab1, text="Polling save location",
                                                command=lambda: self.select_folder(self.pollingSaveLocationEntry))
        self.pollingSaveLocationButton.grid(row=12, column=1, padx=5, pady=5)

        self.iouEntry = Entry(self.tab1, width=5)
        self.iouEntry.grid(row=5, column=0, sticky=E, padx=5, pady=5)
        self.iouEntry.insert(0, "0.5")

        self.confidenceEntry = Entry(self.tab1, width=5, text=0.5)
        self.confidenceEntry.grid(row=6, column=0, sticky=E, padx=5, pady=5)
        self.confidenceEntry.insert(0, "0.5")

        self.loadWeightsButton = Button(self.tab1, text="Load Weights", command=self.thread_start_weights)
        self.loadWeightsButton.grid(row=4, column=0, padx=5, pady=5)

        self.analyseButton = Button(self.tab1, text="Analyse", command=self.start_analyse, style="G.TButton")
        self.analyseButton.grid(row=8, column=0, padx=5, pady=5, ipady=10)
        # print(self.analyseButton.winfo_class())

        self.pollingButton = Button(self.tab1, text="Start polling", command=self.start_polling, style="P.TButton")
        self.pollingButton.grid(row=13, column=0, padx=5, pady=5)

        self.saveSettingsButton = Button(self.tab2, text="Save settings", command=self.save_options_json)
        self.saveSettingsButton.grid(row=6, column=0, padx=5, pady=5)

        self.textColorButton = Button(self.tab2, text="Text color", command=self.pick_text_color)
        self.textColorButton.grid(row=0, column=2, padx=5, pady=5)

        self.textStrokeColorButton = Button(self.tab2, text="Text stroke color", command=self.pick_text_stroke_color)
        self.textStrokeColorButton.grid(row=1, column=2, padx=5, pady=5)

        self.txt = Text(self.tab1, height=30, width=50)
        self.txt.grid(row=0, column=2, pady=5, rowspan=16, padx=5)

        self.vsb = Scrollbar(self.tab1, orient="vertical", command=self.txt.yview)
        self.vsb.grid(row=0, column=2, sticky="nse", rowspan=16, padx=5, pady=5)
        self.txt.configure(yscrollcommand=self.vsb.set)

        self.weightsLocation = self.analyser_config['weightsPath']
        self.classesLocation = self.analyser_config['namesPath']

        self.weightsLabel = Label(self.tab1, text=os.path.basename(self.weightsLocation), width=37, anchor=CENTER)
        self.weightsLabel.grid(row=5, column=0, padx=5, pady=5)

        self.classesLabel = Label(self.tab1, text=os.path.basename(self.classesLocation), width=37, anchor=CENTER)
        self.classesLabel.grid(row=6, column=0, padx=5, pady=5)

        self.iouLbl = Label(self.tab1, text="iou")
        self.iouLbl.grid(row=5, column=1, padx=5, pady=5)

        self.confidenceLbl = Label(self.tab1, text="confidence")
        self.confidenceLbl.grid(row=6, column=1, padx=5, pady=5)

        self.textColorLabel = Label(self.tab2, width=5, borderwidth=2, relief="sunken")
        self.textColorLabel.grid(row=0, column=1, padx=5, pady=5)
        # self.textColorLabel.configure(background='black')
        self.textColorLabel['background'] = self.textColorHex

        self.textStrokeColorLabel = Label(self.tab2, width=5, borderwidth=2, relief="sunken")
        self.textStrokeColorLabel.grid(row=1, column=1, padx=5, pady=5)
        # self.textStrokeColorLabel.configure(background='black')
        self.textStrokeColorLabel['background'] = self.textStrokeColorHex

        self.createCsv = BooleanVar()
        self.csvCheckButton = Checkbutton(self.tab2, text="Create CSV", variable=self.createCsv, onvalue=True,
                                          offvalue=False)
        self.csvCheckButton.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.createCsv.set(self.analyser_config.get("createCsv"))
        self.toggle_checkbutton(self.csvCheckButton, self.createCsv)

        self.printClasses = BooleanVar()
        self.printClassesCheckButton = Checkbutton(self.tab2, text="Print Classes", variable=self.printClasses,
                                                   onvalue=True, offvalue=False)
        self.printClassesCheckButton.grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.printClasses.set(self.analyser_config.get("printClasses"))
        self.toggle_checkbutton(self.printClassesCheckButton, self.printClasses)

        self.printIou = BooleanVar()
        self.printIouCheckButton = Checkbutton(self.tab2, text="Print Iou", variable=self.printIou,
                                               onvalue=True, offvalue=False)
        self.printIouCheckButton.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.printIou.set(self.analyser_config.get("printIou"))
        self.toggle_checkbutton(self.printIouCheckButton, self.printIou)

        self.printConfidence = BooleanVar()
        self.printConfidenceCheckButton = Checkbutton(self.tab2, text="Print Confidence", variable=self.printConfidence,
                                                      onvalue=True, offvalue=False)
        self.printConfidenceCheckButton.grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.printConfidence.set(self.analyser_config.get("printConfidence"))
        self.toggle_checkbutton(self.printConfidenceCheckButton, self.printConfidence)

        self.printNamesPath = BooleanVar()
        self.printNamesPathCheckButton = Checkbutton(self.tab2, text="Print Names Path", variable=self.printNamesPath,
                                                     onvalue=True, offvalue=False)
        self.printNamesPathCheckButton.grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.printNamesPath.set(self.analyser_config.get("printNamesPath"))
        self.toggle_checkbutton(self.printNamesPathCheckButton, self.printNamesPath)

        self.printWeightsPath = BooleanVar()
        self.printWeightsPathCheckButton = Checkbutton(self.tab2, text="Print Weights Path",
                                                       variable=self.printWeightsPath,
                                                       onvalue=True, offvalue=False)
        self.printWeightsPathCheckButton.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.printWeightsPath.set(self.analyser_config.get("printWeightsPath"))
        self.toggle_checkbutton(self.printWeightsPathCheckButton, self.printWeightsPath)

        self.usePollingLocation = BooleanVar()
        self.PollingCheckButton = Checkbutton(self.tab1, text="Use polling location for saving",
                                              variable=self.usePollingLocation, onvalue=True, offvalue=False,
                                              command=self.disable_polling_save_location)
        self.PollingCheckButton.grid(row=11, column=0, columnspan=2, sticky=E, padx=5, pady=5)

    def open_file(self):
        """
        Open image or video file
        """
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
        """
        Select weights file
        """
        ftypes = [('Weights', '*.weights')]
        self.weightsLocation = fd.askopenfilename(filetypes=ftypes)
        if self.weightsLocation == "":
            self.weightsLocation = "./weights/yolov3.weights"
        self.weightsFileEntry.delete(0, END)
        self.weightsFileEntry.insert(0, self.weightsLocation)
        print(self.weightsLocation)

    def select_classes(self):
        """
        Select classes file
        """
        ftypes = [('Classes', '*.names')]
        self.classesLocation = fd.askopenfilename(filetypes=ftypes)
        if self.classesLocation == "":
            self.classesLocation = "./data/labels/coco.names"
        self.classesFileEntry.delete(0, END)
        self.classesFileEntry.insert(0, self.classesLocation)
        print(self.classesLocation)

    def class_names(self):
        """
        Write class names into csv file
        """
        class_names = utils.load_class_names(self.classesFileEntry.get())
        class_names.insert(0, "frame")
        print(class_names)
        filename = "test_file.csv"
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvfile.write("sep=,")
            csvfile.write('\n')
            csvwriter.writerow(class_names)

    def select_folder(self, entry):
        """
        Select folder location and appends it to entry
        :param entry: Entry widget
        :return: None
        """
        folderLocation = fd.askdirectory()
        if folderLocation == "":
            folderLocation = os.getcwd()
        entry.delete(0, END)
        entry.insert(0, folderLocation)
        print(folderLocation)

    def start_polling(self):
        """
        Starts and stops polling
        """
        if not self.isPolling:
            self.save_threshold_json()
            self.pollingButton['text'] = "Stop polling"
            self.pollingButton['style'] = "R.TButton"
            self.append_text("Polling started in location:\n" + self.pollingLocationEntry.get())
            self.isPolling = True
            polling_thread = threading.Thread(target=self.start_polling_thread)
            polling_thread.start()
        elif self.isPolling:
            self.pollingButton['text'] = "Start polling"
            self.pollingButton['style'] = 'P.TButton'
            self.append_text("Polling stopped")
            self.isPolling = False
            self.pollingWatcher.stop()

    def start_polling_thread(self):
        """
        Starts polling thread
        """
        namespath = self.classesLocation
        try:
            namespathfile = open("namespath.txt")
            namespath = namespathfile.read()
            namespathfile.close()
        except Exception as err:
            self.append_text("Couldn't read namespath.txt, using default .names")
            self.append_text(err)
        if self.usePollingLocation.get():
            self.pollingWatcher = watcher.ImagesWatcher(self.pollingLocationEntry.get(), float(self.iouEntry.get()),
                                                        float(self.confidenceEntry.get()), namespath,
                                                        self.createCsv.get(),
                                                        self.pollingLocationEntry.get())
        else:
            self.pollingWatcher = watcher.ImagesWatcher(self.pollingLocationEntry.get(), float(self.iouEntry.get()),
                                                        float(self.confidenceEntry.get()), namespath,
                                                        self.createCsv.get(),
                                                        self.pollingSaveLocationEntry.get())
        self.pollingWatcher.run()

    def start_analyse(self):
        """
        Starts Analyse
        """

        if pathlib.Path(self.dlg[0]).suffix.lower() in self.video_extensions:
            print(pathlib.Path(self.dlg[0]).suffix)
            analyse_thread_video = threading.Thread(target=self.analyse_video)
            analyse_thread_video.start()

        elif pathlib.Path(self.dlg[0]).suffix.lower() in self.image_extensions:
            print(pathlib.Path(self.dlg[0]).suffix)
            analyse_thread_images = threading.Thread(target=self.analyse_images)
            analyse_thread_images.start()
        else:
            self.append_text("Selected file or files are not supported")

    def append_text(self, string):
        """
        Append text to text box
        """
        self.txt.insert(END, "\n" + str(string))
        self.txt.see(END)

    def thread_start_weights(self):
        """
        Start load weights thread
        """

        if self.classesFileEntry.get() == "" or self.weightsFileEntry.get() == "":
            print("no selected classes or weights")
            self.append_text("no selected classes or weights")

            return
        else:
            t = threading.Thread(target=self.start_load_weights)
            t.start()

    def start_load_weights(self):
        """
        Loads weights
        """
        try:
            self.append_text("Loading weights...")
            load_weights.main(weights_file=self.weightsFileEntry.get(), class_names_file=self.classesFileEntry.get())

            self.save_paths_json()
            self.append_text("Weights loaded")
            self.weightsLabel['text'] = os.path.basename(self.weightsFileEntry.get())
            self.classesLabel['text'] = os.path.basename(self.classesFileEntry.get())
        except Exception as err:
            self.append_text("error loading weights")
            print(err)

    def analyse_images(self):
        """
        Analyse image
        """
        self.save_threshold_json()
        namespath = self.analyser_config['namesPath']

        try:
            self.append_text("Starting image analysis...")
            detect.main("images", self.dlg, self.saveLocationEntry.get(), float(self.iouEntry.get()),
                        float(self.confidenceEntry.get()), namespath)
            self.append_text("Image analysis ended successfully")
        except Exception as err:
            self.append_text("error in image analysis")
            print(err)

    def analyse_video(self):
        """
        Analyse video
        """
        self.save_threshold_json()
        namespath = self.analyser_config['namesPath']
        try:
            self.append_text("Starting video analysis...")
            detect.main("video", self.dlg, self.saveLocationEntry.get(), float(self.iouEntry.get()),
                        float(self.confidenceEntry.get()), namespath, self.createCsv.get())
            self.append_text("Video analysis ended successfully")
        except Exception as err:
            self.append_text("error in video analysis")
            self.append_text(err)

    def test(self):
        """
        test function
        """
        color_code = colorchooser.askcolor(title="Choose color")
        self.append_text(color_code[1])
        self.append_text(color_code[0])
        self.textColorLabel['background'] = color_code[1]
        self.textStrokeColorLabel['background'] = color_code[1]

    def pick_text_color(self):
        """
        Pick color for the text that is printed on
        analysed images and videos.
        """

        color_code = colorchooser.askcolor(title="Choose color for text")
        if None not in color_code:
            self.textColorRGB = color_code[0]
            self.textColorHex = color_code[1]
            self.textColorLabel['background'] = color_code[1]
            self.append_text("New text color: " + color_code[1])
            self.append_text(color_code[0])

    def pick_text_stroke_color(self):
        """
        Pick color for the text stroke that is printed on
        analysed images and videos.
        """

        color_code = colorchooser.askcolor(title="Choose color for text stroke")
        if None not in color_code:
            self.textStrokeColorRGB = color_code[0]
            self.textStrokeColorHex = color_code[1]
            self.textStrokeColorLabel['background'] = color_code[1]
            self.append_text("New text stroke color: " + color_code[1])
            self.append_text(color_code[0])

    def disable_polling_save_location(self):
        """
        Disables the usage of custom save location in polling
        """
        if self.usePollingLocation.get():
            self.pollingSaveLocationButton.configure(state=DISABLED)
            self.pollingSaveLocationEntry.configure(state=DISABLED)
            self.append_text("Disabled Polling save location")
            print(self.pollingLocationEntry.get())
        else:
            self.pollingSaveLocationButton.configure(state=NORMAL)
            self.pollingSaveLocationEntry.configure(state=NORMAL)
            self.append_text("Enabled Polling save location")
            print(self.pollingSaveLocationEntry.get())

    def disable_event(self):
        """
        Destroys Ui and stops polling
        """
        if self.isPolling:
            self.pollingWatcher.stop()
            self.isPolling = False
        self.parent.destroy()

    def toggle_checkbutton(self, checkbutton, stateVariable):
        """
        Checks or unchecks given check button
        :param checkbutton: checkbutton widget
        :param stateVariable: Boolean
        :return: None
        """
        checkbutton.state(['!alternate'])
        if stateVariable.get():
            checkbutton.state(['selected'])
        else:
            checkbutton.state(['!selected'])

    def save_options_json(self):
        """
        Saves options to json
        """
        config_location = 'config.json'

        if os.path.exists(config_location):
            config = json.load(open(config_location))

        config['printClasses'] = self.printClasses.get()
        config['printIou'] = self.printIou.get()
        config['printConfidence'] = self.printConfidence.get()
        config['printNamesPath'] = self.printNamesPath.get()
        config['printWeightsPath'] = self.printWeightsPath.get()
        config['createCsv'] = self.createCsv.get()
        config['textColorHex'] = self.textColorHex
        config['textColorRGB'] = self.textColorRGB
        config['textStrokeColorHex'] = self.textStrokeColorHex
        config['textStrokeColorRGB'] = self.textStrokeColorRGB

        json.dump(config, open(config_location, 'w'), sort_keys=True, indent=4)
        self.analyser_config = config
        self.append_text("Settings saved")
        return config

    def save_paths_json(self):
        """
        Saves names and weights path to json
        """
        config_location = 'config.json'

        if os.path.exists(config_location):
            config = json.load(open(config_location))

        config['namesPath'] = self.classesFileEntry.get()
        config['weightsPath'] = self.weightsFileEntry.get()

        json.dump(config, open(config_location, 'w'), sort_keys=True, indent=4)

        self.analyser_config = config
        return config

    def save_threshold_json(self):
        """
        Saves iou and confidence to json
        """
        config_location = 'config.json'

        if os.path.exists(config_location):
            config = json.load(open(config_location))
        config['iou'] = self.iouEntry.get()
        config['confidence'] = self.confidenceEntry.get()

        json.dump(config, open(config_location, 'w'), sort_keys=True, indent=4)

        self.analyser_config = config
        return config


def main():
    """
    Create Ui Window and start Ui mainloop
    """
    root = Tk()

    ui = UI(root)
    s = ttk.Style()
    s.theme_use('vista')
    s.configure("G.TButton", background="#32a62e")
    s.configure("P.TButton", background='#b828ae')
    s.configure("R.TButton", background="red")
    s.configure("B.TFrame", bacground="red")
    print(s.theme_names())
    root.protocol("WM_DELETE_WINDOW", ui.disable_event)
    root.geometry("860x520+300+300")
    root.mainloop()


if __name__ == '__main__':
    main()
