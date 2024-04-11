import random
import time

import schedule
from h2o_wave import ui, site

from watchpane.api import Api

# Create columns for our issue table.
columns = [
    ui.table_column(name='名称', label='名称', max_width='300', cell_overflow='wrap'),
    ui.table_column(name='URL', label='URL', max_width='300', cell_overflow='wrap'),
    ui.table_column(name='tag', label='State', min_width='170px', cell_type=ui.tag_table_cell_type(name='tags', tags=[
        ui.tag(label='RUNNING', color='#D2E3F8'),
        ui.tag(label='FAILED', color='$red'),
        ui.tag(label='UNCHECK', color='$mint'),
    ]
                                                                                                   )),
    ui.table_column(name='检查时间', label='检查时间', data_type='time', sortable=True),
    ui.table_column(name='最后成功时间', label='最后成功时间', data_type='time', sortable=True),
    ui.table_column(name='最后执行时间', label='最后执行时间', data_type='time', sortable=True),
    ui.table_column(name='连续失败次数', label='连续失败次数', data_type='number', sortable=True),
]

page = site['/']


def run():
    api = Api()
    contents = api.all()
    data = [[content["name"], content["url"], content["status"], content["last_check_at"],
             content["last_success_at"], content["last_execute_at"], str(
            content["failed_count"])
             ]
            for content in contents]
    print(data)
    page['form'] = ui.form_card(box='1 1 -1 -1', items=[
        ui.table(
            name='watch',
            columns=columns,

            rows=[ui.table_row(
                name=str(content["id"]),
                cells=[content["name"], content["url"], content["status"], content["last_check_at"] or '',
                       content["last_success_at"] or '', content["last_execute_at"] or '', str(content["failed_count"])
                       ])
                for content in contents],
            groupable=True,
            downloadable=True,
            resettable=True,
            height='1000px',
        )
    ])
    page.save()


if __name__ == '__main__':
    schedule.every(1).minutes.do(run)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)
