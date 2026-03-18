import csv
import random
from datetime import date
from slugify import slugify


def get_full_name(lname, fname):
    l = lname.strip()
    f = fname.strip().replace(' ', '_')
    return '{0}={1}'.format(l, f)

def read_mentors():
    mentors = {}
    first_round = {}
    second_round = {}
    third_round = {}

    with open('./data/mentors.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = []
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                group_number = row[0]
                full_name = get_full_name(row[1], row[2])
                max_mentees = int(row[3].split(' ')[0].strip())
                first = None
                second = None
                third = None

                for j, col in enumerate(row):
                    if (4 <= j <= 13) and bool(col):
                        pref_slug = slugify(header[j])

                        if col == '1':
                            first = pref_slug

                            if pref_slug not in first_round.keys():
                                first_round[pref_slug] = []

                            first_round[pref_slug].append({
                                'group_number': group_number,
                                'full_name': full_name,
                                'max_mentees': max_mentees,
                                'pref': pref_slug
                            })

                        elif col == '2':
                            second = pref_slug

                            if pref_slug not in second_round.keys():
                                second_round[pref_slug] = []

                            second_round[pref_slug].append({
                                'group_number': group_number,
                                'full_name': full_name,
                                'max_mentees': max_mentees,
                                'pref': pref_slug
                            })

                        elif col == '3':
                            third = pref_slug

                            if pref_slug not in third_round.keys():
                                third_round[pref_slug] = []

                            third_round[pref_slug].append({
                                'group_number': group_number,
                                'full_name': full_name,
                                'max_mentees': max_mentees,
                                'pref': pref_slug
                            })                         

                mentors[full_name] = {
                    'group_number': group_number,
                    'full_name': full_name,
                    'first': first,
                    'second': second,
                    'third': third,
                    'max_mentees': max_mentees,
                    'mentees': []
                }

    return mentors, [first_round, second_round, third_round]

def read_mentees():
    mentees = {}

    total_preferences = list(range(1, 11))
    with open('./data/mentees.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = []
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                full_name = get_full_name(row[1], row[2])
                term1_mentor = row[3].split('|')[1].strip()

                prev_mentors = []
                if row[4]:
                    prev_mentors = [mentor.strip() for mentor in row[4].split(',')]

                prev_mentors.append(term1_mentor)
                len_prev_mentors = len(prev_mentors)

                preferences = [''] * 10
                for j, col in enumerate(row):
                    if (5 <= j <= 14) and bool(col):
                        for pref in total_preferences:
                            if col and col == str(pref):
                                preferences[pref-1] = slugify(header[j])

                if len_prev_mentors not in mentees.keys():
                    mentees[len_prev_mentors] = []

                mentees[len_prev_mentors].append({
                    'full_name': full_name,
                    'student_number': row[0],
                    'prev_mentors': prev_mentors,
                    'preferences': preferences
                })

    return mentees

def get_min_mentors(mentors, found_mentors):
    random.shuffle(found_mentors)
    min_mentors = []
    for mentor in found_mentors:
        m = mentors[mentor['full_name']]
        m['curr_mentees'] = len(m['mentees'])
        min_mentors.append(m)
    min_mentors = sorted(min_mentors, key=lambda x: x['curr_mentees'])
    return min_mentors

def assign_first(mentees, mentors, mentors_rounds):
    print('Mentees - First round')
    unassigned = []
    mentees_matching = {}
    mentee_mentors = {}

    mentees = sorted(mentees.items(), reverse=True)

    total = 0
    for mentee in mentees:
        total += len(mentee[1])
        random.shuffle(mentee[1])

    print('Total mentees', total)

    for mentee in mentees:
        score = mentee[0]
        items = mentee[1]

        print('Score group - ', score)
        
        count = 0
        for item in items:
            key = item['full_name'] + '|' + item['student_number']
            if key not in mentee_mentors.keys():
                mentee_mentors[key] = []

            found = False
            for pref in item['preferences']:
                if bool(pref):
                    for i, mentors_round in enumerate(mentors_rounds):
                        if pref in mentors_round.keys():
                            found_mentors = mentors_round[pref]
                            min_mentors = get_min_mentors(mentors, found_mentors)
    
                            for m in min_mentors:
                                if m['full_name'] not in item['prev_mentors']:
                                    mentor = mentors[ m['full_name'] ]
    
                                    info = item['full_name'] + '|' + item['student_number']
                                    if len(mentor['mentees']) == 0 and info not in mentor['mentees']:
                                        mentor['mentees'].append(info)
                                        mentees_matching[item['student_number']] = pref
                                        mentee_mentors[key].append(mentor['full_name'])
                                        found = True
                                        count += 1
                                        break
                        if found:
                            break
                    if found:
                        break
            if not found:
                unassigned.append(item)

        print('Total mentees in this group: ', len(items), ' -> Number of assigned metees: ', count)

    if len(unassigned) > 0:
        print('\nList of unassigned mentees in the 1st round as follows:', len(unassigned))
    else:
        print('Done! all mentees are assigned in the 1st round.')

    return mentors, mentees_matching, mentee_mentors, unassigned


def assign_second(mentees, mentors, mentors_rounds, mentees_matching, mentee_mentors):
    print('\nMentees - Second round')
    unassigned = []

    mentees = sorted(mentees.items(), reverse=False)
    total = 0
    for mentee in mentees:
        total += len(mentee[1])
        random.shuffle(mentee[1])

    print('Total mentees', total)

    for mentee in mentees:
        score = mentee[0]
        items = mentee[1]

        print('Score group - ', score)

        count = 0
        for item in items:
            key = item['full_name'] + '|' + item['student_number']
            if key not in mentee_mentors.keys():
                mentee_mentors[key] = []

            matched = 'anything'
            if item['student_number'] in mentees_matching.keys():
                matched = mentees_matching[item['student_number']]

            found = False
            for pref in item['preferences']:
                if bool(pref) and pref != matched:
                    for i, mentors_round in enumerate(mentors_rounds):
                        if pref in mentors_round.keys():
                            found_mentors = mentors_round[pref]
                            min_mentors = get_min_mentors(mentors, found_mentors)
    
                            for m in min_mentors:
                                if m['full_name'] not in item['prev_mentors']:
                                    mentor = mentors[m['full_name']]
    
                                    info = item['full_name'] + '|' + item['student_number']
                                    if len(mentor['mentees']) == 1 and info not in mentor['mentees']:
                                        mentor['mentees'].append(info)
                                        mentees_matching[item['student_number']] = pref
                                        mentee_mentors[key].append(mentor['full_name'])
                                        found = True
                                        count += 1
                                        break
                        if found:
                            break
                    if found:
                        break
            if not found:
                unassigned.append(item)

        print('Total mentees in this group: ', len(items), ' -> Number of assigned metees: ', count)

    if len(unassigned) > 0:
        print('\nList of unassigned mentees in the 2nd round as follows:', len(unassigned))
    else:
        print('Done! all mentees are assigned in the 2nd round.')

    return mentors, mentee_mentors, unassigned


def assign_third(mentees, mentors, mentors_rounds, mentees_matching, mentee_mentors):
    print('\nMentees - Extra round')
    unassigned = []

    print('Total mentees', len(mentees))

    count = 0
    for item in mentees:
        key = item['full_name'] + '|' + item['student_number']
        if key not in mentee_mentors.keys():
            mentee_mentors[key] = []

        matched = 'anything'
        if item['student_number'] in mentees_matching.keys():
            matched = mentees_matching[item['student_number']]

        found = False
        for pref in item['preferences']:
            if bool(pref) and pref != matched:
                for i, mentors_round in enumerate(mentors_rounds):
                    if pref in mentors_round.keys():
                        found_mentors = mentors_round[pref]
                        min_mentors = get_min_mentors(mentors, found_mentors)
    
                        for m in min_mentors:
                            if m['full_name'] != item['prev_mentors']:
                                mentor = mentors[m['full_name']]
    
                                info = item['full_name'] + '|' + item['student_number']
                                if len(mentor['mentees']) < mentor['max_mentees'] and info not in mentor['mentees']:
                                    mentor['mentees'].append(info)
                                    mentees_matching[item['student_number']] = pref
                                    mentee_mentors[key].append(mentor['full_name'])
                                    found = True
                                    count += 1
                                    break
                    if found:
                        break
                if found:
                    break
        if not found:
            unassigned.append(item)

        print('Total mentees in this group: ', len(mentees), ' -> Number of assigned metees: ', count)

    if len(unassigned) > 0:
        print('\nList of unassigned mentees in an extra round as follows:', len(unassigned))
    else:
        print('Done! all mentees are assigned in an extra round.')

    return mentors, mentee_mentors, unassigned

def write_mentors(mentors, today):
    header = ['First Name', 'Last Name', 'Max Mentees', 'Student 1', 'Student 2', 'Student 3']
    items = []
    for key, value in mentors.items():
        full_name_sp = value['full_name'].split('=')
        item = [full_name_sp[0], full_name_sp[1].replace('_', ' '), value['max_mentees']]

        for mentee in value['mentees']:
            mentee = mentee.replace('=', ' ').replace('_', ' ')
            mentee = mentee.replace('|', ' (') + ')'
            item.append(mentee)

        items.append(item)

    with open('mentorship - mentors.csv - ' + today + '.csv', 'w', newline='', encoding='utf-8') as f:
        write = csv.writer(f)
        write.writerow(header)
        write.writerows(items)


def write_mentees(mentee_mentors, today):
    header = ['Student Number', 'First Name', 'Last Name', 'Mentor 1', 'Mentor 2']
    items = []
    for key, value in mentee_mentors.items():
        key_sp = key.split('|')
        name = key_sp[0].split('=')
        item = [ key_sp[1], name[0], name[1].replace('_', ' ') ]

        for mentor in value:
            mentor = mentor.replace('=', ' ').replace('_', ' ')
            item.append(mentor)

        items.append(item)

    with open('mentorship - mentees.csv - ' + today + '.csv', 'w', newline='', encoding='utf-8') as f:
        write = csv.writer(f)
        write.writerow(header)
        write.writerows(items)

def unassigned_mentees(unassigned):
    items = []
    for i in unassigned:
        name = i['full_name'].split('_')
        item = [i['student_number'], name[0], name[1]]
        items.append(item)
    return items

if __name__ == '__main__':
    mentors, mentors_rounds = read_mentors()
    mentees = read_mentees()
    mentors, mentees_matching, mentee_mentors, unassigned_first = assign_first(mentees, mentors, mentors_rounds)
    mentors, mentee_mentors, unassigned_second = assign_second(mentees, mentors, mentors_rounds, mentees_matching, mentee_mentors)

    unassigned = []
    if len(unassigned_first) > 0:
        unassigned += unassigned_first
    if len(unassigned_second) > 0:
        unassigned += unassigned_second

    if len(unassigned) > 0:
        mentors, mentee_mentors, unassigned_third = assign_third(unassigned, mentors, mentors_rounds, mentees_matching, mentee_mentors)

    today = date.today().strftime('%Y-%m-%d')
    write_mentors(mentors, today)
    write_mentees(mentee_mentors, today)

    header = ['Student Number', 'First Name', 'Last Name']
    if len(unassigned) > 0:
        with open('mentorship - extra round - unassigned_mentees - ' + today + '.csv', 'w', newline='', encoding='utf-8') as f:
            write = csv.writer(f)
            write.writerow(header)
            write.writerows( unassigned_mentees(unassigned) )
