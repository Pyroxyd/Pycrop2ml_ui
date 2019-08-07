import ipywidgets as wg
import os

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.edition import editmenu
from pycrop2ml_ui.menus.setsmanagement.managelink import manageLink
from pycrop2ml_ui.browser.TkinterPath import getPath
from pycropml.composition import model_parser


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

        self._modelname = wg.Textarea(value='',description='Model name:',disabled=False)
        self._modelid = wg.Textarea(value='',description='Model ID:',disabled=False)
        self._version = wg.Textarea(value='',description='Version:',disabled=False)
        self._timestep = wg.Textarea(value='',description='Timestep:',disabled=False)

        self._title = wg.Textarea(value='',description='Title:',disabled=False)
        self._authors = wg.Textarea(value='',description='Authors:',disabled=False)
        self._institution = wg.Textarea(value='',description='Institution:',disabled=False)
        self._reference = wg.Textarea(value='',description='Reference:',disabled=False)
        self._abstract = wg.Textarea(value='',description='Abstract:',disabled=False)
        self._informations = wg.VBox([self._modelname, self._modelid, self._version, self._timestep, self._title, self._authors, self._institution, self._reference, self._abstract])

        #datas
        self._datas = data
        self._listmodel = []
        self._listlink = []
        self._listextpkg = []


  
    def _parse(self):
        """
        Parses the xml file to gather the data set
        """
        
        self._xmlfile, = model_parser(self._datas['Path']+os.path.sep+'composition.{}.xml'.format(self._datas['Model name']))

        self._modelname.value = self._xmlfile.name
        self._version.value = self._xmlfile.version
        self._timestep.value = self._xmlfile.timestep
        self._title.value = self._xmlfile.description.Title
        self._modelid.value = self._xmlfile.id.split('.')[0]
        self._authors.value = self._xmlfile.description.Authors
        self._institution.value = self._xmlfile.description.Institution
        self._reference.value = self._xmlfile.description.Reference
        self._abstract.value = self._xmlfile.description.Abstract

        self._datas['Old name'] = self._modelname.value                   

        for i in self._xmlfile.model:
            if i.package_name:
                self._listextpkg.append(i.package_name)
                self._listmodel.append('{}:{}'.format(i.package_name, i.file))
            else:
                self._listmodel.append(i.file)

        for j in self._xmlfile.inputlink:
            self._listlink.append({'Link type': 'InputLink', 'Source': '', 'Target': j['target']})
        for k in self._xmlfile.internallink:
            self._listlink.append({'Link type': 'InternalLink', 'Source': k['source'], 'Target': k['target']})
        for l in self._xmlfile.outputlink:
            self._listlink.append({'Link type': 'OutputLink', 'Source': l['source'], 'Target': ''})



    def _manageExtpkg(self):
        """
        Manages the external package set
        """

        if self._listextpkg:
            _listpkg = wg.Select(options=self._listextpkg,disabled=False)
            _listpkg_Options = self._listextpkg
            _browse = wg.Button(value=False,description='Browse',disabled=False,button_style='primary')
        _remove = wg.Button(value=False,description='Remove',disabled=False,button_style='danger')

        _listpkgAdded = wg.Select(options=[],disabled=False)
        _listpkgAdded_Options = []

        _apply = wg.Button(value=False,description='Apply',disabled=True,button_style='success')        
        _add_new = wg.Button(value=False,description='Add',disabled=False,button_style='success')
        _remove_new = wg.Button(value=False,description='Remove',disabled=False,button_style='danger')

        if self._listextpkg:
            _displayer = wg.VBox([wg.HTML(value='<font size="5"><b> Model edition : composition.{}.xml<br>-> External packages</b></font>'.format(self._datas['Model name'])), wg.HBox([_listpkg, _browse, _remove]), wg.HBox([_listpkgAdded, _add_new, _remove_new]), wg.HBox([_apply, self._cancel])])
        else:
            _apply.disabled = False
            _displayer = wg.VBox([wg.HTML(value='<font size="5"><b> Model edition : composition.{}.xml<br>-> External packages</b></font>'.format(self._datas['Model name'])), wg.HBox([_listpkgAdded, _add_new, _remove_new]), wg.HBox([_apply, self._cancel])])            
        
        with self._out:
            display(_displayer)


        def _on_value_change(change):
            """
            Handles data change for apply button activation
            """
            self._out2.clear_output()
            if not change['new']:
                _apply.disabled = False


        def _eventApply(b):
            """
            Handles apply button on_click event
            """
            self._out.clear_output()
            self._out2.clear_output()
            self._listextpkg = _listpkgAdded_Options

            self._displayTab()


        def _eventBrowse(b):
            """
            Handles add_new button on_click event
            """
            self._out2.clear_output()

            extpkg = getPath()
            if not 'crop2ml' in os.listdir(extpkg):
                with self._out2:
                    print('This repository is not a model package.')
            
            elif extpkg in _listpkgAdded_Options or extpkg+os.path.sep+'crop2ml' == self._datas['Path']:
                with self._out2:
                    print('This package is already in the list.')

            else:
                _listpkgAdded_Options.append(extpkg)
                _listpkgAdded.options = _listpkgAdded_Options
                _listpkg_Options.remove(_listpkg.value)
                _listpkg.options = _listpkg_Options
                if not _listpkg_Options:
                    _browse.disabled = True
                    _remove.disabled = True


        def _eventRemove(b):
            """
            Handles remove button on_click event
            """
            self._out2.clear_output()

            if _listpkg.value:
                _listpkg_Options.remove(_listpkg.value)
                _listpkg.options = _listpkg_Options


        def _eventAdd_new(b):
            """
            Handles add_new button on_click event
            """
            self._out2.clear_output()

            extpkg = getPath()
            if not 'crop2ml' in os.listdir(extpkg):
                with self._out2:
                    print('This repository is not a model package.')
            
            elif extpkg in _listpkgAdded_Options or extpkg+os.path.sep+'crop2ml' == self._datas['Path']:
                with self._out2:
                    print('This package is already in the list.')

            else:
                _listpkgAdded_Options.append(extpkg)
                _listpkgAdded.options = _listpkgAdded_Options


        def _eventRemove_new(b):
            """
            Handles remove_new button on_click event
            """
            self._out2.clear_output()

            if _listpkgAdded.value:
                _listpkgAdded_Options.remove(_listpkgAdded.value)
                _listpkgAdded.options = _listpkgAdded_Options


        if self._listextpkg:
            _browse.on_click(_eventBrowse)
            _remove.on_click(_eventRemove)
            _listpkg.observe(_on_value_change, names='options')
        _apply.on_click(_eventApply)
        _add_new.on_click(_eventAdd_new)
        _remove_new.on_click(_eventRemove_new)
        self._cancel.on_click(self._eventCancel)



    def _displayTab(self):
        """
        Finds every model able to fit in the model composition according to the external package list and the current package.

        Displays the model tab interface
        """
        
        liste = ['']
        for buffer in os.listdir(self._datas['Path']):
            split = buffer.split('.')
            if split[0] in ['unit','composition'] and split[-1] == 'xml':
                liste.append(buffer)
        
        if self._listextpkg:
            for extpkg in self._listextpkg:
                for name in os.listdir(extpkg+os.path.sep+'crop2ml'):
                    split = name.split('.')
                    if split[0] in ['unit', 'composition'] and split[-1] == 'xml':
                        liste.append(os.path.split(extpkg)[1]+':'+name)

      
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


        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model edition : composition.{}.xml<br>-> Model composition</b></font>'.format(self._datas['Model name'])), self._tab, wg.HBox([self._apply, self._cancel])]))
        
        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)

        self._datamodeltab.on('row_added', self._row_added)
        self._datamodeltab.on('cell_edited', self._cell_edited)



    def _eventApply(self, b):
        """
        Handles apply button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        if all([self._modelname.value, self._version.value, self._timestep.value, self._title.value, self._modelid.value, self._authors.value, self._institution.value, self._reference.value, self._abstract.value]):
            self._dataframe = self._datamodeltab.get_changed_df()
            self._dataframe.reset_index(inplace=True)

            self._datas['Model name'] = self._modelname.value
            self._datas['Model ID'] = self._modelid.value
            self._datas['Version'] = self._version.value
            self._datas['Timestep'] = self._timestep.value
            self._datas['Title'] = self._title.value
            self._datas['Authors'] = self._authors.value
            self._datas['Institution'] = self._institution.value
            self._datas['Reference'] = self._reference.value
            self._datas['Abstract'] = self._abstract.value

            with self._out:
                menu = manageLink(self._datas, [i for i in self._dataframe['Model name'] if i], self._listlink, listextpkg=self._listextpkg, iscreate=False)
                menu.displayMenu()
     
        else:
            with self._out2:
                print("Missing argument(s) :")
                if(not self._modelname.value):
                    print("\t- model name")
                if(not self._modelid.value):
                    print("\t- model ID")
                if(not self._version.value):
                    print("\t- version")
                if(not self._timestep.value):
                    print("\t- timestep")
                if(not self._title.value):
                    print("\t- title")
                if(not self._authors.value):
                    print("\t- authors")
                if(not self._institution.value):
                    print("\t- institution")
                if(not self._reference.value):
                    print("\t- reference")
                if(not self._abstract.value):
                    print("\t- abstract")
    


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
        widget._update_table(triggered_by='remove_row')
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
        self._manageExtpkg()
       