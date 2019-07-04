import os
import re
import ipywidgets as wg

import qgrid
import pandas

from IPython.display import display


class editUnit():


    def __init(self):

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        self.datas = dict()

        self.title = wg.Textarea(value='',description='Title',disabled=False)
        self.authors = wg.Textarea(value='',description='Authors',disabled=False)
        self.institution = wg.Textarea(value='',description='Institution',disabled=False)
        self.reference = wg.Textarea(value='',description='Reference',disabled=False)
        self.abstract = wg.Textarea(value='',description='Abstract',disabled=False)
        self.informations = wg.VBox([self.title, self.authors, self.institution, self.reference, self.abstract])


        self.dataframeInOut = pandas.DataFrame(data={
            'Type': pandas.Categorical([''], categories=['input','output','input & output']),
            'Name':[''],
            'Description': [''],
            'InputType': pandas.Categorical([''], categories=['','variable','parameter']),
            'Category': pandas.Categorical([''], categories=['','constant','species','genotypic','soil','private','state','rate','auxiliary']),
            'DataType': pandas.Categorical([''], categories=['','DOUBLE','DOUBLELIST','CHARLIST','INT','INTLIST','STRING','STRINGLIST','FLOAT','FLOATLIST','BOOLEAN','DATE','DATELIST']),
            'Default': [''],
            'Min': [''],
            'Max': [''],
            'Unit': [''],
            'uri': ['']})

        self.dataframeInOutqgrid = qgrid.show_grid(self.dataframeInOut, show_toolbar=True)


        self.tab = wg.Tab([self.informations, self.dataframeInOutqgrid])
        self.tab.set_title(0, 'Model datas')
        self.tab.set_title(1, 'Inputs & Outputs')

        




    def parse(self):

        try:
            fr = open(self.datas['Path'], 'r')
        
        except IOError as ioerr:
            with self.out2:
                print('File {} could not be opened. {}'.format(self.datas['Path'], ioerr))

        else:

            for buffer in fr:

                if not self.title.value:
                    self.title.value = re.search(r'<Title>(.*?)</Title>', buffer).group(1)
                if not self.authors.value:
                    self.authors.value = re.search(r'<Authors>(.*?)</Authors>', buffer).group(1)
                if not self.institution.value:
                    self.institution.value = re.search(r'<Institution>(.*?)</Institution>', buffer).group(1)
                if not self.reference.value:
                    self.reference.value = re.search(r'<Reference>(.*?)</Reference>', buffer).group(1)
                if not self.abstract.value:
                    self.abstract.value = re.search(r'<Abstract>(.*?)</Abstract>', buffer).group(1)

                if re.search(r'(<Inputs>)', buffer):
                    break

            for buffer in fr:
                pass

                #line = re.search(r'<Input name="(.*?)" ', buffer)
                


    def display(self, dic):

        self.datas = dic

        display(self.out)
        display(self.out2)

        with self.out:
            display()