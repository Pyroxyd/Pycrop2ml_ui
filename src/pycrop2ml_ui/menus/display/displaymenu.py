import ipywidgets as wg
import os

from IPython.display import display

from pycrop2ml_ui.model import MainMenu
from pycrop2ml_ui.browser.TkinterPath import getPath
from pycropml.topology import Topology


class displayMenu():

    """
    Class providing the display of a model for pycrop2ml's user interface.
    """

    def __init__(self):
           
        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        #inputs
        self._modelPath = wg.Textarea(value='',description='Model path:',disabled=True,layout=wg.Layout(width='400px',height='57px'))

        #buttons
        self._browse = wg.Button(value=False,description='Browse',disabled=False,button_style='primary')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='warning')

        self._pathing = wg.HBox([self._modelPath, self._browse])

        #global displayer
        self._displayer = wg.VBox([wg.HTML(value='<font size="5"><b>Model display</b></font>'), self._pathing, self._cancel],layout=wg.Layout(align_items='center'))



    def _eventBrowse(self, b):
        """
        Handles browse button on_click event
        """

        self._out2.clear_output()
        self._modelPath.value = getPath()

        if 'crop2ml' not in os.listdir(self._modelPath.value):
            self._modelPath.value = ''
            with self._out2:
                print('This repository is not a model package.')



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
            


    def _on_value_change(self, change):
        """
        Handles changes from the attribute _modelPath.

        Find every model in xml format in the selected path.
        """

        self._out2.clear_output()

        if change['new']:
            topo = Topology(self._modelPath.value.split(os.path.sep)[-1], pkg=self._modelPath.value)

            with self._out2:
                display(wg.HTML('<font size="5"><b>Package {}</b></font>'.format(self._modelPath.value.split(os.path.sep)[-1])))
                topo.display_wf()



    def displayMenu(self):
        """
        Displays the model edition menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        display(self._out)
        display(self._out2)

        with self._out:
            display(self._displayer)

        self._browse.on_click(self._eventBrowse)
        self._cancel.on_click(self._eventCancel)
        self._modelPath.observe(self._on_value_change, names='value')

