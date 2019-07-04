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
        self.apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self.apply2 = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()



        #IN AND OUT table
        self.dataframeInputs = pandas.DataFrame(data={
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

        self.inouttab = qgrid.show_grid(self.dataframeInputs, show_toolbar=True)
        
        

        #PARAMETERSETS table
        self.parametersetname = wg.Textarea(value='',description='Name',disabled=False)
        self.parametersetdesc = wg.Textarea(value='',description='Description',disabled=False)

        self.paramsets = []
        self.parametersset = wg.VBox([self.parametersetname, self.parametersetdesc])
    
        #TESTSETS table
        self.testsetname = wg.Textarea(value='',description='Testset name',disabled=False)
        self.testsetdesc = wg.Textarea(value='',description='Description',disabled=False)
        self.testsetselecter = wg.Dropdown(options=[''],value='',description='Select a ParametersSet:',disabled=False)
        self.testsetbutton = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        
        self.testsets = []
        self.testsettab = wg.VBox([self.testsetname, self.testsetdesc, self.testsetselecter, wg.HBox([self.testsetbutton, self.cancel])])


        self.datas = dict()



    def createAlgo(self):

        try:
            algo = open("{}/algo/pyx/{}.pyx".format(self.datas['Path'], self.datas['Model name']), 'w')

        except IOError as ioerr:
            with self.out2:
                print("Algorithm file {}.pyx could not be created. {}".format(self.datas['Model name'], ioerr))

        else:

            algo.write('# inputs : ')
            for i in range(0,len(self.dataframeInputs['Name'])):

                if any([self.dataframeInputs['Type'][i] == 'input', self.dataframeInputs['Type'][i] == 'input & output']):
                    algo.write('{}({}):[default={},min={},max={}], '.format(self.dataframeInputs['Name'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i]))

            algo.write('\n# outputs : ')
            for i in range(0,len(self.dataframeInputs['Name'])):

                if any([self.dataframeInputs['Type'][i] == 'output', self.dataframeInputs['Type'][i] == 'input & output']):                    
                    algo.write('{}({}):[default={},min={},max={}], '.format(self.dataframeInputs['Name'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i]))

            with self.out2:
                print("Algorithm file created.")
            algo.close()



    def createXML(self):

        self.dataframeInputs = self.inouttab.get_changed_df()

        try:
            f = open("{}/unit.{}.xml".format(self.datas['Path'], self.datas['Model name']), 'w')

        except IOError as ioerr:
            with self.out2:
                print('File unit.{}.xml could not be opened. {}'.format(self.datas['Model name'], ioerr))

        else:

            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Model PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelUnit.dtd">\n')
            f.write('<ModelUnit modelid="{}.{}" name="{}" timestep="1" version="1.0">'.format(os.path.basename(os.path.basename(self.datas['Path'])),self.datas['Model name'],self.datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{} Model</Title>'.format(self.datas['Model name'])+
                '\n\t\t<Authors>{}</Authors>'.format(self.datas['Author'])+
                '\n\t\t<Institution>{}</Institution>'.format(self.datas['Institution'])+
                '\n\t\t<Reference>{}</Reference>'.format(self.datas['Reference'])+
                '\n\t\t<Abstract>{}</Abstract>'.format(self.datas['Description'])+'\n\t</Description>')
            

            f.write('\n\n\t<Inputs>')
            for i in range(0,len(self.dataframeInputs['Name'])):

                if any([self.dataframeInputs['Type'][i] == 'input', self.dataframeInputs['Type'][i] == 'input & output']):

                    if self.dataframeInputs['InputType'][i] == 'variable':
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['Uri'][i]))
                
                    else:
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['Uri'][i]))
                
            f.write('\n\t</Inputs>\n')


            f.write('\n\t<Outputs>')


            for i in range(0,len(self.dataframeInputs['Name'])):

                if any([self.dataframeInputs['Type'][i] == 'output', self.dataframeInputs['Type'][i] == 'input & output']):

                    if(self.dataframeInputs['InputType'][i]=='variable'):
                        f.write('\n\t\t<Output name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['Uri'][i]))
                
                    else:
                        f.write('\n\t\t<Output name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['Uri'][i]))
                    
            f.write('\n\t</Outputs>')

            self.createAlgo()           

            f.write('\n\n\t<Algorithm language="Cyml" platform="" filename="algo/pyx/{}.pyx" />'.format(self.datas['Model name']))
            

            f.write('\n\n\t<Parametersets>')

            for param in self.paramsets:

                f.write('\n\n\t\t<Parameterset name="{}" description="{}" >'.format(param.name, param.description))
                    
                for k,v in param.dictparam.items():
                        
                    f.write('\n\t\t\t<Param name="{}">{}</Param>'.format(k, v))
                    
                f.write('\n\t\t</Parameterset>')
                
            f.write('\n\t</Parametersets>')


            f.write('\n\n\t<Testsets>')
                
            for i in self.testsets:

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

            with self.out2:
                print('File successfully updated.')            
            f.close()


    def display_isParamset(self):

        tmp1 = wg.Button(value=False,description='New ParametersSet',disabled=False,background_color='blue')
        tmp2 = wg.Button(value=False,description='Go to TestsSet',disabled=False,background_color='blue')
        tmp3 = wg.Button(value=False,description='End',disabled=False,button_style='success')

        self.out.clear_output()

        with self.out:
            display(wg.VBox([tmp1, tmp2, tmp3]))


        def event1(b):
            self.displayParam()

        def event2(b):
            self.displayTestsSet()

        def event3(b):
            self.out.clear_output()
            self.out2.clear_output()
            self.createXML()

        tmp1.on_click(event1)
        tmp2.on_click(event2)
        tmp3.on_click(event3)



    def display_isTestset(self):

        tmp1 = wg.Button(value=False,description='New TestSet',disabled=False,background_color='#decade')
        tmp2 = wg.Button(value=False,description='New Test',disabled=False,background_color='#decade')
        tmp3 = wg.Button(value=False,description='End',disabled=False,button_style='success')

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:
            display(wg.VBox([tmp1, tmp2, tmp3]))

        def event1(b):
            self.displayTestsSet()

        def event2(b):
            self.createTest()

        def event3(b):

            self.out.clear_output()
            self.out2.clear_output()
            self.createXML()


        tmp1.on_click(event1)
        tmp2.on_click(event2)
        tmp3.on_click(event3)


    def displayTestsSet(self):

        self.out.clear_output()
        self.out2.clear_output()

        tmp = ['']
        for param in self.paramsets:
            tmp.append(param.name)
        
        self.testsetselecter.options = tmp

        with self.out:
            display(self.testsettab)

        self.testsetbutton.on_click(self.eventTest)
        self.cancel.on_click(self.eventCancel)



    def getParams(self):
        

        self.paramsets.append(paramSet(self.parametersetname.value, self.parametersetdesc.value))
        self.parametersetdesc.value = ''
        self.parametersetname.value = ''

        self.dataframeInputs = self.inouttab.get_changed_df()

        listeName = []
        listeValue = []
        listeMin = []
        listeMax = []
        listeDataType = []

        for i in range(0, len(self.dataframeInputs['InputType'])):

            if self.dataframeInputs['InputType'][i] == 'parameter':

                listeName.append(format(self.dataframeInputs['Name'][i]))
                listeValue.append('')
                listeMin.append(format(self.dataframeInputs['Min'][i]))
                listeMax.append(format(self.dataframeInputs['Max'][i]))
                listeDataType.append(format(self.dataframeInputs['DataType'][i]))

        
        dataframe = pandas.DataFrame(data={
            'Parameter name': listeName,
            'DataType': listeDataType,
            'Set value': listeValue,
            'Min': listeMin,
            'Max': listeMax
        })


        qgridtab = qgrid.show_grid(dataframe, show_toolbar=False)
        apply = wg.Button(value=False,description='Apply',disabled=False,background_color='#decade')


        def eventApply(b):

            dataframe = qgridtab.get_changed_df()

            self.out2.clear_output()

            if not '' in dataframe['Set value']:
            
                for i in range(0, len(dataframe['Min'])):
                    self.paramsets[-1].dictparam[dataframe['Parameter name'][i]] = dataframe['Set value'][i]

                with self.out:
                    self.display_isParamset()
            
            else:
                with self.out2:
                    print('Missing value(s) for parameter.')



        self.out.clear_output()

        with self.out:
            display(wg.VBox([qgridtab, apply]))

        apply.on_click(eventApply)


    
    
    def eventParam(self, b):

        self.out2.clear_output()

        if self.parametersetdesc.value and self.parametersetname.value:
            self.getParams()
        
        else:
            with self.out2:
                print('Missing argument(s):')
                if not self.parametersetname.value:
                    print('\t- name')
                if not self.parametersetdesc.value:
                    print('\t- description')



    def displayParam(self):

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:
            display(wg.VBox([self.parametersset, wg.HBox([self.apply2, self.cancel])]))

        
        self.apply2.on_click(self.eventParam)
        self.cancel.on_click(self.eventCancel)




    def eventApplyInout(self, b):

        self.out2.clear_output()

        def checkQgrid():

            self.dataframeInputs = self.inouttab.get_changed_df()

            for i in range(0, len(self.dataframeInputs['Name'])):

                if any([self.dataframeInputs['Category'][i]=='', self.dataframeInputs['Type'][i]=='', self.dataframeInputs['Name'][i]=='', self.dataframeInputs['Description'][i]=='', self.dataframeInputs['DataType'][i]=='',self.dataframeInputs['InputType'][i]=='', self.dataframeInputs['Unit'][i]=='']):
                    return False

            return True


        if checkQgrid():            
            self.displayParam()

        else:
            with self.out2:
                print('Missing argument(s), these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Unit')
            


    def eventCancel(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        print('Erasing datas ...')

        del self
        return

    
    def displayTest(self):

        self.out.clear_output()
        self.out2.clear_output()

        listeName = []
        listeValue = []
        listeMin = []
        listeMax = []
        listeDataType = []
        listeType = []

        for i in range(0, len(self.dataframeInputs['InputType'])):

            if self.dataframeInputs['InputType'][i] == 'variable':

                if any([self.dataframeInputs['Type'][i] == 'input', self.dataframeInputs['Type'][i] == 'input & output']):

                    listeName.append(format(self.dataframeInputs['Name'][i]))
                    listeValue.append('')
                    listeMin.append(format(self.dataframeInputs['Min'][i]))
                    listeMax.append(format(self.dataframeInputs['Max'][i]))
                    listeDataType.append(format(self.dataframeInputs['DataType'][i]))
                    listeType.append(format('input'))


                if any([self.dataframeInputs['Type'][i] == 'output', self.dataframeInputs['Type'][i] == 'input & output']):

                    listeName.append(format(self.dataframeInputs['Name'][i]))
                    listeValue.append('')
                    listeMin.append(format(self.dataframeInputs['Min'][i]))
                    listeMax.append(format(self.dataframeInputs['Max'][i]))
                    listeDataType.append(format(self.dataframeInputs['DataType'][i]))
                    listeType.append(format('output'))


        
        dataframe = pandas.DataFrame(data={
            'Type': listeType,
            'Variable name': listeName,
            'DataType': listeDataType,
            'Set value': listeValue,
            'Min': listeMin,
            'Max': listeMax
        })


        testqgridtab = qgrid.show_grid(dataframe, show_toolbar=False)
        apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')

        with self.out:
            display(wg.VBox([testqgridtab, apply]))


        def eventApply(b):

            dataframe = testqgridtab.get_changed_df()

            self.out2.clear_output()

            if not '' in dataframe['Set value']:
            
                for i in range(0, len(dataframe['Type'])):

                    if dataframe['Type'][i] == 'input':
                        self.testsets[-1].listetest[-1].valuesIn[dataframe['Variable name'][i]] = dataframe['Set value'][i]
                    
                    else:
                        self.testsets[-1].listetest[-1].valuesOut[dataframe['Variable name'][i]] = dataframe['Set value'][i]

                self.out.clear_output()
                
                with self.out:
                    self.display_isTestset()
            
            else:
                with self.out2:
                    print('Missing value(s) for variable.')

        apply.on_click(eventApply)




    def createTest(self):

        text = wg.Textarea(value='',description='Test name',disabled=False)
        button = wg.Button(value=False,description='Apply',disabled=False,button_style='success')

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:
            display(wg.VBox([text, button]))
            
        def eventTest(b):

            self.out2.clear_output()
                
            if text.value:
                
                self.testsets[-1].listetest.append(test(text.value))      
                self.displayTest()

            else:
                with self.out2:
                    print('Missing test name.')


        button.on_click(eventTest)



    def eventTest(self, b):
        
        self.out2.clear_output()

        if self.testsetname.value and self.testsetdesc.value and self.testsetselecter.value:

            self.testsets.append(testSet(self.testsetname.value,self.testsetdesc.value,self.testsetselecter.value))
            self.testsetname.value = ''
            self.testsetdesc.value = ''

            self.createTest()

            
        else:
            with self.out2:
                print('Missing argument(s):')
                if not self.testsetname.value:
                    print('\t- name')
                if not self.testsetdesc.value:
                    print('\t- description')
                if not self.testsetselecter.value:
                    print('\t- parametersset')



    def display(self, dic):

        self.datas = dic

        display(self.out)
        display(self.out2)

        with self.out:
            display(wg.VBox([self.inouttab, wg.HBox([self.apply, self.cancel])]))
        

        self.apply.on_click(self.eventApplyInout)
        self.cancel.on_click(self.eventCancel)