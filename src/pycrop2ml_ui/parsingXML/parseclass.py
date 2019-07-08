
class Description():

    def __init__(self):

        self.title = ''
        self.authors = ''
        self.institution = ''
        self.reference = ''
        self.abstract = ''


class Input():

    def __init__(self):

        self.name = ''
        self.description = ''
        self.inputtype = ''
        self.datatype = ''
        self.category = ''
        self.default = ''
        self.mini = ''
        self.maxi = ''
        self.unit = ''
        self.uri = ''


class Inputs():

    def __init__(self):

        self.dictinput = []



class Output(Input):

    def __init__(self):

        super().__init__()


class Outputs():

    def __init__(self):

        self.dictoutput = []


class Algorithm():

    def __init__(self):

        self.language = ''
        self.platform = ''
        self.algo = ''


class Param():

    def __init__(self):

        self.name = ''
        self.value = ''


class Parameterset():

    def __init__(self):

        self.name = ''
        self.description = ''
        self.listparam = []


class ParametersSet():

    def __init__(self):

        self.listParameterset = []


class InputTest():

    def __init__(self):

        self.name = ''
        self.value = ''


class OutputTest(InputTest):

    def __init__(self):

        super().__init__()


class Test():

    def __init__(self):

        self.name = ''
        self.listInput = []
        self.listOutput = []


class Testset():

    def __init__(self):

        self.name = ''
        self.paramset = ''
        self.description = ''
        self.listTest = []


class TestSets():

    def __init__(self):

        self.listTestset = []







