import os
from tkinter import *
from tkinter import filedialog as fd
import load_weights

dlg = os.getcwd()
saveLocation = os.getcwd()
weightsLocation = ""
classesLocation = ""


class UI(Frame):

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

        self.openButton = Button(self.parent, text="Open file", command=self.onOpen)
        self.openButton.grid(row=0, column=1)

        self.saveButton = Button(self.parent, text="Save location", command=self.selectSaveLocation)
        self.saveButton.grid(row=1, column=1)

        # iou & confidence
        # select .weights & select classes .names

        self.loadWeightsButton = Button(self.parent,text="Load Weights", command=self.startLoadWeights)
        self.loadWeightsButton.grid(row=2,column=0)

        self.analyseButton = Button(self.parent, text="Analyse", command=self.startAnalyse)
        self.analyseButton.grid(row=3, column=0)

        self.lbl = Label(self.parent, text="asd")
        self.lbl.grid(row=4, column=0)

    # self.txt = Text(self.parent)
    # self.txt.grid(column=0,row=0)
    # self.txt.pack(fill=BOTH, expand=1)

    # self.lbl = Label(self, text="asd").grid(row=1,column=0)
    # self.lbl.grid(column=1,row=0)
    # self.lbl.pack(fill=BOTH, expand=1)

    def onOpen(self):
        ftypes = [('Video and images', '*.mp4 *.jpg'), ('All files', '*')]
        # dlg = tkFileDialog.Open(self, filetypes = ftypes)
        dlg = fd.askopenfilename(filetypes=ftypes)
        # fl = dlg.show()
        print(dlg)

        if dlg == '':
            dlg = os.getcwd()
            print(dlg)
        # self.txt.insert(END, dlg)
        self.lbl['text'] = dlg
        self.openFileEntry.delete(0, END)
        self.openFileEntry.insert(0, dlg)

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
        ftypes = [('Weights', '*.weights'), ('All files', '*')]
        weightsLocation = fd.askopenfilename(filetypes=ftypes)
        print(weightsLocation)

    def selectClasses(self):
        ftypes = [('Classes', '*.names'), ('All files', '*')]
        classesLocation = fd.askopenfilename(filetypes=ftypes)
        print(classesLocation)

    def selectSaveLocation(self):
        saveLocation = fd.askdirectory()
        self.saveFileEntry.delete(0, END)
        self.saveFileEntry.insert(0, saveLocation)
        print(saveLocation)

    def startAnalyse(self):
        print(saveLocation)

    def startLoadWeights(self):
        load_weights

def main():
    root = Tk()
    ui = UI(root)
    root.geometry("400x450+300+300")
    root.mainloop()


if __name__ == '__main__':
    main()
