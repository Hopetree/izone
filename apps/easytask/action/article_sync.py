import json
import base64
import re
from datetime import datetime

import requests
import yaml

"""
同步博客文章到GitHub思路：
1. 查询出GitHub中指定目录中文章清单，文章统一会放到这里
2. 查询出博客中所有文章，得到一个清单
3. 判断是不是全量同步，如果是，则全量上传所有文章（先查询sha，然后拿着sha上传就是更新），否则增量上传
4. 更新index.md
5. 更新config.ts
关键点：vitepress的action中设置好规则，只有config.ts变动才触发发布操作
"""

def is_over_60_days_ago(date_str):
    """
    判断给定日期是否超过当前日期60天
    @param date_str: 日期字符串，格式 YYYY-MM-DD
    @return: True/False
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (datetime.today().date() - target_date).days > 60
    except ValueError:
        return False

class GitHubManager:
    def __init__(self, token, owner, repo, upload_msg=None, branch='main'):
        """
        初始化 GitHubManager 类
        :param token: GitHub 的个人访问令牌 (Personal Access Token)
        :param owner: 仓库的所有者（GitHub 用户名）
        :param repo: 仓库名称
        :param upload_msg: 文件上传的commit
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.upload_msg = upload_msg or 'Upload file via API'
        self.api_base_url = f"https://api.github.com/repos/{owner}/{repo}"

    def _get_headers(self):
        """
        获取 HTTP 请求头，包含认证信息
        :return: 带有授权信息的 headers
        """
        return {
            'Authorization': f'token {self.token}',
            'Content-Type': 'application/json'
        }

    def _list_files_in_directory(self, path=''):
        """
        列举 GitHub 仓库中指定目录下的所有文件和子目录
        :param path: 要查询的文件路径，默认为仓库根目录
        :return: 文件和子目录列表
        """
        url = f"{self.api_base_url}/contents/{path}"
        headers = self._get_headers()

        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code == 200:
            # 返回文件和目录的列表
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def list_all_files(self, path=''):
        """
        递归列举 GitHub 仓库中的所有文件
        :param path: 要查询的文件路径，默认为仓库根目录
        :return: 所有文件路径列表
        """
        files_list = []

        # 获取当前目录下的文件和目录
        items = self._list_files_in_directory(path)

        if items is None:
            return []

        for item in items:
            if item['type'] == 'file':
                # 如果是文件，保存文件的路径
                files_list.append(item['path'])
            elif item['type'] == 'dir':
                # 如果是目录，递归列举该目录下的文件
                files_list.extend(self.list_all_files(item['path']))

        return files_list

    def list_all_files_v2(self, path=''):
        """
        获取一个目录下所有文件，使用tree接口，而不是递归
        @param path:
        @return:
        """
        files = []
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            # 解析响应
            result = response.json()
            for item in result["tree"]:
                if item["path"].startswith(path) and item["type"] == "blob":
                    files.append(item["path"])
            return files
        else:
            raise Exception(
                f"Query failed with status code {response.status_code}: {response.text}")

    def get_file_sha(self, file_path):
        """
        获取 GitHub 上已有文件的 SHA 值
        :param file_path: 文件路径，相对于仓库根目录
        :return: 文件的 SHA 值，如果文件不存在，返回 None
        """
        url = f"{self.api_base_url}/contents/{file_path}"
        headers = self._get_headers()

        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code == 200:
            file_info = response.json()
            return file_info['sha']
        elif response.status_code == 404:
            print(f"File {file_path} does not exist.")
            return None
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def get_file_content(self, file_path):
        """
        获取 GitHub 上已有文件的内容
        :param file_path: 文件路径，相对于仓库根目录
        :return: 文件的内容，如果文件不存在，返回 None
        """
        url = f"{self.api_base_url}/contents/{file_path}"
        headers = self._get_headers()

        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code == 200:
            file_info = response.json()
            file_content = file_info['content']
            # GitHub 返回的是 base64 编码后的文件内容，所以需要解码
            decoded_content = base64.b64decode(file_content).decode('utf-8')
            return decoded_content
        elif response.status_code == 404:
            print(f"File {file_path} does not exist.")
            return None
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def upload_file(self, file_path, content, sha=None):
        """
        上传文件到 GitHub 仓库
        :param file_path: 上传文件的路径（包括文件名），相对于仓库根目录
        :param content: 文件的内容（字节或字符串）
        :param sha: 文件sha，已存在的时候可以更新
        """
        # 将内容编码为 base64 格式
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content

        encoded_content = base64.b64encode(content_bytes).decode('utf-8')

        url = f"{self.api_base_url}/contents/{file_path}"
        headers = self._get_headers()

        # 数据 payload，包含文件的 base64 编码内容和提交信息
        data = {
            "message": self.upload_msg,
            "content": encoded_content,
            "sha": sha
        }

        response = requests.put(url, json=data, headers=headers, timeout=20)

        if response.status_code == 201:
            print(f"File {file_path} uploaded successfully.")
            return response.json()
        elif response.status_code == 200:
            print(f"File {file_path} updated successfully.")
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None


