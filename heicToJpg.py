
from PIL import Image
from pillow_heif import register_heif_opener
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import threading

register_heif_opener()

sourceDirectory, targetDirectory = "", ""

def selectDirectory():
    global sourceDirectory, targetDirectory
    sourceDirectory = filedialog.askdirectory()
    if sourceDirectory:
        sourceDirectoryLabel.config(text=f"원본 디렉토리: {sourceDirectory}")
        updateFileList()

def selectTargetDirectory():
    global targetDirectory
    targetDirectory = filedialog.askdirectory()
    if targetDirectory:
        targetDirectoryLabel.config(text=f"대상 디렉토리: {targetDirectory}")

def updateFileList():
    fileListbox.delete(0, tk.END)
    heic_files = [f for f in os.listdir(sourceDirectory) if (f.endswith('.heic') or f.endswith(".HEIC"))]
    for file in heic_files:
        fileListbox.insert(tk.END, file)

def showMessageBox(type, message):
    if (type == "warn"):
        messagebox.showwarning("알림", message)
        return

    messagebox.showinfo("알림", message)

def heicToJpgConvertStartValidation(selectedFilesSize):
    if (len(sourceDirectory.strip()) == 0):
        showMessageBox("warn", "파일 조회를 위해 원본 디렉토리를 선택해 주세요.")
        return False

    if (len(targetDirectory.strip()) == 0):
        showMessageBox("warn", "변환된 파일을 저장하기 위해 대상 디렉토리를 선택해 주세요.")
        return False

    if (selectedFilesSize == 0):
        showMessageBox("warn", "변환할 파일을 선택해 주세요.")
        return False

    return True

def convertToJpg():
    progressVar.set(0)
    selectedFiles = fileListbox.curselection()
    selectedFilesSize = len(selectedFiles)

    if (not  heicToJpgConvertStartValidation(selectedFilesSize)): return

    if selectedFiles and sourceDirectory and targetDirectory:
        for i in selectedFiles:

            heicFile = fileListbox.get(i)
            heicFilePath = os.path.join(sourceDirectory, heicFile)
            jpg_file_path = os.path.join(targetDirectory, os.path.splitext(heicFile)[0] + ".jpg")

            with Image.open(heicFilePath) as image:
                image.save(jpg_file_path, "JPEG")

            percent =round((i / selectedFilesSize) * 100)
            progressVar.set(percent)
            root.update_idletasks()
            progressLabel.config(text=f"{percent:.1f}%")

    progressLabel.config(text="100%")
    progressVar.set(100)
    showMessageBox("info", "변환 완료")

def convertToJpgStartThread():
    thread = threading.Thread(target=convertToJpg)
    thread.daemon = True
    thread.start()

root = tk.Tk()
root.title("Heic To Jpg")

root.resizable(False, False)

mainFrame = tk.Frame(root, padx=10, pady=10)
mainFrame.pack(fill="both", expand=True)

sourceDirectoryFrame = tk.Frame(mainFrame)
sourceDirectoryFrame.pack(pady=10, fill="x")

sourceSelectButton = tk.Button(sourceDirectoryFrame, text="원본 디렉토리 선택", command=selectDirectory)
sourceSelectButton.pack(side="left")

sourceDirectoryLabel = tk.Label(sourceDirectoryFrame, text="원본 디렉토리: ")
sourceDirectoryLabel.pack(side="left", padx=10)

targetDirectoryFrame = tk.Frame(mainFrame)
targetDirectoryFrame.pack(pady=10, fill="x")

targetSelectButton = tk.Button(targetDirectoryFrame, text="대상 디렉토리 선택", command=selectTargetDirectory)
targetSelectButton.pack(side="left")

targetDirectoryLabel = tk.Label(targetDirectoryFrame, text="대상 디렉토리: ")
targetDirectoryLabel.pack(side="left", padx=10)

fileListbox = tk.Listbox(mainFrame, width=50, height=15, selectmode=tk.MULTIPLE)
fileListbox.pack(pady=10)

progressLabel = tk.Label(mainFrame, text="0 %")
progressLabel.pack()

progressVar = tk.DoubleVar()
progressBar = ttk.Progressbar(mainFrame, variable=progressVar, maximum=100)
progressBar.pack(fill="x", padx=10, pady=10)

convertButton = tk.Button(mainFrame, text="HEIC to JPG 변환", command=convertToJpgStartThread)
convertButton.pack(pady=10)

root.after(50)

root.mainloop()