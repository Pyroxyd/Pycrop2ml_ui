import os
import re
import ipywidgets as wg

import qgrid
import pandas

from IPython.display import display



class createComposition():


    def __init__(self):

        self.out = wg.Output()
        self.out2 = wg.Output()

        self.end = wg.Button(value=False,description='End',disabled=False,button_style='success')
        self.abort = wg.Button(value=False,description='Abort',disabled=False,button_style='danger')

        self.datas = dict()

        self.dataFrameLink = pandas.DataFrame(data={
            'Link type': pandas.Categorical([''], categories=['','InputLink','InternalLink','OutputLink']),
            'Target': [''],
            'Source': ['']
        })

        self.dataFrameLinkqgrid = qgrid.show_grid(self.dataFrameLink, show_toolbar=True)


    def listdir(self):

        liste = ['']

        for buffer in os.listdir(self.datas['Path']):

            ext = os.path.splitext(buffer)[-1].lower()
            if (ext == '.xml' and (not buffer == 'composition.{}.xml'.format(self.datas['Model name']))):

                if re.search(r'(composition)', buffer):
                    liste.append(buffer)

                elif re.search(r'(unit)', buffer):
                    liste.append(buffer)


        self.dataFrame = pandas.DataFrame(data={
            'Model type': pandas.Categorical([''], categories=['','unit', 'composition']),
            'Model name': pandas.Categorical([''], categories=liste),
        })
        


    def createXML(self):

        self.dataFrame = self.dataframeqgrid.get_changed_df()
        self.dataFrameLink = self.dataFrameLinkqgrid.get_changed_df()
        #self.dataFrameLink.sort_index(axis=1)

        try:
            f = open("{}/composition.{}.xml".format(self.datas['Path'], self.datas['Model name']), 'w')

        except IOError as ioerr:
            with self.out2:
                print('File composition.{}.xml could not be opened. {}'.format(self.datas['Model name'], ioerr))

        else:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE ModelComposition PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelComposition.dtd">\n')
            f.write('<ModelComposition modelid="{}" name="{}" timestep="1" version="1.0">'.format(self.datas['Model name'],self.datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{} Model</Title>'.format(self.datas['Model name'])+
                '\n\t\t<Authors>{}</Authors>'.format(self.datas['Author'])+
                '\n\t\t<Institution>{}</Institution>'.format(self.datas['Institution'])+
                '\n\t\t<Reference>{}</Reference>'.format(self.datas['Reference'])+
                '\n\t\t<Abstract>{}</Abstract>'.format(self.datas['Description'])+'\n\t</Description>')

            f.write('\n\t<Composition>')

            for i in range(0, len(self.dataFrame['Model type'])):

                f.write('\n\t\t<Model name="{0}" id="{1}.{0}" filename="{2}" />'.format(re.search(r'\.(.*?)\.xml',self.dataFrame['Model name'][i]).group(1), self.datas['Model name'], self.dataFrame['Model name'][i]))

            f.write('\n\n\t\t<Links>')

            for i in range(0, len(self.dataFrameLink['Link type'])):

                f.write('\n\t\t\t<{} target="{}" source="{}" />'.format(self.dataFrameLink['Link type'][i], self.dataFrameLink['Target'][i], self.dataFrameLink['Source'][i]))

            f.write('\n\t\t</Links>\n\t</Composition>\n</ModelComposition>')

            f.close()

            with self.out2:
                print("FIle composition.{}.xml successfully updated.".format(self.datas['Model name']))

            
       

    def eventEnd(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        with self.out:
            print("Updating datas to composition.{}.xml".format(self.datas['Model name']))
            self.createXML()



    def eventAbort(self, b):

        self.out.clear_output()
        self.out2.clear_output()

        del self
        return



    def display(self, dic):

        self.datas = dic
        self.listdir()
        self.dataframeqgrid = qgrid.show_grid(self.dataFrame, show_toolbar=True)

        tab = wg.Tab([self.dataframeqgrid, self.dataFrameLinkqgrid])
        tab.set_title(0, 'Composition')
        tab.set_title(1, 'Links')

        display(self.out)
        display(self.out2)

        with self.out:
            display(wg.VBox([tab, wg.HBox([self.end, self.abort])]))

        self.end.on_click(self.eventEnd)
        self.abort.on_click(self.eventAbort)

