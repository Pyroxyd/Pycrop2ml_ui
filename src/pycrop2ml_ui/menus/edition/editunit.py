import os
import re
import ipywidgets as wg

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.menus.edition import editmenu
from pycropml.pparse import model_parser



class editUnit():


    def __init__(self):

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        self.datas = dict()

        self.apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        self.cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='danger')

        self.title = wg.Textarea(value='',description='Title',disabled=False)
        self.authors = wg.Textarea(value='',description='Authors',disabled=False)
        self.institution = wg.Textarea(value='',description='Institution',disabled=False)
        self.reference = wg.Textarea(value='',description='Reference',disabled=False)
        self.abstract = wg.Textarea(value='',description='Abstract',disabled=False)
        self.informations = wg.VBox([self.title, self.authors, self.institution, self.reference, self.abstract])

        self.algoFile = wg.Textarea(value='',description='Filename',disabled=False)


        


    def buildEdit(self):

        self.title.value = self.xmlfile.description.Title
        self.authors.value = self.xmlfile.description.Authors
        self.institution.value = self.xmlfile.description.Institution
        self.reference.value = self.xmlfile.description.Reference
        self.abstract.value = self.xmlfile.description.Abstract

        self.dataframeIn = pandas.DataFrame(data={
            'Name':[i['name'] for i in self.xmlfile.inputs],
            'Description': [i['description'] for i in self.xmlfile.inputs],
            'InputType': pandas.Categorical([i['inputtype'] for i in self.xmlfile.inputs], categories=['variable','parameter']),
            'Category': pandas.Categorical([(i['variablecategory'] if 'variablecategory' in i else i['parametercategory']) for i in self.xmlfile.inputs], categories=['constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([i['datatype'] for i in self.xmlfile.inputs], categories=['DOUBLE','DOUBLELIST','CHARLIST','INT','INTLIST','STRING','STRINGLIST','FLOAT','FLOATLIST','BOOLEAN','DATE','DATELIST']),
            'Default': [i['default'] for i in self.xmlfile.inputs],
            'Min': [i['min'] for i in self.xmlfile.inputs],
            'Max': [i['maxi'] for i in self.xmlfile.inputs],
            'Unit': [i['unit'] for i in self.xmlfile.inputs],
            'uri': [i['uri'] for i in self.xmlfile.inputs]
            })

        self.qgridIn = qgrid.show_grid(self.dataframeIn, show_toolbar=True)
        
        self.dataframeOut = pandas.DataFrame(data={
            'Name':[i['name'] for i in self.xmlfile.outputs],
            'Description': [i['description'] for i in self.xmlfile.outputs],
            'InputType': pandas.Categorical([i['inputtype'] for i in self.xmlfile.outputs], categories=['variable','parameter']),
            'Category': pandas.Categorical([(i['variablecategory'] if 'variablecategory' in i else i['parametercategory']) for i in self.xmlfile.outputs], categories=['constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([i['datatype'] for i in self.xmlfile.outputs], categories=['DOUBLE','DOUBLELIST','CHARLIST','INT','INTLIST','STRING','STRINGLIST','FLOAT','FLOATLIST','BOOLEAN','DATE','DATELIST']),
            'Default': [i['default'] for i in self.xmlfile.outputs],
            'Min': [i['min'] for i in self.xmlfile.outputs],
            'Max': [i['max'] for i in self.xmlfile.outputs],
            'Unit': [i['unit'] for i in self.xmlfile.outputs],
            'uri': [i['uri'] for i in self.xmlfile.outputs]
            })

        self.qgridOut = qgrid.show_grid(self.dataframeOut, show_toolbar=True)

        self.dataframeAlgo = pandas.DataFrame(data={
            'Algorithm': [i.name for i in self.xmlfile.algorithms]
        })

        self.qgridAlgo = qgrid.show_grid(self.dataframeAlgo, show_toolbar=True)
        


    def parse(self):

        name = re.search(r'unit\.(.*?)\.xml', self.datas['Model name'])
        parsing = model_parser(self.datas['Path'])
        
        for i in range(0, len(parsing)):

            if parsing[i].name == name.group(1):        
                self.xmlfile = parsing[i]
                break
        
        self.buildEdit()



    def _updateParam(self):

        self.dataframeIn = self.qgridIn.get_changed_df()
        self.dataframeOut = self.qgridOut.get_changed_df()
        self.dataframeAlgo = self.qgridAlgo.get_changed_df()

        for i in range(0, len(self.dataframeIn)):

            if self.dataframeIn['InputType'][i] == 'parameter':
                
                pass


        


    def displayParamset(self):

        self.out.clear_output()
        self.out2.clear_output()

        self._updateParam()

        self.tmpout = wg.Output()

        paramsetselecter = wg.Select(options=['']+[i.name for i in self.xmlfile.parametersSet.listParameterset],value='',description='ParameterSet',disabled=False)
        self.current = ''

        apply = wg.Button(value=False, description='Apply', disabled=False, button_style='success')
        cancel = wg.Button(value=False, description='Cancel', disabled=False, button_style='danger')

        self.dictparamset = dict()

        for paramset in self.xmlfile.parametersSet.listParameterset:

            self.dictparamset[paramset.name] = [paramset.description, pandas.DataFrame(data={
                'Name': [i.name for i in paramset.listparam],
                'Value': [i.value for i in paramset.listparam]
            })]

        self.tmpqgrid = None
        self.tmpdescription = wg.Textarea(value='',description='Description',disabled=False)

        with self.out:
            display(wg.VBox([paramsetselecter, self.tmpout, wg.HBox([apply, cancel])]))


        def on_value_change(change):
            
            if not self.current:

                if paramsetselecter.value:
                    self.current = paramsetselecter.value
                    self.tmpdescription.value = self.dictparamset[self.current][0]
                    self.tmpqgrid = qgrid.show_grid(self.dictparamset[self.current][1], show_toolbar=False)

                    self.tmpout.clear_output()

                    with self.tmpout:
                        display(wg.VBox([self.tmpdescription, self.tmpqgrid]))
            
            else:

                self.dictparamset[self.current] = self.tmpqgrid.get_changed_df()
                self.current = paramsetselecter.value

                if paramsetselecter.value:
                             
                    self.tmpdescription.value = self.dictparamset[self.current][0]
                    self.tmpqgrid = qgrid.show_grid(self.dictparamset[self.current])

                    self.tmpout.clear_output()

                    with self.tmpout:
                        display(wg.VBox([self.tmpdescription, self.tmpqgrid]))
                
                else:

                    self.tmpout.clear_output()


                


        def eventApply(b):
            pass


        apply.on_click(eventApply)
        cancel.on_click(self.eventCancel)
        paramsetselecter.observe(on_value_change, names='value')



    def eventApply(self, b):

        
        self.dataframeIn = self.qgridIn.get_changed_df()
        self.dataframeOut = self.qgridOut.get_changed_df()

        if any(['' in self.dataframeIn['Name'],'' in self.dataframeIn['Description'],'' in self.dataframeIn['InputType'],'' in self.dataframeIn['Category'],'' in self.dataframeIn['DataType'],'' in self.dataframeIn['Unit']]):
            
            with self.out2:
                print('Missing argument(s) in the input list, these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Unit')
        
        elif any(['' in self.dataframeOut['Name'],'' in self.dataframeOut['Description'],'' in self.dataframeOut['InputType'],'' in self.dataframeOut['Category'],'' in self.dataframeOut['DataType'],'' in self.dataframeOut['Unit']]):
            
            with self.out2:
                print('Missing argument(s) in the output list, these columns are required :\n\t- Type\n\t- Name\n\t- Description\n\t- InputType\n\t- Category\n\t- DataType\n\t- Unit')
        
        elif '' in self.dataframeAlgo['Algorithm']:

            with self.out2:
                print('Missing argument(s) in the algorithm list.')

        else:
            self.displayParamset()


    
    def eventCancel(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        try:
            tmp = editmenu.editMenu()
            tmp.displayMenu()

        except:
            raise Exception('Could not load edition menu.')

        finally:
            del self


    def display(self, dic):

        self.datas = dic

        self.parse()

        display(self.out)
        display(self.out2)

        tab = wg.Tab()
        tab.children = [self.qgridIn, self.qgridOut, self.qgridAlgo]
        tab.set_title(0, 'Inputs')
        tab.set_title(1, 'Outputs')
        tab.set_title(2, 'Algorithms')

        with self.out:
            display(wg.VBox([wg.HTML(value='<b>Model edition : {}.{}.xml<br>-> Inputs, Outputs, Algorithms'.format(self.datas['Model type'], self.datas['Model name'])), tab, wg.HBox([self.apply, self.cancel])]))
    
        self.apply.on_click(self.eventApply)
        self.cancel.on_click(self.eventCancel)
        