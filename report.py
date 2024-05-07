from dataclasses import dataclass
import glob
from datetime import datetime
import markdown

@dataclass
class Report:
    dir: str
    pattern: str = f"stats-result-{datetime.now().strftime('%d-%m-%Y')}-*"
    fname: str = "stats-result-main.md"
    final_result: str = "stats-result.html"
    
    def join_files(self):
        with open(self.fname, "w") as fs:
            files = glob.glob(f"{self.dir}/{self.pattern}")                   
            for n in files:
                with open(n, "r") as f:
                    fs.writelines(f.readlines())
                    fs.write("\n\n")

    def write_html(self):
        markdown.markdownFromFile(input=self.fname, output=self.final_result, output_format="html")

    def run(self):
        try:
            self.join_files()
            self.write_html()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    r = Report("./")
    r.run()
