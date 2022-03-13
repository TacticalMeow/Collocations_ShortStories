from collections import Counter
import math
from string import punctuation
from get_collocations import *
from bigram_dicts import *
import sys
import json
import re
import unicodedata
import argparse


sys.stdout.reconfigure(encoding='utf-8')
stop_words = ["״","׳","של","רב","פי","עם","עליו","עליהם","על","עד","מן","מכל","מי","מהם","מה","מ","למה","לכל","לי","לו","להיות","לה","לא","כן","כמה","כלי","כל","כי"
            ,"יש","ימים","יותר","יד","י","זה","ז","ועל","ומי","ולא","וכן","וכל","והיא","והוא","ואם","ו","הרבה","הנה","היו","היה","היא","הזה","הוא","דבר","ד","ג","בני","בכל","בו"
            ,"בה","בא","את","אשר","אם","אלה","אל","אך","איש","אין","אחת","אחר","אחד","אז","אותו","־","^","?",";",":","1",".","-","*","!","שלשה","בעל","פני",")","גדול"
            ,"שם","עלי","עולם","מקום","לעולם","לנו","להם","ישראל","יודע","זאת","הזאת","הדברים","הדבר","הבית","האמת","במקום","בהם","אמרו","אינם","אחרי"
            ,"אותם","אדם","(","חלק","שני","שכל","שאר","ש","ר","פעמים","נעשה","ן","ממנו","מלא","מזה","ם","לפי","ל","כמו","כבר","כ","זו","ומה","ולכל","ובין","ואין"
            ,"הן","היתה","הא","ה","בל","בין","בזה","ב","אף","אי","אותה","או","אבל","א","\"",",","\n","–","בן־יהודה","לעיל","מתנדבי","באינטרנט"]
punctuations_list=[",",".","!","?",";",'"']
dict_interval_partitions={}
interval = None

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
    if len(word)>1 and (( word[0]=='('  and word[-1]==')' ) or ( word[0]=='['  and word[-1]==']' )):
        return True
    else:
        return False


def load_text_into_dicts(lines,additional_info=[]):
    global stop_words,interval,dict_interval_partitions
    req_key='All'
    if interval!=None:
        if len(additional_info)!=0:
            year = extract_year_from_string(additional_info[0])
            if year==None:
                year = extract_year_from_string(additional_info[1])
            if year!=None:
                number = int(year)-(int(year) % interval)
                req_key=str(number)+ '-' + str(number+interval-1)  


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
                    if w1w2 in dict_interval_partitions[req_key].colloc_dict:
                        dict_interval_partitions[req_key].colloc_dict[w1w2] = dict_interval_partitions[req_key].colloc_dict[w1w2]+1
                    else:
                        dict_interval_partitions[req_key].colloc_dict[w1w2] = 1
                        dict_interval_partitions[req_key].bigram_count=dict_interval_partitions[req_key].bigram_count+1

                    if w1 in dict_interval_partitions[req_key].w1_dict:
                        dict_interval_partitions[req_key].w1_dict[w1]+=1
                    else:
                        dict_interval_partitions[req_key].w1_dict[w1]=1
                    if w2 in dict_interval_partitions[req_key].w2_dict:
                        dict_interval_partitions[req_key].w2_dict[w2]+=1
                    else:
                        dict_interval_partitions[req_key].w2_dict[w2]=1


def write_dicts_to_file(filenames,dicts,title):
    if len(dicts)>0 and len(filenames)==len(dicts):
        for i in range(len(dicts)):
            top_collocs = Counter(dicts[i])
            with open(filenames[i],'a',encoding="utf8") as dict_file:
                dict_file.write(title + ': \n' + '-------------------- \n')
                dict_file.write(json.dumps(top_collocs.most_common(30),ensure_ascii=False))
                dict_file.write('\n -------------------- \n')
                dict_file.close()
    

def populate_pmi_dict(bigram_dicts):
    for k,v in bigram_dicts.colloc_dict.items():
        w1_w2 = k.split('_')
        if len(w1_w2)==2 and w1_w2[0]!='' and w1_w2[1]!='':
           bigram_dicts.pmi_dict[k]=math.log(v) + math.log(bigram_dicts.bigram_count) - math.log(bigram_dicts.w1_dict[w1_w2[0]]) - math.log(bigram_dicts.w2_dict[w1_w2[1]])
        
def init_interval_dict(interval):
    global dict_interval_partitions
    dict_interval_partitions['All']=Bigramdict({},{},{},{},0)
    if interval != None: 
        if interval>100 or interval <10 or interval % 10 !=0 :
            print('bad interval given')
            exit(1)
        else:
            for x in range(int(500/interval)):
                current_range_key = str(1600+interval*x) + '-' + str(1600+interval*(x+1)-1)
                dict_interval_partitions[current_range_key]=Bigramdict({},{},{},{},0)


def extract_year_from_string(str):
    if str==None:
        return None
    match=re.search(r"(\d{4})",str)
    if match==None:
        return None
    else:
        return match.group(1)

def query_short_story_data(cursor):
    global interval
    if interval!=None:
        query(cursor,"SELECT all_stories.path,short_stories.more_information,short_stories.EditionDetails FROM all_stories JOIN short_stories ON all_stories.ID=short_stories.WorkId WHERE (EditionDetails IS NOT NULL) OR (more_information IS NOT NULL)")
    else:
        query(cursor,"SELECT all_stories.path FROM all_stories JOIN short_stories ON all_stories.ID=short_stories.WorkId")

def write_results():
    global interval,dict_interval_partitions
    if interval==None:
        write_dicts_to_file(["top_bigrams.txt","top_pmi.txt"],[dict_interval_partitions['All'].colloc_dict,dict_interval_partitions['All'].pmi_dict],'All')
    else:
        for partition,bigram_dicts in dict_interval_partitions.items():
            if len(bigram_dicts.colloc_dict)>0:
                write_dicts_to_file(["top_bigrams_interval.txt","top_pmi_interval.txt"],[bigram_dicts.colloc_dict,bigram_dicts.pmi_dict],partition)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, required=False)
    args=parser.parse_args()
    interval = args.interval

    init_interval_dict(interval)

    con = connect_db("collocations.db")
    cursor = con.cursor()
    query_short_story_data(cursor)
    

    for row in cursor:
        print(row[0])
        curr_file = open("public_domain_dump-master/txt" + row[0] + ".txt",encoding="utf8")
        lines = curr_file.readlines()
        if interval!=None:
            load_text_into_dicts(lines,[row[1],row[2]])
        else:
            load_text_into_dicts(lines)
        curr_file.close()
    con.close()

    for year,bigramdicts in dict_interval_partitions.items():
        populate_pmi_dict(bigramdicts)

    write_results()
    
    