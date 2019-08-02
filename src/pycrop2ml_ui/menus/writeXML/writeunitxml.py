import re
import os

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
                    'Authors': '',
                    'Institution': '',
                    'Reference': '',
                    'Abstract': '',
                    'Old name':'' IF iscreate=False
                   }

        - df : {'Inputs' : pandas.DataFrame,
                'Algorithms' : [],
                'Functions' : [],
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
        
        self._datas = datas
        self._df = df
        self._paramsetdict = paramsetdict
        self._testsetdict = testsetdict
        self._iscreate = iscreate



    def _getDoc(self, f):

        """
        Returns the documentation of the current's model xml file
        """

        split = re.split(r'\\', self._datas['Path'])

        parse = ''
        for i in split[:-1]:
            parse += i + r'\\'

        parsing = model_parser(parse)
        index = None

        for j in range(0,len(parsing)):
            if parsing[j].name == self._datas['Model name']:
                index = j
                break

        if index is None:
            f.close()

            raise Exception('Critical error : model not found.')
        
        return docGenerator.DocGenerator(parsing[index])



    def _createInit(self):
        
        """
        Creates an empty init file with the model description inside of it
        """

        try:
            init = open("{}\\algo\\pyx\\init.{}.pyx".format(self._datas['Path'], self._datas['Model name']), 'w', encoding='utf8')

        except IOError as ioerr:
            raise Exception("Algorithm file init.{}.pyx could not be created. {}".format(self._datas['Model name'], ioerr))

        else:            
            doc = self._getDoc(init)

            init.write(doc.desc)
            init.write('\n{}'.format(doc.inputs_doc))
            init.write('\n{}'.format(doc.outputs_doc))

            init.close()



    def _createAlgo(self):

        """
        Creates an empty algorithm file with the model description inside of it
        """

        try:
            algo = open("{}\\algo\\pyx\\{}.pyx".format(self._datas['Path'], self._datas['Model name']), 'w', encoding='utf8')

        except IOError as ioerr:
            raise Exception("Algorithm file {}.pyx could not be created. {}".format(self._datas['Model name'], ioerr))

        else:
            doc = self._getDoc(algo)

            algo.write(doc.desc)
            algo.write('\n{}'.format(doc.inputs_doc))
            algo.write('\n{}'.format(doc.outputs_doc))

            algo.close()



    def write(self):

        """
        Saves all gathered datas in an xml format
        """

        try:
            f = open("{}/unit.{}.xml".format(self._datas['Path'], self._datas['Model name']), 'w', encoding='utf8')

        except IOError as ioerr:
            raise Exception('File unit.{}.xml could not be opened. {}'.format(self._datas['Model name'], ioerr))

        else:
            split = []
            path = self._datas['Path']
            for i in range(4):
                split.append(os.path.split(path)[-1])
                path = os.path.split(path)[0]

            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE Model PUBLIC " " "https://raw.githubusercontent.com/AgriculturalModelExchangeInitiative/crop2ml/master/ModelUnit.dtd">\n')
            f.write('<ModelUnit modelid="{0}.{1}.{2}" name="{2}" timestep="1" version="1.0">'.format(split[3],split[1],self._datas['Model name']))
            f.write('\n\t<Description>\n\t\t<Title>{} Model</Title>'.format(self._datas['Model name'])+
                '\n\t\t<Authors>{}</Authors>'.format(self._datas['Authors'])+
                '\n\t\t<Institution>{}</Institution>'.format(self._datas['Institution'])+
                '\n\t\t<Reference>{}</Reference>'.format(self._datas['Reference'])+
                '\n\t\t<Abstract>{}</Abstract>'.format(self._datas['Abstract'])+'\n\t</Description>')

            f.write('\n\n\t<Inputs>')

            for i in range(0,len(self._df['Inputs']['Name'])):
                if any([not self._iscreate,
                        self._iscreate and self._df['Inputs']['Type'][i] == 'input',
                        self._iscreate and self._df['Inputs']['Type'][i] == 'input & output']):

                    if self._df['Inputs']['InputType'][i] == 'variable':
                        if self._df['Inputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" len="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Len'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i]))
                        else:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" variablecategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i]))
                
                    else:
                        if self._df['Inputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" len="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Len'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i]))
                        else:
                            f.write('\n\t\t<Input name="{}" description="{}" inputtype="{}" parametercategory="{}" datatype="{}" default="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['InputType'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Default'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i]))
        
            f.write('\n\t</Inputs>\n')

            f.write('\n\t<Outputs>')

            if self._iscreate:
                for i in range(0,len(self._df['Inputs']['Name'])):
                    if any([self._df['Inputs']['Type'][i] == 'output',
                            self._df['Inputs']['Type'][i] == 'input & output']):

                        if self._df['Inputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                            f.write('\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" len="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Len'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i]))
                        else:
                            f.write('\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Inputs']['Name'][i],self._df['Inputs']['Description'][i],self._df['Inputs']['Category'][i],self._df['Inputs']['DataType'][i],self._df['Inputs']['Min'][i],self._df['Inputs']['Max'][i],self._df['Inputs']['Unit'][i],self._df['Inputs']['Uri'][i]))

            else:
                for i in range(0,len(self._df['Outputs']['Name'])):

                    if self._df['Outputs']['DataType'][i] in ['STRINGARRAY','DATARRAY','INTARRAY','DOUBLEARRAY']:
                        f.write('\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" len="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Outputs']['Name'][i],self._df['Outputs']['Description'][i],self._df['Outputs']['Category'][i],self._df['Outputs']['DataType'][i],self._df['Outputs']['Len'][i],self._df['Outputs']['Min'][i],self._df['Outputs']['Max'][i],self._df['Outputs']['Unit'][i],self._df['Outputs']['Uri'][i]))
                    else:
                        f.write('\n\t\t<Output name="{}" description="{}" variablecategory="{}" datatype="{}" min="{}" max="{}" unit="{}" uri="{}"/>'.format(self._df['Outputs']['Name'][i],self._df['Outputs']['Description'][i],self._df['Outputs']['Category'][i],self._df['Outputs']['DataType'][i],self._df['Outputs']['Min'][i],self._df['Outputs']['Max'][i],self._df['Outputs']['Unit'][i],self._df['Outputs']['Uri'][i]))

            f.write('\n\t</Outputs>\n')

            if self._df['Functions']:
                for i in self._df['Functions']:
                    f.write('\n\t<Function name="{}" language="Cyml" filename="{}" type="" description="" />'.format(i.split('.')[0].split('/')[-1], i))
            
            createalgo = False
            if self._df['Algorithms']:
                f.write('\n')
                for i in self._df['Algorithms']:
                    f.write('\n\t<Algorithm language="Cyml" platform="" filename="{}" />'.format(i))
            else:
                createalgo = True
                f.write('\n\n\t<Algorithm language="Cyml" platform="" filename="algo/pyx/{}.pyx" />'.format(self._datas['Model name']))
            
            f.write('\n\n\t<Initialization name="init.{0}" language="Cyml" filename="algo/pyx/init.{0}.pyx" description="" />'.format(self._datas['Model name']))

            f.write('\n\n\t<Parametersets>')

            for name, args in self._paramsetdict.items():
                f.write('\n\t\t<Parameterset name="{}" description="{}" >'.format(name, args[1]))
                    
                for k,v in args[0].items():                        
                    f.write('\n\t\t\t<Param name="{}">{}</Param>'.format(k, v))
                    
                f.write('\n\t\t</Parameterset>')
            f.write('\n\t</Parametersets>')

            f.write('\n\n\t<Testsets>')
            for testsetname, args in self._testsetdict.items():
                f.write('\n\n\t\t<Testset name="{}" parameterset="{}" description="{}" >'.format(testsetname, args[2], args[1]))
                    
                for testname, data in args[0].items():
                    f.write('\n\t\t\t<Test name="{}" >'.format(testname))
                        
                    for k,v in data['inputs'].items():
                        f.write('\n\t\t\t\t<InputValue name="{}">{}</InputValue>'.format(k,v))
                        
                    for k,v in data['outputs'].items():
                        f.write('\n\t\t\t\t\t<OutputValue name="{}" precision="{}">{}</OutputValue>'.format(k,v[1],v[0]))
                    
                    f.write('\n\t\t\t</Test>')
                f.write('\n\t\t</Testset>')        
            f.write('\n\n\t</Testsets>')
            f.write("\n\n</ModelUnit>")
            f.close()

            if 'init.{}.pyx'.format(self._datas['Model name']) not in os.listdir(self._datas['Path']+os.path.sep+'Algo'+os.path.sep+'pyx'):
                self._createInit()
            if createalgo:
                self._createAlgo()

            if not self._iscreate and self._datas['Model name'] != self._datas['Old name']:
                os.remove('{}{}unit.{}.xml'.format(self._datas['Path'], os.path.sep, self._datas['Old name']))
                os.remove('{0}{1}algo{1}pyx{1}init.{2}.pyx'.format(self._datas['Path'], os.path.sep, self._datas['Old name']))


