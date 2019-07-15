import ipywidgets as wg
import os
import re

from IPython.display import display

from pycrop2ml_ui.browser.PathFetcher import FileBrowser
from pycrop2ml_ui.menus.edition import editunit, editcomposition
from pycrop2ml_ui.model import MainMenu



class editMenu():

    def __init__(self):
           
        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        #inputs
        self._modelPath = wg.Textarea(value='',description='Model path:',disabled=True,layout=wg.Layout(width='400px',height='57px'))
        self._selecter = wg.Dropdown(options=['None'],value='None',description='Model:',disabled=True,layout=wg.Layout(width='400px',height='35px'))

        #buttons
        self._browse = wg.Button(value=False,description='Browse',disabled=False,button_style='primary')
        self._edit = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='warning')

        self._pathing = wg.VBox([wg.HBox([self._modelPath, self._browse]), self._selecter])

        #global displayer
        self._displayer = wg.VBox([wg.HTML(value='<font size="5"><b>Model edition : Selection</b></font>'), self._pathing, wg.HBox([self._edit, self._cancel])],layout=wg.Layout(align_items='center',border='1px'))

        self._paths = dict()



    def _eventBrowse(self, b):

        self._out2.clear_output()
        
        typemodel = re.search(r'(.+?)\.(.+?)\.xml',self._selecter.value)

        if typemodel:

            if typemodel.group(1) == 'unit':

                self._out.clear_output()
                
                with self._out:                  
                    unit = editunit.editUnit()
                    unit.display({'Path': self._modelPath.value, 'Model type': typemodel.group(1), 'Model name': typemodel.group(2)})

            
            elif typemodel.group(1) == 'composition':

                self._out.clear_output()

                with self._out:                   
                    composition = editcomposition.editComposition()
                    composition.display({'Path': self._modelPath.value, 'Model type': typemodel.group(1), 'Model name': typemodel.group(2)})
            
            else:
                
                raise Exception("File {} does not match with a model.".format(self._selecter.value))

        else:
            
            raise Exception("File {} does not match with a model.".format(self._selecter.value))




    def _eventBrowse(self, b):

        def eventTmp(b):
            self._modelPath.value = tmp.path
            self._out2.clear_output()

        self._out2.clear_output()
        tmp = FileBrowser()
        buttontmp = wg.Button(value=False,description='Select',disabled=False,button_style='success')

        with self._out2:
            display(wg.VBox([tmp.widget(), buttontmp]))
        buttontmp.on_click(eventTmp)



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
            

    

    def displayMenu(self):

        def _on_value_change(change):

            self._paths.clear()
            tmp = []
            for f in os.listdir(self._modelPath.value):
                ext = os.path.splitext(f)[-1].lower()
                if ext == '.xml':
                    self._paths[f] = os.path.join(self._modelPath.value,f)
                    tmp.append(f)
            
            self._selecter.options = tmp    
            self._selecter.disabled = False


        display(self._out)
        with self._out:
            display(self._displayer)
        display(self._out2)

        self._edit.on_click(self._eventBrowse)
        self._browse.on_click(self._eventBrowse)
        self._cancel.on_click(self._eventCancel)
        self._modelPath.observe(_on_value_change, names='value')