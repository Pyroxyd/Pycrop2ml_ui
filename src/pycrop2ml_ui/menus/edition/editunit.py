import os
import re
import ipywidgets as wg

import qgrid
import pandas

from IPython.display import display
from pycrop2ml_ui.parsingXML import parser


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
        self.algoPlatform = wg.Textarea(value='',description='Platform',disabled=False)
        self.algoLanguage = wg.Textarea(value='',description='Languague',disabled=False)
        self.algorithm = wg.VBox([self.algoLanguage, self.algoPlatform, self.algoFile])


        


    def buildEdit(self):

        self.title.value = self.xmlfile.description.title
        self.authors.value = self.xmlfile.description.authors
        self.institution.value = self.xmlfile.description.institution
        self.reference.value = self.xmlfile.description.reference
        self.abstract.value = self.xmlfile.description.abstract

        self.dataframeIn = pandas.DataFrame(data={
            'Name':[i.name for i in self.xmlfile.inputs.dictinput],
            'Description': [i.description for i in self.xmlfile.inputs.dictinput],
            'InputType': pandas.Categorical([i.inputtype for i in self.xmlfile.inputs.dictinput], categories=['variable','parameter']),
            'Category': pandas.Categorical([i.category for i in self.xmlfile.inputs.dictinput], categories=['constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([i.datatype for i in self.xmlfile.inputs.dictinput], categories=['DOUBLE','DOUBLELIST','CHARLIST','INT','INTLIST','STRING','STRINGLIST','FLOAT','FLOATLIST','BOOLEAN','DATE','DATELIST']),
            'Default': [i.default for i in self.xmlfile.inputs.dictinput],
            'Min': [i.mini for i in self.xmlfile.inputs.dictinput],
            'Max': [i.maxi for i in self.xmlfile.inputs.dictinput],
            'Unit': [i.unit for i in self.xmlfile.inputs.dictinput],
            'uri': [i.uri for i in self.xmlfile.inputs.dictinput]
            })
        self.qgridIn = qgrid.show_grid(self.dataframeIn, show_toolbar=True)
        
        self.dataframeOut = pandas.DataFrame(data={
            'Name':[i.name for i in self.xmlfile.outputs.dictoutput],
            'Description': [i.description for i in self.xmlfile.outputs.dictoutput],
            'InputType': pandas.Categorical([i.inputtype for i in self.xmlfile.outputs.dictoutput], categories=['variable','parameter']),
            'Category': pandas.Categorical([i.category for i in self.xmlfile.outputs.dictoutput], categories=['constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([i.datatype for i in self.xmlfile.outputs.dictoutput], categories=['DOUBLE','DOUBLELIST','CHARLIST','INT','INTLIST','STRING','STRINGLIST','FLOAT','FLOATLIST','BOOLEAN','DATE','DATELIST']),
            'Default': [i.default for i in self.xmlfile.outputs.dictoutput],
            'Min': [i.mini for i in self.xmlfile.outputs.dictoutput],
            'Max': [i.maxi for i in self.xmlfile.outputs.dictoutput],
            'Unit': [i.unit for i in self.xmlfile.outputs.dictoutput],
            'uri': [i.uri for i in self.xmlfile.outputs.dictoutput]
            })
        self.qgridOut = qgrid.show_grid(self.dataframeOut, show_toolbar=True)

        self.algoPlatform.value = self.xmlfile.algorithm.platform
        self.algoLanguage.value = self.xmlfile.algorithm.language
        self.algoFile.value = self.xmlfile.algorithm.algo

        self.paramsets = wg.HTML(value='<b>Paramsets</b>', placeholder='Paramsets', description='desc')

        self.testsets = wg.HTML(value='<b>Testsets</b>', placeholder='Paramsets', description='desc')
        

    def parse(self):

        self.xmlfile = parser.fileXML(self.datas['Path'])
        self.xmlfile.mainParse()

        self.buildEdit()
                


    def eventApply(self, b):
        pass

    
    def eventCancel(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        del self



    def display(self, dic):

        self.datas = dic

        self.parse()

        display(self.out)
        display(self.out2)

        tab = wg.Tab()
        tab.children = [self.qgridIn, self.qgridOut, self.algorithm, self.paramsets, self.testsets]
        tab.set_title(0, 'Inputs')
        tab.set_title(1, 'Outputs')
        tab.set_title(2, 'Algorithm')
        tab.set_title(3, 'ParametersSet')
        tab.set_title(4, 'TestsSet')

        with self.out:
            display(wg.VBox([tab, wg.HBox([self.apply, self.cancel])]))

        self.apply.on_click(self.eventApply)
        self.cancel.on_click(self.eventCancel)
        