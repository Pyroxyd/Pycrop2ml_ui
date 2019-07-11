from IPython.display import display
import ipywidgets as wg

from pycrop2ml_ui.menus.creation import createmenu
from pycrop2ml_ui.menus.edition import editmenu
from pycrop2ml_ui.menus.display import displaymenu



class displayMainMenu:


    def __init__(self):

        #buttons
        self.layout = wg.Layout(width='200px', height='40px')
        self.create = wg.Button(value=False,description='Model creation',disabled=False,layout=self.layout)
        self.edit = wg.Button(value=False,description='Model edition',disabled=False,layout=self.layout)
        self.display = wg.Button(value=False,description='Model display',disabled=False,layout=self.layout)
        self.about = wg.Button(value=False,description='About',disabled=False,layout=self.layout)

        #global displayer
        self.displayer = wg.VBox([wg.HTML(value='<b>Model manager for Pycrop2ml</b>'), self.create, self.edit, self.display, self.about])

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()



    def eventCreate(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:

            try:
                createWg = createmenu.createMenu()
                createWg.displayMenu()
            
            except:
                raise Exception('Could not load creation menu.')
            
            finally:
                del self
            

    def eventEdit(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:

            try:
                editWg = editmenu.editMenu()
                editWg.displayMenu()
            
            except:
                raise Exception('Could not load edition menu.')
            
            finally:
                del self


    def eventDisplay(self, b):

        self.out2.clear_output()

        with self.out2:
            print("display !")


    def eventAbout(self, b):

        self.out2.clear_output()

        with self.out2:
            print("""
This widget provides a user interface to create a Crop2ML model including any needed parameter.\n
You may use it for model edition and model display aswell.\n
Both ipywidgets and qgrid are required for running this tool, they are enabled with the JupyterLab extension crop2ml.\n""")



    def displayMenu(self):

        display(self.out)
        display(self.out2)

        with self.out:
            display(self.displayer)
        
        self.create.on_click(self.eventCreate)
        self.edit.on_click(self.eventEdit)
        self.display.on_click(self.eventDisplay)
        self.about.on_click(self.eventAbout)
        



def main():

    output = displayMainMenu()
    output.displayMenu()

