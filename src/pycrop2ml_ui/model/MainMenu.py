from IPython.display import display
import ipywidgets as wg

from pycrop2ml_ui.menus.creation import createmenu
from pycrop2ml_ui.menus.edition import editmenu
from pycrop2ml_ui.menus.display import displaymenu



class displayMainMenu:


    def __init__(self):

        #buttons
        self._layout = wg.Layout(width='300px', height='60px')
        self._create = wg.Button(value=False,description='Model creation',disabled=False,layout=self._layout)
        self._edit = wg.Button(value=False,description='Model edition',disabled=False,layout=self._layout)
        self._display = wg.Button(value=False,description='Model display',disabled=False,layout=self._layout)
        self._about = wg.Button(value=False,description='About',disabled=False,layout=self._layout)

        #global displayer
        self._displayer = wg.VBox([wg.HTML(value='<font size="5"><b>Model manager for Pycrop2ml</b></font>'), self._create, self._edit, self._display, self._about])

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()



    def _eventCreate(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:

            try:
                createWg = createmenu.createMenu()
                createWg.displayMenu()
            
            except:
                raise Exception('Could not load creation menu.')
            
            finally:
                del self
            

    def _eventEdit(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:

            try:
                editWg = editmenu.editMenu()
                editWg.displayMenu()
            
            except:
                raise Exception('Could not load edition menu.')
            
            finally:
                del self


    def _eventDisplay(self, b):

        self._out2.clear_output()

        with self._out2:
            print("display !")


    def _eventAbout(self, b):

        self._out2.clear_output()

        with self._out2:
            print("""
This widget provides a user interface to create a Crop2ML model including any needed parameter.\n
You may use it for model edition and model display aswell.\n
Both ipywidgets and qgrid are required for running this interface with the JupyterLab extension crop2ml.\n""")



    def displayMenu(self):

        display(self._out)
        display(self._out2)

        with self._out:
            display(self._displayer)
        
        self._create.on_click(self._eventCreate)
        self._edit.on_click(self._eventEdit)
        self._display.on_click(self._eventDisplay)
        self._about.on_click(self._eventAbout)
        



def main():

    output = displayMainMenu()
    output.displayMenu()