class BlogManager:

    def __init__(self, base_url, base64_string, github_manager, source_media_url, target_media_url,
                 prefix='blog', target=None, full=False, white_list=None):
        """

        @param base_url:
        @param base64_string: 管理员用户密码base64值，用来做接口认证，这个接口只能管理员访问
        @param github_manager:
        @param prefix:
        @param target: 目标清单
        @param full: 是否全量同步
        @param white_list: 同步白名单，有白名单则直接同步
        """
        self.base_url = base_url
        self.api_headers = {'Authorization': f'Basic {base64_string}'}
        self.article_start_url = self.base_url + '/openapi/v1/articles/'
        self.subject_url = self.base_url + '/vitepress/subjects/'
        self.github_manager = github_manager
        self.prefix = prefix
        self.source_media_url = source_media_url
        self.target_media_url = target_media_url
        self.target = target or []
        self.full = full
        self.white_list = white_list or []
        self.free_articles = []  # 无专题文章
        self.free_path = 'free'  # 无专题文章子目录
        self.result = {
            'blog': {
                'total': 0,
                'article': 0,
                'subject': 0,
                'need_download': 0,
                'sync_failed': 0,
                'errors': [],
            },
            'github': {
                'total': len(self.target),
                'upload_success': 0,
                'upload_failed': 0
            }
        }

    def upload_all_articles(self, url):
        """
        递归请求接口上传所有文章
        @param url:
        @return:
        """
        resp = requests.get(url, headers=self.api_headers, timeout=10)
        data = resp.json()
        for item in data['results']:
            self.result['blog']['total'] += 1
            self.result['blog']['article'] += 1
            try:
                self.upload_article(item)
            except Exception as exc:
                # 单篇失败不中断整批，记录后继续
                self.result['blog']['sync_failed'] += 1
                self.result['blog']['errors'].append(
                    {'slug': item.get('slug'), 'error': str(exc)}
                )
        if data['next']:
            self.upload_all_articles(data['next'])

    def get_article_body(self, article_id):
        """
        请求详情接口获取文章正文
        列表接口为性能考虑不返回 body，只有通过过滤器、确定要上传的文章才按需取详情
        @param article_id: 文章 id
        @return: 正文 markdown
        """
        url = f'{self.base_url}/openapi/v1/articles/{article_id}/'
        resp = requests.get(url, headers=self.api_headers, timeout=10)
        resp.raise_for_status()
        return resp.json()['body']

    def upload_article(self, item):
        """
        上传一篇文章
        1. 有主题的传到主题pk下的路径中
        2. 没有主题的直接放到前缀下面
        @param item:
        @return:
        """
        if not item.get('subject'):
            file_path = f'{self.prefix}/{self.free_path}/{item["slug"]}.md'
            self.free_articles.append((item['title'], item['slug']))
        else:
            file_path = f'{self.prefix}/{item["subject"]}/{item["slug"]}.md'

        # ******************* 过滤器 *******************
        # 判断文章的更新日期，如果是60天前，就不要上传，已经超过上传频率
        if is_over_60_days_ago(item['update_date'][:10]):
            return
        # 全量更新则直接进入更新逻辑
        # 增量更新，要判断是否在白名单，当有白名单则强制更新白名单的，否则只添加新文件
        if not self.full:
            if self.white_list:
                if item['slug'] not in self.white_list:
                    return
            else:
                # 这里的判断逻辑是属于增量同步，只新增文件
                if file_path in self.target:
                    return
        # ******************* 过滤器 *******************

        # 能走到这里说明是要提交的文件，需要判断是否已经存在，存在则获取sha来更新
        self.result['blog']['need_download'] += 1
        if file_path in self.target:
            sha = self.github_manager.get_file_sha(file_path)
        else:
            sha = None

        body = self.deal_with_body(self.get_article_body(item['id']), title=item['title'])
        response = self.github_manager.upload_file(file_path, body, sha=sha)
        if response:
            self.result['github']['upload_success'] += 1
        else:
            self.result['github']['upload_failed'] += 1

    def upload_subject_index(self, subject_path, subject_content):
        """
        更新或提交一个专题的index.md文件
        @param subject_path:
        @param subject_content:
        @return:
        """
        if not self.full:
            if subject_path in self.target:
                return

        self.result['blog']['need_download'] += 1
        if subject_path in self.target:
            subject_index_sha = self.github_manager.get_file_sha(subject_path)
        else:
            subject_index_sha = None

        response = self.github_manager.upload_file(subject_path, subject_content,
                                                   subject_index_sha)
        if response:
            self.result['github']['upload_success'] += 1
        else:
            self.result['github']['upload_failed'] += 1

    def deal_with_body(self, body, title=None):
        """
        处理文章内容
        1. 替换图床地址
        2. 替换个性化的markdown语法
        @param title:
        @param body:
        @return:
        """
        # 添加标题
        if title:
            body = f"# {title}\n\n" + body

        # 处理绝对路径的媒体文件
        pattern = r'!\[.*?\]\(\s*({url}.*?)\s*(?:"|\))'.format(url=self.source_media_url)
        media_list = re.findall(pattern, body)
        if media_list:
            for old_url in media_list:
                new_url = old_url.replace(self.source_media_url, self.target_media_url)
                # URL编码：将空格编码为其对应的URL编码
                new_url = new_url.replace(' ', '%20')
                body = body.replace(old_url, new_url)

        # 处理相对路径的媒体文件
        pattern = r'!\[.*?\]\(\s*(/cdn/.*?)\s*(?:"|\))'
        media_list = re.findall(pattern, body)
        if media_list:
            for old_url in media_list:
                new_url = old_url.replace('/cdn/', self.target_media_url)
                # URL编码：将空格编码为其对应的URL编码
                new_url = new_url.replace(' ', '%20')
                body = body.replace(old_url, new_url)

        # 处理markdown个性化语法: 消息块
        if ':::' in body:
            for _key in ['primary', 'secondary', 'success', 'info']:
                body = body.replace(f'::: {_key}', '::: tip')

        return body

    def upload_features_and_sidebar(self):
        features = {'features': []}
        sidebar = {}
        data = requests.get(self.subject_url, timeout=10).json()['data']
        for subject in data:
            features['features'].append({
                'title': subject['name'],
                'details': subject['description'],
                'link': f'/{self.prefix}/{subject["pk"]}/',
                'linkText': '查看主题文章',
                'icon': '📚'
            })

            sidebar[f'/{self.prefix}/{subject["pk"]}/'] = []
            for topic in subject['items']:
                topic_data = {'text': topic['name'], 'collapsed': False, 'items': []}
                for article in topic['items']:
                    topic_data['items'].append({
                        'text': article['title'],
                        'link': f'/{self.prefix}/{subject["pk"]}/{article["slug"]}'
                    })
                sidebar[f'/{self.prefix}/{subject["pk"]}/'].append(topic_data)

            # 创建专题index.md文件，全量更新则全部更新，否则只新增
            self.result['blog']['subject'] += 1
            self.result['blog']['total'] += 1
            subject_path = f'{self.prefix}/{subject["pk"]}/index.md'
            subject_content = f"# {subject['name']}\n\n{subject['description']}"
            self.upload_subject_index(subject_path, subject_content)

        # 添加无专题文章的左侧导航
        sidebar[f'/{self.prefix}/{self.free_path}/'] = [
            {'text': '无分类文章', "collapsed": False, 'items': []}
        ]
        self.result['blog']['subject'] += 1
        self.result['blog']['total'] += 1
        free_subject_path = f'{self.prefix}/{self.free_path}/index.md'
        free_subject_content = f"# 无专题文章"
        self.upload_subject_index(free_subject_path, free_subject_content)
        for article_title, article_slug in self.free_articles:
            sidebar[f'/{self.prefix}/{self.free_path}/'][0]['items'].append({
                'text': article_title,
                'link': f'/{self.prefix}/{self.free_path}/{article_slug}'
            })

        # 添加一个无专题文章块
        features['features'].append({
            'title': '其他文章',
            'details': '未分类文章',
            'link': f'/{self.prefix}/{self.free_path}/',
            'linkText': '查看其他文章',
            'icon': '📘'
        })

        # 补齐内容，保证每行4个
        features_count = len(features['features'])
        if features_count % 4 != 0:
            for i in range(4 - features_count % 4):
                features['features'].append({
                    'title': '待完成',
                    'details': '未完待续',
                    'icon': '📝'
                })

        # 生成 README.md 中文章导航，更新README.md文件
        subject_dict = {f['link']: f['title'] for f in features['features'] if f.get('link')}
        toc_dict = {subject_dict[k]: v for k, v in sidebar.items()}
        # print(json.dumps(toc_dict, indent=2, ensure_ascii=False))
        toc_markdown = '## 文章导航\n'
        for k, v in toc_dict.items():
            subject_toc = f'\n- **{k}**'
            for topic in v:
                topic_toc = f'\n\t- {topic["text"]}'
                for article in topic['items']:
                    article_toc = f'\n\t\t- [{article["text"]}]({article["link"]}.md)'
                    topic_toc += article_toc
                subject_toc += topic_toc
            toc_markdown += subject_toc
        # print(toc_markdown)
        readme_tpl_content = self.github_manager.get_file_content('README.md.tpl')
        readme_sha = self.github_manager.get_file_sha('README.md')
        readme_content = readme_tpl_content.replace('{{article_toc}}', toc_markdown)
        response = self.github_manager.upload_file('README.md', readme_content, readme_sha)
        if response:
            self.result['github']['README.md'] = True
        else:
            self.result['github']['README.md'] = False

        # 使用模板写入index.md
        index_tpl_content = self.github_manager.get_file_content('index.md.tpl')
        features_yaml_text = yaml.dump(features, default_flow_style=False, allow_unicode=True)
        index_content = index_tpl_content.replace('{{features}}', features_yaml_text)
        index_sha = self.github_manager.get_file_sha('index.md')
        # print(index_content)
        response = self.github_manager.upload_file('index.md', index_content, index_sha)
        if response:
            self.result['github']['index.md'] = True
        else:
            self.result['github']['index.md'] = False

        # 使用模板写入config.ts
        config_tpl_content = self.github_manager.get_file_content('.vitepress/config.ts.tpl')
        sidebar_json_text = json.dumps(sidebar, ensure_ascii=False, indent=2)
        update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_content = config_tpl_content.replace('{{sidebar}}', sidebar_json_text)
        save_content = save_content.replace("{{date}}", update_date)
        config_sha = self.github_manager.get_file_sha('.vitepress/config.ts')
        # print(save_content)
        response = self.github_manager.upload_file('.vitepress/config.ts', save_content, config_sha)
        if response:
            self.result['github']['config.ts'] = True
        else:
            self.result['github']['config.ts'] = False


