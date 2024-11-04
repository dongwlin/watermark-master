import os


def extract_file_name_and_ext(filePath: str) -> tuple[str, str]:
    _, file_name = os.path.split(filePath)
    name, ext = os.path.splitext(file_name)
    return name, ext

def create_new_file_path(filePath: str, newFileName: str) -> str:
    dirName, _ = os.path.split(filePath)
    newFilePath = os.path.join(dirName, newFileName)
    return newFilePath