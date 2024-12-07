import json, time, random, os, requests, sys, io #, pygame
import pandas as pd
import msvcrt # 这个模块仅适用于 Windows 系统 如果是在 Linux 系统上 请修改 pause 函数
from pydub import AudioSegment
from pydub.playback import play
from pandas import DataFrame
from bs4 import BeautifulSoup
from typing import Dict, List

system_path = "D:\\pythonTools\\remember-the-words\\Project\\words"
temp_folder_path = f"{system_path}\\tempfile"

class Colors:
	RESET = "\033[0m"
	BLACK = "\033[30m"
	RED = "\033[31m"
	GREEN = "\033[32m"
	YELLOW = "\033[33m"
	BLUE = "\033[34m"
	MAGENTA = "\033[35m"
	CYAN = "\033[36m"
	WHITE = "\033[37m"
	LIGHT_BLACK = "\033[90m"
	LIGHT_RED = "\033[91m"
	LIGHT_GREEN = "\033[92m"
	LIGHT_YELLOW = "\033[93m"
	LIGHT_BLUE = "\033[94m"
	LIGHT_MAGENTA = "\033[95m"
	LIGHT_CYAN = "\033[96m"
	LIGHT_WHITE = "\033[97m"
	BACK_BLACK = "\033[40m"
	BACK_RED = "\033[41m"
	BACK_GREEN = "\033[42m"
	BACK_YELLOW = "\033[43m"
	BACK_BLUE = "\033[44m"
	BACK_MAGENTA = "\033[45m"
	BACK_CYAN = "\033[46m"
	BACK_WHITE = "\033[47m"
	BACK_LIGHT_BLACK = "\033[100m"
	BACK_LIGHT_RED = "\033[101m"
	BACK_LIGHT_GREEN = "\033[102m"
	BACK_LIGHT_YELLOW = "\033[103m"
	BACK_LIGHT_BLUE = "\033[104m"
	BACK_LIGHT_MAGENTA = "\033[105m"
	BACK_LIGHT_CYAN = "\033[106m"
	BACK_LIGHT_WHITE = "\033[107m"
	BOLD = "\033[1m"

def get_words_from_txt(file_path: str) -> List:
	"""
	读取文件中的单词并返回
	参数:
	file_path str: 文件路径，包含文件名
	返回:
	List: 返回单词列表
	"""
	words = []
	with open(file_path, 'r') as file:
		for word in file.readlines():
			words.append(word.strip())
	return words

def get_phonetic(word: str, type: int = 0) -> str:
	"""
	获得单词的音标
	参数:
	word str: 需要获取音标的单词
	type int: 英式音标还是美式音标
	"""
	USA_phonetic = ''
	UK_phonetic = ''
	get_soundmark_url = f"https://dict.youdao.com/result?word={word}&lang=en"
	style = ['美','英']
	text = style[type]
	try:
		response = requests.get(get_soundmark_url)
	except requests.exceptions.SSLError as e:
		print("SSL 错误，请关闭代理或更改网络环境后再使用该软件")
		exit()
	except requests.exceptions.RequestException as e:
		print("请求出错，请检查网络环境")
		exit()
	html_content = response.text
	# 创建 BeautifulSoup 对象
	soup = BeautifulSoup(html_content, 'html.parser')
	# 查找所有带有 'per-phone' 类的 div 标签
	phonetic_divs = soup.find_all('div', class_='per-phone')
	# 提取音标
	for div in phonetic_divs:
		# 找到音标的 span 标签
		phonetic_span = div.find('span', class_='phonetic')
		# 找到描述的语言
		USA_lang_span = div.find('span', string='美')
		UK_lang_span = div.find('span', string='英')
		# 如果找到了相关的音标
		if USA_lang_span and phonetic_span:
			USA_phonetic = phonetic_span.text
		if UK_lang_span and phonetic_span:
			UK_phonetic = phonetic_span.text
	return f"美式发音: {USA_phonetic} | 英式发音: {UK_phonetic}"


