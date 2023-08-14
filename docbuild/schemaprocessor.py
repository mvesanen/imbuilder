from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
import sys
import random
from lxml import etree

#some constants
XMLS = "{http://www.w3.org/2001/XMLSchema}"
TYPEDFEATURE="--ltFeature--gt"
TYPEDPROPERTY="--ltProperty--gt"
FEATURESINELEMENTSFMT="Inframodel%sFeatureCodesType"
PROPERTIESINELEMENTSFMT="%sLabelType"
UNIONSINELEMENTSFMT="Inframodel%sFeatureLabelUnionType"
FEATDICTIONARYNAME="inframodel"

class TypedFeature():
    def __init__(self,elem,rawschema,elementname):
        self.name = get_element_name(elem)
        self.elements = [elementname]
        self.properties = []
        self.propmin = 0
        mintmp=elem.get("minOccurs") or "1"
        maxtmp=elem.get("maxOccurs") or "1"
        if(maxtmp=="unbounded"):
            maxtmp="-1"
        self.minOcc=int(mintmp)
        self.maxOcc=int(maxtmp)
        #dig allowed properties
        if(is_ref(elem)):
            newelem=get_element_definition(rawschema,get_element_name(elem))
        else:
            newelem=elem
        for subelem in newelem.iter(XMLS + "element"):
            if is_typed_property(subelem):
                self.properties.append(get_clean_property(get_element_name(subelem)))
                self.propmin+=int(subelem.get("minOccurs") or "1")
    def get_propmax(self):
        return len(self.properties)
    def get_propmin(self):
        return self.propmin
    def get_name(self):
        return self.name
    def get_paths(self):
        return self.Paths
    def add_instance(self,elem,name):
        if(not name in self.elements):
            elements.append(name)
            mintmp=elem.get("minOccurs") or "1"
            maxtmp=elem.get("maxOccurs") or "1"
            if(maxtmp=="unbounded"):
                maxtmp="-1"
            self.minOcc+=int(mintmp)
            tmpmaxOcc=int(maxtmp)
            if(tmpmax==-1):
                self.maxOcc=-1
            else:
                self.maxOcc+=tmpmaxOcc
    def get_properties(self):
        return self.properties
    def get_clean_name(self):
        if(self.name.find(TYPEDFEATURE)>0):
            return self.name[:self.name.index(TYPEDFEATURE)]
        return self.name
    def get_restriction_name(self):
        return (PROPERTIESINELEMENTSFMT % self.get_clean_name())
    def printout(self):
        print("    %s, minOcc=%d, maxOcc=%d" % (self.get_clean_name(),self.minOcc,self.maxOcc))
    def get_property_restriction_schema_element(self):
        elem = etree.Element(XMLS+"simpleType")
        elem.set("name",self.get_restriction_name())
        restriction=etree.Element(XMLS+"restriction")
        restriction.set("base","xs:string")
        elem.append(restriction)
        for x in self.properties:
            val = etree.Element(XMLS+"enumeration")
            val.set("value",x)
            restriction.append(val)
        return elem
    

class ElementTypedFeatures():
    def __init__(self,name):
        self.name=name
        self.features=[];
    def add_feature(self,elem,rawschema):
        featname=get_element_name(elem)
        found=False;
        for i in self.features:
            if i.get_name()==featname:
                i.add_instance(elem,self.name)
                found=True
        if(not found):
            self.features.append(TypedFeature(elem,rawschema,self.name))
    def get_clean_name(self):
        if(self.name.find(TYPEDFEATURE)>0):
            return self.name[:self.name.index(TYPEDFEATURE)]
        return self.name
    def get_restriction_name(self):
        return (FEATURESINELEMENTSFMT % self.get_clean_name())
    def get_restriction_union_name(self):
        return (UNIONSINELEMENTSFMT % self.get_clean_name())
    def get_feature_minoccurs(self):
        minocc=0
        for x in self.features:
            minocc+=x.minOcc
        return minocc
    def get_feature_maxoccurs(self):
        maxocc=0
        for x in self.features:
            if (x.maxOcc==-1):
                return -1
            maxocc+=x.maxOcc
        return maxocc
    def get_property_minoccurs(self):
        minocc=9999
        for x in self.features:
            if(x.get_propmin()<minocc):
                minocc=x.get_propmin()
        if(minocc==9999):
            return 0
        else:
            return minocc
    def get_property_maxoccurs(self):
        maxocc=-1
        for x in self.features:
            if(x.get_propmax()==-1):
                return -1
            if(x.get_propmax()>maxocc):
                maxocc=x.get_propmax()
        return maxocc
    def get_name(self):
        return self.name
    def get_property_restriction_schema_element_by_owner(self):
        elem = etree.Element(XMLS+"simpleType")
        elem.set("name",self.get_restriction_union_name())
        union=etree.Element(XMLS+"union")
        #union.set("base","xs:string")
        elem.append(union)
        memberTypes=""
        for x in self.features:
            memberTypes+=x.get_restriction_name()+" "
        memberTypes=memberTypes[:-1]
        union.set("memberTypes",memberTypes)
        return elem
    def get_feature_restriction_schema_element_by_owner(self):
        elem = etree.Element(XMLS+"simpleType")
        elem.set("name",self.get_restriction_name())
        restriction=etree.Element(XMLS+"restriction")
        restriction.set("base","xs:string")
        elem.append(restriction)
        for x in self.features:
            val = etree.Element(XMLS+"enumeration")
            val.set("value",x.get_clean_name())
            restriction.append(val)
        return elem
    def printout(self):
        elem=self.get_feature_restriction_schema_element_by_owner()
        print("XML simpleTypes:\n" + etree.tostring(elem,encoding='unicode',method='xml',pretty_print=True))

