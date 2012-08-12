import urllib.request
import zipfile
import logging
import re
import ftplib
import io
import sys
import os
from html.parser import HTMLParser

l = logging.getLogger('root')

#initial variables
page_address = 'http://www.arma2.com/beta-patch.php'

download_path = 'C:\\dev\\'
current_version = ''
latest_version = ''
file_name = ''
ftp_server = ''
ftp_file_path = ''
file_length = 0
downloaded_file = b''

#this is an html parser created to retireve the necessary info from the update page 
class HTMLParser(HTMLParser):
    
    found_div = False
    def handle_starttag(self, tag, attrs):
        
        global latest_version
        global file_name
        global ftp_server
        global ftp_file_path
        
        if tag == 'div':
            for attr in attrs:
                if attr == ('id', 'latest'):
                    self.found_div = True
                else:
                    self.found_div = False
        if tag == 'a' and self.found_div:
            for attr in attrs:
                link = re.search('ftp://(\S*?\.com)(\S*(ARMA2_OA_Build_(\d*).zip))', attr[1])
                if attr[0] == 'href' and link:
                    print('Server: ', link.group(1))
                    print('File path: ', link.group(2))
                    print('File: ', link.group(3))
                    print('Version: ', link.group(4))
                    l.info('found link for the latest version')
                    ftp_server = link.group(1)
                    ftp_file_path = link.group(2)
                    file_name = link.group(3)
                    latest_version = link.group(4)
                    self.found_div = False
                else:
                    l.warning('could not find link for the latest version')

#this is called for every chunk of the ftp download 
def ftp_download(chunk):

    global read_so_far
    global downloaded_file
    
    percent_finished = read_so_far * 100 / file_length
    
    print('download: ' + str(percent_finished) + '%')
    downloaded_file += chunk
    read_so_far += sys.getsizeof(chunk)
    
    
#starts here    
print('looking up page')

req = urllib.request.Request(page_address, None)
f = urllib.request.urlopen(req)      



print('parsing page')

parser = HTMLParser()
parser.feed(f.read(2000).decode('utf-8'))

print('page parsed')


print('requesting file')

ftp = ftplib.FTP(ftp_server)
ftp.login()

file_length = ftp.size(ftp_file_path)
file_length_mb = file_length / 1024000

print('file: ' + file_name)
print('file size: ' + str(file_length_mb) + 'MB')
print('file size bytes: ' + str(file_length))

read_so_far = 0


print('downloading')

ftp.retrbinary('RETR ' + ftp_file_path, ftp_download)  

with io.FileIO(download_path + file_name, 'w') as writer:
    writer.write(downloaded_file)  

print('downloaded')


print('unziping')

file = open(download_path + file_name, 'rb')

zipf = zipfile.ZipFile(file, 'r')
zipf.extractall(download_path + '\\unzip')
zipf.close()
    
print('unziped')

print('running updater')

os.system(download_path + 'unzip\\' +  file_name[:-3] + 'exe')



