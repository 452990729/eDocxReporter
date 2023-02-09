import argparse

class CustomArgs(object):
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="make docx report")
        self.subparsers = self.parser.add_subparsers(help='sub-command help')
    
    def add_efalconampcmc(self, function):
        cus_parser = self.subparsers.add_parser('eFalconAMPCMC', help='make docx report for eFalconAMPCMC')
        cus_parser.set_defaults(func=function)
        cus_parser.add_argument('-chrConfig', help='chr config file [/OPT/Pipeline/eDocxReporter/docs/eFalconAMPAmplicanChr.txt]', default='/OPT/Pipeline/eDocxReporter/docs/eFalconAMPAmplicanChr.txt')
        cus_parser.add_argument('-config', help='input user defined config', required=True)
        cus_parser.add_argument('-sampleSheet', help='Sample data table', required=True)
        cus_parser.add_argument('-qcStandardsConfig', help='qc standards config file [/OPT/Pipeline/eDocxReporter/docs/eFalconAMPQC.yaml]', default='/OPT/Pipeline/eDocxReporter/docs/eFalconAMPQC.yaml')
        cus_parser.add_argument('-docxTemplate', help='docx template [/OPT/Pipeline/eDocxReporter/docs/eFalconAMPCMC.docx]', default='/OPT/Pipeline/eDocxReporter/docs/eFalconAMPCMC.docx')
        cus_parser.add_argument('-resultPath', help='eFalconAMP result root path', required=True)
        cus_parser.add_argument('-full', help='whether generate full docx', action='store_true')
        cus_parser.add_argument('-outpath', help='outfile path [./]', default='./')
    
    def add_efalconampclinical(self, function):
        cus_parser = self.subparsers.add_parser('eFalconAMPClinical', help='make docx report for eFalconAMPCMC')
        cus_parser.set_defaults(func=function)
        cus_parser.add_argument('-chrConfig', help='chr config file [/OPT/Pipeline/eDocxReporter/docs/eFalconAMPAmplicanChr.txt]', default='/OPT/Pipeline/eDocxReporter/docs/eFalconAMPAmplicanChr.txt')
        cus_parser.add_argument('-config', help='input user defined config', required=True)
        cus_parser.add_argument('-sampleSheet', help='Sample data table', required=True)
        cus_parser.add_argument('-qcStandardsConfig', help='qc standards config file [/OPT/Pipeline/eDocxReporter/docs/eFalconAMPQC.yaml]', default='/OPT/Pipeline/eDocxReporter/docs/eFalconAMPQC.yaml')
        cus_parser.add_argument('-docxTemplate', help='docx template [/OPT/Pipeline/eDocxReporter/docs/eFalconAMPClinical.docx]', default='/OPT/Pipeline/eDocxReporter/docs/eFalconAMPClinical.docx')
        cus_parser.add_argument('-resultPath', help='eFalconAMP result root path', required=True)
        cus_parser.add_argument('-outpath', help='outfile path [./]', default='./')