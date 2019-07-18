import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.edition import editmenu



class editComposition():

    def __init__(self):

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        #buttons
        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        self._title = wg.Textarea(value='',description='Title',disabled=False)
        self._authors = wg.Textarea(value='',description='Authors',disabled=False)
        self._institution = wg.Textarea(value='',description='Institution',disabled=False)
        self._reference = wg.Textarea(value='',description='Reference',disabled=False)
        self._abstract = wg.Textarea(value='',description='Abstract',disabled=False)
        self._informations = wg.VBox([self._title, self._authors, self._institution, self._reference, self._abstract])

        #datas
        self._datas = dict()
        self._listmodel = []
        self._listlink = [[],[],[]]



    def _badSyntax(self, file):

        try:
            raise Exception('File {} has a bad syntax critical error.'.format(file))
        
        finally:
            file.close()


  
    def _parse(self):

        with self._out2:
            print(self._datas['Path'])
        
        try:
            f = open(self._datas['Path'],"r")

        except IOError as ioerr:
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
                model = re.search('filename="(.*?)" />',buffer)
                linktype = re.search('<(.*?Link)',buffer)
                target = re.search('target="(.*?)"',buffer)
                source = re.search('source="(.*?)"',buffer)

                if model:
                    self._listmodel.append(model.group(1))

                elif linktype and target and source:
                    self._listlink[0].append(linktype.group(1))
                    self._listlink[1].append(target.group(1))
                    self._listlink[2].append(source.group(1))

            f.close()



    def _write(self):

               
        try:
            fw = open(self._datas['Path'], "w")

        except IOError as ioerr:
            raise Exception('File {} could not be opened in write mode. {}'.format(self._datas['Path'], ioerr))

        else:

            split = re.split(r'\\', self._datas['Path'])

            fw.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE ModelComposition PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelComposition.dtd">')
            fw.write('<ModelComposition name="{0}" id="{1}.{0}" version="001" timestep = "1">'.format(self._datas['Model name'], split[-4]))
            fw.write('\n\t<Description>\n\t\t<Title>{}</Title>\n\t\t<Authors>{}</Authors>\n\t\t<Institution>{}</Institution>\n\t\t<Reference>{}</Reference>\n\t\t<Abstract>{}</Abstract>'.format(self._title.value, self._authors.value, self._institution.value, self._reference.value, self._abstract.value))
            fw.write('\n\t</Description>\n\n\t<Composition>')

            for i in range(0, len(self._dataframe['Model type'])):

                if self._dataframe['Model type'][i] == 'Unit':
                    fw.write('\n\t\t<Model name="{0}" id="{1}.{0}" filename="{2}" />'.format(re.search(r'unit\.(.*?)\.xml',self._dataframe['Model name'][i]).group(1), self._datas['Model name'], self._dataframe['Model name'][i]))
                else:
                    fw.write('\n\t\t<Model name="{0}" id="{0}" filename="{1}" />'.format(re.search(r'composition\.(.*?)\.xml',self._dataframe['Model name'][i]), self._dataframe['Model name'][i]))

            fw.write("\n\n\t\t<Links>")
            
            for i in range(0, len(self._dataframelinks['Link type'])):
                fw.write('\n\t\t\t<{} target="{}" source="{}" />'.format(self._dataframelinks['Link type'][i], self._dataframelinks['Target'][i], self._dataframelinks['Source'][i]))
            
            
            fw.write('\n\n\t\t</Links>\n\t</Composition>\n</ModelComposition>')
            fw.close()

            with self._out2:
                print('File updated.')



    def _eventApply(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        if not any([not self._title.value, not self._authors.value, not self._institution.value, not self._reference.value, not self._abstract.value]):

            self._dataframe = self._datamodeltab.get_changed_df()
            self._dataframe.reset_index(inplace=True)

            self._dataframelinks = self._datalinktab.get_changed_df()
            self._dataframelinks.reset_index(inplace=True)

            self._write()
        
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

        self._out.clear_output()
        self._out2.clear_output()

        try:
            tmp = editmenu.editMenu()
            tmp.displayMenu()

        except:
            raise Exception('Could not load edition menu.')
        


    def display(self, dic):

        display(self._out)
        display(self._out2)

        self._datas = dic
        self._parse()


        if self._listmodel:
            self._dataframe = pandas.DataFrame(data={
                'Model type': pandas.Categorical(['Unit' for i in range(0,len(self._listmodel))], categories=['','Unit','Composition']),
                'Model name':self._listmodel
                },index=None)
            self._datamodeltab = qgrid.show_grid(self._dataframe, show_toolbar=True)

        else:
            self._dataframe = pandas.DataFrame(data={
                'Model type': pandas.Categorical([''], categories=['','Unit','Composition']),
                'Model name': ['']
                },index=None)
            self._datamodeltab = qgrid.show_grid(self._dataframe, show_toolbar=True)


        if self._listlink:
            self._dataframelinks = pandas.DataFrame(data={
                'Link type': pandas.Categorical(self._listlink[0], categories=['','InputLink','OutputLink','InternalLink']),
                'Target': self._listlink[1],
                'Source': self._listlink[2]
                },index=None)
            self._datalinktab = qgrid.show_grid(self._dataframelinks, show_toolbar=True)
        
        else:
            self._dataframelinks = pandas.DataFrame(data={
                'Link type': pandas.Categorical([''], categories=['','InputLink','OutputLink','InternalLink']),
                'Target': [''],
                'Source': ['']
                },index=None)
            self._datalinktab = qgrid.show_grid(self._dataframelinks, show_toolbar=True)
        

        self._tab = wg.Tab([self._informations, self._datamodeltab, self._datalinktab])
        self._tab.set_title(0, 'Informations')
        self._tab.set_title(1, 'Models')
        self._tab.set_title(2, 'Links')



        with self._out:
            display(wg.VBox([self._tab, wg.HBox([self._apply, self._cancel])]))
        
        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)


        def row_added(event, widget):

            self._datalinktab.edit_cell(event['index'], 'Link type', '')
            self._datalinktab.edit_cell(event['index'], 'Target', '')
            self._datalinktab.edit_cell(event['index'], 'Source', '')


        def row_added2(event, widget):

            self._datamodeltab.off('cell_edited', cell_edited)

            self._datamodeltab.edit_cell(event['index'], 'Model name', '')
            self._datamodeltab.edit_cell(event['index'], 'Model type', '')

            self._datamodeltab.on('cell_edited', cell_edited)


        def cell_edited(event, widget):

            self._out2.clear_output()
            self._datamodeltab.off('cell_edited', cell_edited)

            self._dataframe = self._datamodeltab.get_changed_df()

            if event['column'] == 'Model type':
                
                if event['new'] == 'Unit':
                    if event['old'] == '':
                        self._datamodeltab.edit_cell(event['index'], 'Model name', r'unit.{modelname}.xml')
                    if event['old'] == 'Composition':
                        self._datamodeltab.edit_cell(event['index'], 'Model name', 'unit.{}.xml'.format(re.search(r'composition\.(.*?)\.xml', self._dataframe['Model name'][event['index']]).group(1)))
                
                elif event['new'] == 'Composition':
                    if event['old'] == '':
                        self._datamodeltab.edit_cell(event['index'], 'Model name', r'composition.{modelname}.xml')
                    if event['old'] == 'Unit':
                        self._datamodeltab.edit_cell(event['index'], 'Model name', 'composition.{}.xml'.format(re.search(r'unit\.(.*?)\.xml', self._dataframe['Model name'][event['index']]).group(1)))
                
                else:
                    self._datamodeltab.edit_cell(event['index'], 'Model name', '')


            elif event['column'] == 'Model name':
                
                if self._dataframe['Model type'][event['index']] == '':
                    self._datamodeltab.edit_cell(event['index'], 'Model name', '')
                    with self._out2:
                        print('You must assign a model type before giving a name.')

                elif self._dataframe['Model type'][event['index']] == 'Unit':
                    if not re.search(r'(unit\..*?\.xml)', self._dataframe['Model name'][event['index']]):
                        self._datamodeltab.edit_cell(event['index'], 'Model name', r'unit.{modelname}.xml')
                        with self._out2:
                            print(r'Bad format, use unit.{modelname}.xml or switch the model type to enter a composition name.')
                
                elif self._dataframe['Model type'][event['index']] == 'Composition':
                    if not re.search(r'(composition\..*?\.xml)', self._dataframe['Model name'][event['index']]):
                        self._datamodeltab.edit_cell(event['index'], 'Model name', r'composition.{modelname}.xml')
                        with self._out2:
                            print(r'Bad format, use composition.{modelname}.xml or switch the model type to enter a unit name.')
                
            self._datamodeltab.on('cell_edited', cell_edited)

        self._datalinktab.on('row_added', row_added)
        self._datamodeltab.on('row_added', row_added2)
        self._datamodeltab.on('cell_edited', cell_edited)
        