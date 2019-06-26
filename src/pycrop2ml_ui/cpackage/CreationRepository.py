import ipywidgets as wg
import os
import sys

from IPython.display import display
from cookiecutter.main import cookiecutter
from path import Path

from pycrop2ml_ui.browser.Path import FileBrowser

class mkdirModel:

    def __init__(self):

        self.input1 = wg.Textarea(value='AgriculturalModelExchangeIniative',description='Project name',disabled=False)
        self.input2 = wg.Textarea(value='',description='Repository name',disabled=False)
        self.input3 = wg.Textarea(value='',description='Author name',disabled=False)
        self.input4 = wg.Textarea(value='',description='Description',disabled=False)

        self.inputPath = wg.Textarea(value='',description='Path',disabled=True)
        self.buttonPath = wg.Button(value=False,description='Browse',disabled=False,background_color='#d0d0ff')

        self.create = wg.Button(value=False,description='Create',disabled=False,button_style='success')
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        self.displayer = wg.VBox([self.input1, self.input2, wg.HBox([self.inputPath, self.buttonPath]), self.input3, self.input4, wg.HBox([self.create, self.cancel])])

        self.out = wg.Output()
        self.out2 = wg.Output()


    def eventCreate(self, b):
        self.out2.clear_output()
        if(self.input1.value and self.input2.value and self.input3.value and self.input4.value and self.inputPath.value):
            with self.out2:
                if(os.path.exists(os.path.abspath(os.path.join(self.inputPath.value, self.input2.value)))):
                    print("This repository already exists.")
                else:
                    print("Creating repository ...")
                    self.create.disabled = True
                    self.cancel.disabled = True
                    
                    try:
                        self.createRepository()
                    except:
                        print("Could not create the repository.")
                        sys.exit(1)
                    else:
                        print("Done.")
                        self.out.clear_output()
                        self.out2.clear_output()

        
        else:
            with self.out2:
                print("Missing argument(s) :")
                if(not self.input1.value):
                    print("\t- Project name")
                if(not self.input2.value):
                    print("\t- Repository name")
                if(not self.inputPath.value):
                    print("\t- Path")
                if(not self.input3.value):
                    print("\t- Author name")
                if(not self.input4.value):
                    print("\t- Description")


    def eventCancel(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        del self

    
    def eventBrowse(self, b):

        def eventTmp(b):
            self.inputPath.value = tmp.path
            self.out2.clear_output()

        self.out2.clear_output()
        tmp = FileBrowser()
        buttontmp = wg.Button(value=False,description='Select',disabled=False,button_style='success')

        with self.out2:
            display(tmp.widget())
            display(buttontmp)
        buttontmp.on_click(eventTmp)


    def createRepository(self):
        cookiecutter("https://github.com/AgriculturalModelExchangeInitiative/cookiecutter-crop2ml", no_input=True, extra_context={'project_name':self.input1.value, 'repo_name':self.input2.value, 'author_name':self.input3.value, 'description':self.input4.value}, output_dir=self.inputPath.value)

    def display(self):

        self.out.clear_output()
        self.out2.clear_output()

        display(self.out)
        with self.out:
            display(self.displayer)
        display(self.out2)
        self.create.on_click(self.eventCreate)
        self.cancel.on_click(self.eventCancel)
        self.buttonPath.on_click(self.eventBrowse)



def main():
    widget = mkdirModel()
    widget.display()
