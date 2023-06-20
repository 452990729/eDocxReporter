import os
import re
import sys
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
from matplotlib import pyplot as plt
from copy import deepcopy

BasePath = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(BasePath)
sys.path.append(BasePath+"/../")

from YamlHandle import MakeDictFromYaml

def MakeAmplicanChr(file_in):
    dict_chr = {}
    with open(file_in, 'r') as f:
        for line in f:
            list_split = re.split('\t', line.strip())
            dict_chr[list_split[0]] = list_split[1]
    return dict_chr

def MakeQCStandards(file_in):
    dict_out = MakeDictFromYaml(file_in)
    return dict_out
    

def GetIndelList(pd_data, pd_sample, dict_chr, TargetRegion):
    list_tmp = []
    if TargetRegion:
        pd_tmp = pd_data[pd_data['Amplicon']=='EDI_22N']
    else:
        pd_tmp = pd_data[pd_data['Amplicon']!='EDI_22N']
    for index in pd_tmp.index:
        dict_tmp = {}
        dict_tmp['SampleId'] = pd_tmp.loc[index, 'Sample']
        dict_tmp['Amplicon'] = pd_tmp.loc[index, 'Amplicon']
        dict_tmp['Chr'] = dict_chr[pd_tmp.loc[index, 'Amplicon']]
        dict_tmp['Rate'] = str(round(float(pd_tmp.loc[index, 'EditRate'])*100, 2))
        dict_tmp['Depth'] = int(pd_tmp.loc[index, 'SeqRaw'])
        dict_tmp['Date'] = pd_sample[pd_sample['SampleId']==pd_tmp.loc[index, 'Sample']]['SampleCollectDate'].iloc[0]
        list_tmp.append(dict_tmp)
    return sorted(list_tmp, key=AmpliconSorted)

def GetDNAInfor(pd_sample, dict_qc):
    list_tmp = []
    for index in pd_sample.index:
        dict_tmp = {}
        dict_tmp['SampleId'] = pd_sample.loc[index, 'SampleId']
        dict_tmp['SampleType'] = pd_sample.loc[index, 'SampleType']
        dict_tmp['DNATotal'] = round(float(pd_sample.loc[index, 'DNATotal']), 2)
        dict_tmp['A260A280'] = round(float(pd_sample.loc[index, 'A260A280']), 2)
        dict_tmp['A260A230'] = round(float(pd_sample.loc[index, 'A260A230']), 2)
        dict_tmp['SampleTotal'] = float(pd_sample.loc[index, 'SampleTotal'])
        if int(dict_tmp['DNATotal']) >= int(dict_qc["DNATotal"]):
            dict_tmp['QC'] = "合格"
        else:
            dict_tmp['QC'] = "不合格"
        list_tmp.append(dict_tmp)
    return list_tmp

def GetLibraryInfor(pd_sample, dict_qc):
    list_tmp = []
    list_size = [int(i) for i in re.split("~", dict_qc["LibraryMainSize"])]
    for index in pd_sample.index:
        dict_tmp = {}
        dict_tmp['SampleId'] = pd_sample.loc[index, 'SampleId']
        dict_tmp['LibraryMainSize'] = int(pd_sample.loc[index, 'LibraryMainSize'])
        dict_tmp['LibraryMainConcentration'] = round(float(pd_sample.loc[index, 'LibraryMainConcentration']), 2)
        dict_tmp['LibraryMainPCT'] = round(float(pd_sample.loc[index, 'Library_main_pct']), 2)
        if dict_tmp['LibraryMainSize'] >= list_size[0] and dict_tmp['LibraryMainSize'] <= list_size[1] and \
            dict_tmp['LibraryMainConcentration'] >= dict_qc['LibraryMainConcentration'] and \
            dict_tmp['LibraryMainPCT'] >= dict_qc['LibraryMainPCT']:
            dict_tmp['QC'] = "合格"
        else:
            dict_tmp['QC'] = "不合格"
        list_tmp.append(dict_tmp)
    return list_tmp

def GetSequencingInfor(SampleQuilityStat, SampleFinalEditRateStat, dict_qc):
    list_tmp = []
    UniformatyAndDepth = GetUniformatyAndDepth(SampleFinalEditRateStat)
    for index in SampleQuilityStat.index:
        dict_tmp = {}
        dict_tmp['SampleId'] = SampleQuilityStat.loc[index, 'Sample']
        dict_tmp['SequencingBase'] = round(int(SampleQuilityStat.loc[index, 'before_filtering_total_bases'])/1e9, 1)
        dict_tmp['SequencingDepth'] = int(UniformatyAndDepth.loc[SampleQuilityStat.loc[index, 'Sample'], 'SequencingDepth'])
        dict_tmp['MinSequencingDepth'] = int(UniformatyAndDepth.loc[SampleQuilityStat.loc[index, 'Sample'], 'MinSequencingDepth'])
        dict_tmp['SequencingUniformaty'] = round(UniformatyAndDepth.loc[SampleQuilityStat.loc[index, 'Sample'], 'SequencingUniformaty']*100, 2)
        dict_tmp['SequencingMergeRate'] = round(float(SampleQuilityStat.loc[index, 'MergedRate'])*100, 2)
        dict_tmp['SequencingQ30'] = round(float(SampleQuilityStat.loc[index, 'before_filtering_q30_rate'])*100, 2)
        if dict_tmp['SequencingBase'] >= float(dict_qc['SequencingBase']) and \
                dict_tmp['MinSequencingDepth'] >= int(dict_qc['SequencingDepth']) and \
                dict_tmp['SequencingUniformaty'] >= float(dict_qc['SequencingUniformaty'])*100 and \
                dict_tmp['SequencingMergeRate'] >= float(dict_qc['SequencingMergeRate'])*100 and \
                dict_tmp['SequencingQ30'] >= float(dict_qc['SequencingQ30'])*100:
            dict_tmp['QC'] = "合格"
        else:
            dict_tmp['QC'] = "不合格"
        list_tmp.append(dict_tmp)
    return list_tmp

