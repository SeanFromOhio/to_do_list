from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
import re

engine = create_engine("sqlite:///todo.db?check_same_thread=False")

Base = declarative_base()


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    task = Column(String, default="Nothing to do!")
    deadline = Column(Date, default=datetime.today().date())

    def __repr__(self):
        return self.task


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def menu():
    while True:
        user_input = input("""
1) Today's tasks
2) Week's tasks
3) All tasks
4) Missed tasks
5) Add task
6) Delete task
0) Exit
""")
        if user_input == "1":
            today_tasks()

        elif user_input == "2":
            weeks_tasks()

        elif user_input == "3":
            all_tasks()

        elif user_input == "4":
            missed_tasks()

        elif user_input == "5":
            tasks_create()

        elif user_input == "6":
            delete_task()

        elif user_input == "0":
            print("\nBye!")
            break

        else:
            print("That was not an option, try again.")


def today_tasks():
    today_date = datetime.today().date()
    today_row = session.query(Task).filter_by(deadline=today_date).first()
    if today_row:
        return print(f"""
Today {datetime.today().strftime("%d %b")}:
{today_row.task}""")

    else:
        return print(f"""
Today {datetime.today().strftime("%d %b")}
Nothing to do!""")


def weeks_tasks():
    for i in range(7):
        next_day = datetime.today() + timedelta(days=i)
        next_day_format = datetime.date(next_day).strftime("%A %d %b")
        print(f"\n{next_day_format}:")

        day_row = session.query(Task).filter_by(deadline=next_day.date()).all()
        for n in range(1, len(day_row) + 1):
            print(f"{n}. {day_row[n-1]}")


def all_tasks():
    all_rows = session.query(Task).all()
    print("\nALL tasks:")
    i = 1
    for row in all_rows:
        deadline = row.deadline
        deadline_format = deadline.strftime("%d %b")

        print(f"{i}. {row.task}. {deadline_format}")
        i += 1


def missed_tasks():
    past_dates = session.query(Task).filter(Task.deadline <= datetime.today().date()).all()
    print("\nMissed tasks:")
    i = 1
    for task in past_dates:
        print(f"{i}. {task.task}. {task.deadline.strftime('%d %b')}")
        i += 1


def tasks_create():
    the_task = input("\nEnter task\n")
    the_deadline = input("Enter deadline. Format: YYYY-MM-DD\n")

    date_pattern = re.compile(r"\d\d\d\d-\d\d-\d\d")
    date_input_check = re.match(date_pattern, the_deadline)
    while date_input_check is None:
        print("That was not a valid date. Format: YYYY-MM-DD\n")
        the_deadline = input("Enter deadline\n")
        date_input_check = re.match(date_pattern, the_deadline)

    insert_deadline = datetime.strptime(the_deadline, "%Y-%m-%d")
    if the_task is None:
        new_row = Task(
            deadline=insert_deadline
        )
        session.add(new_row)
        session.commit()

    else:
        new_row = Task(
            task=the_task,
            deadline=insert_deadline
        )
        session.add(new_row)
        session.commit()
    print("The task has been added!")


def delete_task():
    tasks_by_date = session.query(Task).order_by(Task.deadline).all()
    print("\nChoose the number of the task you want to delete:")
    i = 1
    for prev_task in tasks_by_date:
        print(f"{i}. {prev_task.task}. {prev_task.deadline.strftime('%d %b')}")
        i += 1

    delete_select = input("\nInput selection: ")
    delete_select_format = re.compile(r"\d+")
    delete_select_check = re.match(delete_select_format, delete_select)

    while delete_select_check is None:
        print("That was not a valid date. Input positive number.")
        delete_select = input("Input selection: ")
        delete_select_check = re.match(delete_select_format, delete_select)

    id_check = session.query(Task).filter(Task.id).all()
    print(len(id_check))
    if int(delete_select) > len(id_check):
        print("Nothing to delete")
    else:
        session.query(Task).filter(Task.id == delete_select).delete()
        session.commit()
        print("The task has been deleted!")


menu()
