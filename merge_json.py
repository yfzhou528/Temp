import os
import json

def merge_json_files(folder_path, output_path):
    merged_json = {}

    # 遍历文件夹中的所有 JSON 文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                merge_json(merged_json, json_data)

    # 将合并后的 JSON 写入到输出文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_json, f, indent=4, ensure_ascii=False)

def merge_json(target, source):
    for name, ids in source.items():
        if name in target:
            target[name].update(ids)
        else:
            target[name] = ids

# 使用示例
folder_path = 'path/to/json/files'
output_path = 'path/to/output/merged.json'
merge_json_files(folder_path, output_path)
