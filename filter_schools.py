import csv
import json
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python filter_schools.py config.json input.csv")
        sys.exit(1)

    config_file = sys.argv[1]
    input_file = sys.argv[2]

    with open(config_file, 'r') as f:
        config = json.load(f)

    filters = config.get('filters', [])
    output_file = config.get('output_file', 'filtered.csv')

    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        orig_fieldnames = reader.fieldnames
        poa_index = orig_fieldnames.index('poa_school_net')
        fieldnames = list(orig_fieldnames)  # copy, do NOT mutate reader.fieldnames
        fieldnames.insert(poa_index + 1, 'teacher_ratio')
        fieldnames.insert(poa_index + 1, 'bachelor_education_likelihood')
        fieldnames.insert(poa_index + 1, 'master_education_likelihood')
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                row['master_education_likelihood'] = calculate_master_likelihood(row)
                row['bachelor_education_likelihood'] = calculate_bachelor_likelihood(row)
                row['teacher_ratio'] = calculate_teacher_ratio(row)
                if all(apply_filter(row, f) for f in filters):
                    writer.writerow(row)

NUMERIC_OPS = {
    'gt':  lambda a, b: a > b,
    'lt':  lambda a, b: a < b,
    'gte': lambda a, b: a >= b,
    'lte': lambda a, b: a <= b,
    'eq':  lambda a, b: a == b,
    'neq': lambda a, b: a != b,
}

def apply_filter(row, filter_dict):
    col = filter_dict['column']
    typ = filter_dict['type']
    cell = row.get(col, '')
    if typ in NUMERIC_OPS:
        try:
            return NUMERIC_OPS[typ](float(cell), float(filter_dict['value']))
        except (ValueError, TypeError):
            return False
    values = filter_dict.get('values', [])
    if typ == 'include':
        return any(val in cell for val in values)
    elif typ == 'exclude':
        return not any(val in cell for val in values)
    else:
        return True  # unknown type, pass

def calculate_master_likelihood(row):
    try:
        teachers = float(row.get('previous_year_tsi_total_no_of_teachers', 0) or 0)
        training = float(row.get('previous_year_tsi_percent_of_received_teacher_training', 0) or 0) / 100
        master = float(row.get('previous_year_tsi_percent_of_master_doctorate_or_above', 0) or 0) / 100
        classes = float(row.get('current_year_no_of_class_total', 0) or 0)
        if classes == 0:
            return 0.00
        value = teachers * training * master / classes
        return round(value, 2)
    except (ValueError, TypeError):
        return 0.00

def calculate_bachelor_likelihood(row):
    try:
        teachers = float(row.get('previous_year_tsi_total_no_of_teachers', 0) or 0)
        training = float(row.get('previous_year_tsi_percent_of_received_teacher_training', 0) or 0) / 100
        bachelor = float(row.get('previous_year_tsi_percent_of_bacherlor', 0) or 0) / 100
        classes = float(row.get('current_year_no_of_class_total', 0) or 0)
        if classes == 0:
            return 0.00
        value = (teachers * training * bachelor) / classes
        return round(value, 2)
    except (ValueError, TypeError):
        return 0.00

def calculate_teacher_ratio(row):
    try:
        teachers = float(row.get('previous_year_tsi_total_no_of_teachers', 0) or 0)
        training = float(row.get('previous_year_tsi_percent_of_received_teacher_training', 0) or 0) / 100
        classes = float(row.get('current_year_no_of_class_total', 0) or 0)
        if classes == 0:
            return 0.00
        value = teachers * training / classes
        return round(value, 2)
    except (ValueError, TypeError):
        return 0.00

if __name__ == "__main__":
    main()