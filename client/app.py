import datetime
import pathlib
import time

import schedule
import os
import subprocess

from loguru import logger

from api import Api
from settings import Settings

setting = Settings()


# 获取当前系统是windows还是linux
def get_system():
    if os.name == "nt":
        return "windows"
    elif os.name == "posix":
        return "linux"
    else:
        return "unknown"


def run_script():
    file = pathlib.Path(setting.script)
    print("系统: ", get_system(), "执行: ", setting.script)

    if file.is_file() and file.exists():
        if get_system() == "windows":
            os.system(f"start {file}")
        elif get_system() == "linux":
            subprocess.Popen(["sh", file])
        else:
            print("unknown system")
    elif file.is_file() and not file.exists():
        print("文件不存在")
    elif not file.is_file():
        # 直接作为脚本执行
        if get_system() == "windows":
            os.system(f"start {setting.script}")
        elif get_system() == "linux":
            subprocess.Popen(["sh", setting.script], )
        else:
            print("unknown system")


def run():
    api = Api()
    content = api.get_by_name(setting.device_name)
    if content["status"] == "failed":
        # 执行shell文件
        api = Api()
        content["last_execute_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        api.update_watch(content)
        run_script()
        time.sleep(60 * 5)


def main():
    try:
        run()
    except Exception as e:
        logger.exception(e)
        logger.error("执行失败")


if __name__ == '__main__':
    schedule.every(setting.interval).seconds.do(main)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)
