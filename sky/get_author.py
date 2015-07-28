import re
import json
import os

try:
    from .helper import *
except:
    from helper import *

with open(os.path.join('/Users/pascal/GDrive/sky/sky/author_translation_table.json')) as f:
    author_translation_table = json.load(f)
    uppered = {x.title() : author_translation_table[x] for x in author_translation_table}
    author_translation_table.update(uppered)

def author_translation(txt, lang): 
    if lang in author_translation_table:
        for month in author_translation_table[lang]:
            txt = txt.replace(month, author_translation_table[lang][month])
    return txt       

def get_text_author(txt):
    res = re.findall(r"\b([A-Z][a-zA-Z' ]+)", txt)
    if res:
        for r in res:
            rsplit = r.split()
            if len(rsplit) < 5 and len(rsplit) > 1:
                return r.strip()
    return False
    
def get_author(tree, lang = 'en'):     
    # Couple ways of matching:
    # - Both in meta and in text
    # - Node has one of the goods in it, text has it in it, and the case is authoric
    # - Node has one of the goods in it
    # - Text has one of the goods in it
    goods = ['author', 'by', 'publi', 'write', 'written', 'info']
    hard_authors = [] 
    meta_authors = [] 
    text_hard_authors = [] 
    text_soft_authors = [] 
    meta_nodes = tree.xpath('//head/meta')
    
    for option in goods: 

        for meta in meta_nodes:
            if not any([option in a for a in meta.values()]):
                continue

            for attr in meta.attrib:
                meta_authors.append(get_text_author(author_translation(meta.attrib[attr], lang)))
                
    for num, node in enumerate(tree.iter()): 
        # hard author    
        for parent in node.iterancestors():
            attr_values = parent.attrib.values()
            if any([g in a for a in attr_values for g in goods]): 
                break
        else:
            # if no goods match, ignore node
            continue        
        tailtext = get_text_and_tail(node).strip() 
        if tailtext:
            if lang != 'en':
                tailtext = author_translation(tailtext, lang)
            hard_author = get_text_author(tailtext)
            if hard_author: 
                hard_authors.append((num, hard_author))

    for num, node in enumerate(tree.iter()): 
        tailtext = get_text_and_tail(node).strip()
        if tailtext and len(tailtext) < 200:
            res = re.findall(r"author[:;]* ([a-zA-Z' ]+)", tailtext, re.IGNORECASE)
            if res:
                res = res[0]
                if res in meta_authors:
                    text_hard_authors.append((res, num))
                else:
                    text_soft_authors.append((res, num))                
            else:
                res = re.findall(r"\bby[:;]* ([a-zA-Z' ]+)", tailtext, re.IGNORECASE)        
                if res:
                    res = res[0]
                    if res in meta_authors:
                        text_hard_authors.append((res, num))
                    else:
                        text_soft_authors.append((res, num))                                        

    hardest_authors = []
    not_hardest_authors = []
    for num, ha in hard_authors:
        if ha in meta_authors:
            hardest_authors.append((ha, num))
        else:
            not_hardest_authors.append((ha, num))                

    meta_authors = set(meta_authors)

    return hardest_authors, not_hardest_authors, text_hard_authors, text_soft_authors, meta_authors