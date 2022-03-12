from collections import Counter
import math
from string import punctuation
from get_collocations import *
import sys
import json
import re
import unicodedata
sys.stdout.reconfigure(encoding='utf-8')
stop_words = ["״","׳","של","רב","פי","עם","עליו","עליהם","על","עד","מן","מכל","מי","מהם","מה","מ","למה","לכל","לי","לו","להיות","לה","לא","כן","כמה","כלי","כל","כי"
            ,"יש","ימים","יותר","יד","י","זה","ז","ועל","ומי","ולא","וכן","וכל","והיא","והוא","ואם","ו","הרבה","הנה","היו","היה","היא","הזה","הוא","דבר","ד","ג","בני","בכל","בו"
            ,"בה","בא","את","אשר","אם","אלה","אל","אך","איש","אין","אחת","אחר","אחד","אז","אותו","־","^","?",";",":","1",".","-","*","!","שלשה","בעל","פני",")","גדול"
            ,"שם","עלי","עולם","מקום","לעולם","לנו","להם","ישראל","יודע","זאת","הזאת","הדברים","הדבר","הבית","האמת","במקום","בהם","אמרו","אינם","אחרי"
            ,"אותם","אדם","(","חלק","שני","שכל","שאר","ש","ר","פעמים","נעשה","ן","ממנו","מלא","מזה","ם","לפי","ל","כמו","כבר","כ","זו","ומה","ולכל","ובין","ואין"
            ,"הן","היתה","הא","ה","בל","בין","בזה","ב","אף","אי","אותה","או","אבל","א","\"",",","\n","–","בן־יהודה","לעיל","מתנדבי","באינטרנט"]
punctuations_list=[",",".","!","?",";",'"']
colloc_dict={}
w1_dict={}
w2_dict={}
pmi_dict={}
word_count_corpus=0

def remove_nikud(word):
    normalized = unicodedata.normalize('NFKD',word)
    flattened=''.join([c for c in normalized if not unicodedata.combining(c)])
    return flattened


def check_punctuation(word):
    global punctuations_list
    if word!='':
        if word[-1] in punctuations_list:
            return False
        else:
            return True
    else:
        return False
        

def strip_punctuation_from_word(word):
    return re.sub('[;,.!?;:#()"…“”]','',word)


def check_parenthesis(word):
    if word!='' and word[0]=='(' and len(word)>1 and word[-1]==')':
        return True
    else:
        return False


def load_text_into_dicts(lines):
    global word_count_corpus,stop_words
    for line in lines:
        lines_split = line.split()
        for index,word in enumerate(lines_split):
            if index<len(lines_split)-1:
                pre_w1=remove_nikud(word)
                pre_w2=remove_nikud(lines_split[index+1])
                if check_punctuation(pre_w1) and pre_w1 not in stop_words and pre_w2 not in stop_words and not check_parenthesis(pre_w2) and not check_parenthesis(pre_w1):
                    w1=strip_punctuation_from_word(pre_w1)
                    w2=strip_punctuation_from_word(pre_w2)
                    w1w2= w1 + '_' + w2
                    if w1w2 in colloc_dict:
                        colloc_dict[w1w2] = colloc_dict[w1w2]+1
                    else:
                        colloc_dict[w1w2] = 1
                        word_count_corpus=word_count_corpus+1
                    if w1 in w1_dict:
                        w1_dict[w1]+=1
                    else:
                        w1_dict[w1]=1
                    if w2 in w2_dict:
                        w2_dict[w2]+=1
                    else:
                        w2_dict[w2]=1


def write_dicts_to_file(filenames):
    global colloc_dict
    if len(filenames)==3:
        with open(filenames[0],'w',encoding="utf8") as dict_file:
            dict_file.write(json.dumps(colloc_dict,ensure_ascii=False))
            dict_file.close()
        with open(filenames[1],'w',encoding="utf8") as dict_file:
            dict_file.write(json.dumps(w1_dict,ensure_ascii=False))
            dict_file.close()
        with open(filenames[2],'w',encoding="utf8") as dict_file:
            dict_file.write(json.dumps(w2_dict,ensure_ascii=False))
            dict_file.close()
    

def populate_pmi_dict():
    global colloc_dict,pmi_dict,w1_dict,w2_dict,word_count_corpus
    for k,v in colloc_dict.items():
        w1_w2 = k.split('_')
        if len(w1_w2)==2 and w1_w2[0]!='' and w1_w2[1]!='':
            pmi_dict[k]=math.log(v) + math.log(word_count_corpus) - math.log(w1_dict[w1_w2[0]]) - math.log(w2_dict[w1_w2[1]])
        
    
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    con = connect_db("collocations.db")
    cursor = con.cursor()
    query(cursor,"SELECT all_stories.path FROM all_stories JOIN short_stories ON all_stories.ID=short_stories.WorkId WHERE (EditionDetails IS NOT NULL) OR (more_information IS NOT NULL)")
    for file_name in cursor:
        print(file_name[0])
        curr_file = open("public_domain_dump-master/txt" + file_name[0] + ".txt",encoding="utf8")
        lines = curr_file.readlines()
        load_text_into_dicts(lines)
        curr_file.close()
    con.close()
    populate_pmi_dict()
    top_collocs = Counter(colloc_dict)
    with open("top_bigrams.txt",'w',encoding="utf8") as dict_file:
            dict_file.write(json.dumps(top_collocs.most_common(100),ensure_ascii=False))
            dict_file.close()
    with open("top_pmi.txt",'w',encoding="utf8") as dict_file:
            dict_file.write(json.dumps(top_collocs.most_common(200),ensure_ascii=False))
            dict_file.close()
    
    