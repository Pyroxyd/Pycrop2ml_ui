import ipywidgets as wg
import os
import re

from IPython.display import display

from pycrop2ml_ui.browser.TkinterPath import getPath
from pycrop2ml_ui.menus.edition import editunit, editcomposition
from pycrop2ml_ui.model import MainMenu



class editMenu():

    """
    Class providing the display of the model edition menu for pycrop2ml's user interface.
    """

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



    def _eventEdit(self, b):


        """
        Handles edit button on_click event
        """

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

        """
        Handles browse button on_click event
        """
        
        self._out2.clear_output()
        self._modelPath.value = getPath()



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
                raise Exception('Could not load mainMenu.')
            

    

    def displayMenu(self):

        """
        Displays the model edition menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        def _on_value_change(change):

            """
            Handles changes from the attribute _modelPath.

            Find every model in xml format in the selected path.
            """

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

        self._edit.on_click(self._eventEdit)
        self._browse.on_click(self._eventBrowse)
        self._cancel.on_click(self._eventCancel)
        self._modelPath.observe(_on_value_change, names='value')