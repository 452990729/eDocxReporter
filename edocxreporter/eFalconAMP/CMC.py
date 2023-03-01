import os
import sys
import re
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
        self.outpath = kwargs['outpath']
        if not os.path.exists(self.outpath):
            os.mkdir(self.outpath)
        self.__handleResultPath()
        self.sampleQuilityStat = pd.read_csv(self.resultPath+'/9.FINALSTAT/SampleQuilityStat.tsv', sep='\t', header=0, index_col=None)
        self.sampleFinalEditRateStat = pd.read_csv(self.resultPath+'/9.FINALSTAT/SampleFinalEditRateStat.tsv', sep='\t', header=0, index_col=None)
        self.full = kwargs['full']
        dict_trans = {}
        dict_rtrans = {}
        for index in self.sampleSheet.index:
            dict_trans[self.sampleSheet.loc[index, 'SampleInnerId']] = self.sampleSheet.loc[index, 'SampleId']
            dict_rtrans[self.sampleSheet.loc[index, 'SampleId']] = self.sampleSheet.loc[index, 'SampleInnerId']
        self.sampleQuilityStat['Sample'] = [dict_trans[i] for i in self.sampleQuilityStat['Sample']]
        self.sampleFinalEditRateStat['Sample'] = [dict_trans[i] for i in self.sampleFinalEditRateStat['Sample']]
        self.dict_rtrans = dict_rtrans
    
    def GenerateYaml(self):
        dict_config_target = self.__makeGeneralConfig()
        dict_config_offtarget = deepcopy(dict_config_target)
        targetIndelList = self.__makeIndelConfig(True)
        offTargetIndelList = self.__makeIndelConfig(False)
        dict_config_target['IndelList'] =  {
                'type': 'list',
                'name': 'IndelList',
                'value': self.__generateYamlFromStringList(targetIndelList)
                }
        dict_config_target['TargetRegion'] = {
            'type': 'string',
            'name': 'TargetRegion',
            'value': 'true',
        }
        dict_config_offtarget['IndelList'] = {
                'type': 'list',
                'name': 'IndelList',
                'value': self.__generateYamlFromStringList(offTargetIndelList)
                }
        dict_config_target['TargetRegion'] = {
            'type': 'string',
            'name': 'TargetRegion',
            'value': 'false',
        }
        YamlHandle.MakeYamlFromDict(dict_config_target, os.path.join(self.outpath, 'targetReport.yaml'))
        YamlHandle.MakeYamlFromDict(dict_config_offtarget, os.path.join(self.outpath, 'offTargetReport.yaml'))
        
        
    def __makeGeneralConfig(self):
        dict_out = {}
        imagePath = os.path.join(self.outpath, 'images')
        if not os.path.exists(imagePath):
            os.mkdir(imagePath)
            
        SequencingInfor = utils.GetSequencingInfor(self.sampleQuilityStat, self.sampleFinalEditRateStat, self.qcStandards)
        DepthPics = utils.MakeDepthPlot(self.sampleFinalEditRateStat, imagePath)
        BaseQualityPics = utils.MakeBaseQulityPlot(self.sampleQuilityStat, self.resultPath, imagePath, self.dict_rtrans)
        
        dict_out['ProjectType'] = {
            'type': 'richtext',
            'name': 'ProjectType',
            'value': self.config['ProjectType'],
            'color': '#0070C0',
            'bold': 'false'
        }
        dict_out['ProjectSource'] = {
            'type': 'string',
            'name': 'ProjectSource',
            'value': self.config['ProjectSource'],
        }
        dict_out['ProjectBatch'] = {
            'type': 'string',
            'name': 'ProjectBatch',
            'value': self.config['ProjectBatch'],
        }
        dict_out['ProjectPeople'] = {
            'type': 'string',
            'name': 'ProjectPeople',
            'value': self.config['ProjectPeople'],
        }
        dict_out['ProjectDate'] = {
            'type': 'string',
            'name': 'ProjectDate',
            'value': time.strftime("%Y-%m-%d", time.localtime()),
        }
        dict_out['ProjectId'] = {
            'type': 'string',
            'name': 'ProjectId',
            'value': self.config['ProjectId'],
        }
        dict_out['Full'] = {
            'type': 'string',
            'name': 'Full',
            'value': self.full,
        }
        dict_out['SequencingInfor'] = {
                'type': 'list',
                'name': 'SequencingInfor',
                'value': self.__generateYamlFromStringList(SequencingInfor)
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

        if self.full:
            DNAInfor = utils.GetDNAInfor(self.sampleSheet, self.qcStandards)
            LibraryInfor = utils.GetLibraryInfor(self.sampleSheet, self.qcStandards)
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
            
        return dict_out
        
    def __makeIndelConfig(self, targetRegion):
        IndelList = utils.GetIndelList(self.sampleFinalEditRateStat, self.sampleSheet, self.chrConfig, targetRegion)
        return IndelList

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
    
    def __handleResultPath(self):
        list_split = re.split(',', self.resultPath.strip(','))
        if len(list_split) == 1:
            return
        else:
            tmpDir = os.path.join(self.outpath, 'tmp')
            qcPath = os.path.join(tmpDir, '2.QC')
            finalStatPath = os.path.join(tmpDir, '9.FINALSTAT')
            list_SampleFinalEditRateStat = []
            list_SampleQuilityStat = []
            os.system('mkdir -p {}'.format(qcPath))
            os.system('mkdir -p {}'.format(finalStatPath))
            for path in list_split:
                root, drs, files = next(os.walk(os.path.join(path, '2.QC')))
                for dr in drs:
                    os.system('ln -s {} {}'.format(os.path.join(root, dr), os.path.join(qcPath, dr)))
                list_SampleFinalEditRateStat.append(os.path.join(path, '9.FINALSTAT/SampleFinalEditRateStat.tsv'))
                list_SampleQuilityStat.append(os.path.join(path, '9.FINALSTAT/SampleQuilityStat.tsv'))
            self.__mergeFiles(list_SampleFinalEditRateStat, os.path.join(finalStatPath, 'SampleFinalEditRateStat.tsv'))
            self.__mergeFiles(list_SampleQuilityStat, os.path.join(finalStatPath, 'SampleQuilityStat.tsv'))
            self.resultPath = tmpDir
    
    def __mergeFiles(self, list_fl, outfile):
        pd_tmp = pd.read_csv(list_fl[0], sep='\t', header=0, index_col=None)
        out = pd.DataFrame(columns=list(pd_tmp.columns))
        m = 0
        for fl in list_fl:
            pd_data = pd.read_csv(fl, sep='\t', header=0, index_col=None)
            for index in pd_data.index:
                out.loc[m, :] = pd_data.loc[index, :]
                m += 1
        out.to_csv(outfile, sep='\t', header=True, index=False)
        
        