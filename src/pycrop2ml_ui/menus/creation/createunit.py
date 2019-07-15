import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.cpackage.CreationRepository import mkdirModel



class paramSet():

    def __init__(self, name, description):

        self.name = name
        self.description = description
        self.dictparam = dict()


class test():

    def __init__(self, name):

        self.name = name
        self.valuesIn = dict()
        self.valuesOut = dict()


class testSet():

    def __init__(self, name, description, paramset):

        self.name = name
        self.description = description
        self.paramset = paramset
        self.listetest = []



class createUnit():


    def __init__(self):


        #buttons
        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._apply2 = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        #outputs
        self._out = wg.Output()
        self._out2 = wg.Output()



        #IN AND OUT table
        self._dataframeInputs = pandas.DataFrame(data={
            'Type': pandas.Categorical([''], categories=['','input','output','input & output']),
            'Name':[''],
            'Description': [''],
            'InputType': pandas.Categorical([''], categories=['','variable','parameter']),
            'Category': pandas.Categorical([''], categories=['','constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([''], categories=['','DOUBLE','DOUBLELIST','DOUBLEARRAY','INT','INTLIST','INTARRAY','STRING','STRINGLIST','STRINGARRAY','BOOLEAN','DATE','DATELIST','DATEARRAY']),
            'Default': [''],
            'Min': [''],
            'Max': [''],
            'Unit': [''],
            'Uri': ['']})

        self._inouttab = qgrid.show_grid(self._dataframeInputs, show_toolbar=True)
        
        

        #PARAMETERSETS
        self._parametersetname = wg.Textarea(value='',description='Name',disabled=False)
        self._parametersetdescription = wg.Textarea(value='',description='Description',disabled=False)

        self._paramsets = []
        self._parametersset = wg.VBox([self._parametersetname, self._parametersetdescription])
    
        #TESTSETS
        self._testsetname = wg.Textarea(value='',description='Testset name',disabled=False)
        self._testsetdescription = wg.Textarea(value='',description='Description',disabled=False)
        self._testsetselecter = wg.Dropdown(options=[''],value='',description='ParametersSet:',disabled=False)
        self._testsetbutton = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        
        self._testsets = []
        self._testsettab = wg.VBox([self._testsetname, self._testsetdescription, self._testsetselecter, wg.HBox([self._testsetbutton, self._cancel])])


        self._datas = dict()




    def _createAlgo(self):

        try:
            algo = open("{}/algo/pyx/{}.pyx".format(self._datas['Path'], self._datas['Model name']), 'w')

        except IOError as ioerr:
            with self._out2:
                print("Algorithm file {}.pyx could not be created. {}".format(self._datas['Model name'], ioerr))

        else:

            algo.write('# inputs : ')
            for i in range(0,len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Type'][i] == 'input', self._dataframeInputs['Type'][i] == 'input & output']):
                    algo.write('{}({}):[default={},min={},max={}], '.format(self._dataframeInputs['Name'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i]))

            algo.write('\n# outputs : ')
            for i in range(0,len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Type'][i] == 'output', self._dataframeInputs['Type'][i] == 'input & output']):                    
                    algo.write('{}({}):[default={},min={},max={}], '.format(self._dataframeInputs['Name'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i]))

            with self._out2:
                print("Algorithm file created.")
            algo.close()



    def _createXML(self):

        self._dataframeInputs = self._inouttab.get_changed_df()

        try:
            f = open("{}/unit.{}.xml".format(self._datas['Path'], self._datas['Model name']), 'w')

        except IOError as ioerr:
            with self._out2:
                print('File unit.{}.xml could not be opened. {}'.format(self._datas['Model name'], ioerr))

        else:

            with self._out:
                display(wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> XML writing</b>'.format(self._datas['Model name'])))

            split = re.split(r'\\', self._datas['Path'])
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Model PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelUnit.dtd">\n')
            f.write('<ModelUnit modelid="{}.{}.{}" name="{}" timestep="1" version="1.0">'.format(split[-4],split[-2],self._datas['Model name'],self._datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{} Model</Title>'.format(self._datas['Model name'])+
                '\n\t\t<Authors>{}</Authors>'.format(self._datas['Author'])+
                '\n\t\t<Institution>{}</Institution>'.format(self._datas['Institution'])+
                '\n\t\t<Reference>{}</Reference>'.format(self._datas['Reference'])+
                '\n\t\t<Abstract>{}</Abstract>'.format(self._datas['Abstract'])+'\n\t</Description>')
            

            f.write('\n\n\t<Inputs>')
            for i in range(0,len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Type'][i] == 'input', self._dataframeInputs['Type'][i] == 'input & output']):

                    if self._dataframeInputs['InputType'][i] == 'variable':
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                
                    else:
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                
            f.write('\n\t</Inputs>\n')


            f.write('\n\t<Outputs>')


            for i in range(0,len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Type'][i] == 'output', self._dataframeInputs['Type'][i] == 'input & output']):

                    if(self._dataframeInputs['InputType'][i]=='variable'):
                        f.write('\n\t\t<Output name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                
                    else:
                        f.write('\n\t\t<Output name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                    
            f.write('\n\t</Outputs>')

            self._createAlgo()           

            f.write('\n\n\t<Algorithm language="Cyml" platform="" filename="algo/pyx/{}.pyx" />'.format(self._datas['Model name']))
            

            f.write('\n\n\t<Parametersets>')

            for param in self._paramsets:

                f.write('\n\n\t\t<Parameterset name="{}" description="{}" >'.format(param.name, param.description))
                    
                for k,v in param.dictparam.items():
                        
                    f.write('\n\t\t\t<Param name="{}">{}</Param>'.format(k, v))
                    
                f.write('\n\t\t</Parameterset>')
                
            f.write('\n\t</Parametersets>')


            f.write('\n\n\t<Testsets>')
                
            for i in self._testsets:

                f.write('\n\t\t<Testset name="{}" parameterset="{}" description="{}" >'.format(i.name, i.paramset, i.description))
                    
                for test in i.listetest:

                    f.write('\n\t\t\t<Test name="{}" >'.format(test.name))
                        
                    for k,v in test.valuesIn.items():

                        f.write('\n\t\t\t\t<InputValue name="{}">{}</InputValue>'.format(k,v))
                        
                    for k,v in test.valuesOut.items():

                        f.write('\n\t\t\t\t\t<OutputValue name="{}">{}</OutputValue>'.format(k,v))
                    
                    f.write('\n\t\t\t</Test>')
                    
                f.write('\n\t\t</Testset>')
                
            f.write('\n\t</Testsets>')



            f.write("\n\n</ModelUnit>")

            with self._out2:
                print('File successfully updated.')            
            f.close()



    def _display_isParamset(self):

        tmp1 = wg.Button(value=False,description='New ParametersSet',disabled=False,button_style='primary')
        tmp2 = wg.Button(value=False,description='Go to TestsSet',disabled=False,button_style='primary')
        tmp3 = wg.Button(value=False,description='End',disabled=False,button_style='success')

        self._out.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> ParametersSet</b>'.format(self._datas['Model name'])), tmp1, tmp2, wg.HBox([tmp3, self._cancel])]))


        def event1(b):
            self._displayParam()

        def event2(b):
            self._displayTestsSet()

        def event3(b):
            self._out.clear_output()
            self._out2.clear_output()
            self._createXML()

        tmp1.on_click(event1)
        tmp2.on_click(event2)
        tmp3.on_click(event3)
        self._cancel.on_click(self._eventCancel)



    def _display_isTestset(self):

        tmp1 = wg.Button(value=False,description='New TestSet',disabled=False,button_style='primary')
        tmp2 = wg.Button(value=False,description='New Test',disabled=False,button_style='primary')
        tmp3 = wg.Button(value=False,description='End',disabled=False,button_style='success')

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> TestsSet</b>'.format(self._datas['Model name'])), tmp1, tmp2, wg.HBox([tmp3, self._cancel])]))

        def event1(b):
            self._displayTestsSet()

        def event2(b):
            self._createTest()

        def event3(b):

            self._out.clear_output()
            self._out2.clear_output()
            self._createXML()


        tmp1.on_click(event1)
        tmp2.on_click(event2)
        tmp3.on_click(event3)
        self._cancel.on_click(self._eventCancel)



    def _displayTestsSet(self):

        self._out.clear_output()
        self._out2.clear_output()

        tmp = ['']
        for param in self._paramsets:
            tmp.append(param.name)
        
        self._testsetselecter.options = tmp

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> TestsSet</b>'.format(self._datas['Model name'])), self._testsettab]))

        self._testsetbutton.on_click(self._eventTest)
        self._cancel.on_click(self._eventCancel)



    def _getParams(self):
        

        self._paramsets.append(paramSet(self._parametersetname.value, self._parametersetdescription.value))
        self._parametersetdescription.value = ''
        self._parametersetname.value = ''

        self._dataframeInputs = self._inouttab.get_changed_df()

        listeName = []
        listeValue = []
        listeMin = []
        listeMax = []
        listeDataType = []
        listeDefault = []

        for i in range(0, len(self._dataframeInputs['InputType'])):

            if self._dataframeInputs['InputType'][i] == 'parameter':

                listeName.append(format(self._dataframeInputs['Name'][i]))
                listeValue.append('')
                listeDefault.append(format(self._dataframeInputs['Default'][i]))
                listeMin.append(format(self._dataframeInputs['Min'][i]))
                listeMax.append(format(self._dataframeInputs['Max'][i]))
                listeDataType.append(format(self._dataframeInputs['DataType'][i]))

        
        dataframe = pandas.DataFrame(data={
            'Parameter name': listeName,
            'DataType': listeDataType,
            'Set value': listeValue,
            'Default': listeDefault,
            'Min': listeMin,
            'Max': listeMax
        })


        qgridtab = qgrid.show_grid(dataframe, show_toolbar=False)
        apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')



        def eventApply(b):

            dataframe = qgridtab.get_changed_df()

            self._out2.clear_output()

            if not '' in dataframe['Set value']:
            
                for i in range(0, len(dataframe['Min'])):
                    self._paramsets[-1].dictparam[dataframe['Parameter name'][i]] = dataframe['Set value'][i]

                with self._out:
                    self._display_isParamset()
            
            else:
                with self._out2:
                    print('Missing value(s) for parameter.')



        self._out.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> ParametersSet</b>'.format(self._datas['Model name'])), qgridtab, wg.HBox([apply, self._cancel])]))

        apply.on_click(eventApply)
        self._cancel.on_click(self._eventCancel)


    
    
    def _eventParam(self, b):

        self._out2.clear_output()

        if self._parametersetdescription.value and self._parametersetname.value:
            self._getParams()
        
        else:
            with self._out2:
                print('Missing argument(s):')
                if not self._parametersetname.value:
                    print('\t- name')
                if not self._parametersetdescription.value:
                    print('\t- description')



    def _displayParam(self):

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> ParametersSet</b>'.format(self._datas['Model name'])), self._parametersset, wg.HBox([self._apply2, self._cancel])]))

        
        self._apply2.on_click(self._eventParam)
        self._cancel.on_click(self._eventCancel)




    def _eventApplyInout(self, b):

        self._out2.clear_output()

        def _checkQgrid():

            self._dataframeInputs = self._inouttab.get_changed_df()

            for i in range(0, len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Category'][i]=='', self._dataframeInputs['Type'][i]=='', self._dataframeInputs['Name'][i]=='', self._dataframeInputs['Description'][i]=='', self._dataframeInputs['DataType'][i]=='',self._dataframeInputs['InputType'][i]=='', self._dataframeInputs['Unit'][i]=='']):
                    return False

            return True


        if _checkQgrid():

            liste = []
            for i in range(0,len(self._dataframeInputs['Name'])):
                liste.append(self._dataframeInputs['InputType'][i])

            if 'parameter' in liste:
                self._displayParam()
            
            elif 'variable' in liste:      
                self._displayTestsSet()
            
            else:
                raise Exception('No input nor output !')

        else:
            with self._out2:
                print('Missing argument(s), these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Unit')
            


    def _eventCancel(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        os.remove("{}/unit.{}.xml".format(self._datas["Path"], self._datas['Model name']))

        del self
        return



    def _displayTest(self):

        self._out.clear_output()
        self._out2.clear_output()

        listeName = []
        listeValue = []
        listeDefault = []
        listeMin = []
        listeMax = []
        listeDataType = []
        listeType = []

        for i in range(0, len(self._dataframeInputs['InputType'])):

            if self._dataframeInputs['InputType'][i] == 'variable':

                if any([self._dataframeInputs['Type'][i] == 'input', self._dataframeInputs['Type'][i] == 'input & output']):

                    listeName.append(format(self._dataframeInputs['Name'][i]))
                    listeValue.append('')
                    listeDefault.append(format(self._dataframeInputs['Default'][i]))
                    listeMin.append(format(self._dataframeInputs['Min'][i]))
                    listeMax.append(format(self._dataframeInputs['Max'][i]))
                    listeDataType.append(format(self._dataframeInputs['DataType'][i]))
                    listeType.append(format('input'))


                if any([self._dataframeInputs['Type'][i] == 'output', self._dataframeInputs['Type'][i] == 'input & output']):

                    listeName.append(format(self._dataframeInputs['Name'][i]))
                    listeValue.append('')
                    listeDefault.append(format(self._dataframeInputs['Default'][i]))
                    listeMin.append(format(self._dataframeInputs['Min'][i]))
                    listeMax.append(format(self._dataframeInputs['Max'][i]))
                    listeDataType.append(format(self._dataframeInputs['DataType'][i]))
                    listeType.append(format('output'))


        
        dataframe = pandas.DataFrame(data={
            'Type': listeType,
            'Variable name': listeName,
            'DataType': listeDataType,
            'Set value': listeValue,
            'Default': listeDefault,
            'Min': listeMin,
            'Max': listeMax
        })

        dataframe.sort_values(by='Type', ascending=True)


        testqgridtab = qgrid.show_grid(dataframe, show_toolbar=False)
        apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> TestsSet</b>'.format(self._datas['Model name'])), testqgridtab, wg.HBox([apply, self._cancel])]))


        def eventApply(b):

            dataframe = testqgridtab.get_changed_df()

            self._out2.clear_output()

            if not any([dataframe['Set value'][i] == '' for i in range(0,len(dataframe['Set value']))]):
            
                for i in range(0, len(dataframe['Type'])):

                    if dataframe['Type'][i] == 'input':
                        self._testsets[-1].listetest[-1].valuesIn[dataframe['Variable name'][i]] = dataframe['Set value'][i]
                    
                    else:
                        self._testsets[-1].listetest[-1].valuesOut[dataframe['Variable name'][i]] = dataframe['Set value'][i]

                self._out.clear_output()
                
                with self._out:
                    self._display_isTestset()
            
            else:
                with self._out2:
                    print('Missing value(s) for variable.')

        def cell_edited(event, widget):

            testqgridtab.off('cell_edited', cell_edited)
            #dataframe = testqgridtab.get_changed_df()

            if not event['column'] == 'Set value':
                testqgridtab.edit_cell(event['index'],event['column'],event['old'])

            else:
                pass
                #HERE TO DO THE EVENT MANAGING FOR A GOOD SET VALUE DEPENDING ON DATATYPE AND MIN/MAX
                
            testqgridtab.on('cell_edited', cell_edited)


        apply.on_click(eventApply)
        self._cancel.on_click(self._eventCancel)
        testqgridtab.on('cell_edited', cell_edited)




    def _createTest(self):

        text = wg.Textarea(value='',description='Test name',disabled=False)
        button = wg.Button(value=False,description='Apply',disabled=False,button_style='success')

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> TestsSet</b>'.format(self._datas['Model name'])), text, wg.HBox([button, self._cancel])]))
            
        def _eventTest(b):

            self._out2.clear_output()
                
            if text.value:
                
                self._testsets[-1].listetest.append(test(text.value))      
                self._displayTest()

            else:
                with self._out2:
                    print('Missing test name.')


        button.on_click(_eventTest)
        self._cancel.on_click(self._eventCancel)


        
    def _eventTest(self, b):
        
        self._out2.clear_output()

        liste = []
        for i in range(0,len(self._dataframeInputs['Name'])):
            liste.append(self._dataframeInputs['InputType'][i])

        if self._testsetname.value and self._testsetdescription.value and any([self._testsetselecter.value, not self._testsetselecter.value and not 'parameter' in liste]):

            self._testsets.append(testSet(self._testsetname.value,self._testsetdescription.value,self._testsetselecter.value))
            self._testsetname.value = ''
            self._testsetdescription.value = ''

            self._createTest()

            
        else:
            with self._out2:
                print('Missing argument(s):')
                if not self._testsetname.value:
                    print('\t- name')
                if not self._testsetdescription.value:
                    print('\t- description')
                if not self._testsetselecter.value:
                    print('\t- parametersset')


    
    def _cell_edited(self, event, widget):

        self._out2.clear_output()
        self._inouttab.off('cell_edited', self._cell_edited)


        #UPDATE INPUTTYPE
        if event['column'] == 'InputType':

            if not event['new'] == event['old']:
                self._inouttab.edit_cell(event['index'], 'Category', '')

        
        #UPDATE CATEGORY
        if event['column'] == 'Category':

            self._dataframeInputs = self._inouttab.get_changed_df()

            if self._dataframeInputs['InputType'][event['index']] == 'variable':

                if event['new'] not in ['','state','rate','auxiliary']:
                    self._inouttab.edit_cell(event['index'], 'Category', event['old'])

                    with self._out2:
                        print("Variable category must be among the list ['state','rate','auxiliary'].")
            
            elif self._dataframeInputs['InputType'][event['index']] == 'parameter':

                if event['new'] not in ['','constant','species','genotypic','soil','private']:
                    self._inouttab.edit_cell(event['index'], 'Category', event['old'])

                    with self._out2:
                        print("Parameter category must be among the list ['constant','species','genotypic','soil','private'].")

            else:
                self._inouttab.edit_cell(event['index'], 'Category', '')
                
                with self._out2:
                    print('You must assign an input type before giving a category.')
        

        #UPDATE DATATYPE
        elif event['column'] == 'DataType' and not event['new'] == event['old']:

            self._inouttab.edit_cell(event['index'], 'Min', '')
            self._inouttab.edit_cell(event['index'], 'Max', '')

            if event['new'] in ['STRING','DATE','']:
                self._inouttab.edit_cell(event['index'], 'Default', '')

            if any([event['new'] == 'STRINGLIST', event['new'] == 'DATELIST']):
                self._inouttab.edit_cell(event['index'], 'Default', '[]')

            if any([event['new'] == 'STRINGARRAY', event['new'] == 'DATEARRAY']):
                self._inouttab.edit_cell(event['index'], 'Default', '[[]]')

            if event['new'] == 'DOUBLE':
                self._inouttab.edit_cell(event['index'], 'Default', '0.0')
            
            if event['new'] == 'DOUBLELIST':
                self._inouttab.edit_cell(event['index'], 'Default', '[0.0]')
            
            if event['new'] == 'DOUBLEARRAY':
                self._inouttab.edit_cell(event['index'], 'Default', '[[0.0]]')

            if event['new'] == 'INT':
                self._inouttab.edit_cell(event['index'], 'Default', '0')
            
            if event['new'] == 'INTLIST':
                self._inouttab.edit_cell(event['index'], 'Default', '[0]')
            
            if event['new'] == 'INTARRAY':
                self._inouttab.edit_cell(event['index'], 'Default', '[[0]]')

            if event['new'] == 'BOOLEAN':
                self._inouttab.edit_cell(event['index'], 'Default', 'False')
        

        #UPDATE DEFAULT
        elif event['column'] == 'Default' and not event['new'] == event['old']:

            self._dataframeInputs = self._inouttab.get_changed_df()

            if self._dataframeInputs['DataType'][event['index']] in ['DATELIST','DATEARRAY','']:                
                self._inouttab.edit_cell(event['index'], 'Default', event['old'])
            
            if self._dataframeInputs['DataType'][event['index']] == 'DATE':
                if not re.search(r'^(?:(?:31(\/|-)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$', event['new']):
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print('Bad DATE format : use dd/mm/yyyy or dd-mm-yyyy.')
            
            if self._dataframeInputs['DataType'][event['index']] == 'BOOLEAN':
                if not any([self._dataframeInputs['Default'][event['index']] == 'True', self._dataframeInputs['Default'][event['index']] == 'False']):
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print('Bad BOOLEAN format : use True|False.')

            
            if self._dataframeInputs['DataType'][event['index']] == 'INT':

                search = re.search(r'^-? ?\d+\.', event['new'])
                if search:
                    if any([self._dataframeInputs['Min'][event['index']] and (float(self._dataframeInputs['Min'][event['index']]) > float(event['new'])),
                            self._dataframeInputs['Max'][event['index']] and (float(self._dataframeInputs['Max'][event['index']]) < float(event['new']))
                            ]):
                        self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                    else:                            
                        self._inouttab.edit_cell(event['index'], 'Default', event['new'][:search.end()-1])

                elif re.search(r'^-? ?\d+$', event['new']):
                    if any([self._dataframeInputs['Min'][event['index']] and (float(self._dataframeInputs['Min'][event['index']]) > float(event['new'])),
                            self._dataframeInputs['Max'][event['index']] and (float(self._dataframeInputs['Max'][event['index']]) < float(event['new']))
                            ]):
                        self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                else:

                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad INT format : use -?[0-9]+ .')

            
            if self._dataframeInputs['DataType'][event['index']] == 'DOUBLE':

                if re.search(r'^-? ?\d+\.$', event['new']):
                    if any([self._dataframeInputs['Min'][event['index']] and (float(self._dataframeInputs['Min'][event['index']]) > float(event['new'])),
                            self._dataframeInputs['Max'][event['index']] and (float(self._dataframeInputs['Max'][event['index']]) < float(event['new']))
                            ]):
                        self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                    else:
                        self._inouttab.edit_cell(event['index'], 'Default', event['new']+'0')
                    
                elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                    if any([self._dataframeInputs['Min'][event['index']] and (float(self._dataframeInputs['Min'][event['index']]) > float(event['new'])),
                            self._dataframeInputs['Max'][event['index']] and (float(self._dataframeInputs['Max'][event['index']]) < float(event['new']))
                            ]):
                        self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                elif re.search(r'^-? ?\d+$', event['new']):
                    if any([self._dataframeInputs['Min'][event['index']] and (float(self._dataframeInputs['Min'][event['index']]) > float(event['new'])),
                            self._dataframeInputs['Max'][event['index']] and (float(self._dataframeInputs['Max'][event['index']]) < float(event['new']))
                            ]):
                        self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Default value must be in between Min and Max.')

                    else:
                        self._inouttab.edit_cell(event['index'], 'Default', event['new']+'.0')

                else:
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLE format : use -?[0-9]+.[0-9]* .')


            if self._dataframeInputs['DataType'][event['index']] == 'DOUBLELIST':

                if re.search(r'^(\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])$', event['new'].replace(' ','')):
                    self._inouttab.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))

                else:
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLELIST format : use [{DOUBLE},*] .','\n',r'{DOUBLE} = -?[0-9]+.[0-9]* .')


            if self._dataframeInputs['DataType'][event['index']] == 'INTLIST':
                if re.search(r'^(\[(?:-? ?\d+)(?:,-? ?\d+)*\])$', event['new'].replace(' ','')):
                    self._inouttab.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                
                else:
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad INTLIST format : use [{INT},*] .','\n',r'{INT} = -?[0-9]+ .')
            

            if self._dataframeInputs['DataType'][event['index']] == 'DOUBLEARRAY':

                if re.search(r'^\[(?:\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])?(?:,\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])*]$', event['new'].replace(' ','')):
                    self._inouttab.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                
                else:
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLEARRAY format : use [[{DOUBLE},*],*] .','\n',r'{DOUBLE} = -?[0-9]+.[0-9]* .')
            

            if self._dataframeInputs['DataType'][event['index']] == 'INTARRAY':

                if re.search(r'^\[(?:\[(?:-? ?\d+)?(?:,-? ?\d+)*\])?(?:,\[(?:-? ?\d+)?(?:,-? ?\d+)*\])*]$', event['new'].replace(' ','')):
                    self._inouttab.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))
                
                else:
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLEARRAY format : use [[{INT},*],*] .','\n',r'{INT} = -?[0-9]+ .')

            
            if self._dataframeInputs['DataType'][event['index']] == 'STRINGLIST':

                if not re.search(r"^\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\]$", event['new'].strip()):
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r"Bad STRINGLIST format : use ['',*] .")
                
                else:
                    tmp = event['new'].strip()[1:-1].split(',')
                    tmp = [x.strip() for x in tmp]
                    string = '['
                    for i in tmp:
                        string += i+','
                    self._inouttab.edit_cell(event['index'], 'Default', string[:-1]+']')


            if self._dataframeInputs['DataType'][event['index']] == 'STRINGARRAY':

                if not re.search(r"^\[ *(?:\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\])?(?: *, *\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\] *)* *\]$", event['new'].strip()):
                    self._inouttab.edit_cell(event['index'], 'Default', event['old'])

                    with self._out2:
                        print(r"Bad STRINGLIST format : use [['',*],*] .")
        
        
        #UPDATE MIN
        elif event['column'] == 'Min':

            self._dataframeInputs = self._inouttab.get_changed_df()

            if self._dataframeInputs['DataType'][event['index']] == 'INT':

                search = re.search(r'^-? ?\d+\.', event['new'])
                if search:
                    if self._dataframeInputs['Default'][event['index']] and (float(self._dataframeInputs['Default'][event['index']]) < float(event['new'][:search.end()-1])):
                        self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                    else:
                        self._inouttab.edit_cell(event['index'], 'Min', event['new'][:search.end()-1])


                elif re.search(r'^-? ?\d+$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (float(self._dataframeInputs['Default'][event['index']]) < float(event['new'])):
                        self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                else:

                    self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                    with self._out2:
                        print(r'Bad INT format : use -?[0-9]+ .')

            
            elif self._dataframeInputs['DataType'][event['index']] == 'DOUBLE':

                if re.search(r'^-? ?\d+\.$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (float(self._dataframeInputs['Default'][event['index']]) < float(event['new']+'0')):
                        self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                    self._inouttab.edit_cell(event['index'], 'Min', event['new']+'0')
                    
                elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (float(self._dataframeInputs['Default'][event['index']]) < float(event['new'])):
                        self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                elif re.search(r'^-? ?\d+$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (float(self._dataframeInputs['Default'][event['index']]) < float(event['new'])):
                        self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print('Minimum > Default !')

                    else:
                        self._inouttab.edit_cell(event['index'], 'Min', event['new']+'.0')

                else:
                    self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLE format : use -?[0-9]+.[0-9]* .')
                

            else:
                self._inouttab.edit_cell(event['index'], 'Min', event['old'])

                with self._out2:
                    print('This data type does not handle min nand max, or is not defined yet.')
        

        #UPDATE MAX
        elif event['column'] == 'Max':

            self._dataframeInputs = self._inouttab.get_changed_df()

            if self._dataframeInputs['DataType'][event['index']] == 'INT':

                search = re.search(r'^-? ?\d+\.', event['new'])
                if search:
                    if self._dataframeInputs['Default'][event['index']] and (self._dataframeInputs['Default'][event['index']] > event['new'][:search.end()-1]):
                        self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                    else:
                        self._inouttab.edit_cell(event['index'], 'Max', event['new'][:search.end()-1])


                elif re.search(r'^-? ?\d+$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (self._dataframeInputs['Default'][event['index']] > event['new']):
                        self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                else:

                    self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                    with self._out2:
                        print(r'Bad INT format : use -?[0-9]+ .')

            
            elif self._dataframeInputs['DataType'][event['index']] == 'DOUBLE':

                if re.search(r'^-? ?\d+\.$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (self._dataframeInputs['Default'][event['index']] > event['new']+'0'):
                        self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                    self._inouttab.edit_cell(event['index'], 'Max', event['new']+'0')
                    
                elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (self._dataframeInputs['Default'][event['index']] > event['new']):
                        self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                elif re.search(r'^-? ?\d+$', event['new']):
                    if self._dataframeInputs['Default'][event['index']] and (self._dataframeInputs['Default'][event['index']] > event['new']):
                        self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print('Maximum < Default !')

                    else:
                        self._inouttab.edit_cell(event['index'], 'Max', event['new']+'.0')

                else:
                    self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                    with self._out2:
                        print(r'Bad DOUBLE format : use -?[0-9]+.[0-9]* .')
                

            else:
                self._inouttab.edit_cell(event['index'], 'Max', event['old'])

                with self._out2:
                    print('This data type does not handle min nand max, or is not defined yet.')




        self._inouttab.on('cell_edited', self._cell_edited)




    def _row_added(self, event, widget):

        self._inouttab.off('cell_edited', self._cell_edited)

        self._inouttab.edit_cell(event['index'], 'Type', '')
        self._inouttab.edit_cell(event['index'], 'Name', '')
        self._inouttab.edit_cell(event['index'], 'Description', '')
        self._inouttab.edit_cell(event['index'], 'InputType', '')
        self._inouttab.edit_cell(event['index'], 'DataType', '')
        self._inouttab.edit_cell(event['index'], 'Category', '')
        self._inouttab.edit_cell(event['index'], 'Default', '')
        self._inouttab.edit_cell(event['index'], 'Min', '')
        self._inouttab.edit_cell(event['index'], 'Max', '')
        self._inouttab.edit_cell(event['index'], 'Unit', '')
        self._inouttab.edit_cell(event['index'], 'Uri', '')

        self._inouttab.on('cell_edited', self._cell_edited)



    def display(self, dic):

        self._datas = dic

        display(self._out)
        display(self._out2)

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> Inputs and Outputs</b>'.format(self._datas['Model name'])), self._inouttab, wg.HBox([self._apply, self._cancel])]))
        

        self._inouttab.on('cell_edited', self._cell_edited)
        self._inouttab.on('row_added', self._row_added)
        self._apply.on_click(self._eventApplyInout)
        self._cancel.on_click(self._eventCancel)