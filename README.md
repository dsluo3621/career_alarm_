process_grades(): search student_id, course_id, assignment_title for student who has a score less than 50.


process_attendance(): search student_id, course_id, date for student who has a status of 0 (lack of attendance).


process_student_alarm(): search student_id for who meet the requirement to be regarded as in risk.

structure of the file:
my_project/
├── code/
│   └── main.py
├── data/
│   ├── grades.csv
│   └── attendance_time.csv  # 确保此文件存在
└── output/
