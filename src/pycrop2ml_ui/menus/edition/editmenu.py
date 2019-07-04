import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.cpackage.CreationRepository import mkdirModel
from pycrop2ml_ui.browser.PathFetcher import FileBrowser
from pycrop2ml_ui.menus.edition import editunit, editcomposition
from pycrop2ml_ui.model import CreationModel



class editMenu():

    def __init__(self):
           
        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        #inputs
        self.modelPath = wg.Textarea(value='',description='Model path:',disabled=True)
        self.selecter = wg.Dropdown(options=['None'],value='None',description='Select a model:',disabled=True)

        #buttons
        self.browse = wg.Button(value=False,description='Browse',disabled=False,background_color='#d0d0ff')
        self.edit = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        #global displayer
        self.displayer = wg.VBox([wg.HBox([self.modelPath, self.browse]), self.selecter, wg.HBox([self.edit, self.cancel])])

        self.table = editunit.editUnit()
        self.list = editcomposition.editComposition()

        self.paths = dict()



    def eventEdit(self, b):
        self.out2.clear_output()
        
        typemodel = re.search(r'(.+?)\.(.+?)\.xml',self.selecter.value)

        if typemodel:
            if typemodel.group(1) == 'unit':
                self.out.clear_output()
                with self.out:                  
                    print("Editing {}".format(self.selecter.value))
                    self.table.display({'Path': self.paths[self.selecter.value], 'Model type': typemodel.group(1), 'Model name': typemodel.group(2), 'Option': '2'})

            
            elif typemodel.group(1) == 'composition':
                self.out.clear_output()
                with self.out:
                    print("Editing {}".format(self.selecter.value))
                    self.list.display({'Path': self.paths[self.selecter.value], 'Model type': typemodel.group(1), 'Model name': typemodel.group(2)})
            
            else:
                with self.out2:
                    print("The selected file does not match with a model ({}).".format(self.selecter.value))

        else:
            with self.out2:
                print("The selected file does not match with a model ({}).".format(self.selecter.value))




    def eventBrowse(self, b):

        def eventTmp(b):
            self.modelPath.value = tmp.path
            self.out2.clear_output()

        self.out2.clear_output()
        tmp = FileBrowser()
        buttontmp = wg.Button(value=False,description='Select',disabled=False,button_style='success')

        with self.out2:
            display(wg.VBox([tmp.widget(), buttontmp]))
        buttontmp.on_click(eventTmp)



    def eventCancel(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        with self.out:
            tmp = CreationModel.displayMainMenu()
            tmp.displayMenu()

    

    def displayMenu(self):

        def on_value_change(change):

            self.paths.clear()
            tmp = []
            for f in os.listdir(self.modelPath.value):
                ext = os.path.splitext(f)[-1].lower()
                if ext == '.xml':
                    self.paths[f] = os.path.join(self.modelPath.value,f)
                    tmp.append(f)
            
            self.selecter.options = tmp    
            self.selecter.disabled = False


        display(self.out)
        with self.out:
            display(self.displayer)
        display(self.out2)

        self.edit.on_click(self.eventEdit)
        self.browse.on_click(self.eventBrowse)
        self.cancel.on_click(self.eventCancel)
        self.modelPath.observe(on_value_change, names='value')