class ElementsWithFeatures:
    def __init__(self):
       self.elements=[]
    def add_feature(self,elem,rawschema,name):
        found=False
        name=name.replace("/","")
        for x in self.elements:
            if (x.name==name):
                found=True
                x.add_feature(elem,rawschema)
                break
        if not found:
            self.elements.append(ElementTypedFeatures(name))
            self.elements[-1].add_feature(elem,rawschema)
    def get_list_of_property_sets(self):
        seen_ext=[]
        flist=[]
        for x in self.elements:
            for y in x.features:
                if (not y.name in seen_ext):
                    seen_ext.append(y.name)
                    flist.append(y)
        return flist
    def append_xml_restriction_types(self,root):
        for x in self.elements:
            root.append(x.get_feature_restriction_schema_element_by_owner())
        flist=self.get_list_of_property_sets()
        for y in flist:
            root.append(y.get_property_restriction_schema_element())
        for z in self.elements:
            root.append(z.get_property_restriction_schema_element_by_owner())
    def printout(self):
        print("List of allowed values for different Inframodel featurecodes per LandXML element")
        for x in self.elements:
            x.printout()
        print("\n\nProperty labels per Inframodel Feature")
        flist=self.get_list_of_property_sets()
        for y in flist:
            print("XML simpleType %s:" % y.get_restriction_name())
            
            elem=y.get_property_restriction_schema_element()
            
            print(etree.tostring(elem,encoding='unicode',method='xml',pretty_print=True))
            
        print("\n\nFeature Property labels selection per parent LandXML element")
        for x in self.elements:
            print("XML simpleType %s:" % x.get_restriction_union_name())
            elem=x.get_property_restriction_schema_element_by_owner()
            print(etree.tostring(elem,encoding='unicode',method='xml',pretty_print=True))
            
    def print_element_list(self):
        for x in self.elements:
            print(x.name)
    def get_element_by_name(self,name):
        newname=name.replace("/","")
        for x in self.elements:
            if(x.name==newname):
                return x
        return None

def get_clean_property(name):
    if(name.find(TYPEDPROPERTY)>0):
        return name[:name.index(TYPEDPROPERTY)]
    return name

def get_element_definition(el, typename):
    for x in el.iter(XMLS + "element"):
        if ((x.get("name")==typename) and (GetAllParentElementNames(x)=="")):
            return x
    return None

def get_element_name(elem):
    if(elem is None):
        return ""
    if isinstance(elem.get("ref"),str):
        name = elem.get("ref")
    elif isinstance(elem.get("name"),str):
        name = elem.get("name")
    else:
        name = ""
    return name

def is_ref(elem):
    if(elem is None):
        return False
    if isinstance(elem.get("ref"),str):
        return True
    else:
        return False

def is_element(elem):
    if(elem is None):
        return False
    if(elem.tag==(XMLS + "element")):
        return True
    else:
        return False

def is_typed_feature(elem):
    if(elem is None):
        return False
    elemname = get_element_name(elem)
    if len(elemname)>0:
        if elemname.find(TYPEDFEATURE) > 0:
            return True
        else:
            return False
    else:
        return False

