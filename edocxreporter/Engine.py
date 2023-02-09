import os
import sys

BasePath = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(BasePath)

from eFalconAMP import CMC
from eFalconAMP import Clinical
from ReportHandle import ReporterFromYaml
from YamlHandle import MakeDictFromYaml

def Engine(pipe, *args, **kwargs):
    if pipe == 'eFalconAMPForCMC':
        outpath = kwargs['outpath']
        ob = CMC.ReportYamlMaker(*args, **kwargs)
        ob.GenerateYaml()
        targetOb = ReporterFromYaml(**{
            'yaml': os.path.join(outpath, 'targetReport.yaml'),
            'docx_template': kwargs['docxTemplate'],
            'outfile': os.path.join(outpath, 'targetReport.docx')
            })
        offTargetOb = ReporterFromYaml(**{
            'yaml': os.path.join(outpath, 'offTargetReport.yaml'),
            'docx_template': kwargs['docxTemplate'],
            'outfile': os.path.join(outpath, 'offTargetReport.docx')
            })
        targetOb.MakeReporter()
        offTargetOb.MakeReporter()
    elif pipe == 'eFalconAMPForClinical':
        outpath = kwargs['outpath']
        ob = Clinical.ReportYamlMaker(*args, **kwargs)
        ob.GenerateYaml()
        Ob = ReporterFromYaml(**{
            'yaml': os.path.join(outpath, 'clinicalReport.yaml'),
            'docx_template': kwargs['docxTemplate'],
            'outfile': os.path.join(outpath, 'clinicalReport.docx')
            })
        Ob.MakeReporter()