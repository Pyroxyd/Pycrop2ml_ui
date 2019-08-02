import os
import re
import ipywidgets as wg

import qgrid
import pandas

from pycropml import pparse
from pycrop2ml_ui.menus.setsmanagement.managelink import manageLink

from IPython.display import display



class createComposition():

    """
    Class providing the display of composition model creation menu for pycrop2ml's user interface.

    Parameters :\n
            - data : {
                        'Path': '',
                        'Model type': 'composition',
                        'Model name': '',
                        'Authors': '',
                        'Institution': '',
                        'Reference': '',
                        'Abstract': ''
                     }
    """

    def __init__(self, data):

        self._out = wg.Output()
        self._out2 = wg.Output()

        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._apply2 = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._exit = wg.Button(value=False,description='Exit',disabled=False,button_style='danger')

        self._datas = data



    def _listdir(self):

        """
        Collects xml files list in the given directory
        """

        liste = ['']

        for buffer in os.listdir(self._datas['Path']):
            ext = os.path.splitext(buffer)[-1].lower()
            if (ext == '.xml' and buffer != 'composition.{}.xml'.format(self._datas['Model name'])):
                if re.search(r'composition', buffer) or re.search(r'unit', buffer):
                    liste.append(buffer)

        self._dataFrame = pandas.DataFrame(data={'Model name': pandas.Categorical([''], categories=liste)})
        self._dataFrameqgrid = qgrid.show_grid(self._dataFrame, show_toolbar=True)
        


    def _eventApply(self, b):

        """
        Handles apply button on_click event
        """

        self._out2.clear_output()
        self._dataFrame = self._dataFrameqgrid.get_changed_df()
        self._dataFrame.reset_index(inplace=True)


        def checkQgrid():

            """
            Checks wheter the tab of qgrid widgets is complete or not
            """

            if '' in [j for j in self._dataFrame['Model name']]:
                return False
            return True
        

        if checkQgrid():

            self._out.clear_output()

            with self._out:
                try:
                    menu = manageLink(self._datas, [j for j in self._dataFrame['Model name']], [], iscreate=True)
                    menu.displayMenu()           
                except:
                    raise Exception('Could not load link manager menu.')

        else:
            with self._out2:
                print('Missing data(s) in the model composition.')



    def _eventExit(self, b):

        """
        Handles exit button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        os.remove("{}{}composition.{}.xml".format(self._datas["Path"], os.path.sep, self._datas['Model name']))



    def _cell_edited(self, event, widget):

        """
        Handles every cell edition event in model list qgrid widget
        """

        widget.off('cell_edited', self._cell_edited)
        self._out2.clear_output()
        
        df = widget.get_changed_df()

        names = [i for i in df['Model name']]
        names.remove(event['new'])

        if event['new'] in names:
            widget.edit_cell(event['index'], 'Model name', event['old'])

            with self._out2:
                print('Error : this model is already in the composition.')


        widget.on('cell_edited', self._cell_edited)



    def _row_added(self, event, widget):

        """
        Handles a row addition in the qgrid widget
        """

        widget.off('cell_edited', self._cell_edited)

        widget.edit_cell(event['index'], 'Model name', '')

        widget.on('cell_edited', self._cell_edited)



    def displayMenu(self):

        """
        Displays the composition model creation menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        listekeys = ['Path','Model type','Model name','Authors','Institution','Reference','Abstract']

        display(self._out)
        display(self._out2)

        for i in self._datas.keys():

            with self._out:
                if i not in listekeys:
                    raise Exception("Could not display composition model creation menu : parameter data from createComposition(data) must contain these keys ['Path','Model type','Model name','Authors','Institution','Reference','Abstract']")
                
                elif i == 'Model type' and not self._datas[i] == 'composition':
                    raise Exception("Bad value error : Model type key's value must be composition.")

                else:
                    listekeys.remove(i)

        self._listdir()
        
        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model creation : composition.{}.xml<br>-> Model composition</b></font>'.format(self._datas['Model name'])), self._dataFrameqgrid, wg.HBox([self._apply, self._exit])]))

        self._apply.on_click(self._eventApply)
        self._exit.on_click(self._eventExit)

        self._dataFrameqgrid.on('cell_edited', self._cell_edited)
        self._dataFrameqgrid.on('row_added', self._row_added)
