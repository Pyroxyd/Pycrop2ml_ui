import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.setsmanagement import manageparamset
from pycrop2ml_ui.menus.setsmanagement import managetestset


class createUnit():
    """
    Class providing the display of unit model creation menu for pycrop2ml's user interface.

    Parameters :\n
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
                        'Abstract': ''
                     }
    """

    def __init__(self, data):

        #buttons
        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._apply2 = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._exit = wg.Button(value=False,description='Exit',disabled=False,button_style='danger')

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()

        #dataframes and QGRID
        self._dataframeInputs = pandas.DataFrame(data={
            'Type': pandas.Categorical([''], categories=['','input','output','input & output']),
            'Name':[''],
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
        self._inouttab = qgrid.show_grid(self._dataframeInputs, show_toolbar=True)

        self._dataframeFunc = pandas.DataFrame(data={
            'Filename':[''],
            'Type': pandas.Categorical([''], categories=['','internal','external'])
            })
        self._functionqgrid = qgrid.show_grid(self._dataframeFunc, show_toolbar=True)

        #data
        self._datas = data



    def _eventApply(self, b):
        """
        Handles apply button on_click event
        """

        self._out2.clear_output()

        def _checkInOut():
            """
            Checks wheter the dataframe has at least one input and one output
            """

            listType = []
            for i in [j for j in self._dataframeInputs['Type']]:
                if i not in listType:
                    listType.append(i)
            
            return not any([not ('input' in listType or 'input & output' in listType), not ('output' in listType or 'input & output' in listType)])

        def _checkQgrid():
            """
            Checks wheter the whole required data set is verified in the inout dataframe
            """

            self._dataframeInputs = self._inouttab.get_changed_df()
            self._dataframeInputs.reset_index(inplace=True)

            for i in range(0, len(self._dataframeInputs['Name'])):

                if any([not self._dataframeInputs['Category'][i],
                        not self._dataframeInputs['Type'][i],
                        not self._dataframeInputs['Name'][i],
                        not self._dataframeInputs['Description'][i],
                        not self._dataframeInputs['DataType'][i],
                        not self._dataframeInputs['InputType'][i],
                        not self._dataframeInputs['Unit'][i],
                        (self._dataframeInputs['DataType'][i] in ['STRINGARRAY','DATEARRAY','INTARRAY','DOUBLEARRAY'] and not self._dataframeInputs['Len'][i])]):
                    return False
            return True

        def _checkFunc():
            """
            Checks wheter the whole required data set is verified in the function dataframe
            """
            self._dataframeFunc = self._functionqgrid.get_changed_df()
            filenames = [i for i in self._dataframeFunc['Filename']]
            types = [j for j in self._dataframeFunc['Type']]
            count = 0
            for f in range(len(filenames)):
                if not filenames[f-count] and not types[f-count]:
                    del types[f-count]
                    del filenames[f-count]
                    count += 1                  

            return '' not in filenames+types



        if _checkQgrid() and _checkInOut() and _checkFunc():
            
            paramdict = dict()
            vardict = {'inputs':dict(),'outputs':dict()}

            for i in range(0, len(self._dataframeInputs['Name'])):
                if self._dataframeInputs['InputType'][i] == 'parameter':    
                    paramdict[self._dataframeInputs['Name'][i]] = ''
                else:
                    if self._dataframeInputs['Type'][i] in ['input', 'input & output']:
                        vardict['inputs'][self._dataframeInputs['Name'][i]] = ''

                    if self._dataframeInputs['Type'][i] in ['output', 'input & output']:
                        vardict['outputs'][self._dataframeInputs['Name'][i]] = ['','']

            self._out.clear_output()
            self._out2.clear_output()
                
            with self._out:
                if paramdict:
                    try:
                        menu = manageparamset.manageParamset(self._datas, paramdict, dict(), {'Inputs': self._dataframeInputs, 'Functions': dict(zip([i for i in self._dataframeFunc['Filename'] if i],[j for j in self._dataframeFunc['Type'] if j]))}, vardict, dict(), iscreate=True)
                        menu.displayMenu()
                    except:
                        raise Exception('Could not load parametersets managing menu')
            
                elif vardict:      
                    try:
                        menu = managetestset.manageTestset(self._datas, vardict, dict(), dict(), {'Inputs': self._dataframeInputs, 'Functions': dict(zip([i for i in self._dataframeFunc['Filename']],[j for j in self._dataframeFunc['Type']]))}, iscreate=True)
                        menu.displayMenu()
                    except:
                        raise Exception('Could not load testsets managing menu')
            
                else:
                    raise Exception('No input nor output !')

        else:
            with self._out2:
                if not _checkInOut():
                    print('Model must contain at least one input and one output.')
                if not _checkQgrid:
                    print('Missing argument(s), these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Len (for array)\n\t- Unit')
                if not _checkFunc:
                    print('Missing argument(s) in Functions tab.')



    def _eventExit(self, b):
        """
        Handles exit button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()



    def _cell_edited(self, event, widget):
        """
        Handles every event occuring when a cell is edited in the qgrid widget for inputs and outputs
        """

        self._out2.clear_output()
        widget.off('cell_edited', self._cell_edited)

        df = widget.get_changed_df()

        #UPDATE NAME
        if event['column'] == 'Name':
            
            names = [i for i in df['Name']]
            names.remove(event['new'])
            
            if event['new'] in names:
                widget.edit_cell(event['index'], 'Name', event['old'])

                with self._out2:
                    print('Error : this name is already defined.')


        #UPDATE TYPE
        elif event['column'] == 'Type':

            if not event['new']:
                widget.edit_cell(event['index'], 'Category', '')
                widget.edit_cell(event['index'], 'InputType', '')

            elif event['new'] in ['output','input & output']:
                if df['InputType'][event['index']] == 'parameter':
                    widget.edit_cell(event['index'], 'Category', '')
                
                widget.edit_cell(event['index'], 'InputType', 'variable')
            
            if event['new'] == 'output':
                widget.edit_cell(event['index'], 'Default', '')


        #UPDATE INPUTTYPE
        elif event['column'] == 'InputType':

            if event['new'] == 'parameter':
                if df['Type'][event['index']] in ['output','input & output']:
                    widget.edit_cell(event['index'], 'InputType', event['old'])

                    with self._out2:
                        print('Warning : a parameter is always an input.')
                
                else:
                    widget.edit_cell(event['index'], 'Category', '')
            
            else:
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
            widget.edit_cell(event['index'], 'Default', '')

            if df['Type'][event['index']] != 'output':

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
            
            elif df['Type'][event['index']] == 'output':
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
                        
                        elif df['Max'][event['index']] and (int(df['Max'][event['index']]) < int(event['new'])):
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

                        else:
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

            if (df['DataType'][event['index']] not in ['STRINGARRAY','DATEARRAY','INTARRAY','DOUBLEARRAY']):
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

        widget.on('cell_edited', self._cell_edited)



    def _row_added(self, event, widget):
        """
        Handles a row addition in the input & output list qgrid widget
        """

        widget.off('cell_edited', self._cell_edited)

        for column in ['Type','Name','Description','InputType','DataType','Len','Category','Default','Min','Max','Unit','Uri']:
            widget.edit_cell(event['index'], column, '')
        widget._update_table(triggered_by='remove_row')

        widget.on('cell_edited', self._cell_edited)



    def _cell_edited_func(self, event, widget):
        """
        Handles every event occuring when a cell is edited in the function list qgrid widget
        """

        self._out2.clear_output()

        widget.off('cell_edited', self._cell_edited_func)

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
        
        widget.on('cell_edited', self._cell_edited_func)


    
    def _row_added_func(self, event, widget):
        """
        Handles a row addition in the function list qgrid widget
        """

        widget.off('cell_edited', self._cell_edited_func)

        widget.edit_cell(event['index'], 'Filename', '')
        widget.edit_cell(event['index'], 'Type', '')
        widget._update_table(triggered_by='remove_row')

        widget.on('cell_edited', self._cell_edited_func)



    def displayMenu(self):
        """
        Displays the unit model creation menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """


        display(self._out)
        display(self._out2)

        listkeys = ['Path','Model type','Model name','Model ID','Version','Timestep','Title','Authors','Institution','Reference','Abstract']

        for i in self._datas.keys():
            with self._out:
                if i not in listkeys:
                    raise Exception("Could not display unit model creation menu : parameter data from createUnit(data) must contain these keys ['Path','Model type','Model ID','Model name','Version','Timestep','Title','Authors','Institution','Reference','Abstract']")

                elif i == 'Model type' and self._datas[i] != 'unit':
                    raise Exception("Bad value error : Model type key's value must be unit.")

                else:
                    listkeys.remove(i)

        self._tab = wg.Tab([self._inouttab, self._functionqgrid])
        self._tab.set_title(0, 'Inputs & Outputs')
        self._tab.set_title(1, 'Functions')
   
        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> Inputs and Outputs</b>'.format(self._datas['Model name'])), self._tab, wg.HBox([self._apply, self._exit])]))
        
        self._inouttab.on('cell_edited', self._cell_edited)
        self._inouttab.on('row_added', self._row_added)
        self._functionqgrid.on('cell_edited', self._cell_edited_func)
        self._functionqgrid.on('row_added', self._row_added_func)
        self._apply.on_click(self._eventApply)
        self._exit.on_click(self._eventExit)
