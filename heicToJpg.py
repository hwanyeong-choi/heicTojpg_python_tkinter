
from PIL import Image, ImageTk
from pillow_heif import register_heif_opener
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import threading
import concurrent.futures

register_heif_opener()

class ConvertImageType:
    def __init__(self, type, fileNameType):
        self.type = type
        self.fileNameType = fileNameType

sourceDirectory = ""
fileList = []
imageType = {}
imageTypeList = ["JPEG", "PNG"]

imageType["JPEG"] = ConvertImageType("JPEG", "jpg")
imageType["PNG"] = ConvertImageType("PNG", "png")

def selectDirectory():
    global sourceDirectory
    sourceDirectory = filedialog.askdirectory()
    if sourceDirectory:
        sourceDirectoryLabel.config(text=f"HEIC 파일 폴더 선택: {sourceDirectory}")
        updateFileList()

def updateFileList():
    global fileList
    fileListbox.delete(0, tk.END)
    heic_files = [f for f in os.listdir(sourceDirectory) if (f.endswith('.heic') or f.endswith(".HEIC"))]
    for file in heic_files:
        fileList.append(file)
        fileListbox.insert(tk.END, file)

def showMessageBox(type, message):
    if (type == "warn"):
        messagebox.showwarning("알림", message)
        return

    messagebox.showinfo("알림", message)

def heicToJpgConvertStartValidation(selectedFilesSize):
    if (len(sourceDirectory.strip()) == 0):
        showMessageBox("warn", "파일 조회를 위해 폴더를 선택해 주세요.")
        return False

    if (selectedFilesSize == 0):
        showMessageBox("warn", "변환할 파일이 존재하지 않습니다.")
        return False

    return True

def convertToJpgFile(file):
    heicFilePath = os.path.join(sourceDirectory, file)
    jpg_file_path = os.path.join(f"{sourceDirectory}/{imageType[imageTypeCombo.get()].fileNameType}", str(os.path.splitext(file)[0]) + f".{imageType[imageTypeCombo.get()].fileNameType}")

    with Image.open(heicFilePath) as image:
        iccProfile = image.info.get("icc_profile")
        exif = image.getexif()
        image.save(jpg_file_path, imageType[imageTypeCombo.get()].type, exif=exif, icc_profile=iccProfile)

def convertToJpg():
    progressVar.set(0)
    selectedFilesSize = len(fileList)
    increment = (1 / selectedFilesSize) * 100

    if (not heicToJpgConvertStartValidation(selectedFilesSize)): return

    if not os.path.exists(f"{sourceDirectory}/{imageType[imageTypeCombo.get()].fileNameType}"):
        os.mkdir(f"{sourceDirectory}/{imageType[imageTypeCombo.get()].fileNameType}")

    if fileList and sourceDirectory:
        with concurrent.futures.ThreadPoolExecutor(max_workers=round(os.cpu_count() * 0.7)) as executor:
            futures = [executor.submit(convertToJpgFile, file) for file in fileList]
            for future in concurrent.futures.as_completed(futures):
                progressVar.set(round(progressVar.get() + increment))
                root.update_idletasks()

    progressVar.set(100)
    showMessageBox("info", "변환 완료")

def handleSelection(event):
    selected_index = fileListbox.curselection()

    if selected_index:
        selected_file = fileListbox.get(selected_index)
        heicFilePath = f"{sourceDirectory}/{selected_file}"
        loadImage(heicFilePath)

        with Image.open(heicFilePath) as image:
            exif = image.getexif()
            exifInfo = f"[제조사: {exif[271]}] [촬영기종: {exif[316]}] [촬영일자: {exif[306]}]"
            exifInfoLabel.config(text=exifInfo)

def resizeImage(image, canvas_width, canvas_height):
    img_width, img_height = image.size
    ratio = min(canvas_width / img_width, canvas_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def loadImage(path):
    image = Image.open(path)
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    resized_image = resizeImage(image, canvas_width, canvas_height)
    photo = ImageTk.PhotoImage(resized_image)
    canvas_image = canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo, anchor='center')
    canvas.image = photo

def convertToJpgStartThread():
    thread = threading.Thread(target=convertToJpg)
    thread.daemon = True
    thread.start()

root = tk.Tk()
root.title("Heic To Jpg")
root.resizable(False, False)

#
sourceSelectButton = tk.Button(root, width=20, text="HEIC 파일 폴더 선택", command=selectDirectory)
sourceSelectButton.grid(row=0, column=0, padx=10, pady=10, sticky='news')

imageTypeCombo = ttk.Combobox(root, values=imageTypeList, state='readonly')
imageTypeCombo.set(imageTypeList[0])
imageTypeCombo.grid(row=0, column=1, padx=10, pady=10,sticky='news')

sourceDirectoryLabel = tk.Label(root, width=70, anchor='w', text="HEIC 파일 폴더 선택")
sourceDirectoryLabel.grid(row=0, column=2, padx=10, pady=10, sticky='news')
#

#
fileListbox = tk.Listbox(root, width=35, height=15, selectmode=tk.SINGLE)
fileListbox.bind('<<ListboxSelect>>', handleSelection)
fileListbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='news')
#

#
canvas = tk.Canvas(root, width=600, height=300, bg="white")
canvas.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='news')
#

#
exifInfoLabel = tk.Label(root, width=40, anchor='w', text="EXIF 정보")
exifInfoLabel.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='news')
#

#
progressVar = tk.DoubleVar()
progressBar = ttk.Progressbar(root, variable=progressVar, maximum=100)
progressBar.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='news')

convertButton = tk.Button(root, text="전체 HEIC to JPG 변환", command=convertToJpgStartThread)
convertButton.grid(row=4, column=2, padx=10, pady=10, sticky='news')
#

root.after(50)

root.mainloop()
