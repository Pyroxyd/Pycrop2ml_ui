import os
import re
import ipywidgets as wg

import qgrid
import pandas

from pycropml import pparse

from IPython.display import display



class createComposition():


    """
    Class providing a display of composition model creation menu for pycrop2ml's user interface.
    """


    def __init__(self):

        self._out = wg.Output()
        self._out2 = wg.Output()

        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._apply2 = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        self._datas = dict()



    def _listdir(self):

        """
        Collects xml files list in the given directory
        """

        liste = ['']

        for buffer in os.listdir(self._datas['Path']):

            ext = os.path.splitext(buffer)[-1].lower()

            if (ext == '.xml' and (not buffer == 'composition.{}.xml'.format(self._datas['Model name']))):

                if re.search(r'(composition)', buffer):
                    liste.append(buffer)

                elif re.search(r'(unit)', buffer):
                    liste.append(buffer)


        self._dataFrame = pandas.DataFrame(data={'Model name': pandas.Categorical([''], categories=liste)})
        


    def _createXML(self):

        """
        Saves all gathered datas in an xml format
        """

        self._dataFrame = self._dataFrameqgrid.get_changed_df()
        self._dataFrame.reset_index(inplace=True)

        self._dataFrameLink = self._dataFrameLinkqgrid.get_changed_df()
        self._dataFrameLink.sort_values(by='Link type',axis=0,ascending=True,inplace=True)
        self._dataFrameLink.reset_index(inplace=True)

        try:
            f = open("{}/composition.{}.xml".format(self._datas['Path'], self._datas['Model name']), 'w')

        except IOError as ioerr:
            raise Exception('File composition.{}.xml could not be opened. {}'.format(self._datas['Model name'], ioerr))

        else:

            split = re.split(r'\\', self._datas['Path'])
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE ModelComposition PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelComposition.dtd">\n')
            f.write('<ModelComposition modelid="{}.{}" name="{}" timestep="1" version="1.0">'.format(split[-4], self._datas['Model name'],self._datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{}</Title>\n\t\t<Authors>{}</Authors>\n\t\t<Institution>{}</Institution>\n\t\t<Reference>{}</Reference>\n\t\t<Abstract>{}</Abstract>\n\t</Description>'.format(self._datas['Model name'], self._datas['Authors'], self._datas['Institution'], self._datas['Reference'], self._datas['Abstract']))

            f.write('\n\t<Composition>')

            for i in range(0, len(self._dataFrame['Model name'])):

                f.write('\n\t\t<Model name="{0}" id="{1}.{0}" filename="{2}" />'.format(re.search(r'\.(.*?)\.xml',self._dataFrame['Model name'][i]).group(1), self._datas['Model name'], self._dataFrame['Model name'][i]))

            f.write('\n\n\t\t<Links>')

            for i in range(0, len(self._dataFrameLink['Link type'])):

                f.write('\n\t\t\t<{} target="{}" source="{}" />'.format(
                    self._dataFrameLink['Link type'][i],
                    self._dataFrameLink['Target'][i] if (not self._dataFrameLink['Link type'][i] == 'OutputLink') else self._dataFrameLink['Source'][i].split('.')[-1],
                    self._dataFrameLink['Source'][i] if (not self._dataFrameLink['Link type'][i] == 'InputLink') else self._dataFrameLink['Target'][i].split('.')[-1]))

            f.write('\n\t\t</Links>\n\t</Composition>\n</ModelComposition>')

            f.close()

            self._out.clear_output()
            self._out2.clear_output()

            return



    def _eventApply(self, b):

        """
        Handles apply button on_click event
        """

        self._out2.clear_output()
        self._dataFrame = self._dataFrameqgrid.get_changed_df()


        def checkQgrid():

            """
            Checks wheter the tab of qgrid widgets is complete or not
            """

            for i in range(0,len(self._dataFrame['Model name'])):
                
                if self._dataFrame['Model name'][i] == '':
                    return False

            return True
        

        if checkQgrid():

            self._listModel = []
            self._listLinkSource = ['']
            self._listLinkTarget = ['']


            for it in range(0,len(self._dataFrame['Model name'])):
                self._listModel.append(re.search(r'\.(.*?)\.xml',self._dataFrame['Model name'][it]).group(1))
            
            split = re.split(r'\\', self._datas['Path'])

            parse = ''
            for i in split[:-1]:
                parse += i + '\\'
            
            parsing = pparse.model_parser(parse)

            for i in range(0,len(parsing)):

                if parsing[i].name in self._listModel:         
                    for j in range(0, len(parsing[i].inputs)):

                        self._listLinkTarget.append('{}.{}'.format(parsing[i].name, parsing[i].inputs[j].name))

                    for k in range(0, len(parsing[i].outputs)):

                        self._listLinkSource.append('{}.{}'.format(parsing[i].name, parsing[i].outputs[k].name))

            self._displayLink()

        else:
            with self._out2:
                print('Missing data(s) in the model composition.')



    def _displayLink(self):

        """
        Displays the link list qgrid widget
        """

        self._dataFrameLink = pandas.DataFrame(data={
                'Link type': pandas.Categorical([''], categories=['','InputLink','InternalLink','OutputLink'], ordered=True),
                'Source': pandas.Categorical([''], categories=self._listLinkSource),
                'Target': pandas.Categorical([''], categories=self._listLinkTarget)
                })

        self._dataFrameLinkqgrid = qgrid.show_grid(self._dataFrameLink, show_toolbar=True)

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model creation : composition.{}.xml<br>-> Links</b><font>'.format(self._datas['Model name'])), self._dataFrameLinkqgrid, wg.HBox([self._apply2, self._cancel])]))

        self._apply2.on_click(self._eventApply2)
        self._cancel.on_click(self._eventCancel)
        self._dataFrameLinkqgrid.on('cell_edited', self._cell_edited_link)
        self._dataFrameLinkqgrid.on('row_added', self._row_added_link)



    def _eventApply2(self, b):

        """
        Handles apply2 button on_click event
        """

        self._out2.clear_output()
        self._dataFrameLink = self._dataFrameLinkqgrid.get_changed_df()


        def checkLinks():

            """
            Checks wheter the qgrid widget is complete or not
            """

            for i in range(0,len(self._dataFrameLink['Link type'])):

                if any([self._dataFrameLink['Link type'][i] == '',
                        self._dataFrameLink['Source'][i] == '' and not self._dataFrameLink['Link type'][i] == 'InputLink',
                        self._dataFrameLink['Target'][i] == '' and not self._dataFrameLink['Link type'][i] == 'OutputLink'
                        ]):
                    return False

            return True


        if checkLinks():

            self._out.clear_output()
            self._out2.clear_output()

            with self._out:
                display(wg.HTML(value='<b> Model creation : composition.{}.xml<br>-> XML writing</b>'.format(self._datas['Model name'])))
                self._createXML()
        
        else:
            with self._out2:
                print('Missing datas : Target, Source, or Link type.')



    def _eventCancel(self, b):

        """
        Handles cancel button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        os.remove("{}/composition.{}.xml".format(self._datas["Path"], self._datas['Model name']))

        return



    def _cell_edited_link(self, event, widget):

        """
        Handles every cell edition event in link list qgrid widget
        """

        self._out2.clear_output()
        self._dataFrameLinkqgrid.off('cell_edited', self._cell_edited_link)

        self._dataFrameLink = self._dataFrameLinkqgrid.get_changed_df()

        if event['column'] == 'Link type':
            if event['new'] == 'InputLink':
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Source', '')
            
            elif event['new'] == 'OutputLink':
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Target', '')


        if event['column'] == 'Source' and not event['new'] == '':
            if self._dataFrameLink['Link type'][event['index']] == 'InputLink':
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Source', '')

                with self._out2:
                    print('Warning : Source is not required for an input link.')
            
            elif event['new'] == self._dataFrameLink['Target'][event['index']]:
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Source', event['old'])
            
                with self._out2:
                    print('Warning : Source and Target cannot reach the same value.')
            
            elif event['new'].split('.')[0] == self._dataFrameLink['Target'][event['index']].split('.')[0]:
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Source', event['old'])

                with self._out2:
                    print('Warning : Source and Target cannot come from the same model.')
        
        elif event['column'] == 'Target' and not event['new'] == '':
            if self._dataFrameLink['Link type'][event['index']] == 'OutputLink':
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Target', '')

                with self._out2:
                    print('Warning : Target is not required for an output link.')
            
            elif event['new'] == self._dataFrameLink['Source'][event['index']]:
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Target', event['old'])
            
                with self._out2:
                    print('Warning : Source and Target cannot reach the same value.')
            
            elif event['new'].split('.')[0] == self._dataFrameLink['Source'][event['index']].split('.')[0]:
                self._dataFrameLinkqgrid.edit_cell(event['index'], 'Target', event['old'])

                with self._out2:
                    print('Warning : Source and Target cannot come from the same model.')

        self._dataFrameLinkqgrid.on('cell_edited', self._cell_edited_link)



    def _cell_edited(self, event, widget):

        """
        Handles every cell edition event in model list qgrid widget
        """

        self._dataFrameqgrid.off('cell_edited', self._cell_edited)
        self._out2.clear_output()
        
        self._dataFrame = self._dataFrameqgrid.get_changed_df()
        self._dataFrame.reset_index(inplace=True)

        for i in range(0, len(self._dataFrame['Model name'])):

            if not i == event['index'] and self._dataFrame['Model name'][i] == event['new']:
                self._dataFrameqgrid.edit_cell(event['index'], 'Model name', event['old'])

                with self._out2:
                    print('This model is already in the composition.')


        self._dataFrameqgrid.on('cell_edited', self._cell_edited)



    def _row_added(self, event, widget):

        """
        Handles a row addition in the qgrid widget
        """

        self._dataFrameqgrid.off('cell_edited', self._cell_edited)

        self._dataFrameqgrid.edit_cell(event['index'], 'Model name', '')

        self._dataFrameqgrid.on('cell_edited', self._cell_edited)



    def _row_added_link(self, event, widget):
        
        """
        Handles a row addition in the qgrid widget
        """

        self._dataFrameLinkqgrid.off('cell_edited', self._cell_edited_link)

        self._dataFrameLinkqgrid.edit_cell(event['index'], 'Link type', '')
        self._dataFrameLinkqgrid.edit_cell(event['index'], 'Target', '')
        self._dataFrameLinkqgrid.edit_cell(event['index'], 'Source', '')

        self._dataFrameLinkqgrid.on('cell_edited', self._cell_edited_link)



    def displayMenu(self, dic):


        """
        Displays the composition model creation menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.

        Parameters :\n
            - dic : dict(type:datas)\n
                datas = {
                        'Path': '',
                        'Model type': 'composition',
                        'Model name': '',
                        'Authors': '',
                        'Institution': '',
                        'Reference': '',
                        'Abstract': ''
                        }
        """

        listekeys = ['Path','Model type','Model name','Authors','Institution','Reference','Abstract']

        for i in dic.keys():

            if i not in listekeys:
                raise Exception("Could not display composition model creation menu : parameter dic from self.displayMenu(self, dic) must contain these keys ['Path','Model type','Model name','Authors','Institution','Reference','Abstract']")
            
            elif i == 'Model type' and not dic[i] == 'composition':
                raise Exception('Bad parameter error : model type is not composition whereas this is composition creation model menu.')

            else:
                listekeys.remove(i)


        display(self._out)
        display(self._out2)
        
        self._datas = dic
        self._listdir()
        self._dataFrameqgrid = qgrid.show_grid(self._dataFrame, show_toolbar=True)

        with self._out:
            display(wg.VBox([wg.HTML(value='<font size="5"><b> Model creation : composition.{}.xml<br>-> Model composition</b></font>'.format(self._datas['Model name'])), self._dataFrameqgrid, wg.HBox([self._apply, self._cancel])]))

        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)

        self._dataFrameqgrid.on('cell_edited', self._cell_edited)
        self._dataFrameqgrid.on('row_added', self._row_added)
