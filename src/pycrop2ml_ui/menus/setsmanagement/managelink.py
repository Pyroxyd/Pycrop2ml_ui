import os

import ipywidgets as wg
import pandas
import qgrid
from IPython.display import display

from pycropml import pparse
from pycropml.composition import model_parser
from pycrop2ml_ui.menus.writeXML import writecompositionxml


class manageLink():
    """
    Class managing the display of a composition model's link list for pycrop2ml' user interface.

    Parameters : \n
        - data : {
                    'Path': '',
                    'Model type': 'unit',
                    'Model name': '',
                    'Model ID': '',
                    'Version': '',
                    'Timestep': '',
                    'Title': '',
                    'Authors': '',
                    'Institution': '',
                    'Reference': '',
                    'Abstract': '',
                    'Old name':'' IF iscreate=False
                   }
        
        - listmodel : []

        - listlink : [
                       {
                        'Link type': '',
                        'Target': '',
                        'Source': ''
                       }
                     ]
        
        - listpkg : []
        
        - iscreate : bool
    """

    def __init__(self, data, listmodel, listlink, listextpkg=[], iscreate=True):

        self._out = wg.Output()
        self._out2 = wg.Output()

        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._exit = wg.Button(value=False,description='Exit',disabled=False,button_style='danger')
        
        self._datas = data
        self._listmodel = listmodel
        self._listlink = listlink # [{'Link type': '', 'Target': '', 'Source': ''}]
        self._iscreate = iscreate
        self._listextpkg = listextpkg


  
    def _buildEdit(self):
        """
        Creates the link qgrid widget
        """

        self._listLinkSource = ['']
        self._listLinkTarget = ['']
      
        parse = os.path.split(self._datas['Path'])[0]
        parsing = pparse.model_parser(parse)

        for i in parsing:
            if 'unit.{}.xml'.format(i.name) in self._listmodel: 
                for j in i.inputs:
                    self._listLinkTarget.append('{}.{}'.format(i.name, j.name))

                for k in i.outputs:
                    self._listLinkSource.append('{}.{}'.format(i.name, k.name))

        for model in self._listmodel:
            if ':' in model:
                pkgname, model_attr = model.split(':')
                model_attr = model_attr.split('.')
                path, = [i for i in self._listextpkg if pkgname in os.path.split(i)[1]]

                if model_attr[0] == 'composition':
                    pkg, = model_parser(path+os.path.sep+'crop2ml'+os.path.sep+'composition.{}.xml'.format(model_attr[1]))
                    for j in pkg.inputs:
                        self._listLinkTarget.append('{}.{}'.format(model_attr[1], j))
                    for k in pkg.outputs:
                        self._listLinkSource.append('{}.{}'.format(model_attr[1], k))
                
                else:
                    pkg = pparse.model_parser(path)
                    for m in pkg:
                        if m.name == model_attr[1]:
                            for y in m.inputs:
                                self._listLinkTarget.append('{}.{}'.format(model_attr[1], y.name))
                            for z in m.outputs:
                                self._listLinkSource.append('{}.{}'.format(model_attr[1], z.name))
                            break


        if self._iscreate:
            self._dfLink = pandas.DataFrame(data={
                'Link type': pandas.Categorical([''], categories=['','InputLink','InternalLink','OutputLink'], ordered=True),
                'Source': pandas.Categorical([''], categories=self._listLinkSource),
                'Target': pandas.Categorical([''], categories=self._listLinkTarget)
                })
        
        else:
            self._dfLink = pandas.DataFrame(data={
                'Link type': pandas.Categorical([i['Link type'] for i in self._listlink], categories=['','InputLink','InternalLink','OutputLink'], ordered=True),
                'Source': pandas.Categorical([i['Source'] if i['Source'] in self._listLinkSource else '' for i in self._listlink], categories=self._listLinkSource),
                'Target': pandas.Categorical([i['Target'] if i['Target'] in self._listLinkTarget else '' for i in self._listlink], categories=self._listLinkTarget)
                })
        
        self._dfLinkqgrid = qgrid.show_grid(self._dfLink, show_toolbar=True)



    def _row_added_link(self, event, widget):      
        """
        Handles a row addition in the link qgrid widget
        """

        widget.off('cell_edited', self._cell_edited_link)

        for column in ['Link type','Target','Source']:
            widget.edit_cell(event['index'], column, '')
        widget._update_table(triggered_by='remove_row')

        widget.on('cell_edited', self._cell_edited_link)
    

    
    def _cell_edited_link(self, event, widget):
        """
        Handles every cell edition event in link list qgrid widget
        """

        self._out2.clear_output()
        widget.off('cell_edited', self._cell_edited_link)

        df = widget.get_changed_df()

        if event['column'] == 'Link type':
            if event['new'] == 'InputLink':
                widget.edit_cell(event['index'], 'Source', '')
            
            elif event['new'] == 'OutputLink':
                widget.edit_cell(event['index'], 'Target', '')


        if event['column'] == 'Source' and event['new']:
            if df['Link type'][event['index']] == 'InputLink':
                widget.edit_cell(event['index'], 'Source', '')

                with self._out2:
                    print('Warning : Source is not required for an input link.')
            
            elif event['new'].split('.')[0] == df['Target'][event['index']].split('.')[0]:
                widget.edit_cell(event['index'], 'Source', event['old'])

                with self._out2:
                    print('Warning : Source and Target cannot come from the same model.')
        
        elif event['column'] == 'Target' and event['new']:
            if df['Link type'][event['index']] == 'OutputLink':
                widget.edit_cell(event['index'], 'Target', '')

                with self._out2:
                    print('Warning : Target is not required for an output link.')
            
            elif event['new'].split('.')[0] == df['Source'][event['index']].split('.')[0]:
                widget.edit_cell(event['index'], 'Target', event['old'])

                with self._out2:
                    print('Warning : Source and Target cannot come from the same model.')

        widget.on('cell_edited', self._cell_edited_link)
    


    def _eventApply(self, b):       
        """
        Handles apply button on_click event
        """

        self._out2.clear_output()
        self._dfLink = self._dfLinkqgrid.get_changed_df()
        self._dfLink.sort_values('Link type', ascending=True, inplace=True)
        self._dfLink.reset_index(inplace=True)


        def checkLinks():
            """
            Checks wheter the link qgrid widget is complete or not
            """

            for i in range(0,len(self._dfLink['Link type'])):
                if any([not self._dfLink['Link type'][i],
                        not self._dfLink['Source'][i] and self._dfLink['Link type'][i] != 'InputLink',
                        not self._dfLink['Target'][i] and self._dfLink['Link type'][i] != 'OutputLink'
                        ]):
                    return False
            return True


        if checkLinks():
            self._out.clear_output()
            self._out2.clear_output()

            newlist = []

            for i in range(0, len(self._dfLink['Link type'])):
                newlist.append({
                    'Link type':self._dfLink['Link type'][i],
                    'Target':self._dfLink['Target'][i] if self._dfLink['Target'][i] else self._dfLink['Source'][i].split('.')[-1],
                    'Source':self._dfLink['Source'][i] if self._dfLink['Source'][i] else self._dfLink['Target'][i].split('.')[-1]
                    })

            try:
                menu = writecompositionxml.writecompositionXML(self._datas, self._listmodel, newlist, iscreate=self._iscreate)
                menu.write()
            except:
                with self._out:
                    raise Exception('Could not load writecompositionxml menu.')
        
        else:
            with self._out2:
                print('Missing datas : Target, Source, or Link type.')



    def _eventExit(self, b):
        """
        Handles exit button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()



    def displayMenu(self):
        """
        Displays the link manager menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        display(self._out)
        display(self._out2)

        self._buildEdit()

        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model {} : composition.{}.xml<br>-> Links</b><font>'.format('creation' if self._iscreate else 'edition', self._datas['Model name'])), self._dfLinkqgrid, wg.HBox([self._apply, self._exit])]))

        self._dfLinkqgrid.on('cell_edited', self._cell_edited_link)
        self._dfLinkqgrid.on('row_added', self._row_added_link)
        
        self._apply.on_click(self._eventApply)
        self._exit.on_click(self._eventExit)