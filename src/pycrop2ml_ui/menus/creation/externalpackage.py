import os
import ipywidgets as wg

from pycrop2ml_ui.browser.TkinterPath import getPath
from pycrop2ml_ui.menus.creation.createcomposition import createComposition
from pycrop2ml_ui.menus.creation import createmenu

from IPython.display import display


class externalPackageMenu():
    """
    Class providing the external package addition of composition model creation menu for pycrop2ml's user interface.

    Parameters : \n
        - data : {
                    'Path': '',
                    'Model type': 'unit',
                    'Model name': '',
                    'Model ID': '',
                    'Authors': '',
                    'Institution': '',
                    'Reference': '',
                    'Abstract': ''
                   }
        
        - listpkg : []
    """

    def __init__(self, data, listpkg=[]):

        self._datas = data
        self._out = wg.Output()
        self._out2 = wg.Output()
        self._list = wg.Select(options=listpkg,disabled=False)
        self._listpkg = listpkg

        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='warning')
        self._add = wg.Button(value=False,description='Add',disabled=False,button_style='success')
        self._remove = wg.Button(value=False,description='Remove',disabled=False,button_style='danger')

    

    def _eventAdd(self, b):    
        """
        Handles add button on_click event
        """

        self._out2.clear_output()

        extpkg = getPath()
        if 'crop2ml' not in os.listdir(extpkg):
            with self._out2:
                print('This repository is not a model package.')
        
        elif any([extpkg in self._listpkg, extpkg+os.path.sep+'crop2ml' == self._datas['Path']]):
            with self._out2:
                print('This package is already in the list.')

        else:
            self._listpkg.append(extpkg)
            self._list.options = self._listpkg



    def _eventRemove(self, b):      
        """
        Handles remove button on_click event
        """

        self._out2.clear_output()

        if self._list.value:
            self._listpkg.remove(self._list.value)
            self._list.options = self._listpkg



    def _eventApply(self, b):   
        """
        Handles apply button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            try:
                tmp = createComposition(self._datas, externalpackagelist=[i for i in self._listpkg if i])
                tmp.displayMenu()
            except:
                raise Exception('Could not load model composition creation menu.')


    
    def _eventCancel(self, b):
        """
        Handles cancel button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            try:
                tmp = createmenu.createMenu()
                tmp.displayMenu()
            except:
                raise Exception('Could not load mainmenu.')



    def displayMenu(self):
        """
        Displays the package selection menu of pycrop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        display(self._out)
        display(self._out2)

        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model creation : composition.{}.xml<br>-> External packages</b></font>'.format(self._datas['Model name'])), wg.HBox([self._list, wg.VBox([self._add, self._remove])]), wg.HBox([self._apply, self._cancel])]))

        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)
        self._add.on_click(self._eventAdd)
        self._remove.on_click(self._eventRemove)
