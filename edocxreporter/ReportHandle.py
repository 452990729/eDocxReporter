import os
import sys
from docxtpl import DocxTemplate,RichText,InlineImage
from docx.shared import Mm

BasePath = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(BasePath)

from YamlHandle import MakeDictFromYaml

class ReporterFromYaml(object):
    DICT_BASE = {
    "true": True,
    "false": False
    }
    
    def __init__(self, *args, **kwargs):
        self.yaml = kwargs["yaml"]
        self.docx_template = kwargs["docx_template"]
        self.outfile = kwargs["outfile"]
    
    def MakeReporter(self):
        doc = DocxTemplate(self.docx_template)
        dict_all = MakeDictFromYaml(self.yaml)
        dict_out = {}
        for key in dict_all:
            ob = dict_all[key]
            if ob["type"] == "list":
                list_tmp = []
                for child in ob["value"]:
                    if type(child) == list:
                        dict_tmp = {}
                        for childchild in child:
                            dict_tmp[childchild["name"]] = self.__handleElement(childchild, doc)
                        list_tmp.append(dict_tmp)
                    elif type(child) == dict:
                        list_tmp.append( self.__handleElement(child, doc))
                dict_out[ob["name"]] = list_tmp
            else:
                dict_out[ob["name"]] = self.__handleElement(ob, doc)
        doc.render(dict_out)
        doc.save(self.outfile)
                
    def __handleString(self, ob):
        return ob["value"]

    def __handleImage(self, ob, doc):
        return InlineImage(doc, 
                            image_descriptor=ob["value"], 
                            width=Mm(int(ob["width"])), 
                            height=Mm(int(ob["height"])))

    def __handleRichText(self, ob):
        return RichText(ob["value"], color=ob["color"], bold=self.DICT_BASE[ob["bold"]])

    def __handleElement(self, ob, doc):
        if ob["type"] == "string":
            return self.__handleString(ob)
        elif ob["type"] == "image":
            return self.__handleImage(ob, doc)
        elif ob["type"] == "richtext":
            return self.__handleRichText(ob)
        return 0