def is_typed_property(elem):
    if(elem is None):
        return False
    elemname = get_element_name(elem)
    if len(elemname)>0:
        if elemname.find(TYPEDPROPERTY) > 0:
            return True
        else:
            return False
    else:
        return False


def is_not_recursive(elem,rawschema):
    if(not is_element(elem)):
        return True
    elemname=get_element_name(elem)
    if(is_ref(elem)):
        newelem = get_element_definition(rawschema,elemname)
    else:
        newelem = elem
    if(not is_element(newelem)):
        return True
    hits=0
    for x in newelem.iter(XMLS + "element"):
        if get_element_name(x)==elemname:
            hits+=1
    if(hits>1):
        return False
    else:
        return True

def get_feature_code(elem):
    code = elem.get("code")
    if(code is None):
        return ""
    else:
        return code

def GetAllParentElementNames(elem):
    previous=elem.getparent()
    name=""
    while previous is not None:
        if(is_element(previous)):
            name=get_element_name(previous)+"/"+name
        previous=previous.getparent()
    if(len(name)>0):
        if(name[-1]=="/"):
            name=name[:-1]
    return name

def GetParentElementName(elem):
    previous=elem.getparent()
    name=""
    while previous is not None:
        if(is_element(previous)):
            name=get_element_name(previous)
            if(len(name)>0):
                break
        previous=previous.getparent()
    return name

def populate_element_list(elem,rawschema,feature_elements,treeorigin=""):
    if(elem is None):
        return
    
    for subelem in elem.iter(XMLS + "element"):
        if(get_element_name(subelem)==treeorigin):
            continue
        if(is_typed_feature(subelem)):
            if(treeorigin is None):
                parentelemname = GetAllParentElementNames(subelem)
            else:
                parentelemname = get_element_path(treeorigin,subelem)
                feature_elements.add_feature(subelem,rawschema,parentelemname)
            if(is_ref(subelem)) and (is_not_recursive(subelem,rawschema)):
                newsub = get_element_definition(rawschema,get_element_name(subelem))
                populate_element_list(newsub,rawschema,feature_elements,get_element_name(subelem))
        else:
            if(is_ref(subelem)) and (is_not_recursive(subelem,rawschema)):
                newsub = get_element_definition(rawschema,get_element_name(subelem))
                populate_element_list(newsub,rawschema,feature_elements,get_element_name(subelem))

def make_xsd_generic_feature_element(te,feature_elements,parentelem=None):
    feat_restr_name=te.get_restriction_name()
    minfeat=te.get_feature_minoccurs()
    maxfeat=te.get_feature_maxoccurs()
    prop_restr_name=te.get_restriction_union_name()
    minprop=te.get_property_minoccurs()
    maxprop=te.get_property_maxoccurs()
    elem = etree.Element(XMLS+"element")
    elem.set("name","Feature")
    if(parentelem is not None):
        if(parentelem.get("minOccurs")=="0"):
            minfeat=0
    if(minfeat!=1):
        elem.set("minOccurs",("%d" % minfeat))
    if(maxfeat==-1):
        elem.set("maxOccurs","unbounded")
    else: 
        if maxfeat!=1:
            elem.set("maxOccurs",("%d" % maxfeat))
    cmplx=etree.SubElement(elem,XMLS+"complexType")
    seq=etree.SubElement(cmplx,XMLS+"sequence")
    nameattrib=etree.SubElement(cmplx,XMLS+"attribute")
    nameattrib.set("name","name")
    nameattrib.set("type","xs:string")
    codeattrib=etree.SubElement(cmplx,XMLS+"attribute")
    codeattrib.set("name","code")
    codeattrib.set("type",feat_restr_name)
    codeattrib.set("use","required")
    sourceattrib=etree.SubElement(cmplx,XMLS+"attribute")
    sourceattrib.set("name","source")
    sourceattrib.set("use","required")
    if(len(FEATDICTIONARYNAME)):
        sourceattrib.set("fixed",FEATDICTIONARYNAME)
    propelem=etree.SubElement(seq,XMLS+"element")
    propelem.set("name","Property")
    if(minprop!=1):
        propelem.set("minOccurs",("%d" % minprop))
    if(maxprop==-1):
        propelem.set("maxOccurs","unbounded")
    else:
        if maxprop!=1:
            propelem.set("maxOccurs",("%d" % maxprop))
    propcplx=etree.SubElement(propelem,XMLS+"complexType")
    labelattrib=etree.SubElement(propcplx,XMLS+"attribute") 
    labelattrib.set("name","label")
    labelattrib.set("type",prop_restr_name)
    labelattrib.set("use","required")
    labelvalue=etree.SubElement(propcplx,XMLS+"attribute") 
    labelvalue.set("name","value")
    labelvalue.set("type","xs:string")
    labelvalue.set("use","required")
    for x in te.features:
        if x.name.find(TYPEDFEATURE) > 0:
            child = feature_elements.get_element_by_name(x.name)
            if(child is not None):
                seq.append(make_xsd_generic_feature_element(child,feature_elements,elem))
    return elem

