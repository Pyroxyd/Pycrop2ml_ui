import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.cpackage.CreationRepository import mkdirModel
from pycropml.pparse import model_parser
from pycropml.transpiler.generators import docGenerator



class paramSet():

    """
    Class for storing a parametersSet
    """

    def __init__(self, name, description):

        self.name = name
        self.description = description
        self.dictparam = dict()


class test():

    """
    Class for storing a test
    """

    def __init__(self, name):

        self.name = name
        self.valuesIn = dict()
        self.valuesOut = dict()


class testSet():

    """
    Class for storing a testSet
    """

    def __init__(self, name, description, paramset):

        self.name = name
        self.description = description
        self.paramset = paramset
        self.listetest = []



class createUnit():

    """
    Class providing a display of unit model creation menu for pycrop2ml's user interface.
    """


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
            'Len': [''],
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



    def _getDoc(self, f):

        """
        Returns the documentation of the current's model xml file
        """

        split = re.split(r'\\', self._datas['Path'])

        parse = ''
        for i in split[:-1]:
            parse += i + r'\\'

        parsing = model_parser(parse)
        index = None

        for j in range(0,len(parsing)):
            if parsing[j].name == self._datas['Model name']:
                index = j
                break

        if index is None:
            f.close()
            self._out.clear_output()
            self._out2.clear_output()

            raise Exception('Critical error : model not found.')
        
        return docGenerator.DocGenerator(parsing[index])



    def _createInit(self):
        
        """
        Creates the init file with the model description inside of it
        """

        try:
            init = open("{}\\algo\\pyx\\init.{}.pyx".format(self._datas['Path'], self._datas['Model name']), 'w')

        except IOError as ioerr:
            self._out.clear_output()
            self._out2.clear_output()
            raise Exception("Algorithm file init.{}.pyx could not be created. {}".format(self._datas['Model name'], ioerr))

        else:            
            doc = self._getDoc(init)

            init.write(doc.desc)
            init.write('\n{}'.format(doc.inputs_doc))
            init.write('\n{}'.format(doc.outputs_doc))

            init.close()

            with self._out2:
                print('Init file successfully updated.')



    def _createAlgo(self):

        """
        Creates the algorithm file with the model description inside of it
        """

        try:
            algo = open("{}\\algo\\pyx\\{}.pyx".format(self._datas['Path'], self._datas['Model name']), 'w')

        except IOError as ioerr:
            self._out.clear_output()
            self._out2.clear_output()
            raise Exception("Algorithm file {}.pyx could not be created. {}".format(self._datas['Model name'], ioerr))

        else:
            doc = self._getDoc(algo)

            algo.write(doc.desc)
            algo.write('\n{}'.format(doc.inputs_doc))
            algo.write('\n{}'.format(doc.outputs_doc))

            algo.close()

            with self._out2:
                print('Algorithm file successfully updated.')



    def _createXML(self):

        """
        Saves all gathered datas in an xml format
        """

        self._dataframeInputs = self._inouttab.get_changed_df()
        self._dataframeInputs.reset_index(inplace=True)

        try:
            f = open("{}/unit.{}.xml".format(self._datas['Path'], self._datas['Model name']), 'w')

        except IOError as ioerr:
            raise Exception('File unit.{}.xml could not be opened. {}'.format(self._datas['Model name'], ioerr))

        else:

            with self._out:
                display(wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> XML writing</b>'.format(self._datas['Model name'])))

            split = re.split(r'\\', self._datas['Path'])
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Model PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelUnit.dtd">\n')
            f.write('<ModelUnit modelid="{}.{}.{}" name="{}" timestep="1" version="1.0">'.format(split[-4],split[-2],self._datas['Model name'],self._datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{} Model</Title>'.format(self._datas['Model name'])+
                '\n\t\t<Authors>{}</Authors>'.format(self._datas['Authors'])+
                '\n\t\t<Institution>{}</Institution>'.format(self._datas['Institution'])+
                '\n\t\t<Reference>{}</Reference>'.format(self._datas['Reference'])+
                '\n\t\t<Abstract>{}</Abstract>'.format(self._datas['Abstract'])+'\n\t</Description>')
            
            f.write('\n\n\t<Inputs>')
            for i in range(0,len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Type'][i] == 'input', self._dataframeInputs['Type'][i] == 'input & output']):

                    if self._dataframeInputs['InputType'][i] == 'variable':
                        if self._dataframeInputs['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" len="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Len'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                        else:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                
                    else:
                        if self._dataframeInputs['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" len="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Len'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                        else:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['InputType'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Default'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                
            f.write('\n\t</Inputs>\n')
            f.write('\n\t<Outputs>')

            for i in range(0,len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Type'][i] == 'output', self._dataframeInputs['Type'][i] == 'input & output']):

                    if self._dataframeInputs['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                        f.write('\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" len="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Len'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                    else:
                        f.write('\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._dataframeInputs['Name'][i],self._dataframeInputs['Description'][i],self._dataframeInputs['Category'][i],self._dataframeInputs['DataType'][i],self._dataframeInputs['Min'][i],self._dataframeInputs['Max'][i],self._dataframeInputs['Unit'][i],self._dataframeInputs['Uri'][i]))
                                   
            f.write('\n\t</Outputs>')
            f.write('\n\n\t<Function name="" language="Cyml" filename="" type="" description="" />')
            f.write('\n\n\t<Algorithm language="Cyml" platform="" filename="algo/pyx/{}.pyx" />'.format(self._datas['Model name']))
            f.write('\n\n\t<Initialization name="init.{0}" language="Cyml" filename="algo/pyx/init.{0}.pyx" />'.format(self._datas['Model name']))
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
                print('Xml file successfully updated.')

            f.close()

            self._createAlgo()
            self._createInit()       



    def _display_isParamset(self):

        """
        Displays a menu to know wheter to create a new parametersSet or to display testsSet creation
        """

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

        """
        Displays a menu to know wheter to create a new testsSet/test or to end the creation and write the xml format
        """

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

        """
        Displays testsSet creation menu
        """

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

        """
        Collects the parameters' list
        """
        

        self._paramsets.append(paramSet(self._parametersetname.value, self._parametersetdescription.value))
        self._parametersetdescription.value = ''
        self._parametersetname.value = ''

        self._dataframeInputs = self._inouttab.get_changed_df()
        self._dataframeInputs.reset_index(inplace=True)

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
            dataframe.reset_index(inplace=True)

            self._out2.clear_output()

            if not any([dataframe['Set value'][i] == '' for i in range(0,len(dataframe['Set value']))]):
            
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

        qgridtab.on('cell_edited', self._cell_edited_testandparam)
        apply.on_click(eventApply)
        self._cancel.on_click(self._eventCancel)


    
    def _eventParam(self, b):

        """
        Handles apply2 button on_click event
        """

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

        """
        Displays the parametersSet creation menu
        """

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> ParametersSet</b>'.format(self._datas['Model name'])), self._parametersset, wg.HBox([self._apply2, self._cancel])]))

        
        self._apply2.on_click(self._eventParam)
        self._cancel.on_click(self._eventCancel)



    def _eventApplyInout(self, b):

        """
        Handles apply button on_click event
        """

        self._out2.clear_output()

        def _checkQgrid():

            """
            Checks wheter the whole required data set is verified in the dataframe
            """

            self._dataframeInputs = self._inouttab.get_changed_df()
            self._dataframeInputs.reset_index(inplace=True)

            for i in range(0, len(self._dataframeInputs['Name'])):

                if any([self._dataframeInputs['Category'][i]=='',
                        self._dataframeInputs['Type'][i]=='',
                        self._dataframeInputs['Name'][i]=='',
                        self._dataframeInputs['Description'][i]=='',
                        self._dataframeInputs['DataType'][i]=='',
                        self._dataframeInputs['InputType'][i]=='',
                        self._dataframeInputs['Unit'][i]=='',
                        (self._dataframeInputs['DataType'][i] in ['STRINGARRAY','DATEARRAY','INTARRAY','DOUBLEARRAY'] and self._dataframeInputs['Len'][i] == '')]):
                    return False

            return True


        if _checkQgrid():

            liste = [i for i in self._dataframeInputs['InputType']]

            if 'parameter' in liste:
                self._displayParam()
            
            elif 'variable' in liste:      
                self._displayTestsSet()
            
            else:
                raise Exception('No input nor output !')

        else:
            with self._out2:
                print('Missing argument(s), these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Len (for array)\n\t- Unit')
            


    def _eventCancel(self, b):

        """
        Handles cancel button on_click event
        """

        self._out.clear_output()
        self._out2.clear_output()

        os.remove("{}/unit.{}.xml".format(self._datas["Path"], self._datas['Model name']))

        return



    def _displayTest(self):

        """
        Displays a qgrid containing every variable in the model having a test value to input
        """

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
            'Type': pandas.Categorical(listeType, categories=['input','output'], ordered=True),
            'Variable name': listeName,
            'DataType': listeDataType,
            'Set value': listeValue,
            'Default': listeDefault,
            'Min': listeMin,
            'Max': listeMax
        })

        dataframe.sort_values(by='Type',ascending=True,inplace=True)
        dataframe.reset_index(inplace=True)


        testqgridtab = qgrid.show_grid(dataframe, show_toolbar=False)
        apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> TestsSet</b>'.format(self._datas['Model name'])), testqgridtab, wg.HBox([apply, self._cancel])]))


        def eventApply(b):

            dataframe = testqgridtab.get_changed_df()
            dataframe.reset_index(inplace=True)

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


        apply.on_click(eventApply)
        self._cancel.on_click(self._eventCancel)
        testqgridtab.on('cell_edited', self._cell_edited_testandparam)



    def _createTest(self):

        """
        Displays the test creation menu
        """

        text = wg.Textarea(value='',description='Test name',disabled=False)
        button = wg.Button(value=False,description='Apply',disabled=False,button_style='success')

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> TestsSet</b>'.format(self._datas['Model name'])), text, wg.HBox([button, self._cancel])]))
            
        
        def _eventTest(b):

            """
            Handles apply:test button on_click event
            """

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

        liste = [i for i in self._dataframeInputs['InputType']]

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


    
    def _cell_edited_testandparam(self, event, widget):

        """
        Handles every event occuring when a cell is edited in the qgrid widget for parametersSet and testsSet
        """

        self._out2.clear_output()
        widget.off('cell_edited', self._cell_edited_testandparam)

        df = pandas.DataFrame(widget.get_changed_df())

        if event['column'] == 'Set value':

            if df['DataType'][event['index']] == 'DATE':
                    if not re.search(r'^(?:(?:31\/(?:0?[13578]|1[02]))\/|(?:(?:29|30)\/(?:0?[13-9]|1[0-2])\/))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29\/0?2\/(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])\/(?:(?:0?[1-9])|(?:1[0-2]))\/(?:(?:1[6-9]|[2-9]\d)?\d{2})$', event['new']):
                        widget.edit_cell(event['index'], 'Set value', event['old'])

                        with self._out2:
                            print('Error : bad DATE format -> use dd/mm/yyyy.')
                

            elif df['DataType'][event['index']] in ['DATELIST','DATEARRAY']:

                if re.search(r'^\[(?:(?:[0-2]\d|3[0-1])\/(?:0?[1-9]|1[0-2])\/\d{4})?(?:,(?:(?:[0-2]\d|3[0-1])\/(?:0?[1-9]|1[0-2])\/\d{4}))*\]$', event['new'].replace(' ','')):
                    widget.edit_cell(event['index'], 'Set value', event['new'].replace(' ',''))
                
                else:
                    widget.edit_cell(event['index'], 'Set value', event['old'])

                    with self._out2:
                        print('Error : bad {}'.format(df['DataType'][event['index']]),r'format -> use [{DATE},*] .','\n',r'{DATE} = dd/mm/yyyy.')
                




            elif df['DataType'][event['index']] == 'BOOLEAN':
                if not any([df['Set value'][event['index']] == 'True',
                            df['Set value'][event['index']] == 'False']):
                    widget.edit_cell(event['index'], 'Set value', event['old'])

                    with self._out2:
                        print('Error : bad BOOLEAN format -> use True|False.')

            
            elif df['DataType'][event['index']] == 'INT':
                if re.search(r'^-? ?\d+$', event['new']):
                    if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                            df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Set value', event['old'])

                        with self._out2:
                            print('Error : Set value value must be in between Min and Max.')

                else:
                    widget.edit_cell(event['index'], 'Set value', event['old'])

                    with self._out2:
                        print(r'Error : bad INT format -> use -?[0-9]+ .')

            
            elif df['DataType'][event['index']] == 'DOUBLE':

                if re.search(r'^-? ?\d+\.$', event['new']):
                    if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                            df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Set value', event['old'])

                        with self._out2:
                            print('Error : Set value value must be in between Min and Max.')

                    else:
                        widget.edit_cell(event['index'], 'Set value', event['new']+'0')
                    
                elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                    if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                            df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                            ]):
                        widget.edit_cell(event['index'], 'Set value', event['old'])

                        with self._out2:
                            print('Error : Set value value must be in between Min and Max.')

                else:
                    widget.edit_cell(event['index'], 'Set value', event['old'])

                    with self._out2:
                        print(r'Error : bad DOUBLE format -> use -?[0-9]+.[0-9]* .')


            elif df['DataType'][event['index']] in ['DOUBLELIST','DOUBLEARRAY']:

                if re.search(r'^(\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])$', event['new'].replace(' ','')):
                    widget.edit_cell(event['index'], 'Set value', event['new'].replace(' ',''))

                else:
                    widget.edit_cell(event['index'], 'Set value', event['old'])

                    with self._out2:
                        print('Error : bad {}'.format(df['DataType'][event['index']]),r'format -> use [{DOUBLE},*] .','\n',r'{DOUBLE} = -?[0-9]+.[0-9]* .')


            elif df['DataType'][event['index']] in ['INTLIST','INTARRAY']:
                if re.search(r'^(\[(?:-? ?\d+)(?:,-? ?\d+)*\])$', event['new'].replace(' ','')):
                    widget.edit_cell(event['index'], 'Set value', event['new'].replace(' ',''))
                
                else:
                    widget.edit_cell(event['index'], 'Set value', event['old'])

                    with self._out2:
                        print('Error : bad {}'.format(df['DataType'][event['index']]),' format -> use [{INT},*] .','\n',r'{INT} = -?[0-9]+ .')

            
            elif df['DataType'][event['index']] in ['STRINGLIST','STRINGARRAY']:

                if not re.search(r"^\[(?: *'[^\[\],']*' *)?(?:, *'[^\[\],']*' *)*\]$", event['new'].strip()):
                    widget.edit_cell(event['index'], 'Set value', event['old'])

                    with self._out2:
                        print('Error : bad {}'.format(df['DataType'][event['index']]),r" format -> use ['',*] .")
                
                else:
                    tmp = event['new'].strip()[1:-1].split(',')
                    tmp = [x.strip() for x in tmp]
                    string = '['
                    for i in tmp:
                        string += i+','
                    widget.edit_cell(event['index'], 'Set value', string[:-1]+']')

        else:
            widget.edit_cell(event['index'], event['column'], event['old'])

        widget.on('cell_edited', self._cell_edited_testandparam)



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

            if event['new'] == '':
                widget.edit_cell(event['index'], 'Category', '')
                widget.edit_cell(event['index'], 'InputType', '')

            elif event['new'] == 'output' or event['new'] == 'input & output':
                if df['InputType'][event['index']] == 'parameter':
                    widget.edit_cell(event['index'], 'Category', '')
                
                widget.edit_cell(event['index'], 'InputType', 'variable')
            
            if event['new'] == 'output':
                widget.edit_cell(event['index'], 'Default', '')


        #UPDATE INPUTTYPE
        elif event['column'] == 'InputType':

            if event['new'] == event['old']:
                pass

            else:
                if event['new'] == 'parameter':
                    if df['Type'][event['index']] == 'output' or df['Type'][event['index']] == 'input & output':
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

            if not df['Type'][event['index']] == 'output':

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

            if df['Type'][event['index']] == 'output':
                widget.edit_cell(event['index'], 'Default', '')

            else:      
                if df['DataType'][event['index']] == '':                
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

                    if re.search(r'^-? ?\d+$', event['new']):
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

                    if re.search(r'^-? ?\d+\.$', event['new']):
                        if any([df['Min'][event['index']] and (float(df['Min'][event['index']]) > float(event['new'])),
                                df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new']))
                                ]):
                            widget.edit_cell(event['index'], 'Default', event['old'])

                            with self._out2:
                                print('Error : default value must be in between Min and Max.')

                        else:
                            widget.edit_cell(event['index'], 'Default', event['new']+'0')
                        
                    elif re.search(r'^-? ?\d+\.\d+$', event['new']):
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

                    if re.search(r'^(\[(?:-? ?\d+\.\d*)?(?:,-? ?\d+\.\d*)*\])$', event['new'].replace(' ','')):
                        widget.edit_cell(event['index'], 'Default', event['new'].replace(' ',''))

                    else:
                        widget.edit_cell(event['index'], 'Default', event['old'])

                        with self._out2:
                            print('Error : bad {}'.format(df['DataType'][event['index']]),r' format -> use [{DOUBLE},*] .','\n',r'{DOUBLE} = -?[0-9]+.[0-9]* .')


                elif df['DataType'][event['index']] in ['INTLIST','INTARRAY']:
                    if re.search(r'^(\[(?:-? ?\d+)(?:,-? ?\d+)*\])$', event['new'].replace(' ','')):
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

            if df['Max'][event['index']] and (float(df['Max'][event['index']]) < float(event['new'])):
                widget.edit_cell(event['index'], 'Min', event['old'])

                with self._out2:
                    print('Error : Minimum > Maximum.')

            else:
                if df['DataType'][event['index']] == 'INT':

                    if re.search(r'^-? ?\d+$', event['new']):
                        if df['Default'][event['index']] and (int(df['Default'][event['index']]) < int(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Default.')

                    else:
                        widget.edit_cell(event['index'], 'Min', event['old'])

                        with self._out2:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')

                
                elif df['DataType'][event['index']] == 'DOUBLE':

                    if re.search(r'^-? ?\d+\.$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) < float(event['new']+'0')):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Default.')

                        widget.edit_cell(event['index'], 'Min', event['new']+'0')
                        
                    elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) < float(event['new'])):
                            widget.edit_cell(event['index'], 'Min', event['old'])

                            with self._out2:
                                print('Error : Minimum > Default.')

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

            if df['Min'][event['index']] and (float(event['new']) < float(df['Min'][event['index']])):
                widget.edit_cell(event['index'], 'Max', event['old'])

                with self._out2:
                    print('Error : Minimum > Maximum.')
            
            else:
                if df['DataType'][event['index']] == 'INT':

                    if re.search(r'^-? ?\d+$', event['new']):
                        if df['Default'][event['index']] and (int(df['Default'][event['index']]) > int(event['new'])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Maximum < Default.')

                    else:
                        widget.edit_cell(event['index'], 'Max', event['old'])

                        with self._out2:
                            print(r'Error : bad INT format -> use -?[0-9]+ .')

                
                elif df['DataType'][event['index']] == 'DOUBLE':

                    if re.search(r'^-? ?\d+\.$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) > float(event['new'])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Maximum < Default.')

                        widget.edit_cell(event['index'], 'Max', event['new']+'0')
                        
                    elif re.search(r'^-? ?\d+\.\d+$', event['new']):
                        if df['Default'][event['index']] and (float(df['Default'][event['index']]) > float(event['new'])):
                            widget.edit_cell(event['index'], 'Max', event['old'])

                            with self._out2:
                                print('Error : Maximum < Default.')

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

            if not df['DataType'][event['index']] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                widget.edit_cell(event['index'], 'Len', '')

                with self._out2:
                    print('Error : Len is exclusive to ARRAY type.')
            
            elif not df['DataType'][event['index']]:
                widget.edit_cell(event['index'], 'Len', event['old'])

                with self._out2:
                    print('Error : you must assign a DataType before gibing a lenght.')
            
            else:
                if not re.search(r'^ *-? ?\d+$', event['new']):
                    widget.edit_cell(event['index'], 'Len', event['old'])

                    with self._out2:
                        print(r'Error : bad INT format -> use -?[0-9]+ .')

        widget.on('cell_edited', self._cell_edited)



    def _row_added(self, event, widget):

        """
        Handles a row addition in the input & output qgrid widget
        """

        widget.off('cell_edited', self._cell_edited)

        for column in ['Type','Name','Description','InputType','DataType','Len','Category','Default','Min','Max','Unit','Uri']:
            widget.edit_cell(event['index'], column, '')

        widget.on('cell_edited', self._cell_edited)



    def displayMenu(self, dic):

        """
        Displays the unit model creation menu of pyrcop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.

        Parameters :\n
            - dic : dict(type:datas)\n
                datas = {
                        'Path': '',
                        'Model type': 'unit',
                        'Model name': '',
                        'Authors': '',
                        'Institution': '',
                        'Reference': '',
                        'Abstract': ''
                        }
        """

        listkeys = ['Path','Model type','Model name','Authors','Institution','Reference','Abstract']

        for i in dic.keys():

            if i not in listkeys:
                raise Exception("Could not display composition model creation menu : parameter dic from self.displayMenu(self, dic) must contain these keys ['Path','Model type','Model name','Authors','Institution','Reference','Abstract']")

            elif i == 'Model type' and not dic[i] == 'unit':
                raise Exception("Bad value error : Model type key's value must be unit.")

            else:
                listkeys.remove(i)


        self._datas = dic

        display(self._out)
        display(self._out2)

        with self._out:
            display(wg.VBox([wg.HTML(value='<b>Model creation : unit.{}.xml<br>-> Inputs and Outputs</b>'.format(self._datas['Model name'])), self._inouttab, wg.HBox([self._apply, self._cancel])]))
        

        self._inouttab.on('cell_edited', self._cell_edited)
        self._inouttab.on('row_added', self._row_added)
        self._apply.on_click(self._eventApplyInout)
        self._cancel.on_click(self._eventCancel)
