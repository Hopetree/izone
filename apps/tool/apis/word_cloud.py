import os
import re
from collections import Counter

import jieba

# 只显示前N个词
max_word = 80

root_path = os.path.dirname(__file__)
stopwords_path = os.path.join(root_path, 'stopwords')


def get_stop_words(stop_text, filename='ChineseStopWords.txt'):
    '''读取指定停用词文件'''
    fp = os.path.join(stopwords_path, filename)
    with open(fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    stop_words = [word.strip() for word in lines]
    if stop_text:
        input_stop_words = stop_text.strip().split('\n')
        if input_stop_words:
            stop_words.extend(input_stop_words)
    return stop_words


def get_word_count(text, stop_text):
    '''精确分词'''
    words = jieba.lcut(text)
    stop_words = get_stop_words(stop_text)
    new_words = [
        word for word in words if word not in stop_words and word.strip()
    ]
    # 删除纯数字
    if r'\d+' in stop_words:
        new_words = [
            word for word in new_words if not re.findall(r'^\d+$', word)
        ]
    c = Counter(new_words).most_common(max_word)
    result = [{'name': k, 'weight': v} for k, v in c]
    return result


def jieba_word_cloud(text, stop_text=None):
    '''成功返回200，失败500，可以将失败的报错输出到console日志'''
    try:
        result = get_word_count(text, stop_text)
        ret = {'result': result, 'code': 200, 'error': ''}
    except Exception as e:
        ret = {'code': 500, 'error': e}
    return ret


if __name__ == "__main__":
    fp = '/tmp/test.txt'
    with open(fp, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    print(jieba_word_cloud(text, stop_text='\n词\n'))
