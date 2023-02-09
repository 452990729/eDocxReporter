import os
import sys
import time
from copy import deepcopy
import pandas as pd

BasePath = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(BasePath)
sys.path.append(BasePath+"/../")

import utils
import YamlHandle

class ReportYamlMaker(object):
    
    def __init__(self, *args, **kwargs):
        self.chrConfig = utils.MakeAmplicanChr(kwargs['chrConfig'])
        self.config = YamlHandle.MakeDictFromYaml(kwargs['config'])
        self.sampleSheet = pd.read_csv(kwargs['sampleSheet'], sep='\t', header=0, index_col=None)
        self.qcStandards = YamlHandle.MakeDictFromYaml(kwargs['qcStandardsConfig'])
        self.resultPath = kwargs['resultPath']
        self.sampleQuilityStat = pd.read_csv(self.resultPath+'/9.FINALSTAT/SampleQuilityStat.tsv', sep='\t', header=0, index_col=None)
        self.sampleFinalEditRateStat = pd.read_csv(self.resultPath+'/9.FINALSTAT/SampleFinalEditRateStat.tsv', sep='\t', header=0, index_col=None)
        self.outpath = kwargs['outpath']
        if not os.path.exists(self.outpath):
            os.mkdir(self.outpath)
    
    def GenerateYaml(self):
        dict_config = self.__makeGeneralConfig()
        YamlHandle.MakeYamlFromDict(dict_config, os.path.join(self.outpath, 'clinicalReport.yaml'))
    
    def __makeGeneralConfig(self):
        dict_out = {}
        imagePath = os.path.join(self.outpath, 'images')
        if not os.path.exists(imagePath):
            os.mkdir(imagePath)
        
        DNAInfor = utils.GetDNAInfor(self.sampleSheet, self.qcStandards)
        LibraryInfor = utils.GetLibraryInfor(self.sampleSheet, self.qcStandards) 
        SequencingInfor = utils.GetSequencingInfor(self.sampleQuilityStat, self.sampleFinalEditRateStat, self.qcStandards)
        IndelInfor = utils.GetIndelList(self.sampleFinalEditRateStat, self.sampleSheet, self.chrConfig, False) + \
            utils.GetIndelList(self.sampleFinalEditRateStat, self.sampleSheet, self.chrConfig, True)
        DepthPics = utils.MakeDepthPlot(self.sampleFinalEditRateStat, imagePath)
        BaseQualityPics = utils.MakeBaseQulityPlot(self.sampleQuilityStat, self.resultPath, imagePath)
        TargetEditRate,TargetResult,OffTagetResult,TargetList,OffTargetList = self.__getEditRate(IndelInfor)
        BioQC = utils.GetBioQC(DNAInfor[0], LibraryInfor[0], SequencingInfor[0])
        dict_out['ProjectType'] = {
            'type': 'richtext',
            'name': 'ProjectType',
            'value': self.config['ProjectType'],
            'color': '#0070C0',
            'bold': 'false'
        }
        dict_out['PatientNumber'] = {
            'type': 'string',
            'name': 'PatientNumber',
            'value': self.config['PatientNumber'],
        }
        dict_out['SampleNumber'] = {
            'type': 'string',
            'name': 'SampleNumber',
            'value': self.config['SampleNumber'],
        }
        dict_out['SampleType'] = {
            'type': 'string',
            'name': 'SampleType',
            'value': self.config['SampleType'],
        }
        dict_out['ResearchInst'] = {
            'type': 'string',
            'name': 'ResearchInst',
            'value': self.config['ResearchInst'],
        }
        dict_out['SampleCollectDate'] = {
            'type': 'string',
            'name': 'SampleCollectDate',
            'value': self.config['SampleCollectDate'],
        }
        dict_out['SampleReciveDate'] = {
            'type': 'string',
            'name': 'SampleReciveDate',
            'value': self.config['SampleReciveDate'],
        }
        dict_out['ProjectDate'] = {
            'type': 'string',
            'name': 'ProjectDate',
            'value': time.strftime("%Y-%m-%d", time.localtime()),
        }
    
        dict_out['TargetResult'] = {
            'type': 'string',
            'name': 'TargetResult',
            'value': TargetResult,
        }
        dict_out['TargetEditRate'] = {
            'type': 'string',
            'name': 'TargetEditRate',
            'value': TargetEditRate,
        }
        dict_out['OffTagetResult'] = {
            'type': 'string',
            'name': 'OffTagetResult',
            'value': OffTagetResult,
        }
        dict_out['TargetList'] = {
                'type': 'list',
                'name': 'TargetList',
                'value': self.__generateYamlFromStringList(TargetList)
                }
        dict_out['OffTargetList'] = {
                'type': 'list',
                'name': 'OffTargetList',
                'value': self.__generateYamlFromStringList(OffTargetList)
                }
        
        dict_out['DNAInfor'] = {
                'type': 'list',
                'name': 'DNAInfor',
                'value': self.__generateYamlFromStringList(DNAInfor)
                }
        dict_out['LibraryInfor'] = {
                'type': 'list',
                'name': 'LibraryInfor',
                'value': self.__generateYamlFromStringList(LibraryInfor)
                }
        dict_out['SequencingInfor'] = {
                'type': 'list',
                'name': 'SequencingInfor',
                'value': self.__generateYamlFromStringList(SequencingInfor)
                }
        
        dict_out['BioQC'] = {
            'type': 'string',
            'name': 'BioQC',
            'value': BioQC,
        }
        
        dict_out['DepthPics'] = {
                'type': 'list',
                'name': 'DepthPics',
                'value': [
                    {
                'type': 'image',
                'name': 'image',
                'value': i,
                'width': 160,
                'height': 106
            } for i in DepthPics
                ]
        }
        dict_out['BaseQualityPics'] = {
                'type': 'list',
                'name': 'BaseQualityPics',
                'value': [
                    {
                'type': 'image',
                'name': 'image',
                'value': i,
                'width': 160,
                'height': 106
            } for i in BaseQualityPics
                ]
        }
        
        dict_out['Full'] = {
            'type': 'string',
            'name': 'Full',
            'value': True,
        }
        
        return dict_out
    
    def __getEditRate(self, IndelInfor):
        TargetEditRate = 0
        OffTagetResult = 0
        TargetResult = ''
        TargetList = []
        OffTargetList = []
        for i in IndelInfor:
            if i['Amplicon'] == 'EDI_22N':
                TargetEditRate = i['Rate']
                if TargetEditRate >= 2:
                    TargetResult = '有效编辑'
                else:
                    TargetResult = '无效编辑'
                TargetList.append(i)
            else:
                if i['Rate'] > 1:
                    OffTagetResult += 1
                OffTargetList.append(i)
        return TargetEditRate,TargetResult,OffTagetResult,TargetList,OffTargetList
    
    def __generateYamlFromStringList(self, list_in):
        list_out = []
        for dict_o in list_in:
            list_tmp = []
            for key in dict_o:
                list_tmp.append({
                    'type': 'string',
                    'name': key,
                    'value': dict_o[key]
                })
            list_out.append(list_tmp)
        return list_out