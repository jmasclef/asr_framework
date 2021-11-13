import os

def asr_load_doc(file_name,encoding_value="utf-8"):
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

def asr_save_doc(file_name,doc,encoding_value="utf-8",binaryMode=False,append_mode=False):
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
