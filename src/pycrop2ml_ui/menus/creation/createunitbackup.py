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
        self.values = dict()


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
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()
        self.outparam = wg.Output()
        self.outtest = wg.Output()


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

        self.inputstab = qgrid.show_grid(self.dataframeInputs, show_toolbar=True)

        #PARAMETERSETS table
        self.parametersetname = wg.Textarea(value='',description='Name',disabled=False)
        self.parametersetdesc = wg.Textarea(value='',description='Description',disabled=False)
        self.parametersetbutton = wg.Button(value=False,description='Create',disabled=False,background_color='#decade')

        self.paramsets = []
        self.parameterssetstab = wg.VBox([self.parametersetname, self.parametersetdesc, self.parametersetbutton])
    
        #TESTSETS table
        self.testsetname = wg.Textarea(value='',description='Testset name',disabled=False)
        self.testsetdesc = wg.Textarea(value='',description='Description',disabled=False)
        self.testsetselecter = wg.Dropdown(options=[''],value='',description='Select a model:',disabled=True)
        self.testsetbutton = wg.Button(value=False,description='Create',disabled=False,background_color='#decade')
        
        self.testsets = []
        self.testsetstab = wg.VBox([self.testsetname, self.testsetdesc, self.testsetselecter, self.testsetbutton])


        #global table
        self.tab = wg.Tab([self.inputstab, self.outparam, self.outtest])
        self.tab.set_title(0, 'Inputs & Outputs')
        self.tab.set_title(1, 'ParametersSet')
        self.tab.set_title(2, 'TestsSet')
        self.tab.close

        self.displayer = wg.VBox([self.tab, wg.HBox([self.apply, self.cancel])])

        self.datas = dict()




    def createXML(self):

        self.dataframeInputs = self.inputstab.get_changed_df()

        try:
            f = open("{}/unit.{}.xml".format(self.datas['Path'], self.datas['Model name']), 'w')

        except IOError as ioerr:
            with self.out2:
                print('File unit.{}.xml could not be opened. {}'.format(self.datas['Model name'], ioerr))

        else:

            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Model PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelUnit.dtd">\n')
            f.write('<ModelUnit modelid="{}.{}" name="{}" timestep="1" version="1.0">'.format(os.path.basename(self.datas['Path']),self.datas['Model name'],self.datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{} Model</Title>'.format(self.datas['Model name'])+
                '\n\t\t<Authors>{}</Authors>'.format(self.datas['Author'])+
                '\n\t\t<Institution>{}</Institution>'.format(self.datas['Institution'])+
                '\n\t\t<Reference>{}</Reference>'.format(self.datas['Reference'])+
                '\n\t\t<Abstract>{}</Abstract>'.format(self.datas['Description'])+'\n\t</Description>')
            
            f.write('\n\n\t<Inputs>')
            for i in range(0,len(self.dataframeInputs['Name'])):

                if any([self.dataframeInputs['Type'][i] == 'input', self.dataframeInputs['Type'][i] == 'input & output']):

                    if(self.dataframeInputs['InputType'][i]=='variable'):
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['uri'][i]))
                
                    else:
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['uri'][i]))
                
            f.write('\n\t</Inputs>\n')


            f.write('\n\t<Outputs>')            
            for i in range(0,len(self.dataframeInputs['Name'])):

                if any([self.dataframeInputs['Type'][i] == 'output', self.dataframeInputs['Type'][i] == 'input & output']):

                    if(self.dataframeInputs['InputType'][i]=='variable'):
                        f.write('\n\t\t<Output name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['uri'][i]))
                
                    else:
                        f.write('\n\t\t<Output name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['uri'][i]))
                    
            f.write('\n\t</Outputs>')

             
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

            

            f.write('\n\n\t<Algorithm language="Cyml" platform="" filename="algo/pyx/{}.pyx" />'.format(self.datas['Model name']))
            
            f.write('\n\n\t<Parametersets>')

            for param in self.paramsets:

                f.write('\n\n\t\t<Parameterset name="{}" description="{}" >'.format(param.name, param.description))
                
                for k,v in param.dictparam.items():
                    
                    f.write('\n\t\t\t<Param name="{}">{}</Param>'.format(k, v))
                
                f.write('\n\t\t</Parameterset>')
            
            f.write('\n\t</Parametersets>')


            f.write("\n\n</ModelUnit>")

            with self.out2:
                print('File successfully updated.')            
            f.close()



    def getParams(self):

        self.paramsets.append(paramSet(self.parametersetname.value, self.parametersetdesc.value))
        self.parametersetdesc.value = ''
        self.parametersetname.value = ''

        self.outparam.clear_output()

        self.dataframeInputs = self.inputstab.get_changed_df()

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
        button = wg.Button(value=False,description='Save',disabled=False,background_color='#decade')


        def eventButton(b):

            dataframe = qgridtab.get_changed_df()

            for i in range(1, len(dataframe['Min'])):
                self.paramsets[-1].dictparam[dataframe['Parameter name'][i]] = dataframe['Set value'][i]

            self.outparam.clear_output()
            with self.outparam:
                display(self.parameterssetstab)
                self.parametersetbutton.on_click(self.eventParam)


        with self.outparam:
            display(wg.VBox([qgridtab, button]))

        button.on_click(eventButton)


        

    def eventApply(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:
          print("Updating datas to unit.{}.xml".format(self.datas['Model name']))

        self.createXML()



    def eventCancel(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        del self
        return

    
    def eventParam(self, b):

        self.out2.clear_output()

        if self.parametersetdesc.value and self.parametersetname.value:
            self.getParams()
        
        else:
            with self.out2:
                print('Missing argument(s):')
                if not self.parametersetname.value:
                    print('\n\t- name')
                if not self.parametersetdesc.value:
                    print('\n\t- description')


    def eventTest(self, b):
        
        self.out2.clear_output()

        if self.testsetname.value and self.testsetdesc.value:

            self.testsets.append(testSet(self.testsetname.value,self.testsetdesc.value,self.testsetselecter.value))
            self.testsetname.value = ''
            self.testsetdesc.value = ''
            self.testsetselecter.disabled = True

            text = wg.Textarea(value='',description='Test name',disabled=False)
            button = wg.Button(value=False,description='Create',disabled=False,button_style='success')

            self.outtest.clear_output()

            with self.outtest:
                display(wg.VBox([text, button]))
            


            def eventTest(b):
                
                if text.value:
                
                    self.testsets[-1].listetest.append(test(text.value))
                    # HERE TO DO





                    self.outtest.clear_output()

                    with self.outtest:
                        display("""QGRID + apply""")

                else:
                    with self.out2:
                        print('Missing test name.')


            button.on_click(eventTest)


        else:
            with self.out2:
                print('Missing argument(s):')
                if not self.testsetname.value:
                    print('\n\t- name')
                if not self.testsetdesc.value:
                    print('\n\t- dexcription')


    
    def on_value_change(self, change):

        tmp = []

        for param in self.paramsets:
            tmp.append(param.name)
        
        self.testsetselecter.options = tmp
        self.testsetselecter.disabled = False



    def display(self, dic):

        self.datas = dic

        display(self.out)
        display(self.out2)

        with self.out:
            display(self.displayer)

        with self.outparam:
            display(self.parameterssetstab)

        with self.outtest:
            display(self.testsetstab)
        

        self.apply.on_click(self.eventApply)
        self.cancel.on_click(self.eventCancel)
        self.parametersetbutton.on_click(self.eventParam)
        self.testsetbutton.on_click(self.eventTest)
        self.testsetname.observe(self.on_value_change, names='value')