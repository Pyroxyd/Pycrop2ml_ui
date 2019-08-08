import ipywidgets as wg
import os

from IPython.display import display

from pycrop2ml_ui.menus.creation import createunit
from pycrop2ml_ui.menus.creation import createcomposition

from pycrop2ml_ui.model import MainMenu
from pycrop2ml_ui.browser.TkinterPath import getPath
from pycrop2ml_ui.menus.creation.externalpackage import externalPackageMenu


class createMenu():
    """
    Class providing a display of model creation menu for pycrop2ml's user interface.
    """

    def __init__(self):

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()
        self._outextpkg = wg.Output()
         
        #datas
        self._layout = wg.Layout(width='400px',height='57px')
        self._path = wg.Textarea(value='',description='Path:',disabled=True,layout=self._layout)
        self._modelName = wg.Textarea(value='',description='Name:',disabled=False,layout=self._layout)
        self._modelID = wg.Textarea(value='',description='Model ID:',disabled=False,layout=self._layout)
        self._version = wg.Textarea(value='1.0',description='Version:',disabled=False,layout=self._layout)
        self._timestep = wg.Textarea(value='1',description='Timestep:',disabled=False,layout=self._layout)
        self._title = wg.Textarea(value='',description='Title:',disabled=False,layout=self._layout)
        self._authors = wg.Textarea(value='',description='Authors:',disabled=False,layout=self._layout)
        self._institution = wg.Textarea(value='',description='Institution:',disabled=False,layout=self._layout)
        self._abstract = wg.Textarea(value='',description='Abstract:',disabled=False,layout=self._layout) 
        self._reference = wg.Textarea(value='',description='Reference:',disabled=False,layout=self._layout)
        
        #model type
        self._toggle = wg.ToggleButtons(options=["unit", "composition"], description="Type:", disabled=False, layout=self._layout)
        self._extpkg = wg.Checkbox(value=False,description='Enable external package',indent=True)

        #buttons
        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='warning')
        self._browse = wg.Button(value=False,description='Browse',disabled=False,button_style='primary')

        self._header = wg.VBox([self._toggle,  self._outextpkg, wg.HBox([self._path, self._browse]), self._modelName, self._modelID, self._version, self._timestep, self._title, self._authors, self._institution, self._reference, self._abstract])

        #global menu displayer
        self._displayer = wg.VBox([wg.HTML(value='<font size="5"><b>Model creation : Header</b></font>'), self._header, wg.HBox([self._apply, self._cancel])], layout=wg.Layout(align_items='center'))

        #model datas
        self._datas = dict()


    def _checkFile(self):
        """
        Initializes the model's xml file.
        """

        self._out2.clear_output()
        
        if(any([(os.path.exists("{}{}unit.{}.xml".format(self._datas["Path"], os.path.sep, self._modelName.value)) and self._datas['Model type']=='unit'),
                (os.path.exists("{}{}composition.{}.xml".format(self._datas["Path"], os.path.sep, self._modelName.value)) and self._datas['Model type']=='composition')])):
            
            self._out.clear_output()
            with self._out:
                raise Exception("File composition|unit.{}.xml already exists.".format(self._modelName.value))
        return True



    def _eventApply(self, b):
        """
        Handles apply button on_click event
        """

        self._out2.clear_output()

        if all([self._modelName.value,self._modelID.value,self._timestep.value,self._version.value,self._title.value,
                self._authors.value,self._institution.value,self._abstract.value,self._path.value,self._reference.value]):

            self._datas = {
                        'Path': self._path.value+os.path.sep+'crop2ml',
                        'Model type': self._toggle.value,
                        'Model name': self._modelName.value,
                        'Model ID': self._modelID.value,
                        'Version': self._version.value,
                        'Timestep': self._timestep.value,
                        'Title': self._title.value,
                        'Authors': self._authors.value,
                        'Institution': self._institution.value,
                        'Reference': self._reference.value,
                        'Abstract': self._abstract.value
                        }

            self._out.clear_output()
                
            if self._checkFile():
                with self._out:
                    if self._datas['Model type'] == 'unit':
                        try:   
                            unit = createunit.createUnit(self._datas)
                            unit.displayMenu()
                        except:                      
                            raise Exception('Could not load unit creation model menu.')

                    else:
                        if self._extpkg.value:
                            try:
                                composition = externalPackageMenu(self._datas)
                                composition.displayMenu()
                            except:
                                raise Exception('Could not load external package manager menu.')

                        else:
                            try:
                                composition = createcomposition.createComposition(self._datas)
                                composition.displayMenu()
                            except:
                                raise Exception('Could not load composition creation model menu.')

        else:
            with self._out2:
                print("Missing argument(s) :")
                if(not self._path.value):
                    print("\t- path name")
                if(not self._modelName.value):
                    print("\t- model name")
                if(not self._modelID.value):
                    print("\t- model ID")
                if(not self._version.value):
                    print("\t- version")
                if(not self._timestep.value):
                    print("\t- timestep")
                if(not self._title.value):
                    print("\t- title")
                if(not self._authors.value):
                    print("\t- authors")
                if(not self._institution.value):
                    print("\t- institution")
                if(not self._reference.value):
                    print("\t- reference")
                if(not self._abstract.value):
                    print("\t- abstract")


                  
    def _eventCancel(self, b):
        """
        Handles cancel button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            try:
                tmp = MainMenu.mainMenu()
                tmp.displayMenu()
            except:
                raise Exception('Could not load mainmenu.')



    def _eventBrowse(self, b):
        """
        Handles browse button on_click event
        """

        self._out2.clear_output()
        self._path.value = getPath() 

        if 'crop2ml' not in os.listdir(self._path.value):
            self._path.value = ''
            with self._out2:
                print('This repository is not a model package.')           
            


    def _on_change_value(self, change):
        """
        Handles toggle widget value change
        """

        if change['new'] == 'unit':
            self._outextpkg.clear_output()
            self._extpkg.value = False
        else:
            with self._outextpkg:
                display(self._extpkg)



    def displayMenu(self):
        """
        Displays the model creation menu of pycrop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        display(self._out)
        display(self._out2)

        with self._out:
            display(self._displayer)
        
        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)
        self._browse.on_click(self._eventBrowse)

        self._toggle.observe(self._on_change_value, names='value')