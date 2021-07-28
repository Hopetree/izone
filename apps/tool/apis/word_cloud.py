import os
import re
from collections import Counter

import jieba

# 只显示前N个词
from .common import OpenApi

MAX_WORD = 80

root_path = os.path.dirname(__file__)
stopwords_path = os.path.join(root_path, 'stopwords')


def get_stop_words(stop_text, filename='ChineseStopWords.txt'):
    """读取指定停用词文件"""
    _fp = os.path.join(stopwords_path, filename)
    with open(_fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    stop_words = [word.strip() for word in lines]
    if stop_text:
        input_stop_words = stop_text.strip().split('\n')
        if input_stop_words:
            stop_words.extend(input_stop_words)
    return stop_words


def get_word_count(text, stop_text):
    """精确分词"""
    words = jieba.lcut(text)
    stop_words = get_stop_words(stop_text)
    new_words = [
        word for word in words if word not in stop_words and word.strip()
    ]
    # 停用纯数字
    if 'num-' in stop_words:
        new_words = [
            word for word in new_words if not re.findall(r'^\d+$', word)
        ]
    # 停用长度为1的词
    if 'single-' in stop_words:
        new_words = [
            word for word in new_words if len(word) > 1
        ]
    c = Counter(new_words).most_common(MAX_WORD)
    result = [{'name': k, 'weight': v} for k, v in c]
    return result


def jieba_word_cloud(text, stop_text=None):
    """成功返回200，失败500，可以将失败的报错输出到console日志"""
    op = OpenApi()
    try:
        result = get_word_count(text, stop_text)
        op.data = {"list": result, "total": len(result), "max": MAX_WORD}
    except Exception as e:
        op.code = op.error_50001
        op.error = "请求错误，未获得词频统计"
        op.message = e
    return op.body


if __name__ == "__main__":
    fp = '/tmp/test.txt'
    with open(fp, 'r', encoding='utf-8') as f:
        tex = f.read().strip()
    print(jieba_word_cloud(tex, stop_text='\n词\nless-'))
