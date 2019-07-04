import ipywidgets as wg
import os

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.creation import createunit
from pycrop2ml_ui.menus.creation import createcomposition

from pycrop2ml_ui.cpackage.CreationRepository import mkdirModel
from pycrop2ml_ui.model import CreationModel
from pycrop2ml_ui.browser.PathFetcher import FileBrowser


class createMenu():

    def __init__(self):

        #input datas
        self.modelName = wg.Textarea(value='',description='Model name',disabled=False)
        self.author = wg.Textarea(value='',description='Author',disabled=False)
        self.institution = wg.Textarea(value='',description='Institution',disabled=False)
        self.description = wg.Textarea(value='',description='Description',disabled=False)
        self.package = wg.Textarea(value='',description='Package',disabled=True) 
        self.reference = wg.Textarea(value='',description='Reference',disabled=False)

        #model type
        self.toggle = wg.ToggleButtons(options=["unit", "composition"], description="Model type :", disabled=False)

        #buttons
        self.save = wg.Button(value=False,description='Save',disabled=False,button_style='success')
        self.create = wg.Button(value=False,description='Create',disabled=False,button_style='success')
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')
        self.browse = wg.Button(value=False,description='Browse',disabled=False,background_color='#d0d0ff')

        #global menu displayer
        self.displayer = wg.VBox([self.toggle, wg.HBox([self.package, self.browse, self.create]), self.modelName, self.author, self.institution, self.description, self.reference, wg.HBox([self.save, self.cancel])])

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        #model datas
        self.export = dict()

        #child creation menu
        self.unit = createunit.createUnit()
        self.composition = createcomposition.createComposition()





    def createFile(self):

        self.out2.clear_output()
        
        if(any([(os.path.exists("{}/unit.{}.xml".format(self.export["Path"],self.modelName.value)) and self.export['Model type']=='unit'), (os.path.exists("{}/crop2ml/composition.{}.xml".format(self.export["Path"],self.modelName.value)) and self.export['Model type']=='composition')])):
            with self.out2:
                print("This file already exists.")
            return False
        
        else:
            if(self.export['Model type'] == 'unit'):
                try:
                    tmpFile = open("{}/unit.{}.xml".format(self.export["Path"], self.export['Model name']), 'w')
                except IOError as ioerr:
                    with self.out2:
                        print('File {} could not be opened. {}'.format(self.export['Path'], ioerr))
                    return False
                else:
                    tmpFile.close()
                    return True
                
            else:
                try:
                    tmpFile = open("{}/composition.{}.xml".format(self.export["Path"], self.export['Model name']), 'w')

                except IOError as ioerr:
                    with self.out2:
                        print('File {} could not be opened. {}'.format(self.export['Path'], ioerr))
                    return False

                else:
                    tmpFile.close()
                    return True


    def eventCreate(self, b):

        self.out2.clear_output()
        with self.out2:
            tmp = mkdirModel()
            tmp.display()



    def eventSave(self, b):
        self.out2.clear_output()
        if(self.modelName.value and self.author.value and self.institution.value and self.description.value and self.package.value and self.reference.value):
            if(os.path.exists(self.package.value)):

                self.export = {'Path': self.package.value, 'Model type': self.toggle.value, 'Model name': self.modelName.value, 'Author': self.author.value, 'Institution': self.institution.value, 'Reference': self.reference.value, 'Description': self.description.value, 'Option': '1'}
                self.out.clear_output()
                    
                if self.createFile():

                    with self.out:
                        print("Creating {}.{}.xml ...".format(self.export['Model type'], self.export['Model name']))

                        if self.export['Model type'] == 'unit':
                            self.unit.display(self.export)

                        else:
                            self.composition.display(self.export)

                else:
                    with self.out:
                        print("File could not be opened, aborting ...")
                    return


            else:
                with self.out:
                    print("This package does not exist.")

        else:
            with self.out2:
                print("Missing argument(s) :")
                if(not self.package.value):
                    print("\t- Package name")
                if(not self.modelName.value):
                    print("\t- Model name")
                if(not self.author.value):
                    print("\t- Author")
                if(not self.institution.value):
                    print("\t- Institution")
                if(not self.reference.value):
                    print("\t- Reference")
                if(not self.description.value):
                    print("\t- Description")


                  
    def eventCancel(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:
            tmp = CreationModel.displayMainMenu()
            tmp.displayMenu()


    def eventBrowse(self, b):

        def eventTmp(b):
            self.package.value = tmp.path
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

        self.save.on_click(self.eventSave)
        self.cancel.on_click(self.eventCancel)
        self.create.on_click(self.eventCreate)
        self.browse.on_click(self.eventBrowse)