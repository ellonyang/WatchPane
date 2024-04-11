import datetime
from typing import Optional

from database import WatchModel, Session, select, curd
from fastapi import FastAPI, Depends, HTTPException

import schemas
from settings import Settings

setting = Settings()

app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@app.get("/watches/order", response_model=list[schemas.WatchSchema])
async def get_watches_order(db=Depends(get_db)):
    data = curd.all(db)
    return data


@app.get("/watches", response_model=list[schemas.WatchSchema])
async def get_watches(interval: Optional[int] = None, db=Depends(get_db)):
    if interval is None:
        interval = setting.check_interval
    data = curd.filter_by_last_check_at(interval, db)
    return data


@app.post("/update", )
async def update_watch(watch: schemas.WatchUpdateSchema, db=Depends(get_db)):
    watch = db.get(WatchModel, watch.id)
    watch.status = watch.status
    watch.last_check_at = datetime.datetime.now()
    watch.last_success_at = watch.last_success_at
    watch.last_executed_at = watch.last_executed_at
    watch.failed_count = watch.failed_count
    curd.update_by_model(watch, db)
    return {
        "code": 200,
        "msg": "success"
    }


@app.get("/watch", response_model=schemas.WatchSchema)
async def get_watch(watch_id: int, db=Depends(get_db)):
    return curd.get_watch(watch_id, db)


@app.get("/watch/by_name", response_model=schemas.WatchSchema)
async def get_watch_by_name(name: str, db=Depends(get_db)):
    return curd.get_by_name(name, db)


@app.post("/add_watch", response_model=schemas.WatchSchema)
async def add_watch(watch: schemas.WatchCreateSchema, db=Depends(get_db)):
    watch = WatchModel(name=watch.name, url=watch.url)
    if curd.get_by_name(watch.name, db):
        raise HTTPException(status_code=400, detail="name already exists")
    db.add(watch)
    db.commit()
    db.refresh(watch)
    return watch