def search_word_in_dict_youdao(word: str) -> str:
	"""
	通过有道词典接口查询单词
	参数:
	word str: 单词
	返回:
	str: 查询结果，json数据格式
	"""
	dict_youdao_api = "http://dict.youdao.com/suggest?num=10000&ver=3.0&doctype=json&cache=false&le=en&q={}"
	user_agents = [
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
		"Mozilla/5.0 (Linux; Android 10; Pixel 3 XL Build/QQ1A.200205.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36",
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
		"Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
	]
	random_user_agent = random.choice(user_agents)
	headers = {
		"User-Agent": random_user_agent,
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
		"Accept-Encoding": "gzip, deflate, br",
		"Connection": "keep-alive",
	}
	try:
		response = requests.get(url=dict_youdao_api.format(word), headers=headers)
	except requests.exceptions.SSLError as e:
		print("SSL 错误，请关闭代理或更改网络环境后再使用该软件")
		exit()
	except requests.exceptions.RequestException as e:
		print("请求出错，请检查网络环境")
		exit()
	result = json.loads(response.text)["data"]["entries"]
	return result

def read_word(word: str, type: int = 2) -> None:
	"""
	用于播放单词的发音
	参数:
	word str: 需要发音的单词
	type int: 美式或英式发音
	返回:
	None
	"""
	temp_file_path = f"{temp_folder_path}\\{word}.mp3"
	voice_url = f"http://dict.youdao.com/dictvoice?type={type}&audio={word}"
	try:
		response = requests.get(voice_url)
	except requests.exceptions.SSLError as e:
		print("SSL 错误，请关闭代理或更改网络环境后再使用该软件")
		exit()
	except requests.exceptions.RequestException as e:
		print("请求出错，请检查网络环境")
		exit()
	with open(temp_file_path, 'wb') as f:
		f.write(response.content)
	audio = AudioSegment.from_file(temp_file_path)
	play(audio)
	# pygame 方式播放音频 不推荐
	# with open(temp_file_path, 'wb') as f:
	# 	f.write(response.content)
	# pygame.mixer.init()
	# pygame.mixer.music.load(temp_file_path)
	# pygame.mixer.music.play()
	# while pygame.mixer.music.get_busy():
	# 	pygame.time.Clock().tick(10)

def search_word_mode():
	while True:
		word = input(f"{Colors.LIGHT_GREEN}请输入需要查询的单词 >>> {Colors.RESET}")
		if word != '' and word != "EXIT":
			phonetic = get_phonetic(word)
			lengths = [len(word),len(phonetic)]
			form = "+-" + '-+-'.join(['-' * length for length in lengths])
			print(form)
			print(f"| {Colors.LIGHT_RED}{Colors.BOLD}{word}{Colors.RESET} | {Colors.LIGHT_GREEN}{Colors.BOLD}{phonetic}{Colors.RESET}")
			print(form) # 这里输出写的有点丑，需要改改
			read_word(word)
			result = search_word_in_dict_youdao(word)
			format_print(result)
			pause("请按任意键查询下一个单词...[Q/q]uite,[E/e]xit")
		elif word == "EXIT":
			clear_screen()
			print(f"{Colors.BLACK}{Colors.BACK_LIGHT_WHITE}============ 程序已退出! 欢迎下次使用! ============{Colors.RESET}")
			clear_temp_folder(temp_folder_path)
			exit()
		else:
			continue

def format_table(df: DataFrame, max_lengths: Dict[str,int]) -> str:
	"""
	生成格式化表格数据
	参数:
	df DataFrame: DataFrame对象，一个二维标记数组，可以存储异构数据类型
	max_lengths Dict[str,int]: 记录每一列最大的字符长度
	返回:
	str: 格式化表格数据
	"""
	header = '| ' + ' | '.join([f"{col:<{max_lengths[col]}}" for col in df.columns])
	separator = '+-' + '-+-'.join(['-' * max_lengths[col] for col in df.columns])
	rows = '\n| '.join([' | '.join([f"{str(value):<{max_lengths[col]}}" for col, value in zip(df.columns, row)]) for row in df.values])
	return f"{separator}\n{Colors.YELLOW}{header}{Colors.RESET}\n{separator}\n| {rows}\n{separator}"

def format_print(data: str) -> None:
	"""
	更好的表格格式化输出
	参数:
	data str: json格式数据
	返回:
	None
	"""
	df = pd.DataFrame(data)
	new_order = ['entry', 'explain']
	df = df[new_order]
	# 找到每列的最大长度
	max_lengths = {col: max(df[col].astype(str).map(len).max(), len(col)) for col in df.columns}
	# 打印列宽
	# for col, length in max_lengths.items():
	# 	print(f"Column '{col}', width: {length}")
	print(format_table(df, max_lengths))

