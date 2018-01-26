# -*- coding: utf-8 -*-
from user_agent import generate_user_agent


def get_user_agent(os=None, navigator=None, device_type=None):
    try:
        u = generate_user_agent(os=os, navigator=navigator, device_type=device_type)
    except Exception as e:
        u = str(e)
    return u


if __name__ == '__main__':
    get_user_agent()
