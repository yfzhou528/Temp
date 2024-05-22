import zipfile
import csv
import json
import hashlib
from collections import defaultdict


class ZipComparator:
    class ZipComparisonError(Exception):
        def __init__(self, message, differences):
            super().__init__(message)
            self.differences = differences

    @staticmethod
    def read_zip_file(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            return {name: zip_ref.read(name).decode('utf-8').splitlines() for name in zip_ref.namelist()}

    @staticmethod
    def compare_decimal(str1, str2):
        part1, part2 = str1.split('.'), str2.split('.')
        return part1[0] == part2[0] and part1[1] == part2[1]

    @staticmethod
    def parse_row(row):
        return list(csv.reader([row], delimiter='|'))[0]

    @staticmethod
    def hash_row(row):
        parsed_row = ZipComparator.parse_row(row)
        hash_columns = [parsed_row[i] for i in range(len(parsed_row))]

        for i in [2, 3, 4, 9, 10]:  # 0-based index for columns 3, 4, 5, 10, 11
            decimal_part = parsed_row[i].split('.')
            hash_columns[i] = decimal_part[0] + '.' + (decimal_part[1][:8] if len(decimal_part) > 1 else '')

        hash_input = '|'.join(hash_columns)
        return hashlib.md5(hash_input.encode()).hexdigest()

    @staticmethod
    def compare_files(data1, data2):
        differences = []

        if data1 == data2:
            return True, differences

        data1_dict = defaultdict(list)
        data2_dict = defaultdict(list)

        for row in data1:
            hash_key = ZipComparator.hash_row(row)
            data1_dict[hash_key].append(row)

        for row in data2:
            hash_key = ZipComparator.hash_row(row)
            data2_dict[hash_key].append(row)

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
                    differences.append(f"Different number of rows for hash key {key}: {len(rows1)} vs {len(rows2)}")

        return not differences, differences

    @staticmethod
    def compare_zip_files(zip1, zip2):
        data1 = ZipComparator.read_zip_file(zip1)
        data2 = ZipComparator.read_zip_file(zip2)

        differences = []

        if set(data1.keys()) != set(data2.keys()):
            differences.append(f"Different sets of files: {set(data1.keys())} vs {set(data2.keys())}")
            return {"status": "failed", "diff": differences}

        for file_name in data1:
            result, file_differences = ZipComparator.compare_files(data1[file_name], data2[file_name])
            if not result:
                differences.extend([f"In file '{file_name}': {diff}" for diff in file_differences])

        if differences:
            return {"status": "failed", "diff": differences}

        return {"status": "success"}


# Example usage
result = ZipComparator.compare_zip_files('file1.zip', 'file2.zip')
print(json.dumps(result, indent=4))