def random_return_word(words: List) -> str:
	"""
	用于随机选取单词并将其从列表中移除
	参数:
	words List: 剩余单词的列表
	返回:
	str: 随机选中的单词
	"""
	if not words:
		return None # 或者抛出异常
	word = random.choice(words)
	words.remove(word)
	return word

def pause(message: str = "请按任意键继续...") -> None:
	"""
	用于暂停程序让用户进行思考
	输入:
	message str: 展示暂停时显示的提示信息
	返回:
	None
	"""
	print(f"{Colors.LIGHT_BLACK}{message}{Colors.RESET}")
	# msvcrt.getch() # 等待用户按下任意键
	key = msvcrt.getch() # 等待用户按下任意键，并获取它的值
	if key == b'q' or key == b'Q' or key == b'e' or key == b'E':
		clear_screen()
		print(f"{Colors.BLACK}{Colors.BACK_LIGHT_WHITE}============ 程序已退出! 欢迎下次使用! ============{Colors.RESET}")
		clear_temp_folder(temp_folder_path)
		exit()

def clear_screen():
	if os.name == 'nt': # Windows
		os.system('cls')
	else: # macOS 和 Linux
		os.system('clear')

def clear_temp_folder(temp_folder_path):
	if not os.path.exists(temp_folder_path):
		print(f"文件夹 {temp_file_path} 不存在")
		return
	if not os.listdir(temp_folder_path):
		# print(f"文件夹 {temp_file_path} 是空的")
		return
	while True:
		try:
			for filename in os.listdir(temp_folder_path):
				file_path = os.path.join(temp_folder_path, filename)
				if os.path.isfile(file_path):
					os.remove(file_path)
					# print(f"已删除文件: {file_path}")
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
					# print(f"已删除文件夹: {file_path}")
			print(f"{Colors.RED}临时文件夹 {temp_folder_path} 中的所有内容已删除{Colors.RESET}")
			break
		except PermissionError:
			sleep(0.1)
		except Exception as e:
			print(f"删除文件时发生错误: {e}")

if __name__ == '__main__':
	file_path = f"{system_path}\\阅读词汇.txt"
	words = get_words_from_txt(file_path)
	total_words = len(words)
	clear_screen()
	print(f'{Colors.MAGENTA}{Colors.BOLD}################## 单词导入成功，开始记单词吧 #################{Colors.RESET}')
	# print(words)
	# result = search_word_in_dict_youdao(words[0])
	# format_print(result)
	while words:
		print(f'{Colors.CYAN}{Colors.BOLD}########################     {total_words - len(words) + 1} / {total_words}     #######################{Colors.RESET}')
		word = random_return_word(words)
		phonetic = get_phonetic(word)
		lengths = [len(word),len(phonetic)]
		form = "+-" + '-+-'.join(['-' * length for length in lengths])
		print(form)
		print(f"| {Colors.LIGHT_RED}{Colors.BOLD}{word}{Colors.RESET} | {Colors.LIGHT_GREEN}{Colors.BOLD}{phonetic}{Colors.RESET}")
		print(form) # 这里输出写的有点丑，需要改改
		read_word(word)
		pause("请按任意键展示翻译...[Q/q]uite,[E/e]xit")
		result = search_word_in_dict_youdao(word)
		format_print(result)
		pause("请按任意键进入下一个单词...[Q/q]uite,[E/e]xit")
		clear_screen()
	print(f"{Colors.GREEN}恭喜你已完成 {file_path} 中的所有单词{Colors.RESET}")
	clear_temp_folder(temp_folder_path)
	# clear_screen()
	# search_word_mode()
	# clear_temp_folder(temp_folder_path)






