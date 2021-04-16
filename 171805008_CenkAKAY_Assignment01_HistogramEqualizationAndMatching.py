from PIL import Image
import PySimpleGUI as sg
import io
import cv2
import numpy
import matplotlib.pyplot as plt
import copy

# Created Images class for Original and Desired image objects.
class Images:

    # Defined attributes of image object.
    def __init__(self, PILimage):
        self.PILimage = PILimage
        self.SizedCvImage = None
        self.ImageSize = 500
        self.HistogramImage = None
        self.HistogramArray = None
        self.EqualizedImage = None
        self.ArrayforEqualization = None

    # PIL image changed to Sized CV image.
    def PILtoSızedCV(self):
        cvImage = cv2.cvtColor(numpy.array(self.PILimage), cv2.COLOR_RGB2GRAY)
        self.SizedCvImage = cv2.resize(
            cvImage, (self.ImageSize, self.ImageSize), interpolation=cv2.INTER_AREA
        )

    # Created histogram plot and transformed to PIL image.
    def GetHıstogramPILImage(self):
        ImageHistogramArray = numpy.zeros(([256]))
        copySizedCvImage = copy.deepcopy(self.SizedCvImage)
        for x in range(copySizedCvImage.shape[0]):
            for y in range(copySizedCvImage.shape[1]):
                px_vl = copySizedCvImage[x, y]
                ImageHistogramArray[px_vl] = ImageHistogramArray[px_vl] + 1

        self.HistogramArray = copy.deepcopy(ImageHistogramArray)
        plt.figure()
        plt.title("Histogram of Image")
        plt.bar(numpy.arange(len(ImageHistogramArray)), ImageHistogramArray)
        plt.xlabel("Gray Level")
        plt.ylabel("No. of Pixel (Counting)")

        Originalpic_IObytes = io.BytesIO()
        plt.savefig(Originalpic_IObytes, format="png")
        Originalpic_IObytes.seek(0)
        plt.close()
        self.HistogramImage = copy.deepcopy(Image.open(Originalpic_IObytes))
    
    # Histgoram Equalization operations have been done.
    def histogramEqualization(self):
        ProcessedArray = numpy.zeros(([256]))
        copyHistogramArray = copy.deepcopy(self.HistogramArray)
        for x in range(len(copyHistogramArray)):
            ProcessedArray[x] = copyHistogramArray[x] / (
                self.ImageSize * self.ImageSize
            )
        for x in range(len(copyHistogramArray) - 1):
            ProcessedArray[x + 1] = ProcessedArray[x] + ProcessedArray[x + 1]
        for x in range(len(copyHistogramArray)):
            ProcessedArray[x] = ProcessedArray[x] * 255

        self.ArrayforEqualization = copy.deepcopy(ProcessedArray)
    # Equalized image getted.
    def getEqualizedImage(self):
        tempImage = copy.deepcopy(self.SizedCvImage)
        copyArrayforEqualization = copy.deepcopy(self.ArrayforEqualization)
        for k in range(tempImage.shape[0]):
            for y in range(tempImage.shape[1]):
                originalGreyValue = tempImage[k, y]
                tempImage[k, y] = copyArrayforEqualization[originalGreyValue]
        self.EqualizedImage = copy.deepcopy(tempImage)

# Function for finding nearest value in the array. Used for image value matching.
def find_nearest_value(array, value):
    idx_sorted = numpy.argsort(array)
    sorted_array = numpy.array(array[idx_sorted])
    idx = numpy.searchsorted(sorted_array, value, side="left")
    if idx >= len(array):
        idx_nearest = idx_sorted[len(array) - 1]
    elif idx == 0:
        idx_nearest = idx_sorted[0]
    else:
        if abs(value - sorted_array[idx - 1]) < abs(value - sorted_array[idx]):
            idx_nearest = idx_sorted[idx - 1]
        else:
            idx_nearest = idx_sorted[idx]
    return idx_nearest

# Two image matched here.
def MatchtheImages():
    desiredImage.histogramEqualization()
    matchedArray = copy.deepcopy(originalImage.ArrayforEqualization)
    NondublicateArrayDesired = numpy.unique(
        copy.deepcopy(desiredImage.ArrayforEqualization), axis=0
    )
    for x in range(256):
        matchedArray[x] = find_nearest_value(NondublicateArrayDesired, matchedArray[x])

    matchedImage = copy.deepcopy(originalImage.SizedCvImage)
    for k in range(matchedImage.shape[0]):
        for y in range(matchedImage.shape[1]):
            originalGreyValue = matchedImage[k, y]
            matchedImage[k, y] = matchedArray[originalGreyValue]
    return matchedImage

# Histogram image function for non object images.
def getHistogramImageofEqualizedCvImage(cvimage):
    TempHistogramArray = numpy.zeros(([256]))
    for x in range(cvimage.shape[0]):
        for y in range(cvimage.shape[1]):
            px_vl = cvimage[x, y]
            TempHistogramArray[px_vl] = TempHistogramArray[px_vl] + 1

    plt.figure()
    plt.title("Histogram of Image")
    plt.bar(numpy.arange(len(TempHistogramArray)), TempHistogramArray)
    plt.xlabel("Gray Level")
    plt.ylabel("No. of Pixel (Counting)")

    Originalpic_IObytes = io.BytesIO()
    plt.savefig(Originalpic_IObytes, format="png")
    Originalpic_IObytes.seek(0)
    plt.close()
    HistogramImageofEqualizedCvImage = Image.open(Originalpic_IObytes)
    return HistogramImageofEqualizedCvImage

