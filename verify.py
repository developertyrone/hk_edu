import csv

with open('chsc-chsc-primary-school-profiles-2025-filtered.csv') as f:
    orig = {r['school_name']: r for r in csv.DictReader(f)}

with open('filtered_public.csv') as f:
    filt = {r['school_name']: r for r in csv.DictReader(f)}

mismatches = 0
for name in filt:
    o = orig[name]
    fi = filt[name]
    if o['previous_year_no_of_class_total'] != fi['previous_year_no_of_class_total'] or \
       o['current_year_no_of_class_total'] != fi['current_year_no_of_class_total']:
        print(f'MISMATCH: {name}')
        print(f'  orig prev={o["previous_year_no_of_class_total"]} curr={o["current_year_no_of_class_total"]}')
        print(f'  filt prev={fi["previous_year_no_of_class_total"]} curr={fi["current_year_no_of_class_total"]}')
        mismatches += 1
    else:
        teachers = float(o.get('previous_year_tsi_total_no_of_teachers') or 0)
        training = float(o.get('previous_year_tsi_percent_of_received_teacher_training') or 0) / 100
        master = float(o.get('previous_year_tsi_percent_of_master_doctorate_or_above') or 0)
        classes = float(o.get('current_year_no_of_class_total') or 0)
        if classes == 0:
            expected = 0.0
        else:
            expected = round(teachers * training * ((100 + master) / 100) / classes, 2)
        actual = float(fi['education_likelihood'])
        if abs(expected - actual) > 0.01:
            print(f'LIKELIHOOD WRONG: {name}: expected={expected}, got={actual}')
            mismatches += 1

if mismatches == 0:
    print('All values match correctly.')
