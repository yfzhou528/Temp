import zipfile
import csv
import json
from collections import defaultdict


class ZipComparisonError(Exception):
    def __init__(self, message, differences):
        super().__init__(message)
        self.differences = differences


def read_zip_file(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        return {name: zip_ref.read(name).decode('utf-8').splitlines() for name in zip_ref.namelist()}


def compare_decimal(str1, str2):
    # Compare integer parts and first 8 decimal places
    part1, part2 = str1.split('.'), str2.split('.')
    return part1[0] == part2[0] and part1[1][:8] == part2[1][:8]


def compare_files(data1, data2):
    differences = []

    data1_dict = defaultdict(list)
    data2_dict = defaultdict(list)

    for row in data1:
        data1_dict[tuple(csv.reader([row], delimiter='|')).__next__()].append(row)

    for row in data2:
        data2_dict[tuple(csv.reader([row], delimiter='|')).__next__()].append(row)

    all_keys = set(data1_dict.keys()).union(data2_dict.keys())

    for key in all_keys:
        rows1 = data1_dict.get(key, [])
        rows2 = data2_dict.get(key, [])

        if len(rows1) != len(rows2):
            if rows1 and not rows2:
                differences.extend([f"Row '{row}' found in file1 but not in file2" for row in rows1])
            elif rows2 and not rows1:
                differences.extend([f"Row '{row}' found in file2 but not in file1" for row in rows2])
            else:
                differences.append(f"Different number of rows for key {key}: {len(rows1)} vs {len(rows2)}")

        while rows1:
            row1 = rows1.pop(0)
            match_found = False
            for row2 in rows2:
                if all(compare_decimal(col1, col2) if i in [0, 1, 2] else col1 == col2
                       for i, (col1, col2) in enumerate(zip(csv.reader([row1], delimiter='|').__next__(),
                                                            csv.reader([row2], delimiter='|').__next__()))):
                    match_found = True
                    rows2.remove(row2)
                    break

            if not match_found:
                differences.append(f"Row '{row1}' found in file1 but not in file2")

        while rows2:
            row2 = rows2.pop(0)
            differences.append(f"Row '{row2}' found in file2 but not in file1")

    return not differences, differences


def compare_zip_files(zip1, zip2):
    data1 = read_zip_file(zip1)
    data2 = read_zip_file(zip2)

    differences = []

    if set(data1.keys()) != set(data2.keys()):
        differences.append(f"Different sets of files: {set(data1.keys())} vs {set(data2.keys())}")
        return {"status": "failed", "diff": differences}

    for file_name in data1:
        result, file_differences = compare_files(data1[file_name], data2[file_name])
        if not result:
            differences.extend([f"In file '{file_name}': {diff}" for diff in file_differences])

    for file_name in set(data2.keys()) - set(data1.keys()):
        differences.extend(
            [f"In file '{file_name}': Row '{row}' found in file2 but not in file1" for row in data2[file_name]])

    if differences:
        return {"status": "failed", "diff": differences}

    return {"status": "success"}


# Example usage
result = compare_zip_files('file1.zip', 'file2.zip')
print(json.dumps(result, indent=4))
