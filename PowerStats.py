PLUGIN_METADATA = {
    'id': 'powerstats',
    'version': '1.0.0-SHANPOST',
    'name': 'PowerStats',
    'description': 'Check Power Stats',
    'author': 'Forgot_Dream',
    'link': 'https://github.com/Forgot-Dream',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
    }
}

from mcdreforged.api.types import ServerInterface, Info

from threading import Event, Thread
from time import sleep
import os
import psutil

PowerM = None

Network_name = '以太网' # 检测的网络适配器名称
Check_time = 60 #检测间隔

class Power(Thread):
    def __init__(self,server : ServerInterface):
        super().__init__()
        self.MinecraftServer = server
        self.stop_event = Event()

    def stop(self):
        self.stop_event.set()

    def power_off(self):
        self.MinecraftServer.logger.info('[Power-OFF] 执行关机流程')
        os.system('shutdown -s -t 30') #延迟30s关机
        self.MinecraftServer.stop_exit()
        self.stop()#终止线程

    def check(self):
        stats = psutil.net_if_stats()
        try:
            if stats[Network_name][0] ==  False:
                return False
            else:
                return True
        except:
            return False

    def checktimer(self):
        if self.check() == False:
            self.MinecraftServer.logger.info('[Power-OFF] 确认网卡为离线状态')
            stats = 0
            for i in range(2): #二次确认
                sleep(5)
                if self.check():
                    stats += 1
                else:
                    self.MinecraftServer.logger.info('[Power-OFF] 确认网卡为离线状态')
            if stats == 0:
                self.power_off()
                return

    def run(self):
        while True:
            if self.stop_event.wait(1):
                break
            self.checktimer()
            sleep(Check_time)
        

def on_load(server : ServerInterface, info : Info):
    global PowerM
    PowerM = Power(server)
    PowerM.start()
    server.logger.info("定时器运行中 检测间隔：" + str(Check_time) + " s")
    

def on_unload(server : ServerInterface):
    PowerM.stop()
    server.logger.info("定时器已停止")