# -*- coding: utf-8 -*-
IMAGE_LIST = ['busybox', 'centos', 'docker', 'fedora', 'golang', 'httpd',
              'java', 'jenkins/jenkins', 'jenkinsci/blueocean', 'memcached',
              'mongo', 'mysql', 'nginx', 'node', 'php', 'postgres', 'python',
              'rabbitmq', 'redis', 'registry', 'ruby', 'tomcat', 'ubuntu', 'wordpress']

if __name__ == '__main__':
    print(sorted(IMAGE_LIST))