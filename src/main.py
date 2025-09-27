#########################################################################
# CT60A0203 Introduction to Programming - Online teaching
# Name:Baishun Xing
# Student number:001600263
# Email:Baishun.Xing@student.lut.fi
# Date:30/11/2023
# By submitting this work, I certify that
#
# I used the internet to search for information and solutions,but I wrote the code by myself.
#
#########################################################################

import random
from datetime import datetime
from typing import Any, Callable, Literal, Mapping, Optional, Sequence, Set, Union

MAJOR_DICT: Mapping[str, str] = {'CE': 'Computational Engineering', 'EE': 'Electrical Engineering', 'ET': 'Energy Technology',             'ME': 'Mechanical Engineering',
                                 'SE': 'Software Engineering'}


class CommonBase:
    OBJECT_CACHE: Sequence[object] = []

    def __init__(self, id) -> None:
        self.id = id

    @staticmethod
    def generate_cur_year(format: str) -> str:
        return datetime.now().strftime(format)

    @staticmethod
    def is_target_str_valid(s: Any) -> bool:
        return isinstance(s, str)

    @staticmethod
    def is_str(s: Any) -> bool:
        return isinstance(s, str) and s.isalpha()

    @staticmethod
    def read_data(path: str) -> Sequence[Sequence[Any]]:
        data = []
        with open(path, encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if not line.strip():
                    continue
                data.append(line.strip('\u000A').split(','))

        return data

    @staticmethod
    def init_cache() -> None:
        raise NotImplementedError()

    @classmethod
    def get_obj_from_cache_with_id(cls, id: Union[int, str]) -> Optional[Union['Course', 'Student']]:
        res = None
        for obj in cls.OBJECT_CACHE:
            if obj.id == id:
                res = obj

        return res

    @classmethod
    def is_id_valid(cls, id: Union[int, str]) -> bool:
        if cls.get_obj_from_cache_with_id(id) is not None:
            return True
        else:
            try:
                id = int(id)
                return cls.get_obj_from_cache_with_id(int(id)) is not None
            except Exception as e:
                return False

    def get_txt_format(self) -> str:
        raise NotImplementedError()


class Course(CommonBase):
    OBJECT_CACHE: Sequence['Course'] = []

    def __init__(self, id: str, name: str, point: int) -> None:
        self.name = name
        self.point = point
        self.teacher: Sequence[str] = []
        super().__init__(id)

        Course.OBJECT_CACHE.append(self)

    @staticmethod
    def init_cache() -> None:
        data_path = './data/courses.txt'
        data = Course.read_data(data_path)
        for d in data:
            if len(d) < 4:
                continue
            c = Course(d[0], d[1], int(d[2]))
            teachers = d[3:]
            for t in teachers:
                c.teacher.append(t)

    @staticmethod
    def find_course(target: str) -> Sequence['Course']:
        res = []
        for c in Course.OBJECT_CACHE:
            if target in c.name:
                res.append(c)

            else:
                for t in c.teacher:
                    if target in t:
                        res.append(c)
                        break

        return res

    def get_txt_format(self) -> str:
        s = f'{self.id},{self.name},{self.point}'
        for t in self.teacher:
            s += f',{t}'
        return s


class Student(CommonBase):
    MAIL_EXTENSION = '@lut.fi'
    ID_CACHE: Set[int] = set()
    OBJECT_CACHE: Sequence['Student'] = []

    def __init__(self, last_name: str, first_name: str, major: Literal['CE', 'EE', 'ET', 'ME', 'SE']) -> None:
        self.last_name = last_name
        self.first_name = first_name
        self.major = major
        self.cur_year = Student.generate_cur_year('%Y')
        super().__init__(self.generate_id())
        self.mail = self.generate_mail()

        Student.OBJECT_CACHE.append(self)

    @staticmethod
    def init_cache() -> None:
        data_path = './data/students.txt'
        data = Student.read_data(data_path)
        for d in data:
            if len(d) != 6:
                continue
            s = Student(d[1], d[2], d[4])
            s.id = int(d[0])
            s.cur_year = d[3]
            s.mail = d[5]

            Student.ID_CACHE.add(int(d[0]))

    @staticmethod
    def find_student(name: str) -> Sequence['Student']:
        targets = []
        for stu in Student.OBJECT_CACHE:
            if name in stu.first_name or name in stu.last_name:
                targets.append(stu)

        return targets

    @staticmethod
    def is_target_str_valid(tar: str) -> bool:
        return Student.is_str(tar) and len(tar.strip()) >= 3

    @staticmethod
    def is_name_valid(name: str) -> bool:
        return Student.is_str(name) and name == name.capitalize()

    @staticmethod
    def is_major_valid(major: str) -> bool:
        if not isinstance(major, str):
            return False
        major = major.upper()
        return major in ['CE', 'EE', 'ET', 'ME', 'SE']

    def generate_id(self) -> int:
        while True:
            id = random.randint(10000, 100000)
            if id not in Student.ID_CACHE:
                Student.ID_CACHE.add(id)
                return id

    def generate_mail(self) -> str:
        return f'{self.first_name}.{self.last_name}{Student.MAIL_EXTENSION}'

    def write_to_file(self) -> None:
        with open('./data/students.txt', mode='a', encoding='utf-8') as file:
            file.write(self.get_txt_format() + '\u000A')

    def get_txt_format(self) -> str:
        return f'{self.id},{self.first_name},{self.last_name},{self.cur_year},{self.major},{self.mail}'


class Record:
    OBJECT_CACHE: Sequence['Record'] = []

    def __init__(self, course_id: str, stu_id: int, date_str: str, grade: int) -> None:
        self.course = Course.get_obj_from_cache_with_id(course_id)
        self.stu = Student.get_obj_from_cache_with_id(stu_id)
        self.date_str = date_str
        self.date = datetime.strptime(date_str, '%d/%m/%Y')
        self.grade = grade

        Record.OBJECT_CACHE.append(self)

    @staticmethod
    def init_cache() -> None:
        data_path = './data/passed.txt'
        data = Course.read_data(data_path)
        for d in data:
            if len(d) < 4:
                continue
            course_id = d[0]
            stu_id = int(d[1])
            dt = d[2]
            grade = int(d[3])

            record = Record(course_id, stu_id, dt, grade)

    @staticmethod
    def get_record_from_cache_with_all_id(course_id, stu_id) -> Optional['Record']:
        for r in Record.OBJECT_CACHE:
            if r.course.id == course_id and r.stu.id == stu_id:
                return r

        return None

    @staticmethod
    def get_record_from_cache_with_stu_id(stu_id: int) -> Sequence['Record']:
        res = []
        for r in Record.OBJECT_CACHE:
            if r.stu.id == stu_id:
                res.append(r)

        return res


def console_msg(msg: str) -> None:
    s = '\033[91m' + msg + '\033[0m'
    print(s)


def show_menu() -> str:
    menu_str = """
    You may select one of the following:
    1) Add student
    2) Search student
    3) Search course
    4) Add course completion
    5) Show student's record
    0) Exit
    """

    print(menu_str)
    command = input("What is your selection?\u000A")

    return command


def get_input_with_loop(msg: str, func: Callable[[Any], Any], *args) -> str:
    while True:
        console_msg(msg)
        tmp = input()
        if func(tmp, *args):
            return tmp


def add_student() -> None:
    first_name = get_input_with_loop(
        'Names should contain only letters and start with capital letters.\u000AEnter the first name of the student:', Student.is_name_valid)
    last_name = get_input_with_loop(
        'Names should contain only letters and start with capital letters.\u000AEnter the last name of the student:', Student.is_name_valid)
    major = get_input_with_loop("""
            Select student's major:
            CE: Computational Engineering
            EE: Electrical Engineering
            ET: Energy Technology
            ME: Mechanical Engineering
            SE: Software Engineering
            What is your selection?
                """, Student.is_major_valid)
    s = Student(last_name, first_name, major)
    s.write_to_file()

    console_msg('Student added successfully!')


def show_formatted_data(lst) -> None:
    if lst:
        for s in lst:
            console_msg(s.get_txt_format())
    else:
        console_msg('None')


def search_student() -> None:
    name = get_input_with_loop(
        'Give at least 3 characters of the students first or last name:', Student.is_target_str_valid)
    stu_lst = Student.find_student(name.capitalize())
    show_formatted_data(stu_lst)


def search_course() -> None:
    name = get_input_with_loop(
        'Give at least 3 characters of the name of the course or the teacher:', Course.is_target_str_valid)
    course_lst = Course.find_course(name)
    show_formatted_data(course_lst)


def add_course() -> None:
    course_id = get_input_with_loop('Give the course ID:', Course.is_id_valid)
    stu_id = get_input_with_loop('Give the student ID:', Student.is_id_valid)

    course_target = Course.get_obj_from_cache_with_id(course_id)
    stu_target = Student.get_obj_from_cache_with_id(int(stu_id))
    record = Record.get_record_from_cache_with_all_id(course_id, stu_id)

    while True:
        grade = input('Give the grade:\u000A')
        if record is not None and int(grade) < record.course.point:
            console_msg(
                f'Student has passed this course earlier with grade {record.grade}\u000A')
            return
        if int(grade) > course_target.point:
            console_msg('Grade is not a correct grade.\u000A')
            continue
        break

    while True:
        dt_str = input('Enter a date (DD/MM/YYYY):\u000A')
        try:
            dt = datetime.strptime(dt_str, '%d/%m/%Y')
        except Exception as _:
            console_msg('Invalid date format. Use DD/MM/YYYY. Try again!')
            continue
        if dt > datetime.now():
            console_msg('Input date is later than today. Try again!')
            continue
        if (datetime.now() - dt).days > 30:
            console_msg('Input date is older than 30 days. Contact "opinto".')
            continue
        console_msg('Input date is valid.')
        break

    with open('./data/passed.txt', 'a') as wfile:
        wfile.write(f'{course_id},{stu_id},{dt_str},{grade}\u000A')

    console_msg('Record added!')


def show_record() -> None:
    stu_id: int = int(get_input_with_loop('Student ID:', Student.is_id_valid))
    res = Record.get_record_from_cache_with_stu_id(stu_id)
    stu = Student.get_obj_from_cache_with_id(stu_id)

    s = f'Student ID: {stu.id}\u000AName: {stu.first_name}, {stu.last_name}\u000AMajor:{MAJOR_DICT.get(stu.major)}\u000AEmail: {stu.mail}'
    console_msg(s)
    console_msg('')
    console_msg('Passed courses:')
    console_msg('')

    for r in res:
        s1 = f'Course ID: {r.course.id}, Name: {r.course.name}, Credits: {r.course.point}'
        teachers = ''
        for t in r.course.teacher:
            teachers += f'{t}, '
        teachers = teachers.strip(',').strip()
        s2 = f'Date: {r.date_str}, Teacher(s): Linda Chen, grade: {r.grade}'

        console_msg(s1)
        console_msg(s2)
        console_msg('')


def is_command_valid(command: str) -> bool:
    if not command.isdigit():
        console_msg("Command is not a number Please try again")
        return False

    if command not in COMMAND_RANGE:
        console_msg("The command is not within the specified range")
        return False

    return True


HANDLE_FUNC_DICT: Mapping[int, Callable[[], None]] = {
    1: add_student, 2: search_student, 3: search_course, 4: add_course, 5: show_record}
COMMAND_RANGE = [f'{i}' for i in range(6)]


def main() -> None:
    Student.init_cache()
    Course.init_cache()
    Record.init_cache()

    while True:
        command = show_menu()
        if not is_command_valid(command):
            continue

        command = int(command)
        if 0 == command:
            console_msg('byebye')
            break
        func = HANDLE_FUNC_DICT.get(command)
        func()


if __name__ == '__main__':
    main()
