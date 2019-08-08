import re
import os

import ipywidgets as wg
import qgrid
import pandas
from copy import deepcopy
from IPython.display import display

from pycrop2ml_ui.menus.edition import editmenu
from pycrop2ml_ui.menus.setsmanagement import manageparamset
from pycrop2ml_ui.menus.setsmanagement import managetestset

from pycropml import pparse


class editUnit():
    """
    Class providing the display of the unit model edition menu for pycrop2ml's user interface.

    Parameters :\n
            - data : {
                        'Path': '',
                        'Model type': 'unit',
                        'Model name': ''
                     }
    """

    def __init__(self, data):

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        self._datas = data

        self._apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        self._cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='warning')

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

        self._xmlfile = None
 


    def _buildEdit(self):
        """
        Creates inputs and outputs dataframes with datas collected from the xml file parsing
        """

        self._datas['Old name'] = self._xmlfile.name
        self._modelname.value = self._xmlfile.name
        self._modelid.value = self._xmlfile.modelid.split('.')[0]
        self._version.value = self._xmlfile.version
        self._timestep.value = self._xmlfile.timestep

        self._title.value = self._xmlfile.description.Title
        self._authors.value = self._xmlfile.description.Authors
        self._institution.value = self._xmlfile.description.Institution
        self._reference.value = self._xmlfile.description.Reference
        self._abstract.value = self._xmlfile.description.Abstract

        if self._xmlfile.inputs:
            self._dataframeIn = pandas.DataFrame(data={
                'Name': [i.name for i in self._xmlfile.inputs],
                'Description': [i.description for i in self._xmlfile.inputs],
                'InputType': pandas.Categorical([i.inputtype for i in self._xmlfile.inputs], categories=['','variable','parameter']),
                'Category': pandas.Categorical([(i.variablecategory if hasattr(i,'variablecategory') else i.parametercategory) for i in self._xmlfile.inputs], categories=['','constant','species','genotypic','soil','private','state','rate','auxiliary']),
                'DataType': pandas.Categorical([i.datatype for i in self._xmlfile.inputs], categories=['','DOUBLE','DOUBLELIST','DOUBLEARRAY','INT','INTLIST','INTARRAY','STRING','STRINGLIST','STRINGARRAY','BOOLEAN','DATE','DATELIST','DATEARRAY']),
                'Len': [(i.len if hasattr(i, 'len') else '') for i in self._xmlfile.inputs],
                'Default': [i.default for i in self._xmlfile.inputs],
                'Min': [(i.min if i.min is not None else '') for i in self._xmlfile.inputs],
                'Max': [(i.max if i.max is not None else '') for i in self._xmlfile.inputs],
                'Unit': [i.unit for i in self._xmlfile.inputs],
                'Uri': [(i.uri if i.uri is not None else '') for i in self._xmlfile.inputs]
                })
        
        else:
            self._dataframeIn = pandas.DataFrame(data={
                'Name': [''],
                'Description': [''],
                'InputType': pandas.Categorical([''], categories=['','variable','parameter']),
                'Category': pandas.Categorical([''], categories=['','constant','species','genotypic','soil','private','state','rate','auxiliary']),
                'DataType': pandas.Categorical([''], categories=['','DOUBLE','DOUBLELIST','DOUBLEARRAY','INT','INTLIST','INTARRAY','STRING','STRINGLIST','STRINGARRAY','BOOLEAN','DATE','DATELIST','DATEARRAY']),
                'Len': [''],
                'Default': [''],
                'Min': [''],
                'Max': [''],
                'Unit': [''],
                'Uri': ['']
                })

        self._qgridIn = qgrid.show_grid(self._dataframeIn, show_toolbar=True)
        
        if self._xmlfile.outputs:
            self._dataframeOut = pandas.DataFrame(data={
                'Name':[i.name for i in self._xmlfile.outputs],
                'Description': [i.description for i in self._xmlfile.outputs],
                'Category': pandas.Categorical([(i.variablecategory if hasattr(i, 'variablecategory') else '') for i in self._xmlfile.outputs], categories=['','state','rate','auxiliary']),
                'DataType': pandas.Categorical([i.datatype for i in self._xmlfile.outputs], categories=['','DOUBLE','DOUBLELIST','DOUBLEARRAY','INT','INTLIST','INTARRAY','STRING','STRINGLIST','STRINGARRAY','BOOLEAN','DATE','DATELIST','DATEARRAY']),
                'Len': [(i.len if hasattr(i, 'len') else '') for i in self._xmlfile.outputs],
                'Min': [(i.min if i.min is not None else '') for i in self._xmlfile.outputs],
                'Max': [(i.max if i.max is not None else '') for i in self._xmlfile.outputs],
                'Unit': [i.unit for i in self._xmlfile.outputs],
                'Uri': [(i.uri if i.uri is not None else '') for i in self._xmlfile.outputs]
                })
        
        else:
            self._dataframeOut = pandas.DataFrame(data={
                'Name':[''],
                'Description': [''],
                'Category': pandas.Categorical([''], categories=['','state','rate','auxiliary']),
                'DataType': pandas.Categorical([''], categories=['','DOUBLE','DOUBLELIST','DOUBLEARRAY','INT','INTLIST','INTARRAY','STRING','STRINGLIST','STRINGARRAY','BOOLEAN','DATE','DATELIST','DATEARRAY']),
                'Len': [''],
                'Min': [''],
                'Max': [''],
                'Unit': [''],
                'Uri': ['']
                })

        self._qgridOut = qgrid.show_grid(self._dataframeOut, show_toolbar=True)
        
        if self._xmlfile.function:
            self._dataframeFunction = pandas.DataFrame(data={
                'Filename': [i.filename for i in self._xmlfile.function],
                'Type': pandas.Categorical([i.type for i in self._xmlfile.function], categories=['','internal','external'])
            })
        else:
            self._dataframeFunction = pandas.DataFrame(data={
                'Filename': [''],
                'Type': pandas.Categorical([''], categories=['','internal','external'])
            })

        self._qgridFunction = qgrid.show_grid(self._dataframeFunction, show_toolbar=True)
        


    def _parse(self):
        """
        Parses the xml file and calls _buildEdit method to order collected datas
        """

        parse = os.path.split(self._datas['Path'])[0]
        parsing = pparse.model_parser(parse)
        
        for j in parsing:
            if j.name == self._datas['Model name']:
                self._xmlfile = j
                break

        if self._xmlfile is None:
            self._out.clear_output()
            self._out2.clear_output()
            with self._out:
                raise Exception('Critical error while parsing the file.')

        self._buildEdit()



    def _updateParam(self):
        """
        Fetches inputs changes and updates the parameters' list.
        """

        paramdict = dict()
        paramsetdict = dict() #{paramset_name:[{param:value}, description]}

        for i in range(0, len(self._dataframeIn['Name'])):
            if self._dataframeIn['InputType'][i] == 'parameter':    
                paramdict[self._dataframeIn['Name'][i]] = ''   

        if self._xmlfile.parametersets:
            for paramset in self._xmlfile.parametersets.items():
                paramsetdict[paramset[0]] = [deepcopy(paramdict), self._xmlfile.parametersets[paramset[0]].description]

                for param,value in self._xmlfile.parametersets[paramset[0]].params.items():
                    if param in paramdict:
                        paramsetdict[paramset[0]][0][param] = value

        return paramdict, paramsetdict



    def _updateVar(self):  
        """
        Fetches inputs and outputs changes and updates the variables' list.
        """

        vardict = {'inputs':dict(),'outputs':dict()} #{inputs:{name:value},outputs:{name:value}}
        testsets = dict() #{ testsetname: [ {testname: {inputs: {name:value}, outputs:{name:value}}}, description, parameterset ] }

        for i in range(0,len(self._df['Inputs']['Name'])):
            if self._df['Inputs']['InputType'][i] == 'variable':
                vardict['inputs'][self._df['Inputs']['Name'][i]] = ''

        for i in range(0,len(self._df['Outputs']['Name'])):
            vardict['outputs'][self._df['Outputs']['Name'][i]] = ['','']

        for i in self._xmlfile.testsets:
            testsets[i.name] = [dict(), i.description, i.parameterset if i.parameterset in self._paramsetdict else '']
            
            for j in i.test:
                for k,v in j.items():
                    testsets[i.name][0][k] = deepcopy(vardict)

                    for x,y in v['inputs'].items():
                        if x in testsets[i.name][0][k]['inputs']:
                            testsets[i.name][0][k]['inputs'][x] = y

                    for x,y in v['outputs'].items():
                        if x in testsets[i.name][0][k]['outputs']:
                            testsets[i.name][0][k]['outputs'][x] = y

        return vardict, testsets



    def _updateSets(self):
        """
        Updates paramters and variables to handle sets edition
        """

        self._out.clear_output()
        self._out2.clear_output()

        self._df = {'Functions': dict(zip([i for i in self._dataframeFunction['Filename'] if i],[j for j in self._dataframeFunction['Type'] if j])),'Inputs':self._dataframeIn,'Outputs':self._dataframeOut}

        self._paramdict, self._paramsetdict = self._updateParam()
        self._vardict, self._testsetdict = self._updateVar()

        with self._out:
            if self._paramdict:
                try:
                    menu = manageparamset.manageParamset(self._datas, self._paramdict, self._paramsetdict, self._df, self._vardict, self._testsetdict, iscreate=False)
                    menu.displayMenu()
                except:
                    raise Exception('Could not load parametersets managing menu')
            
            else:
                try:
                    menu = managetestset.manageTestset(self._datas, self._vardict, self._testsetdict, self._paramsetdict, self._df, iscreate=False)
                    menu.displayMenu()
                except:
                    raise Exception('Could not load testsets managing menu.')



    def _eventApply(self, b):
        """
        Handles apply button on_click event
        """

        self._out2.clear_output()


        def _checkHeader():
            """
            Checks wheter header's datas are complete or not
            """

            return all([self._modelname.value,self._modelid.value,self._version.value,self._timestep.value,
                        self._title.value,self._authors.value,self._institution.value,self._reference.value,self._abstract.value,])


        def _checkInputs():

            """
            Checks wheter the input list qgrid widget is complete or not
            """

            self._dataframeIn = self._qgridIn.get_changed_df()
            self._dataframeIn.reset_index(inplace=True)

            for i in range(0, len(self._dataframeIn['Name'])):
                if any([not self._dataframeIn['Category'][i],
                        not self._dataframeIn['Name'][i],
                        not self._dataframeIn['Description'][i],
                        not self._dataframeIn['DataType'][i],
                        not self._dataframeIn['InputType'][i],
                        not self._dataframeIn['Unit'][i],
                        (self._dataframeIn['DataType'][i] in ['STRINGARRAY','DATEARRAY','INTARRAY','DOUBLEARRAY'] and not self._dataframeIn['Len'][i])]):
                    return False
            return True
        

        def _checkOutputs():
            """
            Checks wheter the output list qgrid widget is complete or not
            """

            self._dataframeOut = self._qgridOut.get_changed_df()
            self._dataframeOut.reset_index(inplace=True)

            for i in range(0, len(self._dataframeOut['Name'])):
                if any([not self._dataframeOut['Name'][i],
                        not self._dataframeOut['Description'][i],
                        not self._dataframeOut['Category'][i],
                        not self._dataframeOut['DataType'][i],
                        not self._dataframeOut['Unit'][i],
                        (self._dataframeOut['DataType'][i] in ['STRINGARRAY','DATEARRAY','INTARRAY','DOUBLEARRAY'] and not self._dataframeOut['Len'][i])]):
                    return False
            return True


        def _checkFunc():
            """
            Checks wheter the function list qgrid widget is complete or not
            """
            self._dataframeFunction = self._qgridFunction.get_changed_df()
            filenames = [i for i in self._dataframeFunction['Filename']]
            types = [j for j in self._dataframeFunction['Type']]
            count = 0
            for f in range(len(filenames)):
                if not filenames[f-count] and not types[f-count]:
                    del types[f-count]
                    del filenames[f-count]
                    count += 1          

            return '' not in filenames+types


        if not _checkHeader():
            with self._out2:
                print('Missing argument(s) in the header.')
        
        elif not _checkInputs():
            with self._out2:
                print('Missing argument(s) in the input list, these columns are required :\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Len (if DataType is ARRAY)\n\t- Unit')

        elif not _checkOutputs():           
            with self._out2:
                print('Missing argument(s) in the output list, these columns are required :\n\t- Name\n\t- Description\n\t- Category\n\t- DataType\n\t- Unit')
        
        elif not _checkFunc():
            with self._out2:
                print('Missing argument(s) in the function list.')

        else:
            self._dataframeFunction = self._qgridFunction.get_changed_df()

            self._datas['Model name'] = self._modelname.value
            self._datas['Model ID'] = self._modelid.value
            self._datas['Version'] = self._version.value
            self._datas['Timestep'] = self._timestep.value
            self._datas['Title'] = self._title.value
            self._datas['Authors'] = self._authors.value
            self._datas['Institution'] = self._institution.value
            self._datas['Reference'] = self._reference.value
            self._datas['Abstract'] = self._abstract.value

            self._updateSets()


    
    def _eventCancel(self, b):

        """
        Handles cancel button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            try:
                tmp = editmenu.editMenu()
                tmp.displayMenu()
            except:
                raise Exception('Could not load edition menu.')



    def _cell_edited_In(self, event, widget):
        """
        Handles every event occuring when a cell is edited in the input list qgrid widget
        """

        self._out2.clear_output()
        widget.off('cell_edited', self._cell_edited_In)

        df = widget.get_changed_df()


        #UPDATE NAME
        if event['column'] == 'Name':
            
            names = [i for i in df['Name']]
            names.remove(event['new'])
            
            if event['new'] in names:
                widget.edit_cell(event['index'], 'Name', event['old'])

                with self._out2:
                    print('Error : this name is already defined.')


        #UPDATE INPUTTYPE
        elif event['column'] == 'InputType':

            widget.edit_cell(event['index'], 'Category', '')

        
        #UPDATE CATEGORY
        elif event['column'] == 'Category':

            if df['InputType'][event['index']] == 'variable':

                if event['new'] not in ['','state','rate','auxiliary']:
                    widget.edit_cell(event['index'], 'Category', event['old'])

                    with self._out2:
                        print("Warning : variable category must be among the list ['state','rate','auxiliary'].")
            
            elif df['InputType'][event['index']] == 'parameter':

                if event['new'] not in ['','constant','species','genotypic','soil','private']:
                    widget.edit_cell(event['index'], 'Category', event['old'])

                    with self._out2:
                        print("Warning : parameter category must be among the list ['constant','species','genotypic','soil','private'].")

            else:
                widget.edit_cell(event['index'], 'Category', '')
                
                with self._out2:
                    print('Warning : You must assign an input type before giving a category.')
        

        #UPDATE DATATYPE
        elif event['column'] == 'DataType':

            widget.edit_cell(event['index'], 'Min', '')
            widget.edit_cell(event['index'], 'Max', '')
            widget.edit_cell(event['index'], 'Len', '')

            if event['new'] in ['STRING','DATE','']:
                widget.edit_cell(event['index'], 'Default', '')

            elif event['new'] in ['STRINGLIST','DATELIST','STRINGARRAY','DATEARRAY']:
                widget.edit_cell(event['index'], 'Default', '[]')

            elif event['new'] in ['DOUBLE']:
                widget.edit_cell(event['index'], 'Default', '0.0')
            
            elif event['new'] in ['DOUBLELIST','DOUBLEARRAY']:
                widget.edit_cell(event['index'], 'Default', '[0.0]')

            elif event['new'] in ['INT']:
                widget.edit_cell(event['index'], 'Default', '0')
            
            elif event['new'] in ['INTLIST','INTARRAY']:
                widget.edit_cell(event['index'], 'Default', '[0]')

            elif event['new'] in ['BOOLEAN']:
                widget.edit_cell(event['index'], 'Default', 'False')
            
            else:
                widget.edit_cell(event['index'], 'Default', '')

        
        #UPDATE DEFAULT
        elif event['column'] == 'Default':

            if not event['new'].replace(' ',''):
                widget.edit_cell(event['index'], 'Default', '')

            else:      
                if not df['DataType'][event['index']]:                
                    widget.edit_cell(event['index'], 'Default', event['old'])

                
                elif df['DataType'][event['index']] == 'DATE':
                    if not re.search(r'^(?:(?:31\/(?:0?[13578]|1[02]))\/|(?:(?:29|30)\/(?:0?[13-9]|1[0-2])\/))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29\/0?2\/(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])\/(?:(?:0?[1-9])|(?:1[0-2]))\/(?:(?:1[6-9]|[2-9]\d)?\d{2})$', event['new']):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Error : bad DATE format -> use dd/mm/yyyy.')
                

                elif df['DataType'][event['index']] in ['DATELIST','DATEARRAY']:

                    if re.search(r'^\[(?:(?:[0-2]\d|3[0-1])\/(?:0?[1-9]|1[0-2])\/\d{4})?(?:,(?:(?:[0-2]\d|3[0-1])\/(?:0?[1-9]|1[0-2])\/\d{4}))*\]$', event['new'].replace(' ','')):
                        widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                    
                    else:
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Error : bad {}'.format(df['DataType'][event['index']]),r'format -> use [{DATE},*] .','\n',r'{DATE} = dd/mm/yyyy.')

                
                elif df['DataType'][event['index']] == 'BOOLEAN':
                    if not any([df['Default'][event['index']] == 'True', df['Default'][event['index']] == 'False']):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Error : bad BOOLEAN format -> use True|False.')

                
                elif df['DataType'][event['index']] == 'INT':

                    if re.search(r'^-?\d+$', event['new']):
                        if any([df['Min'][event['index']] and (int(df['Min'][event['index']]) > int(event['new'])),
                                df['Max'][event['index']] and (int(df['Max'][event['index']]) < int(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Default', event['old'])

                            with self._out2:
                                print('Error : default value must be in between Min and Max.')

                    else:
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')

                
                elif df['DataType'][event['index']] == 'DOUBLE':

                    if re.search(r'^-?\d+\.$', event['new']):
                        if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                                df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Default', event['old'])

                            with self._out2:
                                print('Error : default value must be in between Min and Max.')

                        else:
                            widget.edit_cell(event['index'], 'Default', event['new']+'0')
                        
                    elif re.search(r'^-?\d+\.\d+$', event['new']):
                        if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                                df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Default', event['old'])

                            with self._out2:
                                print('Error : default value must be in between Min and Max.')

                    else:
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')


                elif df['DataType'][event['index']] in ['DOUBLELIST','DOUBLEARRAY']:

                    if re.search(r'^(\[(?:-?\d+\.\d*)?(?:,-?\d+\.\d*)*\])$', event['new'].replace(' ','')):
                        widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))

                    else:
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Error : bad {}'.format(df['DataType'][event['index']]),r' format -> use [{DOUBLE},*] .','\n',r'{DOUBLE} = -?[0-9]+.[0-9]* .')


                elif df['DataType'][event['index']] in ['INTLIST','INTARRAY']:
                    if re.search(r'^(\[(?:-?\d+)(?:,-?\d+)*\])$', event['new'].replace(' ','')):
                        widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                    
                    else:
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Error : bad {}'.format(df['DataType'][event['index']]),r' format -> use [{INT},*] .','\n',r'{INT} = -?[0-9]+ .')

                
                elif df['DataType'][event['index']] in ['STRINGLIST','STRINGARRAY']:

                    if not re.search(r"^\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\]$", event['new'].strip()):
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Error : bad {}'.format(df['DataType'][event['index']]),r" format -> use ['',*] .")
                    
                    else:
                        tmp = event['new'].strip()[1:-1].split(',')
                        tmp = [x.strip() for x in tmp]
                        string = '['
                        for i in tmp:
                            string += i+','
                        widget.edit_cell(event['index'], 'Default', string[:-1]+']')

        
        #UPDATE MIN
        elif event['column'] == 'Min':

            if not event['new'].replace(' ',''):
                widget.edit_cell(event['index'], 'Min', '')
                
            else:
                if df['DataType'][event['index']] == 'INT':

                    if re.search(r'^-?\d+$', event['new']):
                        if df['Default'][event['index']] and (int(df['Default'][event['index']]) < int(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Default.')
                        
                        elif df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                    else:
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')

                
                elif df['DataType'][event['index']] == 'DOUBLE':

                    if re.search(r'^-?\d+\.$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) < float(event['new']+'0')):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Default.')
                        
                        elif df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                        else:
                            widget.edit_cell(event['index'], 'Min', event['new']+'0')
                        
                    elif re.search(r'^-?\d+\.\d+$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) < float(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Default.')

                        elif df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                    else:
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')
                    

                else:
                    widget.edit_cell(event['index'], 'Min', event['old'])

                    with self._out2:
                        print('Error : this data type does not handle min nand max, or is not defined yet.')
        

        #UPDATE MAX
        elif event['column'] == 'Max':

            if not event['new'].replace(' ',''):
                widget.edit_cell(event['index'], 'Max', '')
                       
            else:
                if df['DataType'][event['index']] == 'INT':

                    if re.search(r'^-?\d+$', event['new']):
                        if df['Default'][event['index']] and (int(df['Default'][event['index']]) > int(event['new'])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Maximum < Default.')
                        
                        elif df['Min'][event['index']] and (float(event['new']) < float(df['Min'][event['index']])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                    else:
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')

                
                elif df['DataType'][event['index']] == 'DOUBLE':

                    if re.search(r'^-?\d+\.$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) > float(event['new'])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Maximum < Default.')
                        
                        elif df['Min'][event['index']] and (float(event['new']) < float(df['Min'][event['index']])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                        widget.edit_cell(event['index'], 'Max', event['new']+'0')
                        
                    elif re.search(r'^-?\d+\.\d+$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) > float(event['new'])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Maximum < Default.')

                        elif df['Min'][event['index']] and (float(event['new']) < float(df['Min'][event['index']])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                    else:
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')
                    

                else:
                    widget.edit_cell(event['index'], 'Max', event['old'])

                    with self._out2:
                        print('Error : this data type does not handle min nand max, or is not defined yet.')


        #UPDATE LEN
        elif event['column'] == 'Len':

            if df['DataType'][event['index']] not in ['STRINGARRAY','DATEARRAY','INTARRAY','DOUBLEARRAY']:
                widget.edit_cell(event['index'], 'Len', '')

                with self._out2:
                    print('Error : Len is exclusive to ARRAY type.')
            
            elif not df['DataType'][event['index']]:
                widget.edit_cell(event['index'], 'Len', event['old'])

                with self._out2:
                    print('Error : you must assign a DataType before giving a lenght.')
            
            else:
                if not re.search(r'^\d+$', event['new']):
                    widget.edit_cell(event['index'], 'Len', event['old'])

                    with self._out2:
                        print(r'Error : bad LEN format -> use [0-9]+ .')

        widget.on('cell_edited', self._cell_edited_In)



    def _cell_edited_Out(self, event, widget):    
        """
        Handles every event occuring when a cell is edited in the output list qgrid widget
        """

        self._out2.clear_output()
        widget.off('cell_edited', self._cell_edited_Out)

        df = widget.get_changed_df()


        #UPDATE NAME
        if event['column'] == 'Name':
            
            names = [i for i in df['Name']]
            names.remove(event['new'])
            
            if event['new'] in names:
                widget.edit_cell(event['index'], 'Name', event['old'])

                with self._out2:
                    print('Error : this name is already defined.')


        #UPDATE DATATYPE
        elif event['column'] == 'DataType':

            widget.edit_cell(event['index'], 'Min', '')
            widget.edit_cell(event['index'], 'Max', '')
            widget.edit_cell(event['index'], 'Len', '')
        

        #UPDATE MIN
        elif event['column'] == 'Min':

            if not event['new'].replace(' ',''):
                widget.edit_cell(event['index'], 'Min', '')

            else:
                if df['DataType'][event['index']] == 'INT':

                    if not re.search(r'^-?\d+$', event['new']):
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')
                    
                    elif df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new'])):
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Error : Minimum > Maximum.')

                
                elif df['DataType'][event['index']] == 'DOUBLE':

                    if re.search(r'^-?\d+\.$', event['new']):
                        if df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                        else:
                            widget.edit_cell(event['index'], 'Min', event['new']+'0')
                        
                    elif re.search(r'^-?\d+\.\d+$', event['new']):
                        if df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                    else:
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')
                    

                else:
                    widget.edit_cell(event['index'], 'Min', event['old'])

                    with self._out2:
                        print('Error : this data type does not handle min nand max, or is not defined yet.')
        

        #UPDATE MAX
        elif event['column'] == 'Max':

            if not event['new'].replace(' ',''):
                widget.edit_cell(event['index'], 'Max', '')

            else:
                if df['DataType'][event['index']] == 'INT':

                    if not re.search(r'^-?\d+$', event['new']):
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')
                    
                    elif df['Min'][event['index']] and (float(event['new']) < float(df['Min'][event['index']])):
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Error : Minimum > Maximum.')

                
                elif df['DataType'][event['index']] == 'DOUBLE':

                    if re.search(r'^-?\d+\.$', event['new']):
                        if df['Min'][event['index']] and (float(event['new']) < float(df['Min'][event['index']])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')
                        
                        else:
                            widget.edit_cell(event['index'], 'Max', event['new']+'0')
                        
                    elif re.search(r'^-?\d+\.\d+$', event['new']):
                        if df['Min'][event['index']] and (float(event['new']) < float(df['Min'][event['index']])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Minimum > Maximum.')

                    else:
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')
                    

                else:
                    widget.edit_cell(event['index'], 'Max', event['old'])

                    with self._out2:
                        print('Error : this data type does not handle min nand max, or is not defined yet.')


        #UPDATE LEN
        elif event['column'] == 'Len':

            if df['DataType'][event['index']] not in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                widget.edit_cell(event['index'], 'Len', '')

                with self._out2:
                    print('Error : Len is exclusive to ARRAY type.')
            
            elif not df['DataType'][event['index']]:
                widget.edit_cell(event['index'], 'Len', event['old'])

                with self._out2:
                    print('Error : you must assign a DataType before giving a lenght.')
            
            else:
                if not re.search(r'^\d+$', event['new']):
                    widget.edit_cell(event['index'], 'Len', event['old'])

                    with self._out2:
                        print(r'Error : bad LEN format -> use [0-9]+ .')

        widget.on('cell_edited', self._cell_edited_Out)


    
    def _cell_edited_algofunc(self, event, widget):
        """
        Handles a cell edition in the function or algorithm list qgrid widget
        """

        self._out2.clear_output()

        widget.off('cell_edited', self._cell_edited_algofunc)

        if event['column'] == 'Filename' and event['new']:
            if event['new'].split('.')[-1] != 'pyx':
                widget.edit_cell(event['index'], 'Filename', event['old'])

                with self._out2:
                    print('File must be .pyx format.')
            else:
                df = widget.get_changed_df()
                tmplist = [i for i in df['Filename']]
                tmplist.remove(event['new'])
                if event['new'] in tmplist:
                    widget.edit_cell(event['index'], 'Filename', event['old'])

                    with self._out2:
                        print('This filename is already in the list.')

        widget.on('cell_edited', self._cell_edited_algofunc)



    def _row_added_In(self, event, widget):
        """
        Handles a row addition in the input list qgrid widget
        """

        widget.off('cell_edited', self._cell_edited_In)

        for column in ['Name','Description','InputType','DataType','Len','Category','Default','Min','Max','Unit','Uri']:
            widget.edit_cell(event['index'], column, '')
        widget._update_table(triggered_by='remove_row')

        widget.on('cell_edited', self._cell_edited_In)



    def _row_added_Out(self, event, widget):     
        """
        Handles a row addition in the output list qgrid widget
        """

        widget.off('cell_edited', self._cell_edited_Out)

        for column in ['Name','Description','DataType','Len','Category','Min','Max','Unit','Uri']:
            widget.edit_cell(event['index'], column, '')
        widget._update_table(triggered_by='remove_row')

        widget.on('cell_edited', self._cell_edited_Out)
    


    def _row_added_algofunc(self, event, widget):
        """
        Handles a row addition in the function or algorithm qgrid widget
        """

        widget.off('cell_edited', self._cell_edited_algofunc)

        widget.edit_cell(event['index'], 'Filename', '')
        widget.edit_cell(event['index'], 'Type', '')
        widget._update_table(triggered_by='remove_row')
        
        widget.on('cell_edited', self._cell_edited_algofunc)



    def displayMenu(self):
        """
        Displays the unit model creation menu for pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        display(self._out)
        display(self._out2)

        listkeys = ['Path','Model type','Model name']

        for i in self._datas.keys():

            with self._out:
                if i not in listkeys:
                    raise Exception("Could not display unit model edition menu : parameter data from editUnit(data) must contain these keys ['Path','Model type','Model name']")

                elif i == 'Model type' and self._datas[i] != 'unit':
                    raise Exception("Bad value error : Model type key's value must be unit.")

                else:
                    listkeys.remove(i)

        self._parse()

        tab = wg.Tab()
        tab.children = [self._informations, self._qgridIn, self._qgridOut, self._qgridFunction]
        tab.set_title(0, 'Header')
        tab.set_title(1, 'Inputs')
        tab.set_title(2, 'Outputs')
        tab.set_title(3, 'Functions')

        with self._out:
            display(wg.VBox([wg.HTML(value='<b><font size="5">Model edition : {}.{}.xml<br>-> Header and Data</font></b>'.format(self._datas['Model type'], self._datas['Model name'])), tab, wg.HBox([self._apply, self._cancel])]))


        self._qgridIn.on('cell_edited', self._cell_edited_In)
        self._qgridIn.on('row_added', self._row_added_In)

        self._qgridOut.on('cell_edited', self._cell_edited_Out)
        self._qgridOut.on('row_added', self._row_added_Out)

        self._qgridFunction.on('cell_edited', self._cell_edited_algofunc)
        self._qgridFunction.on('row_added', self._row_added_algofunc)

        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)
        