# -*- coding: utf-8 -*-
"""
本模块负责管理aria2进程
"""

import os
import subprocess
from typing import Dict
import asyncio
import threading

# --------------------------#

ENCODING = "gbk"

# --------------------------#

cache: Dict[str, object] = {}


# def single_instance(cls: type):
#     """
#     单例模式装饰器，如果两个aria2进程一同开启必定端口冲突
#     :param cls: 要装饰的类
#     :return:
#     """
#
#     @wraps(cls)
#     def inner(*args, **kw):
#         class_name = cls.__name__
#         if class_name in cache:
#             return cache[class_name]
#         else:
#             instance = cls(*args, **kw)
#             cache[class_name] = instance
#             return instance
#     return inner


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:  # 加锁
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Aria2Server(metaclass=SingletonType):
    """
    aria2进程对象
    """

    def __init__(self, *args: str, daemon=False):
        """
        :param args: 启动aria2的命令行参数
        :param daemon: True:aria2随python解释器同生共死
        """
        if args:
            self.cmd = list(args)
        else:
            self.cmd = []
        if daemon:
            self.cmd.append('--stop-with-process={:d}'.format(os.getpid()))
        self.process = None
        self._is_running = False

    def start(self):
        self.process = subprocess.Popen(self.cmd)
        self._is_running = True

    def wait(self):
        """
        等待进程结束
        :return:
        """
        code = self.process.wait()
        self._is_running = False
        return code

    def terminate(self):
        self.process.terminate()
        return self.wait()

    def kill(self):
        self.process.kill()
        return self.wait()

    @property
    def pid(self):
        return self.process.pid

    @property
    def returncode(self):
        return self.process.returncode

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_running:
            self.terminate()


class AsyncAria2Server(Aria2Server):
    """
    aria2进程对象
    异步io
    """

    def __init__(self, *args: str, daemon=False):
        super().__init__(*args, daemon=daemon)

    async def start(self):
        program, *args = self.cmd
        self.process = await asyncio.create_subprocess_exec(program, *args)
        self._is_running = True

    async def wait(self):
        code = await self.process.wait()
        self._is_running = False
        return code

    async def terminate(self):
        self.process.terminate()
        return await self.wait()

    async def kill(self):
        self.process.kill()
        return await self.wait()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._is_running:
            await self.terminate()


if __name__ == "__main__":
    pass