def add_feature_by_elem(elem,feature_elements,parentname):
    te = feature_elements.get_element_by_name(parentname)
    if(te is not None):
        featureelem=make_xsd_generic_feature_element(te,feature_elements)
        elem.getparent().append(featureelem)
    else:
        print("ELEMENT NOT FOUND:"+ parentname)

def get_element_path(parentelemname,elem):
    subparent=GetParentElementName(elem)
    if ((subparent!=parentelemname) and (len(subparent)>0)):
        return parentelemname+"/"+subparent
    else:
        return parentelemname


def add_generic_features(elem,rawschema,feature_elements,processeditems=[],treeorigin=""):
    if(elem is None):
        return
    
    for subelem in elem.iter(XMLS + "element"):
        if(get_element_name(subelem)==treeorigin):
            continue
        if(is_typed_feature(subelem)):
            if(treeorigin is None):
                parentelemname = GetAllParentElementNames(subelem)
            else:
                parentelemname = get_element_path(treeorigin,subelem)
            
            if(not parentelemname in processeditems):
                processeditems.append(parentelemname)
                add_feature_by_elem(subelem,feature_elements,parentelemname)
            if(is_ref(subelem)) and (is_not_recursive(subelem,rawschema)):
                newsub = get_element_definition(rawschema,get_element_name(subelem))
                add_generic_features(newsub,rawschema,feature_elements,processeditems,get_element_name(subelem))
        else:
            if(is_ref(subelem)) and (is_not_recursive(subelem,rawschema)):
                newsub = get_element_definition(rawschema,get_element_name(subelem))
                add_generic_features(newsub,rawschema,feature_elements,processeditems,get_element_name(subelem))

def add_enumeration_types(rawschema,feature_elements):
    feature_elements.append_xml_restriction_types(rawschema.getroot())

def list_elements_to_remove(elem,rawschema,removelist=[],treeorigin=""):
    if(elem is None):
        return
    
    for subelem in elem.iter(XMLS + "element"):
        if(get_element_name(subelem)==treeorigin):
            continue
        if(is_typed_feature(subelem)) or (is_typed_property(subelem)):
            removelist.append(subelem)
            if(is_ref(subelem)) and (is_not_recursive(subelem,rawschema)):
                newsub = get_element_definition(rawschema,get_element_name(subelem))
                list_elements_to_remove(newsub,rawschema,removelist,get_element_name(subelem))
        else:
            if(is_ref(subelem)) and (is_not_recursive(subelem,rawschema)):
                newsub = get_element_definition(rawschema,get_element_name(subelem))
                list_elements_to_remove(newsub,rawschema,removelist,get_element_name(subelem))

def cleanup_schema(rawschema):
    elem = rawschema.getroot()
    elemlist = []
    list_elements_to_remove(elem,rawschema,elemlist)
    processed=[]
    for e in elemlist:
        if(not e in processed):
            processed.append(e)
            if(e.getparent() is not None):
                e.getparent().remove(e)

def xsd_postprocess(raw_schema_file,output_schema_file):

    rawschema = etree.parse(raw_schema_file)
    elem = get_element_definition(rawschema, "LandXML")
    if(elem is None):
        raise Exception("** ERROR: Can't locate LandXML element! **")
        return
    feature_elements = ElementsWithFeatures()
    populate_element_list(elem,rawschema,feature_elements)
    add_generic_features(elem,rawschema,feature_elements)
    add_enumeration_types(rawschema,feature_elements)
    cleanup_schema(rawschema)
    etree.indent(rawschema)
    rawschema.getroot().addprevious(etree.Comment(" DO NOT EDIT THIS FILE!! This file is automatically generated from:%s " % sys.argv[1]))
    
    rawschema.write(output_schema_file, pretty_print=True,xml_declaration=True, encoding='utf-8')

if __name__ == "__main__":
    xsd_postprocess(sys.argv[1],sys.argv[2])
