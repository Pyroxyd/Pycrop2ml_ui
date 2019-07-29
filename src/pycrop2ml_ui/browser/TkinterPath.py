from tkinter import filedialog, Tk


def getPath():
    
    root = Tk()
    root.wm_attributes('-topmost', 1)
    root.directory = filedialog.askdirectory()

    try:
        return root.directory.replace('/', '\\')+'\\crop2ml'
    
    except:
        raise Exception('Critical error while fetching the path.')

    finally:
        root.destroy()