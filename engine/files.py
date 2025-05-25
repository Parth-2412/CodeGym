from pathlib import Path

def get_extension(path : str):
    return path.split(".")[-1]
def validate_file(extension : str | list[str]):
    def check_file(path: str):
        if path == "terminal.terminal":
            return path
        file_extension = get_extension(path)
        path : Path = Path(path)
        if not path.exists():
            raise Exception(f"[ERROR] File '{path}' does not exist.")
        if not path.is_file():
            raise Exception(f"[ERROR] '{path}' is not a valid file.")
        if not (file_extension == extension if type(extension) == str else file_extension in extension):
            raise Exception(f"[ERROR] File {"type is not supported" if type(extension) != str else f"must be a .{extension} fike"}")
        return str(path)
    return check_file

