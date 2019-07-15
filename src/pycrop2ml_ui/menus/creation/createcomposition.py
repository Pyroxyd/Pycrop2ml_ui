import os
import re
import ipywidgets as wg

import qgrid
import pandas

from IPython.display import display



class createComposition():


    def __init__(self):

        self._out = wg.Output()
        self._out2 = wg.Output()

        self._apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self._cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        self._datas = dict()

        self._dataFrameLink = pandas.DataFrame(data={
            'Link type': pandas.Categorical([''], categories=['','InputLink','InternalLink','OutputLink']),
            'Target': [''],
            'Source': ['']
        })

        self._dataFrameLinkqgrid = qgrid.show_grid(self._dataFrameLink, show_toolbar=True)



    def _listdir(self):

        liste = ['']

        for buffer in os.listdir(self._datas['Path']):

            ext = os.path.splitext(buffer)[-1].lower()

            if (ext == '.xml' and (not buffer == 'composition.{}.xml'.format(self._datas['Model name']))):

                if re.search(r'(composition)', buffer):
                    liste.append(buffer)

                elif re.search(r'(unit)', buffer):
                    liste.append(buffer)


        self._dataFrame = pandas.DataFrame(data={'Model name': pandas.Categorical([''], categories=liste)})
        


    def _createXML(self):

        self._dataFrame = self._dataFrameqgrid.get_changed_df()
        self._dataFrameLink = self._dataFrameLinkqgrid.get_changed_df()

        try:
            f = open("{}/composition.{}.xml".format(self._datas['Path'], self._datas['Model name']), 'w')

        except IOError as ioerr:
            with self._out2:
                print('File composition.{}.xml could not be opened. {}'.format(self._datas['Model name'], ioerr))

        else:

            split = re.split(r'\\', self._datas['Path'])
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE ModelComposition PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelComposition.dtd">\n')
            f.write('<ModelComposition modelid="{}.{}" name="{}" timestep="1" version="1.0">'.format(split[-4], self._datas['Model name'],self._datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{}</Title>\n\t\t<Authors>{}</Authors>\n\t\t<Institution>{}</Institution>\n\t\t<Reference>{}</Reference>\n\t\t<Abstract>{}</Abstract>\n\t</Description>'.format(self._datas['Model name'], self._datas['Author'], self._datas['Institution'], self._datas['Reference'], self._datas['Abstract']))

            f.write('\n\t<Composition>')

            for i in range(0, len(self._dataFrame['Model name'])):

                f.write('\n\t\t<Model name="{0}" id="{1}.{0}" filename="{2}" />'.format(re.search(r'\.(.*?)\.xml',self._dataFrame['Model name'][i]).group(1), self._datas['Model name'], self._dataFrame['Model name'][i]))

            f.write('\n\n\t\t<Links>')

            for i in range(0, len(self._dataFrameLink['Link type'])):

                f.write('\n\t\t\t<{} target="{}" source="{}" />'.format(self._dataFrameLink['Link type'][i], self._dataFrameLink['Target'][i], self._dataFrameLink['Source'][i]))

            f.write('\n\t\t</Links>\n\t</Composition>\n</ModelComposition>')

            f.close()

            with self._out2:
                print("FIle composition.{}.xml successfully updated.".format(self._datas['Model name']))

            
       

    def _eventApply(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        with self._out:

            display(wg.HTML(value='<b> Model creation : composition.{}.xml<br>-> XML writing</b>'.format(self._datas['Model name'])))
            self._createXML()



    def _eventCancel(self, b):

        self._out.clear_output()
        self._out2.clear_output()

        os.remove("{}/composition.{}.xml".format(self._datas["Path"], self._datas['Model name']))

        del self
        return



    def display(self, dic):

        display(self._out)
        display(self._out2)
        
        self._datas = dic
        self._listdir()
        self._dataFrameqgrid = qgrid.show_grid(self._dataFrame, show_toolbar=True)

        children = [self._dataFrameqgrid, self._dataFrameLinkqgrid]
        tab = wg.Tab()
        tab.children = children
        tab.set_title(0, 'Composition')
        tab.set_title(1, 'Links')

        with self._out:
            display(wg.VBox([wg.HTML(value='<b> Model creation : composition.{}.xml</b>'.format(self._datas['Model name'])), tab, wg.HBox([self._apply, self._cancel])]))

        self._apply.on_click(self._eventApply)
        self._cancel.on_click(self._eventCancel)

        

