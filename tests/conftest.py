import os
from typing import Iterable


def read_files_with_extensions(root_dir: str, ext,  mode: str = "r", encoding: str="utf-8"):
    if isinstance(ext, str):
        extensions = [ext]
    else:
        extensions = ext

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, mode, encoding=encoding) as file:
                    yield file.read()

# 使用例：再帰的にディレクトリ内の全ての.txtと.mdファイルの中身を表示


# 自動テストを作りたい
TEST_FILE = os.path.join(os.path.dirname(__file__), "test_kestra.py")
print(TEST_FILE)

RESOURCES_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "../.volume/share/kestra_flows"))
print(RESOURCES_DIR)
print("###########")
for s in read_files_with_extensions(RESOURCES_DIR, ['.yaml', '.yml']):
    print("")
    print("---")
    print(s)
print("###########")

template = """
def test_{name}():
    assert True
"""


"""
curl -X POST http://localhost:8080/api/v1/flows \
-H "Content-Type: application/yaml" \
-d '
id: sample-flow
namespace: my.namespace
tasks:
  - id: first-task
    type: io.kestra.core.tasks.debugs.Echo
    format: "Hello, Kestra!"
'
"""

# flowを登録
"""
curl -X POST http://localhost:8080/api/v1/flows/import \
-H "Content-Type: multipart/form-data" \
-F "fileUpload=@-;filename=flow.yaml;type=application/yaml" <<EOF
namespace: my.namespace
id: sample-flow

inputs:
  - id: user1
    type: STRING
    defaults: user1
  - id: user2
    type: STRING
    defaults: user2
    
tasks:
  - id: first-task
    type: io.kestra.core.tasks.debugs.Echo
    format: "Hello, {{ inputs.user1 }} and {{ inputs.user2 }}!"
EOF
"""

# flowを実行
"""
curl -v -X POST 'http://localhost:8080/api/v1/executions/my.namespace/sample-flow' \
-H 'Content-Type: multipart/form-data' \
-F 'user1=mary' \
-F 'user2=bob'
"""
