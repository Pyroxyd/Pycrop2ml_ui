import re

from copy import deepcopy
import ipywidgets as wg
import qgrid
import pandas
from IPython.display import display

from pycrop2ml_ui.menus.setsmanagement import managetestset


class manageParamset():
    """
    Class providing the display of the parameterset edition menu for pycrop2ml's user interface.

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
        
        - paramdict : {param_name : value}

        - paramsetdict : {paramset_name : [
                                          {param_name : value},
                                          description
                                          ]
                         }

        - df : {
                'Inputs' : pandas.DataFrame,
                'Functions' : dict(),
                'Outputs' : pandas.DataFrame -> only if iscreate is False
               }

        - vardict : {
                     'inputs': {name : value},
                     'outputs' : {name : value}
                    }

        - testsetdict : {name : [
                                {testname : type(vardict)},
                                parameterset,
                                description
                                ]
                        }

        - iscreate : bool
    """

    def __init__(self, datas, paramdict, paramsetdict, df, vardict, testsetdict, iscreate=True):
    
        self._out = wg.Output()
        self._out2 = wg.Output()
        self._out3 = wg.Output()

        self._datas = datas
        self._paramdict = paramdict #{param:value}
        self._paramsetdict = paramsetdict #{paramset_name:[{param:value}, description]}
        self._paramsetdictDataframe = dict()  #{paramset_name:[dataframe, description]}
        self._vardict = vardict
        self._testsetdict = testsetdict
        self._iscreate = iscreate
        self._setlist = ['']
        self._df = df

        self._paramselecter = wg.Dropdown(options=[''],value='',description='ParameterSet:',disabled=False)
        self._description = wg.Textarea(value='',description='Description:',disabled=False)
        self._currentQgrid = None

        self._apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        self._exit = wg.Button(value=False, description='Cancel', disabled=False, button_style='danger')
        self._create = wg.Button(value=False, description='Create', disabled=False, button_style='primary')
        self._delete = wg.Button(value=False, description='Delete', disabled=False, button_style='danger')
        self._applyparam = wg.Button(value=False, description='Apply', disabled=False, button_style='success')



    def _eventCreate(self, b):
        """
        Handles create button on_click event
        """
        
        self._out2.clear_output()
        self._out3.clear_output()
        self._paramselecter.disabled = True
        self._delete.disabled = True
        self._create.disabled = True

        paramsetName = wg.Textarea(value='', description='Name:',disabled=False)
        description = wg.Textarea(value='', description='Description:',disabled=False)
        apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='warning')

        with self._out2:
            display(wg.VBox([paramsetName, description, wg.HBox([apply, cancel])]))
        

        def eventApply(b):

            if paramsetName.value in self._setlist:
                with self._out3:
                    print('This parameterset already exists.')

            elif paramsetName.value and description.value:
                self._out2.clear_output()
                self._out3.clear_output()
                self._paramselecter.disabled = False
                self._delete.disabled = False
                self._create.disabled = False
                self._setlist.append(paramsetName.value)
                self._paramselecter.options = self._setlist

                self._paramsetdict[paramsetName.value] = [deepcopy(self._paramdict), description.value]

                self._paramsetdictDataframe[paramsetName.value] = [pandas.DataFrame(data={
                    'Name': [i[0] for i in self._paramsetdict[paramsetName.value][0].items()],
                    'DataType': [self._df['Inputs']['DataType'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in self._paramsetdict[paramsetName.value][0].items() if self._df['Inputs']['Name'][k] == i[0]],
                    'Value': [j[1] for j in self._paramsetdict[paramsetName.value][0].items()],
                    'Min': [self._df['Inputs']['Min'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in self._paramsetdict[paramsetName.value][0].items() if self._df['Inputs']['Name'][k] == i[0]],
                    'Max': [self._df['Inputs']['Max'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in self._paramsetdict[paramsetName.value][0].items() if self._df['Inputs']['Name'][k] == i[0]]
                }), self._paramsetdict[paramsetName.value][1]]
            
            else:
                with self._out3:
                    print('Missing argument(s).')

        
        def eventCancel(b):

            self._out2.clear_output()
            self._paramselecter.disabled = False
            self._delete.disabled = False
            self._create.disabled = False


        apply.on_click(eventApply)
        cancel.on_click(eventCancel)
        


    def _eventDelete(self, b):
        """
        Handles delete button on_click event
        """

        self._out2.clear_output()
        self._out3.clear_output()

        if self._paramselecter.value:

            self._paramselecter.unobserve(self._on_value_change, names='value')

            self._paramselecter.disabled = True

            del self._paramsetdict[self._paramselecter.value]
            del self._paramsetdictDataframe[self._paramselecter.value]
            self._setlist.remove(self._paramselecter.value)
            self._paramselecter.value = ''
            self._paramselecter.options = self._setlist
            self._description.value = ''
            self._currentQgrid = None

            self._paramselecter.disabled = False
            self._create.disabled = False
            self._apply.disabled = False

            self._paramselecter.observe(self._on_value_change, names='value')



    def _cell_edited(self, event, widget):
        """
        Handles every cell edition in the current qgrid widget
        """

        self._out3.clear_output()
        
        widget.off('cell_edited', self._cell_edited)

        df = widget.get_changed_df()

        if event['column'] != 'Value':
            widget.edit_cell(event['index'], event['column'], event['old'])
        
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



    def _on_value_change(self, change):
        """
        Handles every change in the parameterset selecter
        """
            
        self._out2.clear_output()
        self._out3.clear_output()
        
        if self._paramselecter.value:
            self._create.disabled = True
            self._paramselecter.disabled = True
            self._apply.disabled = True

            self._currentQgrid = qgrid.show_grid(self._paramsetdictDataframe[self._paramselecter.value][0], show_toolbar=False)
            self._description.value = self._paramsetdictDataframe[self._paramselecter.value][1]

            with self._out2:
                display(wg.VBox([self._description, self._currentQgrid, self._applyparam]))
            

            def eventApply(b):

                self._out3.clear_output()
                self._paramsetdictDataframe[self._paramselecter.value][0] = self._currentQgrid.get_changed_df()
                
                if self._description.value:

                    def checkQgrid():

                        for i in range(0, len(self._paramsetdictDataframe[self._paramselecter.value][0]['Value'])):
                            if not self._paramsetdictDataframe[self._paramselecter.value][0]['Value'][i]:
                                return False
                        return True

                    if checkQgrid():
                        self._paramsetdictDataframe[self._paramselecter.value][1] = self._description.value
                        self._description.value = ''
                        self._currentQgrid = None
                        self._out2.clear_output()
                        self._create.disabled = False
                        self._paramselecter.value = ''
                        self._paramselecter.disabled = False
                        self._apply.disabled = False
                        
                    else:
                        with self._out3:
                            print('Missing value(s).')
                
                else:
                    with self._out3:
                        print('Missing description.')


            self._currentQgrid.on('cell_edited', self._cell_edited)
            self._applyparam.on_click(eventApply)



    def _eventApply(self, b):    
        """
        Handles apply button on_click event
        """

        self._out3.clear_output()        

        tmplist = []
        
        for i,j in self._paramsetdictDataframe.items():
            for k in [x for x in j[0]['Value']]:
                if any([not k, not j[1]]) and i not in tmplist:
                    tmplist.append(i)

        if not tmplist:

            self._out.clear_output()
            self._out2.clear_output()
            self._out3.clear_output()

            for i,j in self._paramsetdictDataframe.items():
                self._paramsetdict[i][1] = j[1]
                for k in range(0,len(j[0]['Value'])):
                    self._paramsetdict[i][0][j[0]['Name'][k]] = j[0]['Value'][k]

            with self._out:
                try:
                    menu = managetestset.manageTestset(self._datas, self._vardict, self._testsetdict, self._paramsetdict, self._df, self._iscreate)
                    menu.displayMenu()
                except:
                    raise Exception('Could not load testset unit model edition menu.')
        
        else:
            with self._out3:
                print('Missing value(s) in parametersets : {}.'.format(tmplist))


                
    def _eventExit(self, b):
        """
        Handles exit button on_click event
        """
        
        self._out.clear_output()
        self._out2.clear_output()
        self._out3.clear_output()



    def displayMenu(self):
        """
        Displays the parameterset edition menu for Pycrop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """

        if not self._iscreate:
            for paramset,value in self._paramsetdict.items():
                self._paramsetdictDataframe[paramset] = [pandas.DataFrame(data={
                    'Name': [i[0] for i in value[0].items()],
                    'DataType': [self._df['Inputs']['DataType'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in value[0].items() if self._df['Inputs']['Name'][k] == i[0]],
                    'Value': [j[1] for j in value[0].items()],
                    'Min':[self._df['Inputs']['Min'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in value[0].items() if self._df['Inputs']['Name'][k] == i[0]],
                    'Max':[self._df['Inputs']['Max'][k] for k in range(0,len(self._df['Inputs']['Name'])) for i in value[0].items() if self._df['Inputs']['Name'][k] == i[0]]
                }), value[1]]

                self._setlist.append(paramset)

        self._paramselecter.options = self._setlist

        display(self._out)      
        display(self._out3)

        with self._out:
            if self._iscreate:
                display(wg.VBox([wg.HTML(value='<b><font size="5">Model creation : {}.{}.xml<br>-> ParametersSet</font></b>'.format(self._datas['Model type'], self._datas['Model name'])), wg.HBox([self._paramselecter, self._create, self._delete]), self._out2, wg.HBox([self._apply, self._exit])]))
            else:
                display(wg.VBox([wg.HTML(value='<b><font size="5">Model edition : {}.{}.xml<br>-> ParametersSet</font></b>'.format(self._datas['Model type'], self._datas['Model name'])), wg.HBox([self._paramselecter, self._create, self._delete]), self._out2, wg.HBox([self._apply, self._exit])]))


        self._apply.on_click(self._eventApply)
        self._create.on_click(self._eventCreate)
        self._delete.on_click(self._eventDelete)
        self._exit.on_click(self._eventExit)
        self._paramselecter.observe(self._on_value_change, names='value')
