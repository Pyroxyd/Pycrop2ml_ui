import os
import re

from pycrop2ml_ui.parsingXML import parseclass


class fileXML():

    def __init__(self, fileToParse):

        self.description = parseclass.Description()
        self.inputs = parseclass.Inputs()
        self.outputs = parseclass.Outputs()
        self.algorithm = parseclass.Algorithm()
        self.parametersSet = parseclass.ParametersSet()
        self.testsets = parseclass.TestSets()

        self.file = fileToParse

    
    def fileOpen(self):

        try:
            self.file = open(self.file, 'r')
        
        except IOError as ioerr:
            raise Exception('Could not open file {}. {}'.format(self.file, ioerr))
        
        finally:
            del self

    
    def fileClose(self):

        self.file.close()

    
    def badSyntax(self):

        try:
            raise Exception('File {} has a bad syntax critical error.'.format(self.file))
        
        finally:
            self.fileClose()
            del self



    def parseHeader(self):

        buffer = self.file.readline()
            
        while not re.search(r'(</Description>)', buffer):

            title = re.search(r'<Title>(.*?)</Title>', buffer)
            authors = re.search(r'<Authors>(.*?)</Authors>', buffer)
            institution = re.search(r'<Institution>(.*?)</Institution>', buffer)
            reference = re.search(r'<Reference>(.*?)</Reference>', buffer)
            abstract = re.search(r'<Abstract>(.*?)</Abstract>', buffer)

            if title:
                if not self.description.title:
                    self.description.title = title.group(1)
                else:
                    self.badSyntax()

            if authors:
                if not self.description.authors:
                    self.description.authors = authors.group(1)
                else:
                    self.badSyntax()

            if institution:
                if not self.description.institution:
                    self.description.institution = institution.group(1)
                else:
                    self.badSyntax()
                
            if reference:
                if not self.description.reference:
                    self.description.reference = reference.group(1)
                else:
                    self.badSyntax()

            if abstract:
                if not self.description.abstract:
                    self.description.abstract = abstract.group(1)
                else:
                    self.badSyntax()
            
            buffer = self.file.readline()

            if not buffer:
                self.badSyntax()


        if any([not self.description.title, not self.description.authors, not self.description.institution, not self.description.reference, not self.description.abstract]):

            self.badSyntax()

    
    def parseInputs(self):

        buffer = self.file.readline()

        while not re.search(r'(</Inputs>)', buffer):

            if re.search(r'(<Input )', buffer):
                
                self.inputs.dictinput.append(parseclass.Input())

                name = re.search(r'name="(.*?)"', buffer)
                description = re.search(r'description="(.*?)"', buffer)
                inputtype = re.search(r'inputtype="(.*?)"', buffer)
                category = re.search(r'category="(.*?)"', buffer)
                datatype = re.search(r'datatype="(.*?)"', buffer)            
                default = re.search(r'default="(.*?)"', buffer)
                mini = re.search(r'min="(.*?)"', buffer)
                maxi = re.search(r'max="(.*?)"', buffer)
                unit = re.search(r'unit="(.*?)"', buffer)
                uri = re.search(r'uri="(.*?)"', buffer)

                if any([not name, not description, not inputtype, not datatype, not category, not unit]):

                    self.badSyntax()
                
                else:

                    listeMatch = [name,description,inputtype,datatype,category,default,mini,maxi,unit,uri]
                    listeName = ['name','description','inputtype','datatype','category','default','mini','maxi','unit','uri']

                    for i in range(0, len(listeMatch)):

                        if listeMatch[i]:
                            setattr(self.inputs.dictinput[-1], listeName[i], listeMatch[i].group(1))
          

            buffer = self.file.readline()

            if not buffer:
                self.badSyntax()
        


    def parseOutputs(self):

        buffer = self.file.readline()

        while not re.search(r'(</Outputs>)', buffer):

            if re.search(r'(<Output )', buffer):
                
                self.outputs.dictoutput.append(parseclass.Output())

                name = re.search(r'name="(.*?)"', buffer)
                description = re.search(r'description="(.*?)"', buffer)
                inputtype = re.search(r'inputtype="(.*?)"', buffer)
                datatype = re.search(r'datatype="(.*?)"', buffer)
                category = re.search(r'category="(.*?)"', buffer)
                default = re.search(r'default="(.*?)"', buffer)
                mini = re.search(r'min="(.*?)"', buffer)
                maxi = re.search(r'max="(.*?)"', buffer)
                unit = re.search(r'unit="(.*?)"', buffer)
                uri = re.search(r'uri="(.*?)"', buffer)

                if any([not name, not description, not inputtype, not datatype, not category, not unit]):

                    self.badSyntax()
                
                else:
                    listeMatch = [name,description,inputtype,datatype,category,default,mini,maxi,unit,uri]
                    listeName = ['name','description','inputtype','datatype','category','default','mini','maxi','unit','uri']

                    for i in range(0, len(listeMatch)):

                        if listeMatch[i]:
                            setattr(self.outputs.dictoutput[-1], listeName[i], listeMatch[i].group(1))
          

            buffer = self.file.readline()

            if not buffer:
                self.badSyntax()
        
                
    def parseAlgorithm(self):

        buffer = self.file.readline()

        while True:

            if re.search(r'(<Algorithm)', buffer):

                language = re.search(r'language="(.*?)"', buffer)
                platform = re.search(r'platform="(.*?)"', buffer)
                algo = re.search(r'filename="(.*?)"', buffer)

                listeMatch = [language,platform,algo]
                listeName = ['language','platform','algo']

                for i in range(0, len(listeMatch)):

                    if listeMatch[i]:
                        setattr(self.algorithm, listeName[i], listeMatch[i].group(1))
                
                break

            else:
                buffer = self.file.readline()

                if not buffer:
                    self.badSyntax()
                    break



    def parseParametersets(self):
        
        buffer = self.file.readline()

        while not re.search(r'(</Parametersets>)', buffer):

            if re.search(r'(<Parameterset )', buffer):

                self.parametersSet.listParameterset.append(parseclass.Parameterset())

                name = re.search(r'name="(.*?)"', buffer)
                description = re.search(r'description="(.*?)"', buffer)

                if name and description:

                    setattr(self.parametersSet.listParameterset[-1], format(name), name.group(1))
                    setattr(self.parametersSet.listParameterset[-1], format(description), description.group(1))

                    buffer = self.file.readline()

                    while not re.search(r'(</Parameterset>)', buffer):

                        args = re.search(r'<Param name="(.*?)">(.*?)</Param>', buffer)

                        if args:

                            self.parametersSet.listParameterset[-1].listparam.append(parseclass.Param())
                            self.parametersSet.listParameterset[-1].listparam[-1].name = args.group(1)
                            self.parametersSet.listParameterset[-1].listparam[-1].value = args.group(2)

                        else:
                            self.badSyntax()
                        
                        buffer = self.file.readline()

                else:
                    self.badSyntax()


            buffer = self.file.readline()
            
            if not buffer:
                self.badSyntax()


    
    def parseTestsets(self):
        
        buffer = self.file.readline()

        while not re.search(r'(</Testsets>)', buffer):

            if re.search(r'<Testset ', buffer):

                self.testsets.listTestset.append(parseclass.Testset())

                args = re.search(r'name="(.*?)" parameterset="(.*?)" description="(.*?)"', buffer)

                if args:

                    self.testsets.listTestset[-1].name = args.group(1)
                    self.testsets.listTestset[-1].paramset = args.group(2)
                    self.testsets.listTestset[-1].description = args.group(3)

                    buffer = self.file.readline()

                    while not re.search(r'(</Testset>)', buffer):

                        test = re.search(r'name="(.*?)"', buffer)

                        if test:

                            self.testsets.listTestset[-1].listTest.append(parseclass.Test())
                            self.testsets.listTestset[-1].listTest[-1].name = test.group(1)

                            buffer = self.file.readline()

                            while not re.search(r'(</Test>)', buffer):

                                inval = re.search(r'<InputValue name="(.*?)">(.*?)</InputValue>', buffer)
                                outval = re.search(r'<OutputValue name="(.*?)">(.*?)</OutputValue>', buffer)

                                if inval:
                                    self.testsets.listTestset[-1].listTest[-1].listInput.append(parseclass.InputTest())
                                    self.testsets.listTestset[-1].listTest[-1].listInput[-1].name = inval.group(1)
                                    self.testsets.listTestset[-1].listTest[-1].listInput[-1].value = inval.group(2)

                                elif outval:
                                    self.testsets.listTestset[-1].listTest[-1].listOutput.append(parseclass.OutputTest())
                                    self.testsets.listTestset[-1].listTest[-1].listOutput[-1].name = outval.group(1)
                                    self.testsets.listTestset[-1].listTest[-1].listOutput[-1].value = outval.group(2)
                                
                                else:
                                    self.badSyntax()

                                buffer = self.file.readline()

                        else:
                            self.badSyntax()

                        buffer = self.file.readline()
                            
                
                else:
                     self.badSyntax()
            
            buffer = self.file.readline()

                


    def mainParse(self):

        self.fileOpen()

        self.parseHeader()
        self.parseInputs()
        self.parseOutputs()
        self.parseAlgorithm()
        self.parseParametersets()
        self.parseTestsets()

        self.fileClose()

        
            
