def find_report(file_name: str) -> str:
    try:
        with open(file_name, 'r') as f:
            return f.read()
    except:
        return "File unavailable"
