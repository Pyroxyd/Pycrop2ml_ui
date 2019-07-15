import os
import re
import ipywidgets as wg

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.edition import editmenu
from PyCrop2ML.src.pycropml import pparse



class editUnit():


    def __init__(self):

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        self._datas = dict()

        self._apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        self._cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='danger')

        self._title = wg.Textarea(value='',description='Title:',disabled=False)
        self._authors = wg.Textarea(value='',description='Authors:',disabled=False)
        self._institution = wg.Textarea(value='',description='Institution:',disabled=False)
        self._reference = wg.Textarea(value='',description='Reference:',disabled=False)
        self._abstract = wg.Textarea(value='',description='Abstract:',disabled=False)
        self._informations = wg.VBox([self._title, self._authors, self._institution, self._reference, self._abstract])

        self._xmlfile = None


        


    def _buildEdit(self):

        self._title.value = self._xmlfile.description.Title
        self._authors.value = self._xmlfile.description.Authors
        self._institution.value = self._xmlfile.description.Institution
        self._reference.value = self._xmlfile.description.Reference
        self._abstract.value = self._xmlfile.description.Abstract

        self._dataframeIn = pandas.DataFrame(data={
            'Name': [i.name for i in self._xmlfile.inputs],
            'Description': [i.description for i in self._xmlfile.inputs],
            'InputType': pandas.Categorical([i.inputtype for i in self._xmlfile.inputs], categories=['variable','parameter']),
            'Category': pandas.Categorical([(i.variablecategory if hasattr(i,'variablecategory') else i.parametercategory) for i in self._xmlfile.inputs], categories=['constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([i.datatype for i in self._xmlfile.inputs], categories=['DOUBLE','DOUBLELIST','CHARLIST','INT','INTLIST','STRING','STRINGLIST','FLOAT','FLOATLIST','BOOLEAN','DATE','DATELIST']),
            'Default': [i.default for i in self._xmlfile.inputs],
            'Min': [i.min for i in self._xmlfile.inputs],
            'Max': [i.max for i in self._xmlfile.inputs],
            'Unit': [i.unit for i in self._xmlfile.inputs],
            'uri': [i.uri for i in self._xmlfile.inputs]
            })

        self._qgridIn = qgrid.show_grid(self._dataframeIn, show_toolbar=True)
        
        self._dataframeOut = pandas.DataFrame(data={
            'Name':[i.name for i in self._xmlfile.outputs],
            'Description': [i.description for i in self._xmlfile.outputs],
            'InputType': pandas.Categorical([i.inputtype for i in self._xmlfile.outputs], categories=['variable','parameter']),
            'Category': pandas.Categorical([(i.variablecategory if hasattr(i,'variablecategory') else i.parametercategory) for i in self._xmlfile.outputs], categories=['constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([i.datatype for i in self._xmlfile.outputs], categories=['DOUBLE','DOUBLELIST','CHARLIST','INT','INTLIST','STRING','STRINGLIST','FLOAT','FLOATLIST','BOOLEAN','DATE','DATELIST']),
            'Default': [i.default for i in self._xmlfile.outputs],
            'Min': [i.min for i in self._xmlfile.outputs],
            'Max': [i.max for i in self._xmlfile.outputs],
            'Unit': [i.unit for i in self._xmlfile.outputs],
            'uri': [i.uri for i in self._xmlfile.outputs]
            })

        self._qgridOut = qgrid.show_grid(self._dataframeOut, show_toolbar=True)

        self._dataframeAlgo = pandas.DataFrame(data={
            'Algorithm': [i.filename for i in self._xmlfile.algorithms]
        })

        self._qgridAlgo = qgrid.show_grid(self._dataframeAlgo, show_toolbar=True)
        


    def _parse(self):

        split = re.split(r'\\', self._datas['Path'])
        parse = ''
        for i in split[:-1]:
            parse += i + '\\'
        parsing = pparse.model_parser(parse)
        
        for j in parsing:

            if j.name == self._datas['Model name']:
                self._xmlfile = j
                break

        if self._xmlfile is None:

            try:
                raise Exception('Critical error while parsing the file.')

            finally:
                self._out.clear_output()
                self._out2.clear_output()
                del self
        
        self._buildEdit()



    def _updateParam(self):

        self._dataframeIn = self._qgridIn.get_changed_df()
        self._dataframeOut = self._qgridOut.get_changed_df()
        self._dataframeAlgo = self._qgridAlgo.get_changed_df()

        for i in range(0, len(self._dataframeIn)):

            if self._dataframeIn['InputType'][i] == 'parameter':
                
                pass


        


    def _displayParamset(self):

        self._out.clear_output()
        self._out2.clear_output()

        self._updateParam()

        self._tmpout = wg.Output()

        paramsetselecter = wg.Select(options=['']+[i.name for i in self._xmlfile.parametersSet.listParameterset],value='',description='ParameterSet',disabled=False)
        self._current = ''

        apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='danger')

        self._dictparamset = dict()

        for paramset in self._xmlfile.parametersSet.listParameterset:

            self._dictparamset[paramset.name] = [paramset.description, pandas.DataFrame(data={
                'Name': [i.name for i in paramset.listparam],
                'Value': [i.value for i in paramset.listparam]
            })]

        self._tmpqgrid = None
        self._tmpdescription = wg.Textarea(value='',description='Description',disabled=False)

        with self._out:
            display(wg.VBox([paramsetselecter, self._tmpout, wg.HBox([apply, cancel])]))


        def on_value_change(change):
            
            if not self._current:

                if paramsetselecter.value:
                    self._current = paramsetselecter.value
                    self._tmpdescription.value = self._dictparamset[self._current][0]
                    self._tmpqgrid = qgrid.show_grid(self._dictparamset[self._current][1], show_toolbar=False)

                    self._tmpout.clear_output()

                    with self._tmpout:
                        display(wg.VBox([self._tmpdescription, self._tmpqgrid]))
            
            else:

                self._dictparamset[self._current] = self._tmpqgrid.get_changed_df()
                self._current = paramsetselecter.value

                if paramsetselecter.value:
                             
                    self._tmpdescription.value = self._dictparamset[self._current][0]
                    self._tmpqgrid = qgrid.show_grid(self._dictparamset[self._current])

                    self._tmpout.clear_output()

                    with self._tmpout:
                        display(wg.VBox([self._tmpdescription, self._tmpqgrid]))
                
                else:

                    self._tmpout.clear_output()


                


        def eventApply(b):
            pass


        apply.on_click(eventApply)
        cancel.on_click(self._eventCancel)
        paramsetselecter.observe(on_value_change, names='value')



    def _eventApply(self, b):

        
        self._dataframeIn = self._qgridIn.get_changed_df()
        self._dataframeOut = self._qgridOut.get_changed_df()

        if any(['' in self._dataframeIn['Name'],'' in self._dataframeIn['Description'],'' in self._dataframeIn['InputType'],'' in self._dataframeIn['Category'],'' in self._dataframeIn['DataType'],'' in self._dataframeIn['Unit']]):
            
            with self._out2:
                print('Missing argument(s) in the input list, these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Unit')
        
        elif any(['' in self._dataframeOut['Name'],'' in self._dataframeOut['Description'],'' in self._dataframeOut['InputType'],'' in self._dataframeOut['Category'],'' in self._dataframeOut['DataType'],'' in self._dataframeOut['Unit']]):
            
            with self._out2:
                print('Missing argument(s) in the output list, these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Unit')
        
        elif '' in self._dataframeAlgo['Algorithm']:

            with self._out2:
                print('Missing argument(s) in the algorithm list.')

        else:
            self._displayParamset()


    
    def _eventCancel(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        try:
            tmp = editmenu.editMenu()
            tmp.displayMenu()

        except:
            raise Exception('Could not load edition menu.')

        finally:
            del self



    def _cell_edited(self, event, widget):

        self._out2.clear_output()
        widget.off('cell_edited', self._cell_edited)

        if widget is self._qgridIn:
            dataframetmp = self._dataframeIn
        elif widget is self._qgridOut:
            dataframetmp = self._dataframeOut


        #UPDATE INPUTTYPE
        if event['column'] == 'InputType':

            if not event['new'] == event['old']:
                widget.edit_cell(event['index'], 'Category', '')

        
        #UPDATE CATEGORY
        if event['column'] == 'Category':

            dataframetmp = widget.get_changed_df()

            if dataframetmp['InputType'][event['index']] == 'variable':

                if event['new'] not in ['','state','rate','auxiliary']:
                    widget.edit_cell(event['index'], 'Category', event['old'])

                    with self._out2:
                        print("Variable category must be among the list ['state','rate','auxiliary'].")
            
            elif dataframetmp['InputType'][event['index']] == 'parameter':

                if event['new'] not in ['','constant','species','genotypic','soil','private']:
                    widget.edit_cell(event['index'], 'Category', event['old'])

                    with self._out2:
                        print("Parameter category must be among the list ['constant','species','genotypic','soil','private'].")

            else:
                widget.edit_cell(event['index'], 'Category', '')
                
                with self._out2:
                    print('You must assign an input type before giving a category.')
        

        #UPDATE DATATYPE
        elif event['column'] == 'DataType' and not event['new'] == event['old']:

            widget.edit_cell(event['index'], 'Min', '')
            widget.edit_cell(event['index'], 'Max', '')

            if event['new'] in ['STRING','DATE','']:
                widget.edit_cell(event['index'], 'Default', '')

            if any([event['new'] == 'STRINGLIST', event['new'] == 'DATELIST']):
                widget.edit_cell(event['index'], 'Default', '[]')

            if any([event['new'] == 'STRINGARRAY', event['new'] == 'DATEARRAY']):
                widget.edit_cell(event['index'], 'Default', '[[]]')

            if event['new'] == 'DOUBLE':
                widget.edit_cell(event['index'], 'Default', '0.0')
            
            if event['new'] == 'DOUBLELIST':
                widget.edit_cell(event['index'], 'Default', '[0.0]')
            
            if event['new'] == 'DOUBLEARRAY':
                widget.edit_cell(event['index'], 'Default', '[[0.0]]')

            if event['new'] == 'INT':
                widget.edit_cell(event['index'], 'Default', '0')
            
            if event['new'] == 'INTLIST':
                widget.edit_cell(event['index'], 'Default', '[0]')
            
            if event['new'] == 'INTARRAY':
                widget.edit_cell(event['index'], 'Default', '[[0]]')

            if event['new'] == 'BOOLEAN':
                widget.edit_cell(event['index'], 'Default', 'False')
        

        #UPDATE DEFAULT
        elif event['column'] == 'Default' and not event['new'] == event['old']:

            dataframetmp = widget.get_changed_df()

            if dataframetmp['DataType'][event['index']] in ['DATELIST','DATEARRAY','']:                
                widget.edit_cell(event['index'], 'Default', event['old'])
            
            if dataframetmp['DataType'][event['index']] == 'DATE':
                if not re.search(r'^(?:(?:31(\/|-)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$', event['new']):
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print('Bad DATE format : use dd/mm/yyyy or dd-mm-yyyy.')
            
            if dataframetmp['DataType'][event['index']] == 'BOOLEAN':
                if not any([dataframetmp['Default'][event['index']] == 'True', dataframetmp['Default'][event['index']] == 'False']):
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print('Bad BOOLEAN format : use True|False.')

            
            if dataframetmp['DataType'][event['index']] == 'INT':

                search = re.search(r'^-? ?\d+\.', event['new'])
                if search:
                    if any([dataframetmp['Min'][event['index']] and (float(dataframetmp['Min'][event['index']]) > float(event['new'])),
                            dataframetmp['Max'][event['index']] and (float(dataframetmp['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                    else:                            
                        widget.edit_cell(event['index'], 'Default', event['new'][:search.end()-1])

                elif re.search(r'^-? ?\d+$', event['new']):
                    if any([dataframetmp['Min'][event['index']] and (float(dataframetmp['Min'][event['index']]) > float(event['new'])),
                            dataframetmp['Max'][event['index']] and (float(dataframetmp['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                else:

                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad INT format : use -?[0-9]+ .')

            
            if dataframetmp['DataType'][event['index']] == 'DOUBLE':

                if re.search(r'^-? ?\d+\.$', event['new']):
                    if any([dataframetmp['Min'][event['index']] and (float(dataframetmp['Min'][event['index']]) > float(event['new'])),
                            dataframetmp['Max'][event['index']] and (float(dataframetmp['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                    else:
                        widget.edit_cell(event['index'], 'Default', event['new']+'0')
                    
                elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                    if any([dataframetmp['Min'][event['index']] and (float(dataframetmp['Min'][event['index']]) > float(event['new'])),
                            dataframetmp['Max'][event['index']] and (float(dataframetmp['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                elif re.search(r'^-? ?\d+$', event['new']):
                    if any([dataframetmp['Min'][event['index']] and (float(dataframetmp['Min'][event['index']]) > float(event['new'])),
                            dataframetmp['Max'][event['index']] and (float(dataframetmp['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                    else:
                        widget.edit_cell(event['index'], 'Default', event['new']+'.0')

                else:
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLE format : use -?[0-9]+.[0-9]* .')


            if dataframetmp['DataType'][event['index']] == 'DOUBLELIST':

                if re.search(r'^(\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])$', event['new'].replace(' ','')):
                    widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))

                else:
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLELIST format : use [{DOUBLE},*] .','\n',r'{DOUBLE} = -?[0-9]+.[0-9]* .')


            if dataframetmp['DataType'][event['index']] == 'INTLIST':
                if re.search(r'^(\[(?:-? ?\d+)(?:,-? ?\d+)*\])$', event['new'].replace(' ','')):
                    widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                
                else:
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad INTLIST format : use [{INT},*] .','\n',r'{INT} = -?[0-9]+ .')
            

            if dataframetmp['DataType'][event['index']] == 'DOUBLEARRAY':

                if re.search(r'^\[(?:\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])?(?:,\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])*]$', event['new'].replace(' ','')):
                    widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                
                else:
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLEARRAY format : use [[{DOUBLE},*],*] .','\n',r'{DOUBLE} = -?[0-9]+.[0-9]* .')
            

            if dataframetmp['DataType'][event['index']] == 'INTARRAY':

                if re.search(r'^\[(?:\[(?:-? ?\d+)?(?:,-? ?\d+)*\])?(?:,\[(?:-? ?\d+)?(?:,-? ?\d+)*\])*]$', event['new'].replace(' ','')):
                    widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                
                else:
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLEARRAY format : use [[{INT},*],*] .','\n',r'{INT} = -?[0-9]+ .')

            
            if dataframetmp['DataType'][event['index']] == 'STRINGLIST':

                if not re.search(r"^\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\]$", event['new'].strip()):
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r"Bad STRINGLIST format : use ['',*] .")
                
                else:
                    tmp = event['new'].strip()[1:-1].split(',')
                    tmp = [x.strip() for x in tmp]
                    string = '['
                    for i in tmp:
                        string += i+','
                    widget.edit_cell(event['index'], 'Default', string[:-1]+']')


            if dataframetmp['DataType'][event['index']] == 'STRINGARRAY':

                if not re.search(r"^\[ *(?:\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\])?(?: *, *\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\] *)* *\]$", event['new'].strip()):
                    widget.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r"Bad STRINGLIST format : use [['',*],*] .")
        
        
        #UPDATE MIN
        elif event['column'] == 'Min':

            dataframetmp = widget.get_changed_df()

            if dataframetmp['DataType'][event['index']] == 'INT':

                search = re.search(r'^-? ?\d+\.', event['new'])
                if search:
                    if dataframetmp['Default'][event['index']] and (float(dataframetmp['Default'][event['index']]) < float(event['new'][:search.end()-1])):
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                    else:
                        widget.edit_cell(event['index'], 'Min', event['new'][:search.end()-1])


                elif re.search(r'^-? ?\d+$', event['new']):
                    if dataframetmp['Default'][event['index']] and (float(dataframetmp['Default'][event['index']]) < float(event['new'])):
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                else:

                    widget.edit_cell(event['index'], 'Min', event['old'])

                    with self._out2:
                        print(r'Bad INT format : use -?[0-9]+ .')

            
            elif dataframetmp['DataType'][event['index']] == 'DOUBLE':

                if re.search(r'^-? ?\d+\.$', event['new']):
                    if dataframetmp['Default'][event['index']] and (float(dataframetmp['Default'][event['index']]) < float(event['new']+'0')):
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                    widget.edit_cell(event['index'], 'Min', event['new']+'0')
                    
                elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                    if dataframetmp['Default'][event['index']] and (float(dataframetmp['Default'][event['index']]) < float(event['new'])):
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                elif re.search(r'^-? ?\d+$', event['new']):
                    if dataframetmp['Default'][event['index']] and (float(dataframetmp['Default'][event['index']]) < float(event['new'])):
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                    else:
                        widget.edit_cell(event['index'], 'Min', event['new']+'.0')

                else:
                    widget.edit_cell(event['index'], 'Min', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLE format : use -?[0-9]+.[0-9]* .')
                

            else:
                widget.edit_cell(event['index'], 'Min', event['old'])

                with self._out2:
                    print('This data type does not handle min nand max, or is not defined yet.')
        

        #UPDATE MAX
        elif event['column'] == 'Max':

            dataframetmp = widget.get_changed_df()

            if dataframetmp['DataType'][event['index']] == 'INT':

                search = re.search(r'^-? ?\d+\.', event['new'])
                if search:
                    if dataframetmp['Default'][event['index']] and (dataframetmp['Default'][event['index']] > event['new'][:search.end()-1]):
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                    else:
                        widget.edit_cell(event['index'], 'Max', event['new'][:search.end()-1])


                elif re.search(r'^-? ?\d+$', event['new']):
                    if dataframetmp['Default'][event['index']] and (dataframetmp['Default'][event['index']] > event['new']):
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                else:

                    widget.edit_cell(event['index'], 'Max', event['old'])

                    with self._out2:
                        print(r'Bad INT format : use -?[0-9]+ .')

            
            elif dataframetmp['DataType'][event['index']] == 'DOUBLE':

                if re.search(r'^-? ?\d+\.$', event['new']):
                    if dataframetmp['Default'][event['index']] and (dataframetmp['Default'][event['index']] > event['new']+'0'):
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                    widget.edit_cell(event['index'], 'Max', event['new']+'0')
                    
                elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                    if dataframetmp['Default'][event['index']] and (dataframetmp['Default'][event['index']] > event['new']):
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                elif re.search(r'^-? ?\d+$', event['new']):
                    if dataframetmp['Default'][event['index']] and (dataframetmp['Default'][event['index']] > event['new']):
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                    else:
                        widget.edit_cell(event['index'], 'Max', event['new']+'.0')

                else:
                    widget.edit_cell(event['index'], 'Max', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLE format : use -?[0-9]+.[0-9]* .')
                

            else:
                widget.edit_cell(event['index'], 'Max', event['old'])

                with self._out2:
                    print('This data type does not handle min nand max, or is not defined yet.')




        widget.on('cell_edited', self._cell_edited)



    def _row_added(self, event, widget):

        widget.off('cell_edited', self._cell_edited)

        widget.edit_cell(event['index'], 'Type', '')
        widget.edit_cell(event['index'], 'Name', '')
        widget.edit_cell(event['index'], 'Description', '')
        widget.edit_cell(event['index'], 'InputType', '')
        widget.edit_cell(event['index'], 'DataType', '')
        widget.edit_cell(event['index'], 'Category', '')
        widget.edit_cell(event['index'], 'Default', '')
        widget.edit_cell(event['index'], 'Min', '')
        widget.edit_cell(event['index'], 'Max', '')
        widget.edit_cell(event['index'], 'Unit', '')
        widget.edit_cell(event['index'], 'Uri', '')

        widget.on('cell_edited', self._cell_edited)



    def display(self, dic):

        self._datas = dic

        self._parse()

        display(self._out)
        display(self._out2)

        tab = wg.Tab()
        tab.children = [self._qgridIn, self._qgridOut, self._qgridAlgo]
        tab.set_title(0, 'Inputs')
        tab.set_title(1, 'Outputs')
        tab.set_title(2, 'Algorithms')

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model edition : {}.{}.xml<br>-> Inputs, Outputs, Algorithms'.format(self._datas['Model type'], self._datas['Model name'])), tab, wg.HBox([self._apply, self._cancel])]))


        self._qgridIn.on('cell_edited', self._cell_edited)
        self._qgridIn.on('row_added', self._row_added)

        self._qgridOut.on('cell_edited', self._cell_edited)
        self._qgridOut.on('row_added', self._row_added)
        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)
        