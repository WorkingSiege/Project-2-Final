import os


class FileShipper:
    def __init__(self):
        os.makedirs("output", exist_ok=True)

    def write(self, filename, content):
        with open(f"output/{filename}", "wb") as output_file:
            output_file.write(content)

    def append(self, filename, content):
        with open(f"output/{filename}", "a") as output_file:
            output_file.write(content + "\n")
