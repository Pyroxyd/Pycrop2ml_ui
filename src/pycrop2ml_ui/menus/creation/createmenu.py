import ipywidgets as wg
import os

from IPython.display import display

from pycrop2ml_ui.menus.creation import createunit
from pycrop2ml_ui.menus.creation import createcomposition

from pycrop2ml_ui.cpackage.CreationRepository import mkdirModel
from pycrop2ml_ui.model import MainMenu
from pycrop2ml_ui.browser.PathFetcher import FileBrowser


class createMenu():

    def __init__(self):

        #datas
        self._layout = wg.Layout(width='400px',height='57px')
        self._modelName = wg.Textarea(value='',description='Name:',disabled=False,layout=self._layout)
        self._authors = wg.Textarea(value='',description='Authors:',disabled=False,layout=self._layout)
        self._institution = wg.Textarea(value='',description='Institution:',disabled=False,layout=self._layout)
        self._abstract = wg.Textarea(value='',description='Abstract:',disabled=False,layout=self._layout)
        self._path = wg.Textarea(value='',description='Path:',disabled=True,layout=wg.Layout(height='57px',width='400px')) 
        self._reference = wg.Textarea(value='',description='Reference:',disabled=False,layout=self._layout)
        

        #model type
        self._toggle = wg.ToggleButtons(options=["unit", "composition"], description="Type:", disabled=False, layout=self._layout)

        #buttons
        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._create = wg.Button(value=False,description='Create',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='warning')
        self._browse = wg.Button(value=False,description='Browse',disabled=False,button_style='primary')

        self._header = wg.VBox([self._toggle,  wg.HBox([self._path, wg.VBox([self._browse, self._create])]), self._modelName, self._authors, self._institution, self._reference, self._abstract])

        #global menu displayer
        self._displayer = wg.VBox([wg.HTML(value='<font size="5"><b>Model creation : Header</b></font>'), self._header, wg.HBox([self._apply, self._cancel])], layout=wg.Layout(align_items='center'))

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        #model datas
        self._datas = dict()



    def _createFile(self):

        self._out2.clear_output()
        
        if(any([(os.path.exists("{}/unit.{}.xml".format(self._datas["Path"],self._modelName.value)) and self._datas['Model type']=='unit'),
                (os.path.exists("{}/composition.{}.xml".format(self._datas["Path"],self._modelName.value)) and self._datas['Model type']=='composition')])):
            
            raise Exception("File composition|unit.{}.xml already exists.".format(self._modelName.value))
        
        else:

            if(self._datas['Model type'] == 'unit'):

                try:
                    tmpFile = open("{}/unit.{}.xml".format(self._datas["Path"], self._datas['Model name']), 'w')
                
                except IOError as ioerr:         
                    raise Exception('File {} could not be opened. {}'.format(self._datas['Path'], ioerr))
                
                else:
                    tmpFile.close()
                    return True
                
            else:

                try:
                    tmpFile = open("{}/composition.{}.xml".format(self._datas["Path"], self._datas['Model name']), 'w')

                except IOError as ioerr:
                    raise Exception('File {} could not be opened. {}'.format(self._datas['Path'], ioerr))

                else:
                    tmpFile.close()
                    return True



    def _eventCreate(self, b):

        self._out2.clear_output()

        with self._out2:
            
            try:
                tmp = mkdirModel()
                tmp.display()
            
            except:
                raise Exception('Could not load directory creation function.')
            
            finally:
                self._out.clear_output()
                self._out2.clear_output()
                del self



    def _eventApply(self, b):

        self._out2.clear_output()

        if(self._modelName.value and self._authors.value and self._institution.value and self._abstract.value and self._path.value and self._reference.value):
            if(os.path.exists(self._path.value)):

                self._datas = {
                            'Path': self._path.value,
                            'Model type': self._toggle.value,
                            'Model name': self._modelName.value,
                            'Author': self._authors.value,
                            'Institution': self._institution.value,
                            'Reference': self._reference.value,
                            'Abstract': self._abstract.value}

                self._out.clear_output()
                    
                if self._createFile():

                    with self._out:
                        if self._datas['Model type'] == 'unit':

                            try:
                                unit = createunit.createUnit()
                                unit.display(self._datas)

                            except:
                                os.remove("{}/unit.{}.xml".format(self._datas['Path'], self._datas['Model name']))
                                self._out.clear_output()
                                self._out2.clear_output()
                                raise Exception('Could not load unit creation model.')
                            
                            finally:                             
                                del self

                        else:

                            try:
                                composition = createcomposition.createComposition()
                                composition.display(self._datas)

                            except:
                                os.remove("{}/composition.{}.xml".format(self._datas['Path'], self._datas['Model name']))
                                self._out.clear_output()
                                self._out2.clear_output()
                                raise Exception('Could not load composition creation model.')

                            finally:   
                                del self

            else:
                with self._out:
                    print("This package does not exist.")


        else:
            with self._out2:
                print("Missing argument(s) :")

                if(not self._path.value):
                    print("\t- path name")

                if(not self._modelName.value):
                    print("\t- Model name")

                if(not self._authors.value):
                    print("\t- Author")

                if(not self._institution.value):
                    print("\t- Institution")

                if(not self._reference.value):
                    print("\t- Reference")

                if(not self._abstract.value):
                    print("\t- Abstract")


                  
    def _eventCancel(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            
            try:
                tmp = MainMenu.displayMainMenu()
                tmp.displayMenu()

            except:
                raise Exception('Could not load mainmenu.')

            finally:
                del self



    def _eventBrowse(self, b):

        def eventTmp(b):

            self._path.value = tmp.path
            self._out2.clear_output()


        self._out2.clear_output()
        tmp = FileBrowser()
        buttontmp = wg.Button(value=False,description='Select',disabled=False,button_style='success')

        with self._out2:
            display(tmp.widget())
            display(buttontmp)

        buttontmp.on_click(eventTmp)
            
            

    def displayMenu(self):

        display(self._out)

        with self._out:
            display(self._displayer)
        display(self._out2)

        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)
        self._create.on_click(self._eventCreate)
        self._browse.on_click(self._eventBrowse)