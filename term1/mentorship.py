import csv
import random
from datetime import date
from slugify import slugify


def make_name(fname, lname):
    fname = fname.strip().replace(' ', '_')
    lname = lname.strip().replace(' ', '_')
    return '{0}_{1}'.format(fname, lname)

def convert_year_to_int(s):
    dic = { 'First': 1, 'Second': 2, 'Third': 3, 'Fourth': 4, 'Unclassified': 0 }
    return dic[s] if s in dic.keys() else -1

def read_mentors():
    mentors = {}
    first_round = {}
    second_round = {}
    third_round = {}
    fourth_round = {}
    fifth_round = {}

    with open('./data/mentors.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = []
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                group_number = row[0]
                full_name = make_name(row[1], row[2])
                max_mentees = 2
                first = None
                second = None
                third = None
                fourth = None
                fifth = None

                for j, col in enumerate(row):
                    if (3 <= j <= 12) and bool(col):
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

                        if col == '3':
                            third = pref_slug

                            if pref_slug not in third_round.keys():
                                third_round[pref_slug] = []

                            third_round[pref_slug].append({
                                'group_number': group_number,
                                'full_name': full_name,
                                'max_mentees': max_mentees,
                                'pref': pref_slug
                            })
                        if col == '4':
                            fourth = pref_slug

                            if pref_slug not in fourth_round.keys():
                                fourth_round[pref_slug] = []

                            fourth_round[pref_slug].append({
                                'group_number': group_number,
                                'full_name': full_name,
                                'max_mentees': max_mentees,
                                'pref': pref_slug
                            })

                        if col == '5':
                            fifth = pref_slug

                            if pref_slug not in fifth_round.keys():
                                fifth_round[pref_slug] = []

                            fifth_round[pref_slug].append({
                                'group_number': group_number,
                                'full_name': full_name,
                                'max_mentees': max_mentees,
                                'pref': pref_slug
                            })

                mentors[group_number] = {
                    'group_number': group_number,
                    'full_name': full_name,
                    'first': first,
                    'second': second,
                    'third': third,
                    'fourth': fourth,
                    'fifth': fifth,
                    'max_mentees': max_mentees,
                    'mentees': []
                }

    return mentors, [first_round, second_round, third_round, fourth_round, fifth_round]

def read_mentees():
    mentees = {}

    total_preferences = list(range(1, 11))

    header = []
    data = []
    max_bio = 0
    with open('./data/mentees.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                total_bio = 0
                if bool(row[6]):
                    total_bio += len(row[6])
                if bool(row[7]):
                    total_bio += len(row[7])
                if bool(row[8]):
                    total_bio += len(row[8])

                if total_bio > max_bio:
                    max_bio = total_bio

                row.append(total_bio)
                data.append(row)

    for i, row in enumerate(data):
        full_name = make_name(row[1], row[2])

        score = 0
        if bool(row[3]):
            score += convert_year_to_int(row[3])

        if bool(row[4]):
            if '2025' in row[4] or '2026' in row[4]:
                score += 1

        if bool(row[5]):
            if row[5] == 'Returning Mentee':
                score += 1

        # if bool(row[19]):
        #     score += float(row[19] / max_bio)

        int_score = int(score)

        preferences = [''] * 10
        prev_mentors = []
        for j, col in enumerate(row):
            if (9 <= j <= 18) and bool(col):
                for pref in total_preferences:
                    if col and col == str(pref):
                        preferences[pref-1] = slugify(header[j])

            if (19 <= j <= 21) and bool(col):
                col_strip = col.strip()
                names = []
                if '&' in col_strip:
                    names = col.strip().split('&')
                elif ',' in col_strip:
                    names = col.strip().split(',')
                elif ';' in col_strip:
                    names = col.strip().split(';')

                if len(names) > 0:
                    for name in names:
                        prev_mentors.append(name.strip().replace(' ', '_'))
                else:
                    prev_mentors.append(col_strip.replace(' ', '_'))


        if str(int_score) not in mentees.keys():
            mentees[str(int_score)] = []

        mentees[str(int_score)].append({
            'full_name': full_name,
            'student_number': row[0],
            'preferences': preferences,
            'prev_mentors': prev_mentors,
            'score': score
        })

    return mentees

def get_min_mentors(found_mentors):
    random.shuffle(found_mentors)
    min_mentors = []
    for mentor in found_mentors:
        m = mentors[mentor['group_number']]
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
        # items = sorted(mentee[1], key=lambda d: d['score'], reverse=True)
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
                            min_mentors = get_min_mentors(found_mentors)

                            for m in min_mentors:
                                mentor = mentors[ m['group_number'] ]

                                info = item['full_name'] + '|' + item['student_number']
                                if len(mentor['mentees']) < 1 and info not in mentor['mentees'] and mentor['full_name'] not in item['prev_mentors']:
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

        print('Total mentees: ', len(items), ' -> Number of assigned metees: ', count)

    if len(unassigned) > 0:
        print('\nList of unassigned mentees in the 1st round as follows:', len(unassigned))
    else:
        print('Done! all mentees are assigned in the 1st round.')
    
    return mentors, mentees_matching, mentee_mentors, unassigned

def assign_second(mentees, mentors, mentors_rounds):
    print('Mentees - Second round')
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
        # items = sorted(mentee[1], key=lambda d: d['score'], reverse=True)
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
                            min_mentors = get_min_mentors(found_mentors)

                            for m in min_mentors:
                                mentor = mentors[ m['group_number'] ]

                                info = item['full_name'] + '|' + item['student_number']
                                if len(mentor['mentees']) < mentor['max_mentees'] and info not in mentor['mentees'] and mentor['full_name'] not in item['prev_mentors']:
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

        print('Total mentees: ', len(items), ' -> Number of assigned metees: ', count)

    if len(unassigned) > 0:
        print('\nList of unassigned mentees in the 2nd round as follows:', len(unassigned))
    else:
        print('Done! all mentees are assigned in the 2nd round.')

    return mentors, mentees_matching, mentee_mentors, unassigned

def write_mentors(mentors, today):
    header = ['First Name', 'Last Name', 'Max Mentees', 'Student 1', 'Student 2', 'Student 3']
    items = []
    for key, value in mentors.items():
        full_name_sp = value['full_name'].split('_')
        item = [full_name_sp[0], full_name_sp[1], value['max_mentees']]

        for mentee in value['mentees']:
            mentee = mentee.replace('_', ' ').replace('|', ' (') + ')'
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
        name = key_sp[0].split('_')
        item = [ key_sp[1], name[0], name[1] ]

        for mentor in value:
            item.append(mentor.replace('_', ' '))

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
    today = date.today().strftime('%Y-%m-%d')

    mentors, mentors_rounds = read_mentors()
    mentees = read_mentees()

    mentors, mentees_matching, mentee_mentors_first, unassigned_first = assign_first(mentees, mentors, mentors_rounds)

    new_mentees = {}
    for mentee in unassigned_first:
        score = mentee['score']
        if score not in new_mentees.keys():
            new_mentees[score] = []

        new_mentees[score].append(mentee)

    mentors, mentees_matching, mentee_mentors_second, unassigned_second = assign_second(new_mentees, mentors, mentors_rounds)

    if len(unassigned_second) > 0:
        with open('mentorship - extra round - unassigned_mentees - ' + today + '.csv', 'w', newline='', encoding='utf-8') as f:
            write = csv.writer(f)
            write.writerow(['Student Number', 'First Name', 'Last Name'])
            write.writerows( unassigned_mentees(unassigned_second) )

    mentee_mentors = {**mentee_mentors_first, **mentee_mentors_second}

    write_mentors(mentors, today)
    write_mentees(mentee_mentors, today)