import tomllib
from dataclasses import dataclass
from datetime import datetime
from os import listdir, path, popen, stat, system, uname
from typing import Dict, List


@dataclass
class Services:
    systemctl: List[str]
    service: List[str]


@dataclass
class Config:
    filepaths: List[str]
    drives: Dict[str, bool]
    services: Services


class Monitor:
    def __init__(self, path: str):

        with open(path, "rb") as f:
            d = tomllib.load(f)
            self.config = Config(d["filepaths"], d["drives"], Services(**d["services"]))
        self.customer_name = uname().nodename
        self.data = [f"# data for {self.customer_name}\n", "---\n"]
        self.stats_fname = f"stats-result-{datetime.now().strftime('%d-%m-%Y')}-{self.customer_name}.md"
        self.not_arrived = []

    def check_file(self):
        self.data.append("## file stats data\n")
        for dir in self.config.filepaths:
            file = listdir(dir)[-1]
            f = path.join(dir, file)
            stats = stat(f)
            timestamp = datetime.fromtimestamp(stats.st_atime)
            if timestamp.strftime("%d-%m-%Y") != datetime.now().strftime("%d-%m-%Y"):
                self.not_arrived.append(
                    f"file not arrvied in {dir} for date {datetime.now().strftime("%d-%m-%Y")}\n"
                )
            else:
                size = stats.st_size / 1024
                self.data.append(
                    f"dir &rarr; {dir}, name &rarr; {file}, size &rarr; {size}KB, arrival_date &rarr; {timestamp.strftime('%d-%m-%Y %H:%M:%S')}\n"
                )

    def monitor_drives(self):
        output = popen("df -h").readlines()
        self.data.append("## drive stats data\n")
        for row in output:
            d = row.split()
            # Filesystem Size Used Avail Use% Mounted_on
            if self.config.drives.get(d[-1]):
                self.data.append(
                    f"* filesystem &rarr; {d[0]}, size &rarr; {d[1]}, used &rarr; {d[2]}, available &rarr; {d[3]}, used_percentage &rarr; {d[4]}, mounted_on &rarr; {d[5]}\n"
                )

    def monitor_services(self):
        self.data.append("## services status data\n")
        for s in self.config.services.systemctl:
            status = system(f"systemctl is-active --quiet {s}")
            self.data.append(f"* {s} &rarr; {self.check_status(status)}\n")
        # TODO: status services for `service command` on active product services

    @staticmethod
    def check_status(status: int):
        match status:
            case 0:
                return "active"
            case 768:
                return "inactive"
            case 1024:
                return "not exists"
            case _:
                return "undefined"

    def send_mail(self):
        pass

    def write_stats(self):
        with open(self.stats_fname, "w") as f:
            f.writelines(self.data)

    def run(self):
        self.check_file()
        self.monitor_drives()
        self.monitor_services()
        self.write_stats()


if __name__ == "__main__":
    m = Monitor("./config.toml")
    m.run()