# 测试使用代码如下
# https://dict.youdao.com/result?word=pamphlet&lang=en
# url = "http://dict.youdao.com/suggest?num=10000&ver=3.0&doctype=json&cache=false&le=en&q=parasite"
# result = requests.get(url)
# datas = json.loads(result.text)["data"]["entries"]
# # print(datas)
# for data in datas:
# 	print(f'{data["entry"]}\t:\t{data["explain"]}')
# 	# print(data["entry"])
# 发音测试 url
# https://dict.youdao.com/pronounce/base?product=webdict&appVersion=1&client=web&mid=1&vendor=web&screen=1&model=1&imei=1&network=wifi&keyfrom=dick&keyid=voiceDictWeb&mysticTime=1732214090963&yduuid=abcdefg&le=&phonetic=&rate=4&word=parasite&type=2&id=&sign=e06e415d9a0fdce5f43263531a16264d&pointParam=appVersion,client,imei,keyfrom,keyid,mid,model,mysticTime,network,product,rate,screen,type,vendor,word,yduuid,key
# http://dict.youdao.com/dictvoice?type={2}&audio={word}
"""
POST /jsonapi_s?doctype=json&jsonversion=4 HTTP/1.1
Accept: application/json, text/plain, */*
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: keep-alive
Content-Length: 90
Content-Type: application/x-www-form-urlencoded
Cookie: OUTFOX_SEARCH_USER_ID=347271256@125.111.240.36; OUTFOX_SEARCH_USER_ID_NCOO=111453347.7696337; __yadk_uid=JoYKFYkvcz6D6ngbfdGHhgsLTP6OjBOv; rollNum=true; NTES_YD_SESS=AR8NKNjGA__cjtKjkvyJ75Br0FnKTnEeF0TDskfKttvzBlf2BpU6Vj_WELUTdNssJwKOKE55FQ0VBeFD5HuJlI6KPVWrcFX7TY8QuZ0mXIvYlxE26TXo61zS.tygJ14dhNX122i4GPqFRhB8mGW6rVMZmXmYr84wCO0iIdKaYnROe1xDmUAu9hZ0FaV0t2PChXcuWLjmVDA4mHq_168T_xArSBrtDGvggVUH0MFD6ge7C; NTES_YD_PASSPORT=Vt_7ovtnSbaHsBfQmRsfPe7yZC1BL27ZjK.howW.ubvq7LHE7Muc9bSTw.uhkYffNotAtw22ydXYeQaqgebW_1pbWNjuAUtnpw0om3tPLYXjVept1eszpDwDRn9ZeSj98tlVTzENVjWAdqUqWd6o0oNPhlwMuu.rI9.lhxZ__BqXNQwX5MpqReWns_bIQhQjdTDGrG3C4VhXg2y5WpqbOqMKQICQuVM1V; S_INFO=1730996844|0|0&60##|13123831275; P_INFO=13123831275|1730996844|1|dict_logon|00&99|null&null&null#zhj&null#10#0|&0||13123831275; DICT_SESS=v2|UZPoGIj6Op4PMllhfwS0puhfJK6LeFRJFnL6KhMQ4RkGOMOG0M6LROWPMwyOMPB0OGhfzlhfOE0Ol6LPuhLlY0QBnf6zhf6K0; DICT_PERS=v2|urs-phone-web||DICT||web||-1||1730996845109||240e:878:33:2aef:bcb2:8529:ff38:75c||urs-phoneyd.a00f3e215914482b9@163.com||PFRHOfkL640p4nfq40MOGRJK0fkfRMOWRgFk4ezhMUWRwLkMwunMQBRPShLJ4kLgFRz5P4JLhHPK06BRHTFhMwz0; DICT_LOGIN=3||1730996845113; DICT_UT=wxoXQUDjw04zcnAAmFv1gu6qKpAyXk; _uetsid=1762daa09d2511ef947ad93261243c96; _uetvid=4df676e050f511efb42ff1d0a99dff8c; ___rl__test__cookies=1730997116290
Host: dict.youdao.com
Origin: https://dict.youdao.com
Referer: https://dict.youdao.com/result?word=lj%3Apamphlet&lang=en
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0
sec-ch-ua: "Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"

q=lj%3Apamphlet&le=en&t=8&client=web&sign=fc8d882ae4e78248ef4a114d43856a85&keyfrom=webdict&doctype=json&jsonversion=4
"""
# url1 = "https://dict.youdao.com/result?word=pamphlet&lang=en"
# result1 = requests.get(url1)
# print(result1.text)

# url2 = "http://dict.youdao.com/w/eng/pamphlet/#keyfrom=dict2.index"
# result2 = requests.get(url2)
# print(result2.text)