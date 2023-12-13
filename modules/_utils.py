import os
import json
import MeCab
import jaconv
import base64
import random
import string
import requests
import threading
import markovify
import tls_client
import capmonster_python
from Cryptodome.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

response = requests.get('https://raizou-zap.github.io/thunder/message.txt')
response.encoding = 'utf-8'
message = response.text

response = requests.get('https://raizou-zap.github.io/thunder/update_version.txt')
response.encoding = 'utf-8'
update_version = response.text.replace('\n','')

response = requests.get('https://raizou-zap.github.io/thunder/update_contents.txt')
response.encoding = 'utf-8'
update_contents = response.text

# https://bogdanfinn.gitbook.io/open-source-oasis/tls-client/supported-and-tested-client-profiles
session = tls_client.Session(client_identifier="chrome_117", random_tls_extension_order=True)

file_checklist = ['config.json', 'tokens.txt', 'proxies.txt', 'caches.json', 'markov.txt']
for filename in file_checklist:
    if not os.path.isfile(f'./data/{filename}'):
        open(f'./data/{filename}', 'w')

caches = []
with open('./data/caches.json', mode='r', encoding='utf-8') as f:
    filedata = f.read()
    if not filedata == '':
        caches = json.loads(filedata)

config = {}
with open('./data/config.json', mode='r', encoding='utf-8') as f:
    config = json.loads(f.read())

proxies = []
proxy_details = {None:{'protocol':None,'username':None,'password':None,'host':None,'port':None}}
with open('./data/proxies.txt', mode='r', encoding='utf-8') as f:
    filedata = f.read()
    if filedata != '':
        _proxies = filedata.split('\n')
        for proxy in _proxies:
            if proxy != '':
                proxy_detail_list = proxy.split(':')
                proxy_detail = {}
                if len(proxy_detail_list) == 1:
                    proxy_detail = {
                        'protocol': 'http',
                        'username': None,
                        'password': None,
                        'host': proxy_detail_list[0],
                        'port': '8080'
                    }
                elif len(proxy_detail_list) == 2:
                    proxy_detail = {
                        'protocol': 'http',
                        'username': None,
                        'password': None,
                        'host': proxy_detail_list[0],
                        'port': proxy_detail_list[1]
                    }
                elif len(proxy_detail_list) == 4:
                    proxy_detail = {
                        'protocol': proxy_detail_list[0],
                        'username': proxy_detail_list[1].replace('//', ''),
                        'password': proxy_detail_list[2].split('@')[0],
                        'host': proxy_detail_list[2].split('@')[1],
                        'port': proxy_detail_list[3]
                    }
                if '://' in proxy:
                    proxy_details[proxy] = proxy_detail
                    proxies.append({'http': proxy, 'https': proxy})
                else:
                    proxy_details[f'http://{proxy}'] = proxy_detail
                    proxies.append({'http': f'http://{proxy}', 'https': f'http://{proxy}'})

tokens = []
with open('./data/tokens.txt', mode='r', encoding='utf-8') as f:
    for line in f.read().split('\n'):
        if line != '':
            if line.count(':') == 2:
                account_information = line.split(':')
                tokens.append(account_information[2])
            elif line.count(':') < 2:
                tokens.append(line)

with open("./data/markov.txt", mode="r", encoding='utf-8') as f:
    markov_data = f.read()
    mecab = MeCab.Tagger("-Owakati")
    text = ''
    if markov_data != '':
        for line in markov_data.split('\n'):
            if line != '':
                parsed_data = ' '.join(mecab.parse(line).split())
                text += f'{parsed_data}\n'
        markov_model = markovify.NewlineText(text, well_formed=False)

def markov_sentence():
    if markov_model != None:
        sentence = markov_model.make_sentence(tries=100)
        if sentence != None:
            return sentence.replace(' ', '').replace('@','＠')
        else:
            return ''
    else:
        return ''