def action_article_to_github(base_url, base64_string, token, owner, repo,
                             source_media_url, target_media_url,
                             msg='Upload file via API',
                             full=False, white_list=None, prefix='blog'):
    """
    @param base64_string:
    @param target_media_url:
    @param source_media_url:
    @param base_url:
    @param token:
    @param owner:
    @param repo:
    @param msg:
    @param full:
    @param white_list:
    @param prefix:
    @return:
    """
    white_list = white_list or []
    github_manager = GitHubManager(token, owner, repo, msg)
    # 1. 查询GitHub中所有文件
    github_files = github_manager.list_all_files_v2(path=prefix)

    blog_manager = BlogManager(base_url, base64_string, github_manager,
                               source_media_url, target_media_url, prefix,
                               target=github_files,
                               full=full, white_list=white_list)

    # 2. 全量/增量/白名单同步文章
    blog_manager.upload_all_articles(blog_manager.article_start_url)
    # 3. 更新主页文件和左侧导航文件
    blog_manager.upload_features_and_sidebar()

    return blog_manager.result


if __name__ == '__main__':
    # source_media_url = 'https://tendcode.com/cdn/'
    # target_media_url = 'https://cdn.jsdelivr.net/gh/Hopetree/blog-img@main/'

    keyword_arguments = '{}'
    task_args = json.loads(keyword_arguments)
    task_result = action_article_to_github(**task_args)
    print(json.dumps(task_result, indent=2, ensure_ascii=False))
