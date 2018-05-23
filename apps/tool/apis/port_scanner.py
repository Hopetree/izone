# -*- coding: utf-8 -*-
'''
利用 socket 的链接来扫描端口
'''
import queue
import threading
import socket


class PortScanner:
    def __init__(self, host, ports):
        '''
        :param host: host地址
        :param ports: 需要扫描的端口，是一个列表
        '''
        self.host = host
        self.ports = ports
        self.q = queue.Queue()
        self.r = queue.Queue()

    def scaning(self):
        while not self.q.empty():
            port = self.q.get()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.2)
                s.connect((host, port))
                s.close()
            except:
                self.r.put((port, 'CLOSE'))
            else:
                self.r.put((port, 'OPEN'))

    def main(self):
        for each in self.ports:
            self.q.put(each)
        result = []
        ths = []
        max = len(self.ports)
        # 设置线程数
        n = max if max <= 10 else 10
        for i in range(n):
            t = threading.Thread(target=self.scaning)
            t.start()
            ths.append(t)
        for t in ths:
            t.join()
        while not self.r.empty():
            r = self.r.get()
            result.append({r[0]:r[1]})
        return result


if __name__ == '__main__':
    host = 'tendcode.com'
    ports = [22, 80, 1, 4, 4, 5, 56, 6, ]
    s = PortScanner(host, ports)
    k = s.main()
    print(k)
