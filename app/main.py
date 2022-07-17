import os
import glob
from flask import Flask, send_file, request, redirect

app = Flask(__name__)

@app.route('/generateTimeTable')
def generatePDF():
    print(request.form.get('name'))
    _branch = request.args.get('_branch')
    _section = request.args.get('_section')
    _e1_code = request.args.get('_e1_code')
    _e1_teacher = request.args.get('_e1_teacher')
    _e2_code = request.args.get('_e2_code')
    _e2_teacher = request.args.get('_e2_teacher')
    
    pdfPattern = "app/*.pdf"
    files = glob.glob(pdfPattern)
    print(files)
    # for file in files:
    #     os.remove(file)
    
    pdfName = TimeTableCreator(_branch, _section, _e1_code, _e1_teacher, _e2_code, _e2_teacher, rows)
    print("Aaaaaaaaaaaaaaaaaaaaa pdfName : ", pdfName)
    print(os.listdir())
    return send_file("/app/" + pdfName, as_attachment=True)

@app.route('/download')
def downloadFile():
    path = "Examples.pdf"
    print("root path : ", path)
    path = os.path.join(app.root_path, path)
    print("root path : ", path)
    return send_file('check.pdf', as_attachment=True)

@app.route('/form-data', methods = ['POST'])
def formData():
    _class = request.form.get('class')
    _elective1 = request.form.get('elective1')
    _elective2 = request.form.get('elective2')
    
    if _class == "Select Class . . ." or _elective1 == "Select Elective 1 . . ." or _elective2 == "Select Elective 2 . . .":
        _class = "CSE 21"
        _elective1 = "CI_CS 2"
        _elective2 = "CRP_CS 4"
        
    _branch, _section = _class.split()
    _elective1, _elective2 = _elective1.split(), _elective2.split()
    print('elective 1 :', _elective1, ' elective 2 :', _elective2)
    _e1_teacher, _e2_teacher = _elective1[1], _elective2[1]
    _e1_code, _e2_code = _elective1[0].split('_')[0], _elective2[0].split('_')[0]
    
    return redirect(f"https://dhundo.herokuapp.com/generateTimeTable?_branch={_branch}&_section={_section}&_e1_code={_e1_code}&_e1_teacher={_e1_teacher}&_e2_code={_e2_code}&_e2_teacher={_e2_teacher}", code = 302)
    

import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def listUpperTransform(l):
    return [elem.upper() for elem in l]

central_db = open('app/dhundo_db.csv')
csvreader = csv.reader(central_db)

teacher_db = open('app/dhundo_teacher_db.csv')
teacher_csvreader = csv.reader(teacher_db)
teacherData = []
for row in teacher_csvreader:
    teacherData.append(row)

header = listUpperTransform(next(csvreader))

rows = []
for row in csvreader:
    rows.append(listUpperTransform(row))

header_map = {}

meta_data = {}
meta_data['branch_noOfSections'] = {}
meta_data['branch_electives'] = {}

meta_data['branch_to_elective'] = { 'CSE' : 'CS' , 'IT' : 'IT' , 'CSCE' : 'CE' , 'CSSE' : 'SE' }
meta_data['elective_to_branch'] = { 'CS' : 'CSE' , 'IT' : 'IT' , 'CE' : 'CSCE' , 'SE' : 'CSSE' }

def getBranches(meta_data):
    return list(meta_data['branch_noOfSections'].keys())

def getSections(meta_data, branch):
    branch = branch.upper()
    if branch not in meta_data['branch_noOfSections']:
        return None
    return meta_data['branch_noOfSections'][branch]

def findTeacher(branch, elective, DEId, teacherData):
    try:
        code = elective.replace('(DE)', '') + '_' + meta_data['branch_to_elective'][branch] + str(DEId)
        for teacher in teacherData:
            if teacher[0].upper() == code.upper():
                return teacher[1]
    except Exception as error:
        print(error)
        return None

# branch : branch , section : section , elective1 : (elective_code, elective_section), 
# elective2 : (elective_code, elective_section), totalData : all data
def createTimetable(branch, section, elective1, elective2, totalData):
    timetable = {}
    
    days = set()
    for row in totalData:
        days.add(row[header_map['DAY']])
    days = list(days)
    
    class_code = str(branch + '-' + str(section)).upper()
    # print(header[header_map['DAY']:header_map['SECTION(DE)']])
    
    timetable['HEAD'] = header[header_map['DAY']:header_map['SECTION(DE)']] + header[header_map['ROOM3']:header_map['5 TO 6']+1]
    
    for row in totalData:
        if row[header_map['SECTION']] == class_code:
            timetable[row[header_map['DAY']]] = row[header_map['SECTION']:header_map['SECTION(DE)']]
    
    # print("Timetable : ")
    # print(timetable)
    
    elective1_code = elective1[0] + '_' + meta_data['branch_to_elective'][branch] + '-' + str(elective1[1])
    elective2_code = elective2[0] + '_' + meta_data['branch_to_elective'][branch] + '-' + str(elective2[1])
    
    elective_data = {}
    for row in totalData:
        if row[header_map['DAY']] not in elective_data:
            elective_data[row[header_map['DAY']]] = []
        if row[header_map['SECTION(DE)']] == elective1_code or row[header_map['SECTION(DE)']] == elective2_code:
            elective_data[row[header_map['DAY']]].append(row[header_map['ROOM3']:header_map['5 TO 6']+1])
    
    for day in elective_data.keys():
        elective_schedule = ['X'] * 6
        for schedule in elective_data[day]:
            for index in range(0, 6, 2):
                if elective_schedule[index] != 'X':
                    continue
                if schedule[index] != 'X':
                    elective_schedule[index] = schedule[index]
                    elective_schedule[index + 1] = schedule[index + 1]
        timetable[day] += elective_schedule
        
    # for key in timetable.keys():
    #     print(f"{key} :", timetable[key])
        
    return ' '.join([class_code, elective1_code, elective2_code]) + '.pdf', timetable

