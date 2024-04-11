import pathlib

import pandas as pd
from database import WatchModel, Session


def upload_by_excel(file_path):
    if pathlib.Path(file_path).suffix != ".csv":
        data = pd.read_csv(file_path, encoding='utf-8')
    elif pathlib.Path(file_path).suffix != ".xlsx":
        raise ValueError("文件格式错误")
    else:
        data = pd.read_excel(file_path)
    with Session() as session:
        for index, row in data.iterrows():
            # 批量添加,同名的不要重复添加
            watch = WatchModel(name=row['name'], url=row['url'])
            session.merge(watch)
        session.commit()


if __name__ == '__main__':
    upload_by_excel("watch.xlsx")