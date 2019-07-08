import ipywidgets as wg
import os
import re

import qgrid
import pandas

from IPython.display import display



class editComposition():

    def __init__(self):

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        #buttons
        self.apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')

        #datas
        self.datas = dict()
        self.listmodel = []
        self.listlink = [[],[],[]]


    
    def parse(self):
        
        try:
            f = open(self.datas['Path'],"r")

        except IOError as ioerr:
            with self.out2:
                print('File {} could not be opened in read mode. {}'.format(self.datas['Path'], ioerr))

        else:

            for buffer in f:
                model = re.search('filename="(.*?)" />',buffer)
                linktype = re.search('<(.*?Link)',buffer)
                target = re.search('target="(.*?)"',buffer)
                source = re.search('source="(.*?)"',buffer)

                if model:
                    self.listmodel.append(model.group(1))
                if linktype and target and source:
                    self.listlink[0].append(linktype.group(1))
                    self.listlink[1].append(target.group(1))
                    self.listlink[2].append(source.group(1))

            f.close()




    def write(self):

        try:
            f = open(self.datas['Path'], "r")

        except IOError as ioerr:
            with self.out2:
                print('File {} could not be opened in read mode. {}'.format(self.datas['Path'], ioerr))

        else:
            with self.out2:
                print("Modifying the file ...")


            buffer = f.read()

            f.close()

            balisedebut = re.search("(<Composition>)", buffer)
            balisefin = re.search("(</Links>)", buffer)
        
            if balisedebut and balisefin:
                
                try:
                    fw = open(self.datas['Path'], "w")

                except IOError as ioerr:
                    with self.out2:
                        print('File {} could not be opened in write mode. {}'.format(self.datas['Path'], ioerr))

                else:

                    fw.write(format(buffer[:balisedebut.end()]))

                    for i in range(0, len(self.dataframe['Model type'])):

                        if self.dataframe['Model type'][i] == 'Unit':
                            fw.write('\n\t<Model name="{0}" id="{1}.{0}" filename="{2}" />'.format(re.search(r'unit\.(.*?)\.xml',self.dataframe['Model component'][i]).group(1), self.datas['Model name'], self.dataframe['Model component'][i]))
                        else:
                            fw.write('\n\t<Model name="{0}" id="{0}" filename="{1}" />'.format(re.search(r'composition\.(.*?)\.xml',self.dataframe['Model component'][i]), self.dataframe['Model component'][i]))

                    fw.write("\n\n\t<Links>")
                    
                    for i in range(0, len(self.dataframelinks['Link type'])):
                        fw.write('\n\t\t<{} target="{}" source="{}" />'.format(self.dataframelinks['Link type'][i], self.dataframelinks['Target'][i], self.dataframelinks['Source'][i]))
                    
                    
                    fw.write('\n\n\t'+format(buffer[balisefin.start():]))
                    fw.close()

                    with self.out2:
                        print('File updated.')

            else:
                with self.out2:
                    print("Incomplete xml file. Abording ...")
                    return
                    



    def eventApply(self, b):

        self.out.clear_output()
        self.out2.clear_output()
        self.dataframe = self.datamodeltab.get_changed_df()
        self.dataframelinks = self.datalinktab.get_changed_df()
        self.write()
    


    def eventCancel(self, b):

        self.out.clear_output()
        self.out2.clear_output()
        del self
        return
        


    def display(self, dic):

        display(self.out)
        display(self.out2)

        self.datas = dic
        self.parse()


        if self.listmodel:
            self.dataframe = pandas.DataFrame(data={
                'Model type': pandas.Categorical(['Unit' for i in range(0,len(self.listmodel))], categories=['Unit','Composition']),
                'Model component':self.listmodel
                },index=None)
            self.datamodeltab = qgrid.show_grid(self.dataframe, show_toolbar=True)

        else:
            with self.out2:
                print("No model available in this package.")
            return


        if self.listlink:
            self.dataframelinks = pandas.DataFrame(data={
                'Link type': pandas.Categorical(self.listlink[0], categories=['InputLink','OutputLink','InternalLink']),
                'Target': self.listlink[1],
                'Source': self.listlink[2]
                },index=None)
            self.datalinktab = qgrid.show_grid(self.dataframelinks, show_toolbar=True)

        else:
            with self.out2:
                print("No link available in this package.")
            return
        

        if self.listmodel and self.listlink:
            self.tab = wg.Tab([self.datamodeltab, self.datalinktab])
            self.tab.set_title(0, 'Models')
            self.tab.set_title(1, 'Links')

        with self.out:
            display(wg.VBox([self.tab, wg.HBox([self.apply, self.cancel])]))
        
        self.apply.on_click(self.eventApply)
        self.cancel.on_click(self.eventCancel)