def get_random_cache():
    cache = None
    if len(caches) != 0:
        cache = random.choice(caches)
    return cache

def get_random_proxy():
    proxy = {'http':None,'https':None}
    if len(proxies) != 0:
        proxy = random.choice(proxies)
    return proxy

def get_random_token():
    token = None
    if len(tokens) != 0:
        token = random.choice(tokens)
    return token

def random_string(length, under_length:int=None, contain_punctuation=False):
    if under_length != None:
        length = random.randint(under_length, length)
    if contain_punctuation == False:
       randomstring_list = [random.choice(string.ascii_letters + string.digits) for i in range(length)]
    else:
       randomstring_list = [random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(length)]
    return ''.join(randomstring_list)

hiragana_full = list('ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろわをんーゎゐゑゕゖゔゝゞ・「」。、')
katakana_full = list('ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロワヲンーヮヰヱヵヶヴヽヾ・「」。、')
katakana_half = list('ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝｰヮヰヱヵヶヽヾ･｢｣｡､')
alphabet_big_half = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
alphabet_small_half = list('abcdefghijklmnopqrstuvwxyz')
alphabet_big_full = list('ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ')
alphabet_small_full = list('ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ')
symbol = list('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ')
symbol_full = list('！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～　')
digit = list('0123456789')
digit_full = list('０１２３４５６７８９')
alphabet_big_half_convert_list = dict(zip(alphabet_big_half, alphabet_small_half))
alphabet_small_half_convert_list = dict(zip(alphabet_small_half, alphabet_big_half))
alphabet_big_full_convert_list = dict(zip(alphabet_big_full, alphabet_small_full))
alphabet_small_full_convert_list = dict(zip(alphabet_small_full, alphabet_big_full))
def random_convert(text):
    converted = ''
    for char in list(text):
        if char in hiragana_full:
            converted += random.choice([char, jaconv.hira2kata(char), jaconv.hira2hkata(char)])
        elif char in katakana_full:
            converted += random.choice([char, jaconv.kata2hira(char), jaconv.z2h(char)])
        elif char in katakana_half:
            converted += random.choice([char, jaconv.kata2hira(jaconv.h2z(char)), jaconv.h2z(char)])
        elif char in alphabet_big_half:
            converted += random.choice([char, jaconv.h2z(char, ascii=True), alphabet_big_half_convert_list[char], jaconv.h2z(alphabet_big_half_convert_list[char], ascii=True)])
        elif char in alphabet_small_half:
            converted += random.choice([char, jaconv.h2z(char, ascii=True), alphabet_small_half_convert_list[char], jaconv.h2z(alphabet_small_half_convert_list[char], ascii=True)])
        elif char in alphabet_big_full:
            converted += random.choice([char, jaconv.z2h(char, ascii=True), alphabet_big_full_convert_list[char], jaconv.z2h(alphabet_big_full_convert_list[char], ascii=True)])
        elif char in alphabet_small_full:
            converted += random.choice([char, jaconv.z2h(char, ascii=True), alphabet_small_full_convert_list[char], jaconv.z2h(alphabet_small_full_convert_list[char], ascii=True)])
        elif char in symbol:
            converted += random.choice([char, jaconv.h2z(char, ascii=True)])
        elif char in symbol_full:
            converted += random.choice([char, jaconv.z2h(char)])
        elif char in digit:
            converted += random.choice([char, jaconv.h2z(char)])
        elif char in digit_full:
            converted += random.choice([char, jaconv.z2h(char)])
        else:
            converted += char
    return converted

def remove_string(string:str, remove):
    if type(remove) == str:
        string = string.replace(remove, '')
    elif type(remove) == list:
        for remove_string in remove:
            string = string.replace(remove_string, '')
    return string