def apply2DTransform(timetable):
    transformedList = []
    for key in timetable.keys():
        if key == 'HEAD': transformedList.append(timetable[key])
        else: transformedList.append([key] + timetable[key])
    # print(len(transformedList[0]))
    # print(len(transformedList[1]))
    return transformedList
    
for index in range(len(header)):
    header_map[header[index]] = index
    
# for finding branches and the count of sections under each branch
for row in rows:
    if row[header_map['SECTION']] == 'X':
        continue
    split_section = row[header_map['SECTION']].split('-')
    if len(split_section) != 2:
        continue
    
    branch, section = split_section[0], int(split_section[1])
    
    if branch not in meta_data['branch_noOfSections']:
        meta_data['branch_noOfSections'][branch] = section
    else:
        meta_data['branch_noOfSections'][branch] = max(section, meta_data['branch_noOfSections'][branch])

# for getting the elective data under each branch
for row in rows:
    if row[header_map['SECTION(DE)']] == 'X':
        continue
    
    split_section_1 = row[header_map['SECTION(DE)']].split('_')
    if len(split_section_1) != 2:
        continue
    
    elective, details = split_section_1[0], split_section_1[1]
    split_section_2 = details.split('-')
    if len(split_section_2) != 2:
        continue
    elBranch, DEId = split_section_2[0], int(split_section_2[1])
    
    slot_3_to_4 = row[header_map['3 TO 4']]
    slot_4_to_5 = row[header_map['4 TO 5']]
    slot_5_to_6 = row[header_map['5 TO 6']]
    
    try:
        branch = meta_data['elective_to_branch'][elBranch]
    except Exception as error:
        print(error)
        continue
    
    if branch not in meta_data['branch_electives']:
        meta_data['branch_electives'][branch] = {}
        meta_data['branch_electives'][branch]['electives'] = {}
        for elective in [slot_3_to_4, slot_4_to_5, slot_5_to_6]:
            if elective == 'X':
                continue
            if elective not in meta_data['branch_electives'][branch]['electives']:
                meta_data['branch_electives'][branch]['electives'][elective] = {'DEIDs' : DEId}
                meta_data['branch_electives'][branch]['electives'][elective]['teachers'] = {
                    DEId : findTeacher(branch, elective, DEId, teacherData)
                }
            else:
                meta_data['branch_electives'][branch]['electives'][elective]['DEIDs'] = max(DEId, meta_data['branch_electives'][branch]['electives'][elective]['DEIDs'])
                if DEId not in meta_data['branch_electives'][branch]['electives'][elective]['teachers']:
                    meta_data['branch_electives'][branch]['electives'][elective]['teachers'][DEId] = findTeacher(branch, elective, DEId, teacherData)
    else:
        for elective in [slot_3_to_4, slot_4_to_5, slot_5_to_6]:
            if elective == 'X':
                continue
            if elective not in meta_data['branch_electives'][branch]['electives']:
                meta_data['branch_electives'][branch]['electives'][elective] = {'DEIDs' : DEId}
                meta_data['branch_electives'][branch]['electives'][elective]['teachers'] = {
                    DEId : findTeacher(branch, elective, DEId, teacherData)
                }
            else:
                meta_data['branch_electives'][branch]['electives'][elective]['DEIDs'] = max(DEId, meta_data['branch_electives'][branch]['electives'][elective]['DEIDs'])
                if DEId not in meta_data['branch_electives'][branch]['electives'][elective]['teachers']:
                    meta_data['branch_electives'][branch]['electives'][elective]['teachers'][DEId] = findTeacher(branch, elective, DEId, teacherData)

def TimeTableCreator(_branch, _section, _e1_code, _e1_teacher, _e2_code, _e2_teacher, rows):
    pdfName, result = createTimetable(_branch, _section, (_e1_code, _e1_teacher), (_e2_code, _e2_teacher), rows)
    result2D = apply2DTransform(result)
    DFresult2D = pd.DataFrame(result2D)
    pd.set_option('display.max_columns', None)
    print(DFresult2D)

    fig, ax =plt.subplots(figsize=(12,4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=DFresult2D.values,colLabels=DFresult2D.columns,loc='center')

    pp = PdfPages(pdfName)
    pp.savefig(fig, bbox_inches='tight')
    pp.close()
    return pdfName

if __name__ == '__main__':
    app.run(port=5000,debug=True) 