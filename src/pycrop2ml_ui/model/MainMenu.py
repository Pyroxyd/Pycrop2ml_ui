from IPython.display import display
import ipywidgets as wg

from pycrop2ml_ui.menus.creation import createmenu
from pycrop2ml_ui.menus.edition import editmenu
from pycrop2ml_ui.cpackage.createpackage import createPackage
from pycrop2ml_ui.menus.transformation import transformationmenu



class mainMenu():


    """
    Class providing the launching of pycrop2ml's user interface.
    It is aiming to enhance the model management of pycrop2ml models as well
    as decorating the xml format used to write model attributes.

    It requires mainly ipywidgets, pandas and qgrid to run the whole set of 
    menus. Refering to python's coding manners, do not use methods and class
    attributes beginning with an underscore otherwise code can break.

    The class mainMenu contains 4 branches refering to creation, edition,
    transformation and repository creation :\n
    repository creation -> createPackage\n
    creation -> class createMenu\n
    edition -> class editMenu\n
    transformation -> class transformationMenu

    displayMenu() displays the main menu of the user interface and provides
    four buttons clickable leading to each branch. This is the only method
    usable in this class and does not require any argument.

    To run a mainMenu, use :\n
    mainmenu = mainMenu() #creates an instance of mainMenu\n
    mainmenu.displayMenu()       #calls displayMenu() method
    """



    def __init__(self):

        self._layout = wg.Layout(width='300px', height='60px')
        self._mkdir = wg.Button(value=False,description='Repository creation',disabled=False,layout=self._layout)
        self._create = wg.Button(value=False,description='Model creation',disabled=False,layout=self._layout)
        self._edit = wg.Button(value=False,description='Model edition',disabled=False,layout=self._layout)
        self._transformation = wg.Button(value=False,description='Package transformation',disabled=False,layout=self._layout)
        self._about = wg.Button(value=False,description='About',disabled=False,layout=self._layout)

        self._displayer = wg.VBox([wg.HTML(value='<font size="5"><b>Model manager for Pycrop2ml</b></font>'), self._mkdir, self._create, self._edit, self._transformation, self._about], layout=wg.Layout(align_items='center'))

        self._out = wg.Output()
        self._out2 = wg.Output()



    def _eventMkdir(self, b):

        """
        Displays repository creation menu
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out2: 
            try:
                tmp = createPackage()
                tmp.displayMenu()
            
            except:
                raise Exception('Could not load directory creation function.')



    def _eventCreate(self, b):

        """
        Displays model creation menu
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            try:
                createWg = createmenu.createMenu()
                createWg.displayMenu()          
            except:
                raise Exception('Could not load creation menu.')
            


    def _eventEdit(self, b):

        """
        Displays model edition menu
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            try:
                editWg = editmenu.editMenu()
                editWg.displayMenu()          
            except:
                raise Exception('Could not load edition menu.')



    def _eventTransformation(self, b):
        
        """
        Displays package transformation menu
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            try:
                editWg = transformationmenu.transformationMenu()
                editWg.displayMenu()     
            except:
                raise Exception('Could not load transformation menu.')



    def _eventAbout(self, b):

        """
        Prints the description of the mainMenu class
        """

        self._out2.clear_output()

        with self._out2:
            print("""
                Class providing the launching of pycrop2ml's user interface.
                It is aiming to enhance the model management of pycrop2ml models as well
                as decorating the xml format used to write model attributes.

                It requires mainly ipywidgets, pandas and qgrid to run the whole set of 
                menus. Refering to python's coding manners, do not use methods and class
                attributes beginning with an underscore otherwise code can break.

                The class mainMenu contains 3 branches refering to creation, edition
                and displayment :\n
                creation -> class createMenu\n
                edition -> class editMenu\n
                displayment -> class displayMenu

                displayMenu() displays the main menu of the user interface and provides
                three buttons clickable leading to each branch. This is the only method
                usable in this class and does not require any argument.

                To create a mainMenu, use :\n
                mainmenu = mainMenu() #creates an instance of mainMenu\n
                mainmenu.displayMenu()       #calls displayMenu() method
                """)



    def displayMenu(self):

        """
        Displays the main menu of pycrop2ml's UI.
        
        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        display(self._out)
        display(self._out2)

        with self._out:
            display(self._displayer)
        
        self._mkdir.on_click(self._eventMkdir)
        self._create.on_click(self._eventCreate)
        self._edit.on_click(self._eventEdit)
        self._transformation.on_click(self._eventTransformation)
        self._about.on_click(self._eventAbout)
        



def main():

    output = mainMenu()
    output.displayMenu()