def GetUniformatyAndDepth(SampleFinalEditRateStat):
    list_sample = []
    pd_out = pd.DataFrame(columns=['Sample', 'SequencingDepth', 'SequencingUniformaty', 'MinSequencingDepth'])
    for index in SampleFinalEditRateStat.index:
        sample = SampleFinalEditRateStat.loc[index, 'Sample']
        if sample not in list_sample:
            list_sample.append(sample)
            pd_sub = SampleFinalEditRateStat[SampleFinalEditRateStat['Sample']==sample]
            mean_depth = sum(list(pd_sub['SeqRaw']))/pd_sub.shape[0]
            min_depth = min(list(pd_sub['SeqRaw']))
            m = 0
            for index in pd_sub.index:
                Totalseq = int(SampleFinalEditRateStat.loc[index, 'SeqRaw'])
                if Totalseq >= mean_depth*0.2:
                    m += 1
            pd_out.loc[sample, :] = [sample, mean_depth, round(m/pd_sub.shape[0], 4), min_depth]
    return pd_out

def GetBioQC(dict_DNA, dict_Library, dict_Sequencing):
    if dict_DNA['QC'] == '合格' and dict_Library['QC'] == '合格' and dict_Sequencing['QC'] == '合格':
        return '合格'
    return '不合格'

def MakeBaseQulityPlot(SampleQuilityStat, resultpath, outpath, dict_rtrans):
    list_out = []
    for index in SampleQuilityStat.index:
        sample = SampleQuilityStat.loc[index, 'Sample']
        json_fl = resultpath+'/2.QC/'+dict_rtrans[sample]+'/'+dict_rtrans[sample]+'.json'
        with open(json_fl, 'r') as f:
            dict_json = json.loads(f.read())
        pd_data = pd.DataFrame()
        pd_data['quality'] = dict_json['read1_before_filtering']['quality_curves']['mean'] +\
            dict_json['read2_before_filtering']['quality_curves']['mean']
        pd_data['position'] = range(1, len(pd_data['quality'])+1)
        sns.set_style("ticks")
        fig, axe = plt.subplots(figsize=(24,16))
        sns.lineplot(data=pd_data, x='position', y='quality', linewidth=5)
        plt.axvline(x=150, color='grey', linewidth=4)
        plt.axhline(y=30, color='red', linestyle='--', linewidth=4)
        plt.xticks(size = 40)
        plt.yticks(size = 40)
        axe.set_xlabel(sample, size = 50)
        axe.set_ylabel('Base Quality', size = 50)
        sns.despine()
        axe.spines['bottom'].set_linewidth(4)
        axe.spines['left'].set_linewidth(4)
        axe.spines['right'].set_linewidth(4)
        plt.savefig('{}.png'.format(os.path.join(outpath, str(sample)+'.bq')), dpi=300)
        list_out.append('{}.png'.format(os.path.join(outpath, str(sample)+'.bq')))
    return list_out

def MakeDepthPlot(SampleFinalEditRateStat, outpath):
    list_sample = []
    list_out = []
    for index in SampleFinalEditRateStat.index:
        sample = SampleFinalEditRateStat.loc[index, 'Sample']
        if sample not in list_sample:
            list_sample.append(sample)
            pd_sub = SampleFinalEditRateStat[SampleFinalEditRateStat['Sample']==sample]
            pd_out = pd.DataFrame(columns=['Sample', 'Amplicon', 'SequencingBalance'])
            mean_depth = sum(list(pd_sub['SeqRaw']))/pd_sub.shape[0]
            for index in pd_sub.index:
                pd_out.loc[index, :] = [sample, pd_sub.loc[index, 'Amplicon'], round(pd_sub.loc[index, 'SeqRaw']/mean_depth, 4)]
            sns.set_style("ticks")
            fig, axe = plt.subplots(figsize=(24,20))
            sorted_amplicon = sorted(list(pd_out['Amplicon']), key=lambda x:int(re.split('_', x)[-1].rstrip('N')))
            sns.barplot(x='Amplicon', y='SequencingBalance', data=pd_out, 
                        ci=None, color='blue',
                        order=sorted_amplicon)
            plt.axhline(y=1, color='red', linestyle='--', linewidth=4)
            axe.set_xticklabels(sorted_amplicon, rotation=90)
            plt.xticks(size = 20)
            plt.yticks(size = 40)
            axe.set_xlabel(sample, size = 50)
            axe.set_ylabel('Amplicon Depth Ratio', size = 50)
            sns.despine()
            axe.spines['bottom'].set_linewidth(4)
            axe.spines['left'].set_linewidth(4)
            axe.spines['right'].set_linewidth(4)
            plt.savefig('{}.png'.format(os.path.join(outpath, str(sample)+'.dep')), dpi=300)
            list_out.append('{}.png'.format(os.path.join(outpath, str(sample)+'.dep')))
    return list_out

def AmpliconSorted(item):
    return(item['SampleId'], int(re.split('_', item['Amplicon'])[-1].rstrip('N')))