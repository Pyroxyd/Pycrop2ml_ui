import os
import ipywidgets as wg

import qgrid
import pandas

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
                        'Model ID': '',
                        'Version': '',
                        'Timestep': '',
                        'Title': '',
                        'Authors': '',
                        'Institution': '',
                        'Reference': '',
                        'Abstract': ''
                     }

            - externalpackagelist : []
    """

    def __init__(self, data, externalpackagelist=[]):

        self._out = wg.Output()
        self._out2 = wg.Output()

        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._apply2 = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._exit = wg.Button(value=False,description='Exit',disabled=False,button_style='danger')

        self._datas = data
        self._externalpkglist = externalpackagelist



    def _listdirs(self):
        """
        Collects xml files list in the given directory list
        """

        liste = ['']

        for buffer in os.listdir(self._datas['Path']):
            split = buffer.split('.')
            if split[0] in ['unit','composition'] and split[-1] == 'xml':
                liste.append(buffer)
        
        if self._externalpkglist:
            for extpkg in self._externalpkglist:
                for name in os.listdir(extpkg+os.path.sep+'crop2ml'):
                    split = name.split('.')
                    if split[0] in ['unit', 'composition'] and split[-1] == 'xml':
                        liste.append(os.path.split(extpkg)[1]+':'+name)


        self._dataFrame = pandas.DataFrame(data={'Model name': pandas.Categorical([''], categories=liste)})
        self._dataFrameqgrid = qgrid.show_grid(self._dataFrame, show_toolbar=True)
        


    def _eventApply(self, b):
        """
        Handles apply button on_click event
        """

        self._out2.clear_output()
        self._dataFrame = self._dataFrameqgrid.get_changed_df()
        self._dataFrame.reset_index(inplace=True)

        listmodel = [j for j in self._dataFrame['Model name'] if j]
        if listmodel:
            self._out.clear_output()
            with self._out:
                try:
                    menu = manageLink(self._datas, listmodel, [], listextpkg=self._externalpkglist, iscreate=True)
                    menu.displayMenu()           
                except:
                    raise Exception('Could not load link manager menu.')

        else:
            with self._out2:
                print('Composition model must contain at least one model.')



    def _eventExit(self, b):
        """
        Handles exit button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()



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
        widget._update_table(triggered_by='remove_row')

        widget.on('cell_edited', self._cell_edited)



    def displayMenu(self):
        """
        Displays the composition model creation menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        listekeys = ['Path','Model type','Model ID','Version','Timestep','Title','Model name','Authors','Institution','Reference','Abstract']

        display(self._out)
        display(self._out2)

        for i in self._datas.keys():

            with self._out:
                if i not in listekeys:
                    raise Exception("Could not display composition model creation menu : parameter data from createComposition(data) must contain these keys ['Path','Model type','Model ID','Model name','Version','Timestep','Title','Authors','Institution','Reference','Abstract']")
                
                elif i == 'Model type' and self._datas[i] != 'composition':
                    raise Exception("Bad value error : Model type key's value must be composition.")

                else:
                    listekeys.remove(i)

        self._listdirs()
        
        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model creation : composition.{}.xml<br>-> Model composition</b></font>'.format(self._datas['Model name'])), self._dataFrameqgrid, wg.HBox([self._apply, self._exit])]))

        self._apply.on_click(self._eventApply)
        self._exit.on_click(self._eventExit)

        self._dataFrameqgrid.on('cell_edited', self._cell_edited)
        self._dataFrameqgrid.on('row_added', self._row_added)