def replace_content(content:str, mention_members:list=['']):
    if '<RANDOM_TOKEN>' in content:
        user_id = remove_string(base64.b64encode(str(random.randint(1000000000000000000, 2000000000000000000)).encode()).decode(), '=')
        unixtime = random_string(6)
        hmac = random_string(38)
        content = content.replace('<RANDOM_TOKEN>', f'{user_id}.{unixtime}.{hmac}')
    content = content.replace('\\n', '\n')
    content = content.replace('<RANDOM_STRING>', random_string(15, 5))
    content = content.replace('<RANDOM_MENTION>', random.choice(mention_members))
    content = content.replace('<MARKOV>', markov_sentence())

    return content

def empty_headers(proxy:dict=None):
    if proxy == None:
        proxy = get_random_proxy()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        'Sec-Ch-Ua':f'"Google Chrome";v="{config["chrome_version_major"]}", "Chromium";v="{config["chrome_version_major"]}", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': config['useragent'],
    }
    response = requests.get('https://discord.com/register', headers=headers, proxies=proxy)

    cookie = ''
    for cookie_name in response.cookies.keys():
        cookie += f'{cookie_name}={response.cookies[cookie_name]}; '

    properties = f'{{"os":"Windows","browser":"Chrome","device":"","system_locale":"ja-JP","browser_user_agent":"{config["useragent"]}","browser_version":"{config["chrome_version"]}","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":{config["client_build_number"]},"client_event_source":null}}'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': cookie,
        'Origin': 'https://discord.com',
        'Referer': 'https://discord.com',
        'Sec-Ch-Ua':f'"Google Chrome";v="{config["chrome_version_major"]}", "Chromium";v="{config["chrome_version_major"]}", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': config['useragent'],
        'X-Debug-Options': 'bugReporterEnabled',
        'X-Discord-Locale': 'ja',
        'X-Discord-Timezone': 'Asia/Tokyo',
        'X-Super-Properties': base64.b64encode(properties.encode()).decode(),
    }
    return headers

empty_headers()
def encrypt(data, key, return_bytes=False):
    if type(data) == str:
        data = data.encode()
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    crypted_bytes = cipher.encrypt(pad(data, AES.block_size))
    crypted_string = base64.b64encode(crypted_bytes).decode('utf-8')
    if return_bytes:
        return crypted_bytes
    else:
        return crypted_string

def decrypt(data, key):
    if type(data) == str:
        data = base64.b64decode(data.encode())
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    decrypted_string = unpad(cipher.decrypt(data), AES.block_size).decode('utf-8')
    return decrypted_string

def solve_captcha(sitekey, siteurl, useragent=None, is_invisible=False, custom_data=None, proxy_detail=None):
    if config['captcha']['service'] == 'capmonster.cloud':
        capmonster = capmonster_python.HCaptchaTask(config['captcha']['apikey'])
        if proxy_detail != None:
            capmonster.set_proxy(proxy_type=proxy_detail['protocol'], proxy_address=proxy_detail['host'], proxy_port=proxy_detail['port'], proxy_login=proxy_detail['username'], proxy_password=proxy_detail['password'])
        if useragent != None:
            capmonster.set_user_agent(useragent)
        task = capmonster.create_task(website_url=siteurl, website_key=sitekey, is_invisible=is_invisible, custom_data=custom_data)
        try:
            result = capmonster.join_task_result(task)
            response = result.get('gRecaptchaResponse')
            return response
        except:
            return False
    else:
        return False

class threading_manager:
    def __init__(self):
        self.threads = []

    def start(self, target, args=None, kwargs=None):
        thread = None
        if args != None:
            if kwargs != None:
                thread = threading.Thread(target=target, args=args, kwargs=kwargs)
            else:
                thread = threading.Thread(target=target, args=args)
        else:
            thread = threading.Thread(target=target)
        self.threads.append(thread)
        
        return thread

    def join(self, join=True, clear:bool=True):
        for thread in self.threads:
            thread.start()
        if join:
            for thread in self.threads:
                thread.join()
        if clear:
            self.threads = []