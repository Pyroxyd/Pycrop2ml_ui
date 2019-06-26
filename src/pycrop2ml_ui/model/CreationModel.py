import ipywidgets as wg
import os
import sys

import qgrid
import pandas

from IPython.display import display

from pycrop2ml_ui.cpackage.CreationRepository import mkdirModel
from pycrop2ml_ui.browser.Path import FileBrowser



#editTable class for displaying and managing the edition model menu
class editTable:

    def __init__(self, parentnode):

        #buttons
        self.end = wg.Button(value=False,description='End',disabled=False,button_style='success')

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        #dataframes
        self.dataframeInputs = pandas.DataFrame(data={
            'Type': pandas.Categorical(['input'], categories=['input','output','input & output']),
            'Name':['name'],
            'Description':['description'],
            'InputType': pandas.Categorical(['variable'], categories=['variable','parameter']),
            'Category': ['auxiliary'],
            'DataType': pandas.Categorical(['INT'], categories=['INT','INTLIST','STRING','STRINGLIST','BOOLEAN','DATE','DATELIST']),
            'Default': ['0'],
            'Min': ['0'],
            'Max': ['0'],
            'Unit': ['none'],
            'uri': ['uri']})

        self.dataframeParamsets = pandas.DataFrame(data={})
        self.dataframeTestsets = pandas.DataFrame(data={})

        #qgrids from dataframes above
        self.inputstab = qgrid.show_grid(self.dataframeInputs, show_toolbar=True)
        self.parameterssetstab = qgrid.show_grid(self.dataframeParamsets, show_toolbar=True)
        self.testsetstab = qgrid.show_grid(self.dataframeTestsets, show_toolbar=True)
        self.algorithmtab = wg.Textarea(value='',description='Location',disabled=False)
    
        self.tab = wg.Tab([self.inputstab, self.parameterssetstab, self.testsetstab])
        self.tab.set_title(0, 'Inputs')
        self.tab.set_title(1, 'Parameterssets')
        self.tab.set_title(2, 'Testsets')

        #global menu displayer
        self.displayer = wg.VBox([self.tab,self.end])

        #model datas
        self.datas = dict()

        #parent menu
        self.parent = parentnode



    #creates xml and pyx files from the pandas dataframe
    def createXML(self):

        self.dataframeInputs = self.inputstab.get_changed_df()

        try:
            f = open("{}/crop2ml/{}.{}.xml".format(self.datas['Package name'], self.datas['Model type'], self.datas['Model name']), 'w')
        except IOError:
            with self.out2:
                print('Unable to open file.')
        else:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Model PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelUnit.dtd">\n')
            f.write('<ModelUnit modelid="{}.{}" name="{}" timestep="1" version="1.0">'.format(os.path.basename(self.datas['Package name']),self.datas['Model name'],self.datas['Model name']))
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
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['uri'][i]))
                
                    else:
                        f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self.dataframeInputs['Name'][i],self.dataframeInputs['Description'][i],self.dataframeInputs['InputType'][i],self.dataframeInputs['Category'][i],self.dataframeInputs['DataType'][i],self.dataframeInputs['Default'][i],self.dataframeInputs['Min'][i],self.dataframeInputs['Max'][i],self.dataframeInputs['Unit'][i],self.dataframeInputs['uri'][i]))
                    
            f.write('\n\t</Outputs>')



            
            f.write("\n\n</ModelUnit>")
            with self.out2:
                print('File successfully updated.')            
            f.close()
            
            
            try:
                algo = open("{}/crop2ml/algo/pyx/{}.pyx".format(self.datas['Package name'], self.datas['Model name']), 'w')
            except IOError:
                with self.out2:
                    print("Algorithm file could not be created.")
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


    #on_click event for end button
    def eventEnd(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        with self.out:
            if(self.datas['Model type'] == 'unit'):
                print("Updating datas to unit.{}.xml".format(self.datas['Model name']))
            else:
                print("Updating datas to composition.{}.xml".format(self.datas['Model name']))
            self.createXML()


    #displays the menu
    def display(self, dic):
        self.datas = dic
        display(self.out)
        with self.out:
            display(self.displayer)
        display(self.out2)

        self.end.on_click(self.eventEnd)



#createModel class for displaying and managing the creation model menu
class createModel:

    def __init__(self):

        #input datas
        self.modelName = wg.Textarea(value='',description='Model name',disabled=False)
        self.author = wg.Textarea(value='',description='Author',disabled=False)
        self.institution = wg.Textarea(value='',description='Institution',disabled=False)
        self.description = wg.Textarea(value='',description='Description',disabled=False)
        self.package = wg.Textarea(value='',description='Package',disabled=True) 
        self.reference = wg.Textarea(value='',description='Reference',disabled=False)

        #model type
        self.toggle = wg.ToggleButtons(options=["unit", "composition"], description="Model type :", disabled=False)

        #buttons
        self.save = wg.Button(value=False,description='Save',disabled=False,button_style='success')
        self.create = wg.Button(value=False,description='Create',disabled=False,button_style='success')
        self.cancel = wg.Button(value=False,description='Cancel',disabled=False,button_style='danger')
        self.browse = wg.Button(value=False,description='Browse',disabled=False,background_color='#d0d0ff')

        #global menu displayer
        self.displayer = wg.VBox([self.toggle, wg.HBox([self.package, self.browse, self.create]), self.modelName, self.author, self.institution, self.description, self.reference, wg.HBox([self.save, self.cancel])])

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        #model datas
        self.export = dict()

        #child creation menu
        self.table = editTable(self)



    #getter for self.export
    def getExport(self, n):
        return self.export[n]

    #displays child menu
    def displayTab(self, dic):
        self.table.display(dic)

    #initalyses the new model file
    def createFile(self):
        self.out2.clear_output()
        if(any([(os.path.exists("{}/crop2ml/unit.{}.xml".format(self.export["Package name"],self.modelName.value)) and self.export['Model type']=='unit'), (os.path.exists("{}/crop2ml/composition.{}.xml".format(self.export["Package name"],self.modelName.value)) and self.export['Model type']=='composition')])):
            with self.out2:
                print("This file already exists.")
            return False
        else:
            if(self.getExport('Model type') == 'unit'):
                try:
                    tmpFile = open("{}/crop2ml/unit.{}.xml".format(self.export["Package name"], self.getExport('Model name')), 'w')
                except IOError:
                    with self.out2:
                        print('File could not be opened.')
                    return False
                else:
                    tmpFile.close()
                    return True
                
            else:
                try:
                    tmpFile = open("{}/crop2ml/composition.{}.xml".format(self.export["Package name"], self.getExport('Model name')), 'w')
                except IOError:
                    with self.out2:
                        print('File could not be opened.')
                    return False
                else:
                    tmpFile.close()
                    return True

    #on_click for create button
    def eventCreate(self, b):

        self.out2.clear_output()
        with self.out2:
            tmp = mkdirModel()
            display(tmp.display())


    #on_click for save button
    def eventSave(self, b):
        self.out2.clear_output()
        if(self.modelName.value and self.author.value and self.institution.value and self.description.value and self.package.value and self.reference.value):
            if(os.path.exists(self.package.value)):

                self.export = {'Package name': self.package.value, 'Model type': self.toggle.value, 'Model name': self.modelName.value, 'Author': self.author.value, 'Institution': self.institution.value, 'Reference': self.reference.value, 'Description': self.description.value, 'Option': '1'}
                self.out.clear_output()
                with self.out:
                    try:
                        self.createFile()
                    except IOError:
                        print("Could not open file.")
                    else:
                        print("Creating {}.{}.xml ...".format(self.export['Model type'], self.export['Model name']))
                        # COND : IF unit displayTable ELSE: display un autre truc pas encore implémenté               
                        self.displayTab(self.export)

            else:
                with self.out:
                    print("This package does not exist.")

        else:
            with self.out2:
                print("Missing argument(s) :")
                if(not self.package.value):
                    print("\t- Package name")
                if(not self.modelName.value):
                    print("\t- Model name")
                if(not self.author.value):
                    print("\t- Author")
                if(not self.institution.value):
                    print("\t- Institution")
                if(not self.reference.value):
                    print("\t- Reference")
                if(not self.description.value):
                    print("\t- Description")

    #on_click for cancel button                  
    def eventCancel(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        with self.out:
            tmp = displayMainMenu()
            display(tmp.displayMenu())

    #on_click for browse button
    def eventBrowse(self, b):

        def eventTmp(b):
            self.package.value = tmp.path
            self.out2.clear_output()

        self.out2.clear_output()
        tmp = FileBrowser()
        buttontmp = wg.Button(value=False,description='Select',disabled=False,button_style='success')

        with self.out2:
            display(tmp.widget())
            display(buttontmp)
        buttontmp.on_click(eventTmp)

            
            
    #displays the menu
    def displayMenu(self):
        display(self.out)
        with self.out:
            display(self.displayer)
        display(self.out2)

        self.save.on_click(self.eventSave)
        self.cancel.on_click(self.eventCancel)
        self.create.on_click(self.eventCreate)
        self.browse.on_click(self.eventBrowse)


class editModelMenu:

    def __init__(self, dic):

        self.out = wg.Output()
        self.out2 = wg.Output()

        self.liste = []
        self.data = dic

        self.selector = wg.Select(options=self.liste,value=None,description='Unit models :',disabled=False)




#editModel class for displaying and managing the edition menu
class editModel:

    def __init__(self):
           
        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()

        #inputs
        self.modelName = wg.Textarea(value='',description='Model name',disabled=False)
        self.packageName = wg.Textarea(value='',description='Package name',disabled=True)

        #buttons
        self.button = wg.Button(value=False,description='Browse',disabled=False,background_color='#d0d0ff')
        self.edit = wg.Button(value=False,description='Edit',disabled=False,button_style='success')

        #global displayer
        self.displayer = wg.VBox([wg.HBox([self.packageName, self.button]), self.modelName, self.edit])

        self.table = editTable(self)


    #on_click event for edit button
    def eventEdit(self, b):
        self.out2.clear_output()
        if(self.modelName.value and self.packageName.value):
            if(os.path.exists(self.packageName.value)):

                if(os.path.exists(os.path.abspath("{}/crop2ml/".format(self.packageName.value)+"unit.{}.xml".format(self.modelName.value)))):
                    self.out.clear_output()
                    with self.out:                  
                        print("Editing unit.{}.xml".format(self.modelName.value))
                        self.table.display({'Package name': self.packageName.value, 'Model type': 'unit', 'Model name': self.modelName.value, 'Option': '2'})

                elif(os.path.exists(os.path.abspath("{}/crop2ml/".format(self.packageName.value)+"composition.{}.xml".format(self.modelName.value)))):
                    self.out.clear_output()
                    with self.out:
                        self.edit.disabled = True

                        print("Editing composition.{}.xml".format(self.modelName.value))
                        self.table.display({'Package name': self.packageName.value, 'Model type': 'composition', 'Model name': self.modelName.value, 'Option': '2'})
                else:
                    with self.out2:
                        print("This model does not exist in the package {}.".format(self.packageName.value))

            else:
                with self.out2:
                    print('This package does not exist.')

        else:
            with self.out2:
                print("Enter a model and package name.")


    #on_click event for browse button
    def eventBrowse(self, b):

        def eventTmp(b):
            self.packageName.value = tmp.path
            self.out2.clear_output()

        self.out2.clear_output()
        tmp = FileBrowser()
        buttontmp = wg.Button(value=False,description='Select',disabled=False,button_style='success')

        with self.out2:
            display(tmp.widget())
            display(buttontmp)
        buttontmp.on_click(eventTmp)


    #displays the menu
    def displayMenu(self):
        display(self.out)
        with self.out:
            display(self.displayer)
        display(self.out2)

        self.edit.on_click(self.eventEdit)
        self.button.on_click(self.eventBrowse)



class displayModel:
    out = wg.Output()


#displayMainMenu class for displaying and managing the main menu
class displayMainMenu:


    def __init__(self):

        #buttons
        self.create = wg.Button(value=False,description='Create a model',disabled=False)
        self.edit = wg.Button(value=False,description='Edit a model',disabled=False)
        self.display = wg.Button(value=False,description='Display a model',disabled=False)
        self.about = wg.Button(value=False,description='About',disabled=False)

        #global displayer
        self.displayer = wg.VBox([self.create, self.edit, self.display, self.about])

        #children nodes
        self.createWg = createModel()
        self.editWg = editModel()
        self.displayWg = displayModel()

        #outputs
        self.out = wg.Output()
        self.out2 = wg.Output()
    

    #on_click event for create button
    def eventCreate(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        with self.out: 
            self.createWg.displayMenu()
            

    #on_click event for edit button
    def eventEdit(self, b):
        self.out.clear_output()
        self.out2.clear_output()
        with self.out:
            self.editWg.displayMenu()


    #on_click event for display button
    def eventDisplay(self, b):
        self.out2.clear_output()
        with self.out2:
            print("display !")


    #on_click event for about button
    def eventAbout(self, b):
        self.out2.clear_output()
        with self.out2:
            print("""
This widget provides a way to create a Crop2ML model including any needed parameter.\n
You may use it for model edition and model display aswell.\n
Both ipywidgets and qgrid are required for running this tool, they are enabled with the JupyterLab extension crop2ml.\n""")


    #displays the main menu
    def displayMenu(self):

        display(self.out)
        with self.out:
            display(self.displayer)
        display(self.out2)

        self.create.on_click(self.eventCreate)
        self.edit.on_click(self.eventEdit)
        self.display.on_click(self.eventDisplay)
        self.about.on_click(self.eventAbout)
        



def main():

    output = displayMainMenu()
    output.displayMenu()

