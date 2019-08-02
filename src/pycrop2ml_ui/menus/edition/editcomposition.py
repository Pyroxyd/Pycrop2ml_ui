import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.edition import editmenu
from pycrop2ml_ui.menus.setsmanagement.managelink import manageLink



class editComposition():

    """
    Class providing the display of the composition model edition menu for pycrop2ml's user interface.

    Parameters :\n
            - data : {
                        'Path': '',
                        'Model type': 'composition',
                        'Model name': '',
                     }
    """

    def __init__(self, data):

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        #buttons
        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        self._title = wg.Textarea(value='',description='Model name:',disabled=False)
        self._authors = wg.Textarea(value='',description='Authors:',disabled=False)
        self._institution = wg.Textarea(value='',description='Institution:',disabled=False)
        self._reference = wg.Textarea(value='',description='Reference:',disabled=False)
        self._abstract = wg.Textarea(value='',description='Abstract:',disabled=False)
        self._informations = wg.VBox([self._title, self._authors, self._institution, self._reference, self._abstract])

        #datas
        self._datas = data
        self._listmodel = []
        self._listlink = []



    def _badSyntax(self, file):

        """
        Called for a bad syntax error in the parsed xml file, raises an exception.

        Parameters : \n
            - file : TextIOWrapper
        """

        try:
            self._out.clear_output()
            self._out2.clear_output()
            with self._out:
                raise Exception('File {} has a bad syntax critical error.'.format(file))
        
        finally:
            file.close()


  
    def _parse(self):

        """
        Parses the xml file to gather the data set
        """
        
        try:
            f = open('{}{}{}.{}.xml'.format(self._datas['Path'], os.path.sep, self._datas['Model type'], self._datas['Model name']),"r")

        except IOError as ioerr:
            with self._out:
                raise Exception('File {} could not be opened in read mode. {}'.format(self._datas['Path'], ioerr))

        else:
            buffertmp = f.readline()

            while not re.search(r'(</Description>)', buffertmp):
                title = re.search(r'<Title>(.*?)</Title>', buffertmp)
                authors = re.search(r'<Authors>(.*?)</Authors>', buffertmp)
                institution = re.search(r'<Institution>(.*?)</Institution>', buffertmp)
                reference = re.search(r'<Reference>(.*?)</Reference>', buffertmp)
                abstract = re.search(r'<Abstract>(.*?)</Abstract>', buffertmp)

                if title:
                    if not self._title.value:
                        self._title.value = title.group(1)
                        self._datas['Old name'] = title.group(1)
                    else:
                        self._badSyntax(f)
                if authors:
                    if not self._authors.value:
                        self._authors.value = authors.group(1)
                    else:
                        self._badSyntax(f)
                if institution:
                    if not self._institution.value:
                        self._institution.value = institution.group(1)
                    else:
                        self._badSyntax(f)               
                if reference:
                    if not self._reference.value:
                        self._reference.value = reference.group(1)
                    else:
                        self._badSyntax(f)
                if abstract:
                    if not self._abstract.value:
                        self._abstract.value = abstract.group(1)
                    else:
                        self._badSyntax(f)
                
                buffertmp = f.readline()
                if not buffertmp:
                    self._badSyntax(f)

            if any([not self._title.value, not self._authors.value, not self._institution.value, not self._reference.value, not self._abstract.value]):
                self._badSyntax(f)

            for buffer in f:
                model = re.search(r'filename="(.*?)" />',buffer)
                linktype = re.search(r'<(.*?Link)',buffer)
                target = re.search(r'target="(.*?)"',buffer)
                source = re.search(r'source="(.*?)"',buffer)

                if model:
                    self._listmodel.append(model.group(1))

                elif linktype and target and source:
                    self._listlink.append({'Link type': linktype.group(1), 'Source': source.group(1), 'Target': target.group(1)})

            f.close()

        self._buildEdit()



    def _buildEdit(self):

        """
        Creates the qgrid widget fro displaying model composition
        """

        liste = ['']
        for buffer in os.listdir(self._datas['Path']):
            ext = os.path.splitext(buffer)[-1].lower()
            if (ext == '.xml' and buffer != 'composition.{}.xml'.format(self._datas['Model name'])):
                if re.search(r'composition', buffer) or re.search(r'unit', buffer):
                    liste.append(buffer)
      
        if self._listmodel:
            self._dataframe = pandas.DataFrame(data={
                'Model name': pandas.Categorical([i for i in self._listmodel if i in liste], categories=liste)
                })
        else:
            self._dataframe = pandas.DataFrame(data={
                'Model name': pandas.Categorical([''], categories=liste)
                })

        self._datamodeltab = qgrid.show_grid(self._dataframe, show_toolbar=True)

        self._tab = wg.Tab([self._informations, self._datamodeltab])
        self._tab.set_title(0, 'Header')
        self._tab.set_title(1, 'Model composition')



    def _eventApply(self, b):

        """
        Handles apply button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        if all([self._title.value, self._authors.value, self._institution.value, self._reference.value, self._abstract.value]):
            self._dataframe = self._datamodeltab.get_changed_df()
            self._dataframe.reset_index(inplace=True)

            self._datas['Model name'] = self._title.value
            self._datas['Authors'] = self._authors.value
            self._datas['Institution'] = self._institution.value
            self._datas['Reference'] = self._reference.value
            self._datas['Abstract'] = self._abstract.value

            with self._out:
                menu = manageLink(self._datas, [i for i in self._dataframe['Model name'] if i], self._listlink, iscreate=False)
                menu.displayMenu()
     
        else:
            with self._out2:
                print("Missing argument(s) :")
                if(not self._title.value):
                    print("\t- Title")
                if(not self._authors.value):
                    print("\t- Authors")
                if(not self._institution.value):
                    print("\t- Institution")
                if(not self._reference.value):
                    print("\t- Reference")
                if(not self._abstract.value):
                    print("\t- Abstract")
    


    def _eventCancel(self, b):

        """
        Handles cancel button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        try:
            tmp = editmenu.editMenu()
            tmp.displayMenu()

        except:
            raise Exception('Could not load edition menu.')
        


    def _row_added(self, event, widget):

        """
        Handles row addition for model list tab
        """

        widget.off('cell_edited', self._cell_edited)
        widget.edit_cell(event['index'], 'Model name', '')
        widget.on('cell_edited', self._cell_edited)



    def _cell_edited(self, event, widget):

        """
        Handles cell edition for model list tab
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



    def displayMenu(self):

        """
        Displays the composition model edition menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        display(self._out)
        display(self._out2)

        listkeys = ['Path','Model type','Model name']

        for i in self._datas.keys():

            with self._out:
                if i not in listkeys:
                    raise Exception("Could not display composition model edition menu : parameter data from editComposition(data) must contain these keys ['Path','Model type','Model name']")

                elif i == 'Model type' and self._datas[i] != 'composition':
                    raise Exception("Bad value error : Model type key's value must be composition.")

                else:
                    listkeys.remove(i)

        self._parse()

        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model edition : composition.{}.xml<br>-> Model composition</b></font>'.format(self._datas['Model name'])), self._tab, wg.HBox([self._apply, self._cancel])]))
        
        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)

        self._datamodeltab.on('row_added', self._row_added)
        self._datamodeltab.on('cell_edited', self._cell_edited)
        