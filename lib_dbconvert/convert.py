from pathlib import Path

# 讀取來源檔案
input_file = Path(f"C:\ytdb\sample_voice\mp3List.txt")  # 檔名請依實際命名修改
output_file = Path(f"C:\ytdb\sample_voice\output.sql")

category_id = 13

lines = input_file.read_text(encoding="utf-8").splitlines()
output_lines = []

for i, line in enumerate(lines, start=1):
    filename = line.strip()
    if not filename:
        continue

    if "_" in filename:
        code_value, rest = filename.split("_", 1)
        code_name = rest.rsplit(".", 1)[0]
    else:
        code_value = f"{i:02d}"
        code_name = filename.rsplit(".", 1)[0]

    sql = (
        f"INSERT INTO codes (category_id, code_value, code_name, description, sort_order) "
        f"VALUES ({category_id}, '{code_value}', '{code_name}', '{filename}', {i});"
    )
    output_lines.append(sql)

# 寫入 SQL 到新檔案
output_file.write_text("\n".join(output_lines), encoding="utf-8")
print(f"✅ 已寫入 {len(output_lines)} 筆 SQL 到 {output_file}")
