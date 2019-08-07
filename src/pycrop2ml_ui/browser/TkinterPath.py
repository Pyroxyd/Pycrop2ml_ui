from tkinter import filedialog, Tk
import os
import sys

def getPath():
    """
    Returns the selected directory path.
    """
    
    root = Tk()
    root.wm_attributes('-topmost', 1)
    root.directory = filedialog.askdirectory()

    try:
        return root.directory.replace('/', os.path.sep)
    
    except:
        sys.stderr.write('Critical error while fetching the path.')

    finally:
        root.destroy()