#coding = <gbk>
import os
import urllib.request
from urllib import request
import re
import sys
import shutil
import shelve
import datetime
import send2trash
import time
import queue

Headers = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36', 'Accept-Language':'zh-CN'}
url_pattern = r"href=\"(https://www.91porn.com/view_video.php\?.*?viewkey=.*?)\">.*?id=\".*?_([\d]+)\".*?<span class=.*?(title|videox).*?>(.*?)</span>"
download_url_prefix = r"https://cdn77.91p49.com/m3u8/"
dbfile = "./tsid_db"

homepage_url = "https://www.91porn.com/index.php"
download_error_array = queue.Queue()

page_url_prefix_list = []
temp_url = ""
#page_url_prefix_list.append(temp_url)

page_url_prefix_list.append(r"https://www.91porn.com/v.php?next=watch&page=")
page_url_prefix_list.append(r"https://www.91porn.com/v.php?category=&page=")
page_url_prefix_list.append(r"https://www.91porn.com/v.php?category=rf&viewtype=basic&page=")
page_url_prefix_list.append(r"https://www.91porn.com/v.php?category=ori&viewtype=basic&page=")
#page_url_prefix_list.append("https://www.91porn.com/v.php?category=long&page=")

FST_PAGE=1
URL_RANGE=10

def get_batch_url(parent_url):
    req = urllib.request.Request(parent_url, None, Headers)
    fstr = urllib.request.urlopen(req).read().decode('utf-8')
    '''
    with open("./testdbg.txt", "w") as f:
        f.write(fstr)
    '''
    urls = re.findall(url_pattern, fstr, re.S)
    return urls


'''
fstr = open("./testdbg.txt", "r").read();
urls = re.findall(url_pattern, fstr, re.S)
print(urls)
print(len(urls))
print(urls[0])
print(len(urls[0]))
'''


#print(url)
#urls = get_batch_url(url)
#print(urls)


'''
print(type(urls[0]))
print(type(urls[0][0]))     # url
print(type(urls[0][1]))     # tsid
print(type(urls[0][2]))     # title
'''

def judge_id_old(tsid_str):
    d = shelve.open(dbfile)
    flag = tsid_str in d
    d.close()
    return flag

def store_id(tsid_str, filename):
    d = shelve.open(dbfile)
    d[tsid_str] = filename
    d.close()

def trim_filename(filename):
    character = '\/:*?"<>|'
    new_name = filename
    for s in character:
        if s in new_name:
            new_name = new_name.replace(s, " ")
    return new_name

def add_info_to_glog(log_str, print_en=True):
    glog = open("./glog.txt", "a", errors='ignore')
    if print_en:
        print(log_str)
    glog.write(log_str+"\n")
    glog.close()

def get_cur_time_str():
    year = datetime.datetime.now().year
    mon = datetime.datetime.now().month
    day = datetime.datetime.now().day
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    return str(year)+str(mon)+str(day)+str(hour)+str(minute)+str(second)
    
def rename_filename_to_avoid_duplicate(file_name):
    new_file_name = file_name + "_" + get_cur_time_str()
    add_info_to_glog("rename %s to %s"%(file_name, new_file_name))
    return new_file_name

def getts(tsid_str, filename):
    global download_error_array
    store_en = 0
    ts_en = 0
    add_info_to_glog("Begin to download file %s"%(filename))
    if judge_id_old(tsid_str):
        log_str = "tsid_str-[%s] has been download before..."%(tsid_str)
        add_info_to_glog(log_str, False)
        return
    idc = 0
    dir_path = os.path.join(os.getcwd(), tsid_str)
    #print(dir_path)
    os.makedirs(dir_path, exist_ok=True)
    ts_url_parent_path = download_url_prefix + "/" + tsid_str + "/"
    while True:
        ts_split_id = tsid_str + str(idc)
        ts_url = ts_url_parent_path + "/" + ts_split_id + ".ts"
        ts_file = os.path.join(dir_path, ts_split_id + ".ts")        
        try:
            request.urlretrieve(ts_url, ts_file)
            if(ts_en==0):
                add_info_to_glog("download successfully for %s"%(ts_split_id))
            ts_en = 1  # means ts_url is not 404,has been download at least a split video
            idc += 1
        except BaseException as err: 
            add_info_to_glog("download fail for %s due to %s"%(ts_split_id, err))
            if(type(err) is urllib.error.HTTPError):
                if(err.code==404):
                    if ts_en:
                        store_en = 1
                    else:   # ts_en = 0, ts_url is not a valid url
                        add_info_to_glog("download %s fail for %s due to ts_url invalid"%(tsid_str, filename))
                else:
                    add_info_to_glog("download %s fail for %s due to %s"%(tsid_str, ts_split_id, err))
            else:
                add_info_to_glog("download %s fail for %s due to %s"%(tsid_str, ts_split_id, err))
            break
    if not store_en:
        download_error_array.put((tsid_str, filename))
        add_info_to_glog("list download_error_array:")
        add_info_to_glog(str(download_error_array) + '\n')
        shutil.rmtree(dir_path)
        return
    trim_name = trim_filename(filename)
    final_file_name = rename_filename_to_avoid_duplicate(trim_name)
    merge_file = os.path.join(dir_path, final_file_name + ".ts")
    with open(merge_file, "wb+") as fw:
        for i in range(0, idc):
            ts_file = os.path.join(dir_path, tsid_str + str(i) + ".ts") 
            fw.write(open(ts_file, "rb").read())
    shutil.move(merge_file, os.getcwd())
    shutil.rmtree(dir_path)
    #print("merge ts file-[%s] success!"%(tsid_str))     
    log_str = "merge ts file-[%s] success!"%(tsid_str)   
    add_info_to_glog(log_str)
    store_id(tsid_str, filename)


if(os.path.exists("glog.txt")):
    send2trash.send2trash("./glog.txt")

for i in range(URL_RANGE, 0, -1):    
    for page_url_prefix in page_url_prefix_list:
    #for i in range(FST_PAGE, FST_PAGE+URL_RANGE):
    #for i in range(URL_RANGE, 0, -1):
        url = page_url_prefix + str(i)
        add_info_to_glog(url + '\n')
        urls = get_batch_url(url)
        add_info_to_glog(str(urls) + '\n')
        for item in urls:
            url = item[0]
            tsid_str = item[1]
            title = item[-1]
            #print(url, tsid_str, title)
            getts(tsid_str, title)
            time.sleep(0.5)

add_info_to_glog("Begin redownload...")
while not download_error_array.empty():
    item = download_error_array.get()
    tsid_str = item[0]
    title = item[1]
    getts(tsid_str, title)
    time.sleep(0.5)

