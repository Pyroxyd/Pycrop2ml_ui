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
        self.modelName = wg.Textarea(value='',description='Name',disabled=False)
        self.author = wg.Textarea(value='',description='Author',disabled=False)
        self.institution = wg.Textarea(value='',description='Institution',disabled=False)
        self.abstract = wg.Textarea(value='',description='Abstract',disabled=False)
        self.path = wg.Textarea(value='',description='Path',disabled=True,layout=wg.Layout(height='57px')) 
        self.reference = wg.Textarea(value='',description='Reference',disabled=False)

        #model type
        self.toggle = wg.ToggleButtons(options=["unit", "composition"], description="Type", disabled=False)

        #buttons
        self.apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self.create = wg.Button(value=False,description='Create',disabled=False,button_style='success')
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='warning')
        self.browse = wg.Button(value=False,description='Browse',disabled=False,button_style='primary')

        #global menu displayer
        self.displayer = wg.VBox([wg.HTML(value='<b>Model creation : Header</b>'), self.toggle, wg.HBox([self.path, wg.VBox([self.browse, self.create])]), self.modelName, self.author, self.institution, self.reference, self.abstract, wg.HBox([self.apply, self.cancel])])

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        #model datas
        self.datas = dict()



    def createFile(self):

        self.out2.clear_output()
        
        if(any([(os.path.exists("{}/unit.{}.xml".format(self.datas["Path"],self.modelName.value)) and self.datas['Model type']=='unit'),
                (os.path.exists("{}/composition.{}.xml".format(self.datas["Path"],self.modelName.value)) and self.datas['Model type']=='composition')])):
            
            raise Exception("File composition|unit.{}.xml already exists.".format(self.modelName.value))
        
        else:

            if(self.datas['Model type'] == 'unit'):

                try:
                    tmpFile = open("{}/unit.{}.xml".format(self.datas["Path"], self.datas['Model name']), 'w')
                
                except IOError as ioerr:         
                    raise Exception('File {} could not be opened. {}'.format(self.datas['Path'], ioerr))
                
                else:
                    tmpFile.close()
                    return True
                
            else:

                try:
                    tmpFile = open("{}/composition.{}.xml".format(self.datas["Path"], self.datas['Model name']), 'w')

                except IOError as ioerr:
                    raise Exception('File {} could not be opened. {}'.format(self.datas['Path'], ioerr))

                else:
                    tmpFile.close()
                    return True



    def eventCreate(self, b):

        self.out2.clear_output()

        with self.out2:
            
            tmp = mkdirModel()
            tmp.display()



    def eventApply(self, b):

        self.out2.clear_output()

        if(self.modelName.value and self.author.value and self.institution.value and self.abstract.value and self.path.value and self.reference.value):
            if(os.path.exists(self.path.value)):

                self.datas = {
                            'Path': self.path.value,
                            'Model type': self.toggle.value,
                            'Model name': self.modelName.value,
                            'Author': self.author.value,
                            'Institution': self.institution.value,
                            'Reference': self.reference.value,
                            'Abstract': self.abstract.value}

                self.out.clear_output()
                    
                if self.createFile():

                    with self.out:
                        if self.datas['Model type'] == 'unit':

                            try:
                                unit = createunit.createUnit()
                                unit.display(self.datas)

                            except:
                                os.remove("{}/unit.{}.xml".format(self.datas['Path'], self.datas['Model name']))
                                self.out.clear_output()
                                self.out2.clear_output()
                                raise Exception('Could not load unit creation model.')
                            
                            finally:                             
                                del self

                        else:

                            try:
                                composition = createcomposition.createComposition()
                                composition.display(self.datas)

                            except:
                                os.remove("{}/composition.{}.xml".format(self.datas['Path'], self.datas['Model name']))
                                self.out.clear_output()
                                self.out2.clear_output()
                                raise Exception('Could not load composition creation model.')

                            finally:   
                                del self

            else:
                with self.out:
                    print("This package does not exist.")


        else:
            with self.out2:
                print("Missing argument(s) :")

                if(not self.path.value):
                    print("\t- path name")

                if(not self.modelName.value):
                    print("\t- Model name")

                if(not self.author.value):
                    print("\t- Author")

                if(not self.institution.value):
                    print("\t- Institution")

                if(not self.reference.value):
                    print("\t- Reference")

                if(not self.abstract.value):
                    print("\t- Abstract")


                  
    def eventCancel(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:
            
            try:
                tmp = MainMenu.displayMainMenu()
                tmp.displayMenu()

            except:
                raise Exception('Could not load mainmenu.')

            finally:
                del self



    def eventBrowse(self, b):

        def eventTmp(b):

            self.path.value = tmp.path
            self.out2.clear_output()


        self.out2.clear_output()
        tmp = FileBrowser()
        buttontmp = wg.Button(value=False,description='Select',disabled=False,button_style='success')

        with self.out2:
            display(tmp.widget())
            display(buttontmp)

        buttontmp.on_click(eventTmp)

            
            

    def displayMenu(self):

        display(self.out)

        with self.out:
            display(self.displayer)
        display(self.out2)

        self.apply.on_click(self.eventApply)
        self.cancel.on_click(self.eventCancel)
        self.create.on_click(self.eventCreate)
        self.browse.on_click(self.eventBrowse)