# PySimpleGUI only support PNG files so end of the process we format to PNG for showing image on gui.
def FormatToPngForShow(image):
    image.thumbnail((400, 400), Image.ANTIALIAS)
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    return bio

# Layout for GUI.
layout = [
    [
        sg.Image(key="ShowedImage"),
        sg.Image(key="ShowedImage2"),
        sg.Image(key="ShowedImage5"),
    ],
    [
        sg.Image(key="ShowedImage3"),
        sg.Image(key="ShowedImage4"),
        sg.Image(key="ShowedImage6"),
    ],
    [
        sg.Input(key="_FILEBROWSE_ORIGINAL", enable_events=True, visible=False),
        sg.FileBrowse(
            button_text="1) SELECT ORIGINAL IMAGE",
            target="_FILEBROWSE_ORIGINAL",
            file_types=(
                (
                    "Image Files",
                    "*.jpg *.jpeg *.png *.bmp *.tiff *.dib *.eps *.gif *.ico *.im *.jp2 *.msp *.pcx *.ppm *.sgi *.tga *.webp *.xbm",
                ),
            ),
        ),
        sg.Input(key="_FILEBROWSE_TARGET", enable_events=True, visible=False),
        sg.FileBrowse(
            button_text="2) SELECT DESIRED IMAGE",
            target="_FILEBROWSE_TARGET",
            file_types=(
                (
                    "Image Files",
                    "*.jpg *.jpeg *.png *.bmp *.tiff *.dib *.eps *.gif *.ico *.im *.jp2 *.msp *.pcx *.ppm *.sgi *.tga *.webp *.xbm",
                ),
            ),
        ),
        sg.Button(button_text="3) HISTOGRAM GRAPH OF IMAGES", key="HISTOGRAMBUTTON"),
        sg.Button(
            button_text="4) HISTOGRAM EQUALIZATION OF ORIGINAL IMAGE",
            key="HISTOGRAMEQUALIZATIONBUTTON",
        ),
        sg.Button(
            button_text="5) MATCH THE ORIGINAL IMAGE BY DESIRED IMAGE", key="MATCH",
        ),
    ],
]

# GUI's window matched with layout.
window = sg.Window(
    "HISTOGRAM EQUALIZATION AND MATCHING", auto_size_buttons=True, location=(100, 40)
).Layout(layout)

# Event loop for caught actions on the GUI.
while True:
    event, values = window.read()
    # To close the program break line.
    if event is None:
        break
    # Actions for first button.
    elif event == "_FILEBROWSE_ORIGINAL":
        originalImage = Images(Image.open(values["_FILEBROWSE_ORIGINAL"]))
        originalImage.PILtoSızedCV()
        bio = FormatToPngForShow(copy.deepcopy(originalImage.PILimage))
        window["ShowedImage"].update(data=bio.getvalue())
    # Actions for second button.
    elif event == "_FILEBROWSE_TARGET":
        desiredImage = Images(Image.open(values["_FILEBROWSE_TARGET"]))
        desiredImage.PILtoSızedCV()
        bio2 = FormatToPngForShow(copy.deepcopy(desiredImage.PILimage))
        window["ShowedImage2"].update(data=bio2.getvalue())
    # Actions for third button.
    elif event == "HISTOGRAMBUTTON":
        image3 = Image.fromarray(originalImage.SizedCvImage)
        bio3 = FormatToPngForShow(image3)
        window["ShowedImage"].update(data=bio3.getvalue())

        originalImage.GetHıstogramPILImage()
        image = copy.deepcopy(originalImage.HistogramImage)
        bio = FormatToPngForShow(image)
        window["ShowedImage3"].update(data=bio.getvalue())

        desiredImage.GetHıstogramPILImage()
        image2 = copy.deepcopy(desiredImage.HistogramImage)
        bio2 = FormatToPngForShow(image2)
        window["ShowedImage4"].update(data=bio2.getvalue())

        image4 = Image.fromarray(desiredImage.SizedCvImage)
        bio4 = FormatToPngForShow(image4)
        window["ShowedImage2"].update(data=bio4.getvalue())
    # Actions for fourth button.
    elif event == "HISTOGRAMEQUALIZATIONBUTTON":
        originalImage.histogramEqualization()
        originalImage.getEqualizedImage()
        image = Image.fromarray(copy.deepcopy(originalImage.EqualizedImage))
        bio = FormatToPngForShow(image)
        window["ShowedImage2"].update(data=bio.getvalue())

        image2 = getHistogramImageofEqualizedCvImage(
            copy.deepcopy(originalImage.EqualizedImage)
        )
        bio2 = FormatToPngForShow(image2)
        window["ShowedImage4"].update(data=bio2.getvalue())
    # Actions for fifth button.
    elif event == "MATCH":
        image2 = Image.fromarray(desiredImage.SizedCvImage)
        bio2 = FormatToPngForShow(image2)
        window["ShowedImage2"].update(data=bio2.getvalue())

        cvMatchedImage = MatchtheImages()
        image = Image.fromarray(cvMatchedImage)
        hisImageMatched = getHistogramImageofEqualizedCvImage(cvMatchedImage)
        bio = FormatToPngForShow(image)
        window["ShowedImage5"].update(data=bio.getvalue())

        image3 = copy.deepcopy(hisImageMatched)
        bio3 = FormatToPngForShow(image3)
        window["ShowedImage6"].update(data=bio3.getvalue())

        desiredImage.GetHıstogramPILImage()
        image4 = copy.deepcopy(desiredImage.HistogramImage)
        bio4 = FormatToPngForShow(image4)
        window["ShowedImage4"].update(data=bio4.getvalue())
        
#After the breaking of loop method for close window. 
window.close()

