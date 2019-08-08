import re

from copy import deepcopy
import ipywidgets as wg
import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.writeXML.writeunitxml import writeunitXML


class manageTestset():
    """
    Class providing the display of the testset edition menu for pycrop2ml's user interface.

    Parameters : \n
        - datas : {
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

        - vardict : {'inputs': {name : value},
                     'outputs' : {name : value}
                    }

        - testsetdict : {name : [
                                {testname : type(vardict)},
                                parameterset,
                                description
                                ]
                        }

        - paramsetdict : {paramset_name : [
                                          {param : value},
                                          description
                                          ]
                         }

        - df : {
                'Inputs' : pandas.DataFrame,
                'Functions' : dict(),
                'Outputs' : pandas.DataFrame -> only if iscreate is False
               }

        - iscreate : bool
    """

    def __init__(self, datas, vardict, testsetdict, paramsetdict, df, iscreate=True):

        #OUTPUTS
        self._out = wg.Output()
        self._out_testset = wg.Output()
        self._out_test = wg.Output()
        self._out3 = wg.Output()

        #BUTTONS
        self._editTestset = wg.Button(value=False, description='Edit', disabled=True, button_style='primary')
        self._createTestset = wg.Button(value=False, description='Create', disabled=False, button_style='success')
        self._createTest = wg.Button(value=False, description='Create', disabled=True, button_style='success')
        self._deleteTestset = wg.Button(value=False, description='Delete', disabled=False, button_style='danger')
        self._deleteTest = wg.Button(value=False, description='Delete', disabled=True, button_style='danger')

        self._apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        self._exit = wg.Button(value=False, description='Cancel', disabled=False, button_style='danger')

        self._applyGrid = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        
        #SELECTERS
        self._testsetSelecter = wg.Dropdown(options=[''],value='',description='TestSet:',disabled=False)
        self._testsetlist = ['']
        self._testSelecter = wg.Dropdown(options=[''],value='',description='Test:',disabled=True)
        self._testlist = {'':['']}

        #DATAS
        self._iscreate = iscreate
        self._currentQgrid = None
        self._datas = datas
        self._paramsetdict = paramsetdict
        self._df = df
        self._vardict = vardict             #{inputs:{name:value},outputs:{name:value}}

        self._testsetdict = testsetdict     #{testsetname:[ {testname:{inputs:{name:value},outputs:{name:value}}}, 
                                            #               description,
                                            #               parameterset
                                            #             ]}

        self._testsetsDataframe = dict()    #{testsetname:[ {testname:dataframe}, 
                                            #               description,
                                            #               parameterset
                                            #             ]}
                    


    def _initSet(self):
        """
        Initializes a dataframe for each testset in edition mode, else pass
        """

        if not self._iscreate:
            for k,v in self._testsetdict.items():
                if v[2] not in self._paramsetdict:
                    self._testsetdict[k][2] = ''
                    v[2] = ''

                self._testsetlist.append(k)
                self._testsetsDataframe[k] = [dict(), v[1], v[2]]
                self._testlist[k] = ['']

                for ktest, vtest in v[0].items():
                    self._testlist[k].append(ktest)

                    self._testsetsDataframe[k][0][ktest] = pandas.DataFrame(data={
                        'Name': [i[0] for i in vtest['inputs'].items()] + [i[0] for i in vtest['outputs'].items()],
                        'InputType': pandas.Categorical(['input' for _ in vtest['inputs']]+['output' for _ in vtest['outputs']], categories=['input', 'output']),
                        'DataType': [self._df['Inputs']['DataType'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in vtest['inputs'].items() if self._df['Inputs']['Name'][k] == i[0]] + 
                                    [self._df['Outputs']['DataType'][k] for k in range(0,len(self._df['Outputs']['Name'])) for i in vtest['outputs'].items() if self._df['Outputs']['Name'][k] == i[0]],
                        'Value': [i[1] for i in vtest['inputs'].items()] + [i[1][0] for i in vtest['outputs'].items()],
                        'Precision': ['' for _ in vtest['inputs'].items()] + [i[1][1] for i in vtest['outputs'].items()],
                        'Min': [self._df['Inputs']['Min'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in vtest['inputs'].items() if self._df['Inputs']['Name'][k] == i[0]] +
                                [self._df['Outputs']['Min'][k] for k in range(0,len(self._df['Outputs']['Name'])) for i in vtest['outputs'].items() if self._df['Outputs']['Name'][k] == i[0]],
                        'Max': [self._df['Inputs']['Max'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in vtest['inputs'].items() if self._df['Inputs']['Name'][k] == i[0]] + 
                                [self._df['Outputs']['Max'][k] for k in range(0,len(self._df['Outputs']['Name'])) for i in vtest['outputs'].items() if self._df['Outputs']['Name'][k] == i[0]]
                    })
            
            self._testsetSelecter.options = self._testsetlist



    def _cell_edited(self, event, widget):
        """
        Handles every cell edition in the current qgrid widget
        """

        self._out3.clear_output()
        
        widget.off('cell_edited', self._cell_edited)

        df = widget.get_changed_df()

        if event['column'] not in ['Value','Precision']:
            widget.edit_cell(event['index'], event['column'], event['old'])


        elif event['column'] == 'Precision':
            if df['InputType'][event['index']] != 'output':
                widget.edit_cell(event['index'], 'Precision', event['old'])

                with self._out3:
                    print('Error : this inputtype does not handle a precision.')

            elif df['DataType'][event['index']] not in ['DOUBLE','DOUBLELIST','DOUBLEARRAY']:
                widget.edit_cell(event['index'], 'Precision', event['old'])

                with self._out3:
                    print('Error : this datatype does not handle a precision.')
            
            elif not re.search(r'^\d+$', event['new']):
                widget.edit_cell(event['index'], 'Precision', event['old'])

                with self._out3:
                    print(r'Error : bad INT format -> use [0-9]+ .')
            
            else:
                if df['Value'][event['index']] and df['DataType'][event['index']]=='DOUBLE':
                    if int(event['new']) > int(event['old']):
                        widget.edit_cell(event['index'], 'Value', df['Value'][event['index']]+'0'*(int(event['new'])-int(event['old'])))
                    else:
                        diff = int(event['old'])-int(event['new'])
                        widget.edit_cell(event['index'], 'Value', df['Value'][event['index']][:-diff]) 
        
        else:
            if not event['new'].replace(' ',''):
                widget.edit_cell(event['index'], 'Value', '')

            else:      
                if df['DataType'][event['index']] == 'DATE':
                    if not re.search(r'^(?:(?:31\/(?:0?[13578]|1[02]))\/|(?:(?:29|30)\/(?:0?[13-9]|1[0-2])\/))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29\/0?2\/(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])\/(?:(?:0?[1-9])|(?:1[0-2]))\/(?:(?:1[6-9]|[2-9]\d)?\d{2})$', event['new']):
                        widget.edit_cell(event['index'], 'Value', event['old'])

                        with self._out3:
                            print('Error : bad DATE format -> use dd/mm/yyyy.')
                
                elif df['DataType'][event['index']] == 'BOOLEAN':
                    if not any([df['Default'][event['index']] == 'True', df['Default'][event['index']] == 'False']):
                        widget.edit_cell(event['index'], 'Value', event['old'])

                        with self._out3:
                            print('Error : bad BOOLEAN format -> use True|False.')
                
                elif df['DataType'][event['index']] == 'INT':

                    if re.search(r'^-?\d+$', event['new']):
                        if any([df['Min'][event['index']] and (int(df['Min'][event['index']]) > int(event['new'])),
                                df['Max'][event['index']] and (int(df['Max'][event['index']]) < int(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Value', event['old'])

                            with self._out3:
                                print('Error : Value must be in between Min and Max.')

                    else:
                        widget.edit_cell(event['index'], 'Value', event['old'])

                        with self._out3:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')
                
                elif df['DataType'][event['index']] == 'DOUBLE' and df['Precision'][event['index']] and df['InputType'][event['index']] == 'output':

                    if re.search(r'^-?\d+\.$', event['new']):
                        if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                                df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Value', event['old'])

                            with self._out3:
                                print('Error : Value must be in between Min and Max.')

                        else:
                            widget.edit_cell(event['index'], 'Value', event['new']+'0'*int(df['Precision'][event['index']]))
                        
                    elif re.search(r'^-?\d+\.\d+$', event['new']):
                        if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                                df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Value', event['old'])

                            with self._out3:
                                print('Error : Value must be in between Min and Max.')

                        else:
                            ent,dec = event['new'].split('.')
                            if len(dec) > int(df['Precision'][event['index']]):
                                widget.edit_cell(event['index'], 'Value', ent+'.'+dec[:int(df['Precision'][event['index']])])
                            else:
                                widget.edit_cell(event['index'], 'Value', ent+'.'+dec+'0'*(int(df['Precision'][event['index']])-len(dec)))                                

                    else:
                        widget.edit_cell(event['index'], 'Value', event['old'])

                        with self._out3:
                            print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')
                
                elif df['DataType'][event['index']] == 'DOUBLE' and not df['Precision'][event['index']] and df['InputType'][event['index']] == 'output':
                    widget.edit_cell(event['index'], 'Value', event['old'])

                    with self._out3:
                        print('Warning : DOUBLE type needs a precision first.')
                
                elif df['DataType'][event['index']] == 'DOUBLE':
                    if re.search(r'^-?\d+\.$', event['new']):
                        if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                                df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Value', event['old'])

                            with self._out3:
                                print('Error : Value must be in between Min and Max.')
                        else:
                            widget.edit_cell(event['index'], 'Value', event['new']+'0')
                        
                    elif re.search(r'^-?\d+\.\d+$', event['new']):
                        if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                                df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Value', event['old'])

                            with self._out3:
                                print('Error : Value must be in between Min and Max.')

                    else:
                        widget.edit_cell(event['index'], 'Value', event['old'])

                        with self._out3:
                            print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')

        widget.on('cell_edited', self._cell_edited)



    def _on_value_change_testset(self, change):
        """
        Handles every testset selecter change
        """

        if change['new']:
            self._testSelecter.options = self._testlist[change['new']]
            self._createTest.disabled = False
            self._deleteTest.disabled = False
            self._testSelecter.disabled = False
            self._editTestset.disabled = False

        else:
            self._testSelecter.value = ''
            self._testSelecter.options = self._testlist['']
            self._createTest.disabled = True
            self._deleteTest.disabled = True
            self._testSelecter.disabled = True
            self._editTestset.disabled = True

    

    def _on_value_change_test(self, change):
        """
        Handles every test selecter change
        """
        
        self._out3.clear_output()
        
        if change['new']:
            self._testSelecter.disabled = True
            self._testsetSelecter.disabled = True
            self._createTest.disabled = True
            self._createTestset.disabled = True
            self._apply.disabled = True

            self._currentQgrid = qgrid.show_grid(self._testsetsDataframe[self._testsetSelecter.value][0][self._testSelecter.value], show_toolbar=False)
            apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')

            with self._out_test:
                display(wg.VBox([self._currentQgrid, apply]))
            

            def eventApply(b):
                
                self._out3.clear_output()

                self._testsetsDataframe[self._testsetSelecter.value][0][self._testSelecter.value] = self._currentQgrid.get_changed_df()
                
                if '' in [i for i in self._testsetsDataframe[self._testsetSelecter.value][0][self._testSelecter.value]['Value']]:
                    with self._out3:
                        print('Missing value(s).')
                
                else:
                    self._testSelecter.disabled = False
                    self._testSelecter.unobserve(self._on_value_change_test, names='value')
                    self._testSelecter.value = ''
                    self._testSelecter.observe(self._on_value_change_test, names='value')

                    self._testsetSelecter.disabled = False
                    self._createTest.disabled = False
                    if not self._editTestset.disabled:
                        self._createTestset.disabled = False
                    self._apply.disabled = False
                    self._out_test.clear_output()


            self._currentQgrid.on('cell_edited', self._cell_edited)
            apply.on_click(eventApply)



    def _eventEditTestset(self, b):
        """
        Handles testset edit button on_click event
        """

        self._out3.clear_output()
        
        testsetname = wg.Textarea(value=self._testsetSelecter.value, description='Testset name:', disabled=False)
        description = wg.Textarea(value=self._testsetdict[self._testsetSelecter.value][1], description='Description:', disabled=False)
        paramset = wg.Dropdown(options=['']+[k[0] for k in self._paramsetdict.items()],value=self._testsetdict[self._testsetSelecter.value][2],description='Parameterset:',disabled=False)
        apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='warning')

        self._createTestset.disabled = True
        self._editTestset.disabled = True
        self._testsetSelecter.disabled = True
        self._apply.disabled = True

        with self._out_testset:
            display(wg.VBox([testsetname, description, paramset, wg.HBox([apply, cancel])]))

        
        def eventApply(b):

            self._out3.clear_output()

            tmptestsetlist = deepcopy(self._testsetlist)
            tmptestsetlist.remove(self._testsetSelecter.value)

            if testsetname.value in tmptestsetlist:
                with self._out3:
                    print('This testset already exists.')

            elif all([testsetname.value, description.value, any([paramset.value, not self._paramsetdict])]):
                self._testsetSelecter.unobserve(self._on_value_change_testset, names='value')

                self._testsetlist.append(testsetname.value)
                self._testsetlist.remove(self._testsetSelecter.value)

                self._testlist[testsetname.value] = self._testlist.pop(self._testsetSelecter.value)

                self._testsetdict[testsetname.value] = self._testsetdict.pop(self._testsetSelecter.value)
                self._testsetdict[testsetname.value][1] = description.value
                self._testsetdict[testsetname.value][2] = paramset.value

                self._testsetsDataframe[testsetname.value] = self._testsetsDataframe.pop(self._testsetSelecter.value)
                self._testsetsDataframe[testsetname.value][1] = description.value
                self._testsetsDataframe[testsetname.value][2] = paramset.value

                self._testsetSelecter.value = ''
                self._testsetSelecter.options = self._testsetlist
                self._testsetSelecter.value = testsetname.value

                self._editTestset.disabled = False
                self._createTestset.disabled = False
                self._deleteTestset.disabled = False
                self._testsetSelecter.disabled = False
                self._apply.disabled = False

                self._testsetSelecter.observe(self._on_value_change_testset, names='value')

                self._out_testset.clear_output()

            else:
                with self._out3:
                    print('Missing argument(s).')
        
        def eventCancel(b):
            
            self._out_testset.clear_output()
            self._createTestset.disabled = False
            self._editTestset.disabled = False
            self._testsetSelecter.disabled = False
            self._apply.disabled = False

        apply.on_click(eventApply)
        cancel.on_click(eventCancel)



    def _eventCreateTestset(self, b):
        """
        Handles testset creation button on_click event
        """
        
        self._out3.clear_output()

        testsetname = wg.Textarea(value='', description='Testset name:', disabled=False)
        description = wg.Textarea(value='', description='Description:', disabled=False)
        paramset = wg.Dropdown(options=['']+[k[0] for k in self._paramsetdict.items()],value='',description='Parameterset:',disabled=False)
        apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='warning')

        self._createTestset.disabled = True
        self._deleteTestset.disabled = True
        self._testsetSelecter.disabled = True
        self._createTest.disabled = True
        self._deleteTest.disabled = True
        self._testSelecter.disabled = True
        self._apply.disabled = True

        with self._out_test:
            display(wg.VBox([testsetname, description, paramset, wg.HBox([apply, cancel])]))
    

        def eventApply(b):

            self._out3.clear_output()

            if testsetname.value in self._testsetlist:
                with self._out3:
                    print('This testset already exists.')

            elif all([testsetname.value, description.value, any([paramset.value, not self._paramsetdict])]):
                self._testsetSelecter.unobserve(self._on_value_change_testset, names='value')

                self._testsetSelecter.value = ''
                self._editTestset.disabled = True

                self._testsetlist.append(testsetname.value)
                self._testsetSelecter.options = self._testsetlist
                self._testlist[testsetname.value] = ['']

                self._testSelecter.value = ''
                self._testSelecter.options = ['']

                self._testsetdict[testsetname.value] = [dict(), description.value, paramset.value]
                self._testsetsDataframe[testsetname.value] = [dict(), description.value, paramset.value]

                self._createTestset.disabled = False
                self._deleteTestset.disabled = False
                self._testsetSelecter.disabled = False
                self._apply.disabled = False

                self._testsetSelecter.observe(self._on_value_change_testset, names='value')

                self._out_test.clear_output()

            else:
                with self._out3:
                    print('Missing argument(s).')
        
        def eventCancel(b):
            
            self._out_test.clear_output()
            self._createTestset.disabled = False
            self._deleteTestset.disabled = False
            self._testsetSelecter.disabled = False
            self._createTest.disabled = False
            self._deleteTest.disabled = False
            self._testSelecter.disabled = False
            self._apply.disabled = False
        
        apply.on_click(eventApply)
        cancel.on_click(eventCancel)



    def _eventDeleteTestset(self, b):    
        """
        Handles testset deletion button on_click event
        """

        self._out3.clear_output()
        self._out_test.clear_output()
        self._out_testset.clear_output()
        
        self._apply.disabled = False
        self._testSelecter.disabled = False
        self._testsetSelecter.disabled = False
        self._createTest.disabled = False
        self._createTestset.disabled = False

        if self._testsetSelecter.value:
            
            self._testsetSelecter.unobserve(self._on_value_change_testset, names='value')
            self._testSelecter.unobserve(self._on_value_change_test, names='value')

            self._testsetlist.remove(self._testsetSelecter.value)
            del self._testlist[self._testsetSelecter.value]
            del self._testsetdict[self._testsetSelecter.value]
            del self._testsetsDataframe[self._testsetSelecter.value]
   
            self._testsetSelecter.value = ''
            self._editTestset.disabled = True
            self._testSelecter.value = ''
        
            self._testsetSelecter.options = self._testsetlist           
            self._testSelecter.options = self._testlist['']
   
            self._testsetSelecter.observe(self._on_value_change_testset, names='value')
            self._testSelecter.observe(self._on_value_change_test, names='value')


    
    def _eventCreateTest(self, b):
        """
        Handles test creation button on_click event
        """
        
        self._out3.clear_output()
        self._out_test.clear_output()

        testname = wg.Textarea(value='', description='Test name:', disabled=False)
        apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='warning')

        if self._testsetSelecter.value:
            self._createTestset.disabled = True
            self._deleteTestset.disabled = True
            self._testsetSelecter.disabled = True
            self._createTest.disabled = True
            self._deleteTest.disabled = True
            self._testSelecter.disabled = True
            self._apply.disabled = True

            with self._out_test:
                display(wg.VBox([testname, wg.HBox([apply, cancel])]))
        

            def eventApply(b):

                self._out3.clear_output()

                if testname.value in self._testlist[self._testsetSelecter.value]:
                    with self._out3:
                        print('This test already exists.')
                
                elif testname.value:
                    self._testSelecter.unobserve(self._on_value_change_test, names='value')

                    self._testSelecter.value = ''
                    self._testlist[self._testsetSelecter.value].append(testname.value)
                    self._testSelecter.options = self._testlist[self._testsetSelecter.value]

                    self._testsetdict[self._testsetSelecter.value][0][testname.value] = deepcopy(self._vardict)

                    if not self._iscreate:
                        self._testsetsDataframe[self._testsetSelecter.value][0][testname.value] = pandas.DataFrame(data={
                            'Name': [i[0] for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items()] + [i[0] for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items()],
                            'InputType': pandas.Categorical(['input' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items()]+['output' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items()], categories=['input', 'output']),
                            'DataType': [self._df['Inputs']['DataType'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items() if self._df['Inputs']['Name'][k] == i[0]] + 
                                        [self._df['Outputs']['DataType'][k] for k in range(0,len(self._df['Outputs']['Name'])) for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items() if self._df['Outputs']['Name'][k] == i[0]],
                            'Value': ['' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items()] + ['' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items()],
                            'Precision': ['' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items()] + ['' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items()],
                            'Min': [self._df['Inputs']['Min'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items() if self._df['Inputs']['Name'][k] == i[0]] +
                                    [self._df['Outputs']['Min'][k] for k in range(0,len(self._df['Outputs']['Name'])) for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items() if self._df['Outputs']['Name'][k] == i[0]],
                            'Max': [self._df['Inputs']['Max'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items() if self._df['Inputs']['Name'][k] == i[0]] + 
                                    [self._df['Outputs']['Max'][k] for k in range(0,len(self._df['Outputs']['Name'])) for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items() if self._df['Outputs']['Name'][k] == i[0]]
                        })
                    
                    else:
                        self._testsetsDataframe[self._testsetSelecter.value][0][testname.value] = pandas.DataFrame(data={
                            'Name': [i[0] for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items()] + [i[0] for i in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items()],
                            'InputType': pandas.Categorical(['input' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'].items()]+['output' for _ in self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs'].items()], categories=['input', 'output']),
                            'DataType': [self._df['Inputs']['DataType'][k] for k in range(0,len(self._df['Inputs']['DataType'])) for i in {**self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'], **self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs']}.items() if self._df['Inputs']['Name'][k] == i[0]],
                            'Value': ['' for _ in {**self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'], **self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs']}.items()],
                            'Precision': ['' for _ in {**self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'], **self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs']}.items()],
                            'Min': [self._df['Inputs']['Min'][k] for k in range(0,len(self._df['Inputs']['Min'])) for i in {**self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'], **self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs']}.items() if self._df['Inputs']['Name'][k] == i[0]],
                            'Max': [self._df['Inputs']['Max'][k] for k in range(0,len(self._df['Inputs']['Max'])) for i in {**self._testsetdict[self._testsetSelecter.value][0][testname.value]['inputs'], **self._testsetdict[self._testsetSelecter.value][0][testname.value]['outputs']}.items() if self._df['Inputs']['Name'][k] == i[0]]
                        })
                    
                    self._createTestset.disabled = False
                    self._deleteTestset.disabled = False
                    self._testsetSelecter.disabled = False
                    self._createTest.disabled = False
                    self._deleteTest.disabled = False
                    self._testSelecter.disabled = False
                    self._apply.disabled = False

                    self._testSelecter.observe(self._on_value_change_test, names='value')

                    self._out_test.clear_output()

                else:
                    with self._out3:
                        print('Missing name.')
        

            def eventCancel(b):
                
                self._out_test.clear_output()
                self._createTestset.disabled = False
                self._deleteTestset.disabled = False
                self._testsetSelecter.disabled = False
                self._createTest.disabled = False
                self._deleteTest.disabled = False
                self._testSelecter.disabled = False
                self._apply.disabled = False
            
            apply.on_click(eventApply)
            cancel.on_click(eventCancel)

    

    def _eventDeleteTest(self, b):
        """
        Handles test deletion button on_click event
        """

        self._out3.clear_output()
        self._out_test.clear_output()

        self._apply.disabled = False
        self._testSelecter.disabled = False
        self._testsetSelecter.disabled = False
        self._createTest.disabled = False
        self._createTestset.disabled = False

        if self._testSelecter.value:
            
            self._testSelecter.unobserve(self._on_value_change_test, names='value')

            self._testlist[self._testsetSelecter.value].remove(self._testSelecter.value)
            
            del self._testsetdict[self._testsetSelecter.value][0][self._testSelecter.value]
            del self._testsetsDataframe[self._testsetSelecter.value][0][self._testSelecter.value]
                   
            self._testSelecter.value = ''
            self._testSelecter.options = self._testlist[self._testsetSelecter.value]

            self._testSelecter.observe(self._on_value_change_test, names='value')



    def _eventApply(self, b):
        """
        Handles apply button on_click event
        """

        self._out3.clear_output()

        tmplist = []
        tmplistset = []

        for testsetname,args in self._testsetsDataframe.items():
            if any([not args[1], not args[2] and self._paramsetdict]):
                tmplistset.append(testsetname)

            for testname,dataframe in args[0].items():
                for x in range(0,len(dataframe['Value'])):
                    if dataframe['Value'][x]:
                        if dataframe['InputType'][x] == 'input':
                            self._testsetdict[testsetname][0][testname]['inputs'][dataframe['Name'][x]] = dataframe['Value'][x]
                        else:
                            self._testsetdict[testsetname][0][testname]['outputs'][dataframe['Name'][x]] = [dataframe['Value'][x],dataframe['Precision'][x]]
                    else:
                        if '{}:{}'.format(testsetname,testname) not in tmplist:
                            tmplist.append('{}:{}'.format(testsetname,testname))

        if all([not tmplist, not tmplistset]):
            self._out.clear_output()
            self._out_test.clear_output()
            self._out3.clear_output()

            with self._out:
                try:
                    xml = writeunitXML(self._datas, self._df, self._paramsetdict, self._testsetdict, self._iscreate)
                    xml.displayMenu()
                except:
                    raise Exception('Could not load writeunitxml class.')
        
        else:
            with self._out3:
                if tmplistset:
                    print('Missing value(s) in testsets : {}.'.format(tmplistset))
                if tmplist:
                    print('Missing value(s) in tests : {}.'.format(tmplist))
                


    def _eventExit(self, b):
        """
        Handles exit button on_click event
        """
        
        self._out.clear_output()
        self._out_test.clear_output()
        self._out_testset.clear_output()
        self._out3.clear_output()


            
    def displayMenu(self):
        """
        Displays the testset edition menu for Pycrop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        self._initSet()

        display(self._out)
        display(self._out3)

        with self._out:
            if self._iscreate:
                display(wg.VBox([wg.HTML(value='<b><font size="5">Model creation : {}.{}.xml<br>-> TestSets</font></b>'.format(self._datas['Model type'], self._datas['Model name'])), wg.HBox([self._testsetSelecter, self._editTestset, self._createTestset, self._deleteTestset]), self._out_testset, wg.HBox([self._testSelecter, self._createTest, self._deleteTest]), self._out_test, wg.HBox([self._apply, self._exit])]))
            else:
                display(wg.VBox([wg.HTML(value='<b><font size="5">Model edition : {}.{}.xml<br>-> TestSets</font></b>'.format(self._datas['Model type'], self._datas['Model name'])), wg.HBox([self._testsetSelecter, self._editTestset, self._createTestset, self._deleteTestset]), self._out_testset, wg.HBox([self._testSelecter, self._createTest, self._deleteTest]), self._out_test, wg.HBox([self._apply, self._exit])]))

        self._testsetSelecter.observe(self._on_value_change_testset, names='value')
        self._editTestset.on_click(self._eventEditTestset)
        self._createTestset.on_click(self._eventCreateTestset)
        self._deleteTestset.on_click(self._eventDeleteTestset)

        self._testSelecter.observe(self._on_value_change_test, names='value')
        self._createTest.on_click(self._eventCreateTest)
        self._deleteTest.on_click(self._eventDeleteTest)

        self._apply.on_click(self._eventApply)
        self._exit.on_click(self._eventExit)