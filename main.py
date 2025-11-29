import os
from pathlib import Path
import pandas as pd


# search student_id, course_id, assignment_title for student who has a score less than 50
def process_grades():
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent

    # 构建数据文件路径：上级目录 -> data -> grades.csv
    input_path = current_dir.parent / 'data' / 'grades.csv'

    # 构建输出目录和文件路径：上级目录 -> output -> grade_alarm.csv
    output_dir = current_dir.parent / 'output'
    output_path = output_dir / 'grade_alarm.csv'

    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 读取CSV文件
        df = pd.read_csv(input_path, encoding='utf-8')

        # 检查必要的列是否存在
        required_columns = ['student_id', 'course_id', 'assignment_title', 'score']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"CSV文件缺少必要的列: {missing_columns}")

        # 筛选出score < 50的行，并只保留student_id和course_id列
        alarm_df = df[df['score'] < 50][['student_id', 'course_id', 'assignment_title']].copy()

        # 重置索引（可选）
        alarm_df = alarm_df.reset_index(drop=True)

        # 保存结果到新的CSV文件
        alarm_df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"处理完成！共找到 {len(alarm_df)} 条score < 50的记录")
        print(f"结果已保存至: {output_path}")

        return alarm_df

    except FileNotFoundError:
        print(f"错误：找不到文件 {input_path}")
    except ValueError as e:
        print(f"错误：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def process_attendance():
    """处理考勤数据，筛选status < 1的记录"""
    current_dir = Path(__file__).parent
    input_path = current_dir.parent / 'data' / 'attendance_time.csv'  # 假设文件后缀是.csv
    output_dir = current_dir.parent / 'output'
    output_path = output_dir / 'attendance_alarm.csv'

    os.makedirs(output_dir, exist_ok=True)

    try:
        df = pd.read_csv(input_path, encoding='utf-8')
        required_columns = ['student_id', 'course_id', 'date', 'status']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"CSV文件缺少必要的列: {missing_columns}")

        # 筛选status < 1的记录，并选择指定列
        alarm_df = df[df['status'] < 1][['student_id', 'course_id', 'date']].copy().reset_index(drop=True)
        alarm_df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"\n考勤处理完成！共找到 {len(alarm_df)} 条status < 1的记录")
        print(f"结果已保存至: {output_path}")

        return alarm_df

    except FileNotFoundError:
        print(f"错误：找不到文件 {input_path}")
    except ValueError as e:
        print(f"错误：{e}")
    except Exception as e:
        print(f"发生错误：{e}")


def process_student_alarm():
    """整合考勤和成绩预警数据，生成学生预警信息"""
    current_dir = Path(__file__).parent
    output_dir = current_dir.parent / 'output'

    # 定义文件路径
    attendance_alarm_path = output_dir / 'attendance_alarm.csv'
    grade_alarm_path = output_dir / 'grade_alarm.csv'
    student_alarm_path = output_dir / 'student_alarm.csv'

    try:
        # 读取预警数据文件
        attendance_df = pd.read_csv(attendance_alarm_path, encoding='utf-8')
        grade_df = pd.read_csv(grade_alarm_path, encoding='utf-8')

        # 统计每个student_id的出现次数
        attendance_counts = attendance_df['student_id'].value_counts()
        grade_counts = grade_df['student_id'].value_counts()

        # 找出需要预警的学生
        alarm_students = []

        # 考勤预警（出现3次及以上）
        attendance_alarm_students = attendance_counts[attendance_counts >= 3].index.tolist()

        # 成绩预警（出现1次及以上）
        grade_alarm_students = grade_counts[grade_counts >= 1].index.tolist()

        # 合并所有需要预警的学生ID
        all_alarm_student_ids = set(attendance_alarm_students + grade_alarm_students)

        # 为每个学生确定预警类型
        for student_id in all_alarm_student_ids:
            in_attendance = student_id in attendance_alarm_students
            in_grade = student_id in grade_alarm_students

            if in_attendance and in_grade:
                alarm_type = 2  # 均符合
            elif in_attendance:
                alarm_type = 0  # 仅考勤
            else:
                alarm_type = 1  # 仅成绩

            alarm_students.append({
                'student_id': student_id,
                'type': alarm_type
            })

        # 创建DataFrame并保存
        student_alarm_df = pd.DataFrame(alarm_students)
        student_alarm_df = student_alarm_df.sort_values('student_id').reset_index(drop=True)
        student_alarm_df.to_csv(student_alarm_path, index=False, encoding='utf-8')

        print(f"\n学生预警处理完成！共找到 {len(student_alarm_df)} 名需要预警的学生")
        print(f"结果已保存至: {student_alarm_path}")

        return student_alarm_df

    except FileNotFoundError as e:
        print(f"错误：找不到文件 {e.filename}，请先运行考勤和成绩处理功能")
    except Exception as e:
        print(f"发生错误：{e}")


if __name__ == "__main__":
    # 处理成绩数据
    grade_result = process_grades()

    # 处理考勤数据
    attendance_result = process_attendance()

    # 处理学生预警
    if grade_result is not None and attendance_result is not None:
        student_result = process_student_alarm()

        # 显示结果预览
        if student_result is not None and not student_result.empty:
            print("\n=== 学生预警预览 ===")
            print(student_result.head())