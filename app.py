from datetime import date
from typing import Annotated, Literal, Optional
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

class Order(BaseModel):
    number: int
    dateStart: date = date.today() 
    dateEnd: Optional[date] = None
    device: str
    problemType: str
    description: Optional[str] = None
    client: str
    master: Optional[str] = "Не назначен"
    status: Literal["в ожидании", "в работе", "Выполнено"] = "в ожидании"
    comment: Optional[str] = None

repo = [Order (number = 1, dateStart = "2024-09-27", device = "ноут", problemType = "отвал ГПУ", description = "Черное пятно",  client = "Роберт"), Order (number = 2, dateStart = "2024-09-17", device = "ноут", problemType = "отвал ЦП", description = "Черное пятно",  client = "Роберт"), Order (number = 3, device = "ноут", problemType = "взорвался", description = "Черное пятно",  client = "Роберт")] 

for o in repo:
    o.status = "Выполнено"
    o.dateEnd = date.today()

message = ""
lamp = False



@app.get("/")
async def get_orders():
    global message
    global lamp 
    if(lamp):
        buffer = message
        message = ""
        lamp = False
        return repo, buffer
    else:
        return repo


@app.post("/")
async def add_orders(order: Annotated[Order, Depends()]):
    repo.append(order)
    return "Данные успешно добавлены!"

@app.put("/")
async def update_orders(number: int, status: Literal["в ожидании", "в работе", "Выполнено"], description: str, master: str):
    global message
    global lamp 
    for i in repo:
        if number == i.number:
            if status == "Выполнено":
                i.dateEnd = date.today()
                i.status = status
            elif i.status != status:
                message = f"статус заявки №{i.number} изменён!"
                lamp = True
                i.status = status
            i.description = description
            i.master = master
            return "Данные успешно изменены!"
    raise HTTPException(status_code=404, detail="Заявка не найдена!")

@app.get("/search")
async def get_orders(number: int = None, description: str = None, master: str = None, problemType: str = None):
    for i in repo:
        if number == i.number or description == i.description or master == i.master or problemType == i.problemType:
            return i
    raise HTTPException(status_code=404, detail="Заявка не найдена!")


@app.get("/status_get")
async def get_status(number: int):
    for i in repo:
        if number == i.number:
         return f"статус заявки №{i.number}:  {i.status}" 
    raise HTTPException(status_code=404, detail="Заявка не найдена!")
        



@app.post("/master")
async def add_master(master: str, number: int):
    for i in repo:
        if number == i.number:
            if i.master == "Не назначен":
                i.master = master
            else: 
                i.master = f"{i.master}, {master}"
            return "Данные добавлены!"
    raise HTTPException(status_code=404, detail="Заявка не найдена!")

@app.post("/comment")
async def add_comment(comment: str, number: int):
    for i in repo:
        if number == i.number:
            if i.comment == None:
                i.comment = comment
            else: 
                i.comment = f"{i.comment}, {comment}"
            return "Комментарий добавлен!"
    raise HTTPException(status_code=404, detail="Заявка не найдена!")


@app.get("/stat")
async def get_stat():
    return f"Количество выполненных заявок: {count_complied()}", f"Среднее время выполнения заявки: {avg_date()}", f"Статистика по типам неисправностей: {faul_types()}"


def complete_orders():
    return[o for o in repo if o.status == 'Выполнено']

def count_complied():
    return len(complete_orders())

def faul_types():
    result = {}
    for o in repo:
        if o.problemType in result:
            result[o.problemType] += 1 
        else:
            result[o.problemType] = 1
    return result

def avg_date():
    times = []
    for i in complete_orders():
        times.append(i.dateEnd - i.dateStart)
    timesum = sum([t.days for t in times])
    ordCount = count_complied()
    result = timesum/ordCount
    return result



