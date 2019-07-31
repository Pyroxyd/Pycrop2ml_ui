import ipywidgets as wg
import os

from IPython.display import display
from cookiecutter.main import cookiecutter

from pycrop2ml_ui.browser.TkinterPath import getPath



class createPackage:

    def __init__(self):

        self._projectName = wg.Textarea(value='AgriculturalModelExchangeIniative',description='Project name:',disabled=False)
        self._repositoryName = wg.Textarea(value='',description='Repository name:',disabled=False)
        self._authors = wg.Textarea(value='',description='Authors:',disabled=False)
        self._description = wg.Textarea(value='',description='Description:',disabled=False)

        self._inputPath = wg.Textarea(value='',description='Path:',disabled=True)
        self._browse = wg.Button(value=False,description='Browse',disabled=False,button_style='primary')

        self._create = wg.Button(value=False,description='Create',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        self._displayer = wg.VBox([self._projectName, self._repositoryName, wg.HBox([self._inputPath, self._browse]), self._authors, self._description, wg.HBox([self._create, self._cancel])], layout=wg.Layout(align_items='center'))

        self._out = wg.Output()
        self._out2 = wg.Output()




    def _eventCreate(self, b):

        self._out2.clear_output()

        if(self._projectName.value and self._repositoryName.value and self._authors.value and self._description.value and self._inputPath.value):
            
            with self._out2:
                if(os.path.exists(os.path.abspath(os.path.join(self._inputPath.value, self._repositoryName.value)))):
                    print("This repository already exists.")
                else:
                    self._create.disabled = True
                    self._cancel.disabled = True
                    
                    try:
                        cookiecutter("https://github.com/AgriculturalModelExchangeInitiative/cookiecutter-crop2ml", no_input=True, extra_context={'project_name':self._projectName.value, 'repo_name':self._repositoryName.value, 'author_name':self._authors.value, 'description':self._description.value}, output_dir=self._inputPath.value)

                    except:
                        raise Exception("Could not create the repository.")
                    
                    finally:
                        self._out.clear_output()
                        self._out2.clear_output()
                        
                        
        else:
            with self._out2:
                print("Missing argument(s) :")
                if(not self._projectName.value):
                    print("\t- Project name")
                if(not self._repositoryName.value):
                    print("\t- Repository name")
                if(not self._inputPath.value):
                    print("\t- Path")
                if(not self._authors.value):
                    print("\t- Author name")
                if(not self._description.value):
                    print("\t- Description")



    def _eventCancel(self, b):

        self._out.clear_output()
        self._out2.clear_output()
        return



    def _eventBrowse(self, b):

        self._out2.clear_output()
        self._inputPath.value = getPath()



    def displayMenu(self):

        self._out.clear_output()
        self._out2.clear_output()

        display(self._out)
        display(self._out2)

        with self._out:
            display(self._displayer)

        self._create.on_click(self._eventCreate)
        self._cancel.on_click(self._eventCancel)
        self._browse.on_click(self._eventBrowse)
