import os

def mp_load_doc(file_name,encoding_value="utf-8"):
    doc=[]
    with open(file_name,"r",encoding=encoding_value) as f:
        line=f.readline()
        while line:
            if line[-1]=="\n":
                doc.append(line[:-1])   #retire l'\n qui a ete mis par le save
            else:
                doc.append(line)
            line=f.readline()
    return doc

def mp_save_doc(file_name,doc,encoding_value="utf-8",binaryMode=False,append_mode=False):
    if binaryMode:
        with open(file_name, "wb") as f:
            for line in doc:
                f.write(line)
                f.write("\n")
    else:
        if not append_mode:
            with open(file_name,"w",encoding=encoding_value) as f:
                for line in doc:
                    f.write(line)
                    f.write("\n")
        else:
            with open(file_name,"a",encoding=encoding_value) as f:
                for line in doc:
                    f.write(line)
                    f.write("\n")

# def mp_save_dict(file_name:str,dict_to_save:dict,encoding_value="utf-8",binaryMode=False,append_mode=False):
#     changes_str = [word + "," + dict_to_save[word] for word in dict_to_save.keys()]
#     # changes_str = ["\"" + word + "\",\"" + dict_to_save[word] + "\"\n" for word in dict_to_save.keys()]
#     changes_str = sorted(set(changes_str))
#     mp_save_doc(file_name,changes_str,encoding_value=encoding_value,binaryMode=binaryMode,append_mode=append_mode)
#
# def mp_load_dict(file_name:str,encoding_value="utf-8"):
#     doc=mp_load_doc(file_name,encoding_value=encoding_value)
#     result=dict()
#     for line in doc:
#         tab=line.split(",")
#         result[tab[0]]=tab[1]
#     return result

def mp_save_list(file_name:str,list_to_save:list,encoding_value="utf-8",binaryMode=False,append_mode=False,sort_list=True):
    # changes_str = ["\"" + word + "\",\"" + wholeIterationsRules[word] + "\"\n" for word in wholeIterationsRules.keys()]
    doc=[]
    for line in list_to_save:
        liste=[";".join(element) if isinstance(element,list) else str(element) for element in line ]
        liste_str=",".join(liste)
        doc.append(liste_str)
    if sort_list:
        doc.sort()
    mp_save_doc(file_name,doc,encoding_value=encoding_value,binaryMode=binaryMode,append_mode=append_mode)

def mp_load_list(file_name:str,encoding_value="utf-8"):
    doc=mp_load_doc(file_name,encoding_value=encoding_value)
    result=[]
    for line in doc:
        if "," in line:
            t=line.split(",")
            if ";" in t[1]:
                t0=t[0]
                t1=t[1].split(";")
                result.append([t0,t1])
            else:
                result.append(t)
        # else:
        #     result.append(line)
    return result

def mp_scan_folder(extension,directory="."):
    list = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                t = os.path.join(directory, filename)
                list.append(t)
    return list