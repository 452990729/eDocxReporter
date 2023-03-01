#!/OPT/Env/python3

import os
import sys

BasePath = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(BasePath+'/../')

from edocxreporter.Engine import Engine
from edocxreporter import Args


def LoadeFalconAMPCMC(args):
    kwargs = {'chrConfig': args.chrConfig, 'config':args.config, 'sampleSheet':args.sampleSheet,
              'qcStandardsConfig':args.qcStandardsConfig, 'docxTemplate':args.docxTemplate,
              'resultPath':args.resultPath, 'full':args.full, 'outpath':args.outpath}
    Engine('eFalconAMPForCMC', **kwargs)

def LoadeFalconAMPClinical(args):
    kwargs = {'chrConfig': args.chrConfig, 'config':args.config, 'sampleSheet':args.sampleSheet,
              'qcStandardsConfig':args.qcStandardsConfig, 'docxTemplate':args.docxTemplate,
              'resultPath':args.resultPath, 'outpath':args.outpath}
    Engine('eFalconAMPForClinical', **kwargs)

def LoadArgs():
    Ob = Args.CustomArgs()
    ### load module
    Ob.add_efalconampcmc(LoadeFalconAMPCMC)
    Ob.add_efalconampclinical(LoadeFalconAMPClinical)
    
    ### parse args
    args = Ob.parser.parse_args()
    if len(args.__dict__) <= 1:
        Ob.parser.print_help()
        Ob.parser.exit()
    args.func(args)

def main():
    LoadArgs()


if __name__ == '__main__':
    main()
