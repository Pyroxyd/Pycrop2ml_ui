import os

import ipywidgets as wg
from IPython.display import display

from pycropml.pparse import model_parser
from pycropml.transpiler.generators import docGenerator


class writeunitXML():
    """
    Class managing the writing of a unit model xml file with all gathered data with pycrop2ml' user interface.

    Parameters : \n
        - datas : {
                    'Path': '',
                    'Model type': 'unit',
                    'Model name': '',
                    'Model ID': '',
                    'Version': '',
                    'Timestep': '',
                    'Title': '',
                    'Authors': '',
                    'Institution': '',
                    'Reference': '',
                    'Abstract': '',
                    'Old name':'' IF iscreate=False
                   }

        - df : {'Inputs' : pandas.DataFrame,
                'Algorithms' : [],
                'Functions' : dict(),
                'Outputs' : pandas.DataFrame -> only if iscreate is False
               }

        - paramsetdict : {paramset_name : [
                                          {param : value},
                                          description
                                          ]
                         }

        - testsetdict : {name : [
                                {testname : type(vardict)},
                                parameterset,
                                description
                                ]
                        }
        
        - iscreate : bool
    """


    def __init__(self, datas, df, paramsetdict, testsetdict, iscreate=True):
        
        self._out = wg.Output()
        self._datas = datas
        self._df = df
        self._paramsetdict = paramsetdict
        self._testsetdict = testsetdict
        self._iscreate = iscreate
        self._change_algo = True
        self._change_init = True



    def _getDoc(self, f):
        """
        Returns the documentation of the current's model xml file
        """

        parse = os.path.split(self._datas['Path'])[0]
        parsing = model_parser(parse)
        index = None

        for j in range(0,len(parsing)):
            if parsing[j].name == self._datas['Model name']:
                index = j
                break

        if index is None:
            f.close()
            with self._out:
                raise Exception('Critical error : model not found.')
        
        return docGenerator.DocGenerator(parsing[index])



    def _createInit(self):   
        """
        Creates an empty init file with the model description inside of it
        """

        try:
            init = open("{0}{2}algo{2}pyx{2}init.{1}.pyx".format(self._datas['Path'], self._datas['Model name'], os.path.sep), 'w', encoding='utf8')

        except IOError as ioerr:
            with self._out:
                raise Exception("Initialization file init.{}.pyx could not be created. {}".format(self._datas['Model name'], ioerr))

        else:     
            doc = self._getDoc(init)

            init.write(doc.desc)
            init.write('\n{}'.format(doc.inputs_doc))
            init.write('\n{}'.format(doc.outputs_doc))

            init.close()



    def _createAlgo(self):
        """
        Creates the algorithm file with the model description inside of it
        """

        try:
            algo = open("{0}{2}algo{2}pyx{2}{1}.pyx".format(self._datas['Path'], self._datas['Model name'], os.path.sep), 'w', encoding='utf8')

        except IOError as ioerr:
            with self._out:
                raise Exception("Algorithm file {}.pyx could not be created. {}".format(self._datas['Model name'], ioerr))

        else:
            doc = self._getDoc(algo)

            algo.write(doc.desc)
            algo.write('\n{}'.format(doc.inputs_doc))
            algo.write('\n{}'.format(doc.outputs_doc))

            algo.close()



    def _write(self):
        """
        Saves all gathered datas in an xml format
        """

        try:
            if self._change_algo:
                open("{0}{2}algo{2}pyx{2}{1}.pyx".format(self._datas['Path'], self._datas['Model name'], os.path.sep), 'w', encoding='utf8').close()
            if self._change_init:
                open("{0}{2}algo{2}pyx{2}init.{1}.pyx".format(self._datas['Path'], self._datas['Model name'], os.path.sep), 'w', encoding='utf8').close()
        except IOError as ioerr:
            with self._out:
                raise Exception(ioerr)

        
        split = self._datas['Path'].split(os.path.sep)
        buffer = ''

        buffer += '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Model PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelUnit.dtd">\n'
        buffer += '<ModelUnit modelid="{0}.{1}.{2}" name="{2}" timestep="{3}" version="{4}">'.format(self._datas['Model ID'],split[-2],self._datas['Model name'],self._datas['Timestep'], self._datas['Version'])
        buffer += '\n\t<Description>\n\t\t<Title>{}</Title>'.format(self._datas['Title'])
        buffer += '\n\t\t<Authors>{}</Authors>'.format(self._datas['Authors'])
        buffer += '\n\t\t<Institution>{}</Institution>'.format(self._datas['Institution'])
        buffer += '\n\t\t<Reference>{}</Reference>'.format(self._datas['Reference'])
        buffer += '\n\t\t<Abstract>{}</Abstract>'.format(self._datas['Abstract'])+'\n\t</Description>'
        buffer += '\n\n\t<Inputs>'

        for i in range(0,len(self._df['Inputs']['Name'])):
            if any([not self._iscreate,
                    self._iscreate and self._df['Inputs']['Type'][i] == 'input',
                    self._iscreate and self._df['Inputs']['Type'][i] == 'input & output']):

                if self._df['Inputs']['InputType'][i] == 'variable':
                    if self._df['Inputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                        buffer += '\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" len="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Len'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i])
                    else:
                        buffer += '\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i])
            
                else:
                    if self._df['Inputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                        buffer += '\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" len="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Len'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i])
                    else:
                        buffer += '\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i])
    
        buffer += '\n\t</Inputs>\n\n\t<Outputs>'

        if self._iscreate:
            for i in range(0,len(self._df['Inputs']['Name'])):
                if any([self._df['Inputs']['Type'][i] == 'output',
                        self._df['Inputs']['Type'][i] == 'input & output']):

                    if self._df['Inputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                        buffer += '\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" len="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Len'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i])
                    else:
                        buffer += '\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i])

        else:
            for i in range(0,len(self._df['Outputs']['Name'])):

                if self._df['Outputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                    buffer += '\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" len="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Outputs']['Name'][i],self._df['Outputs']['Description'][i],self._df['Outputs']['Category'][i],self._df['Outputs']['DataType'][i],self._df['Outputs']['Len'][i],self._df['Outputs']['Min'][i],self._df['Outputs']['Max'][i],self._df['Outputs']['Unit'][i],self._df['Outputs']['Uri'][i])
                else:
                    buffer += '\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Outputs']['Name'][i],self._df['Outputs']['Description'][i],self._df['Outputs']['Category'][i],self._df['Outputs']['DataType'][i],self._df['Outputs']['Min'][i],self._df['Outputs']['Max'][i],self._df['Outputs']['Unit'][i],self._df['Outputs']['Uri'][i])

        buffer += '\n\t</Outputs>\n'

        if self._df['Functions']:
            for i,j in self._df['Functions'].items():
                buffer += '\n\t<Function name="{}" language="Cyml" filename="{}" type="{}" description="" />'.format(i.split('.')[0].split('/')[-1], i, j)
        
        buffer += '\n\n\t<Algorithm language="Cyml" platform="" filename="algo/pyx/{}.pyx" />'.format(self._datas['Model name'])
        buffer += '\n\n\t<Initialization name="init.{0}" language="Cyml" filename="algo/pyx/init.{0}.pyx" description="" />'.format(self._datas['Model name'])
        buffer += '\n\n\t<Parametersets>'

        for name, args in self._paramsetdict.items():
            buffer += '\n\t\t<Parameterset name="{}" description="{}" >'.format(name, args[1])
                
            for k,v in args[0].items():                        
                buffer += '\n\t\t\t<Param name="{}">{}</Param>'.format(k, v)
                
            buffer += '\n\t\t</Parameterset>'
        buffer += '\n\t</Parametersets>\n\n\t<Testsets>'

        for testsetname, args in self._testsetdict.items():
            buffer += '\n\n\t\t<Testset name="{}" parameterset="{}" description="{}" >'.format(testsetname, args[2], args[1])
                
            for testname, data in args[0].items():
                buffer += '\n\t\t\t<Test name="{}" >'.format(testname)
                    
                for k,v in data['inputs'].items():
                    buffer += '\n\t\t\t\t<InputValue name="{}">{}</InputValue>'.format(k,v)
                    
                for k,v in data['outputs'].items():
                    buffer += '\n\t\t\t\t\t<OutputValue name="{}" precision="{}">{}</OutputValue>'.format(k,v[1],v[0])
                
                buffer += '\n\t\t\t</Test>'
            buffer += '\n\t\t</Testset>'    
        buffer += '\n\n\t</Testsets>\n\n</ModelUnit>'
        
        try:
            with open("{}/unit.{}.xml".format(self._datas['Path'], self._datas['Model name']), 'w', encoding='utf8') as f:
                f.write(buffer)
        except IOError as ioerr:
            with self._out:
                raise Exception('File unit.{}.xml could not be opened. {}'.format(self._datas['Model name'], ioerr))


        if self._change_init:
            self._createInit()
        
        if self._change_algo:
            self._createAlgo()

        if not self._iscreate and self._datas['Model name'] != self._datas['Old name']:
            os.remove('{}{}unit.{}.xml'.format(self._datas['Path'], os.path.sep, self._datas['Old name']))
            os.remove('{0}{1}algo{1}pyx{1}init.{2}.pyx'.format(self._datas['Path'], os.path.sep, self._datas['Old name']))
            os.remove('{0}{1}algo{1}pyx{1}{2}.pyx'.format(self._datas['Path'], os.path.sep, self._datas['Old name']))



    def displayMenu(self):
        """
        Displays the unit model xml edition menu for Pycrop2ml's UI.

        This method is the only one available for the user in this class. Any other attribute or
        method call may break the code.
        """
    
        if not self._iscreate and self._datas['Model name'] == self._datas['Old name']:
            
            _titlemenu = wg.HTML(value='<font size="5"><b>Model edition : File update</b></font>')
            _toggle_init = wg.ToggleButtons(options=["Yes", "No"], value='No', description="Do you want to change the initialization file ?", disabled=False)
            _toggle_algo = wg.ToggleButtons(options=["Yes", "No"], value='No', description="Do you want to change the algorithm file ?", disabled=False)
            _apply = wg.Button(value=False,description='Apply',disabled=False,button_style='success')
            
            display(self._out)
            with self._out:
                display(wg.VBox([_titlemenu, _toggle_init, _toggle_algo, _apply], layout=wg.Layout(align_items='center')))
            
            def _eventApply(b):
                self._out.clear_output()
                self._change_init = True if _toggle_init.value == 'Yes' else False
                self._change_algo = True if _toggle_algo.value == 'Yes' else False
                self._write()
            
            _apply.on_click(_eventApply)

        else:
            self._write()
