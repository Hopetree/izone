import re
import asyncio
import aiohttp
from blog.models import FriendLink


class LinkChecker:
    def __init__(self, site_link=None, white_list=None):
        """
        :param site_link: 需要在友链页面中检验的外链
        :param white_list: 白名单中的友链将不会被校验
        """
        self.site_link = site_link
        self.white_list = white_list or []
        self.result = {
            'active_num': 0,
            'to_not_show': 0,
            'to_show': 0,
            'version': '20240924.04'
        }
        self.lock = asyncio.Lock()  # 创建一个锁，用于保护共享数据

    async def get_link_status(self, session, url):
        """
        异步获取链接状态码和网页内容
        :param session: aiohttp 的 session 实例
        :param url: 需要请求的 URL
        :return: 状态码和网页文本内容
        """
        try:
            async with session.get(url, timeout=5) as response:
                code = response.status
                text = await response.text()
                return code, text
        except Exception as e:
            return None, str(e)

    async def check_link(self, session, active_friend):
        """
        校验单个友链的状态
        :param session: aiohttp 的 session 实例
        :param active_friend: FriendLink 模型实例
        :return: None
        """
        # 白名单友链直接设置成可访问
        if active_friend.name in self.white_list:
            if not active_friend.is_show:
                active_friend.is_show = True
                active_friend.not_show_reason = ''
                async with self.lock:
                    self.result['to_show'] += 1
                active_friend.save(update_fields=['is_show', 'not_show_reason'])
            return

        # 使用锁保护对共享数据 result 的操作
        async with self.lock:
            self.result['active_num'] += 1

        if active_friend.is_show:
            code, text = await self.get_link_status(session, active_friend.link)
            if code != 200:
                active_friend.is_show = False
                active_friend.not_show_reason = f'网页请求返回{code}'
                async with self.lock:
                    self.result['to_not_show'] += 1
            elif self.site_link and not re.findall(self.site_link, text):
                active_friend.is_show = False
                active_friend.not_show_reason = f'网站未设置本站外链'
                async with self.lock:
                    self.result['to_not_show'] += 1
            active_friend.save(update_fields=['is_show', 'not_show_reason'])
        else:
            code, text = await self.get_link_status(session, active_friend.link)
            if code == 200:
                if not self.site_link or re.findall(self.site_link, text):
                    active_friend.is_show = True
                    active_friend.not_show_reason = ''
                    async with self.lock:
                        self.result['to_show'] += 1
                    active_friend.save(update_fields=['is_show', 'not_show_reason'])

    async def check_all_links(self):
        """
        异步检查所有友链
        """
        active_friend_list = FriendLink.objects.filter(is_active=True)
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_link(session, friend) for friend in active_friend_list]
            await asyncio.gather(*tasks)

        # 返回结果
        return self.result

    def run(self):
        """
        启动异步任务，检查友链
        """
        try:
            # 获取当前事件循环，如果没有则创建一个新的
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # 在非主线程中运行时可能没有默认的事件循环，因此需要手动创建一个
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # 使用事件循环执行任务并返回结果
        return loop.run_until_complete(self.check_all_links())


def action_check_friend_links(site_link=None, white_list=None):
    checker = LinkChecker(site_link, white_list)
    result = checker.run()  # 正确返回 result
    return result


# 用法示例
if __name__ == '__main__':
    r = action_check_friend_links(site_link='https://tendcode.com', white_list=['TendCode'])
    print(r)
