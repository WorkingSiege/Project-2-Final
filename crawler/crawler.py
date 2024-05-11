import os
import json
import requests
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
from crawler.file_shipper import FileShipper
from bs4 import BeautifulSoup


class DirectoryCrawler:
    def __init__(self, stats, profile_queue, active=True):
        self.stats = stats
        self.active = active
        self.surnames = []
        self.shipper = FileShipper()
        self.profile_queue = profile_queue
        self._crawl_process = None

    def start(self):
        print("Starting crawler")
        self.active = True
        self._crawl_process = Process(target=self._crawl, args=(self.stats,))
        self._crawl_process.start()

    def stop(self):
        print("Stopping crawler")
        if self._crawl_process:
            self._crawl_process.terminate()
        self.active = False

    def getProgress(self):
        if self.stats["surnames"] > 0 and self.stats["surnamesProcessed"] > 0:
            return round(
                self.stats["surnamesProcessed"] / self.stats["surnames"] * 100, 2
            )
        else:
            return 0

    def _searchDirectory(self, surname):
        if not self.active:
            return None

        response = requests.get(
            f"https://directory.unl.edu/?format=partial&q={surname}"
        )

        if response.status_code == 200:
            return (surname, response.content)

        return None

    def _parseHTML(self, html):
        profiles = []
        soup = BeautifulSoup(html, features="html.parser")

        # Find all list items with class 'ppl_Sresult student'
        students = soup.find_all("li", class_="ppl_Sresult student")

        # Extract student names, profile photos, and profile URLs
        for student in students:
            name = student.find("a", class_="dcf-txt-decor-hover").text.strip()
            photo_url = student.find("img", class_="photo")["src"]
            profile_url = student["data-href"]
            profile = {"name": name, "photo_url": photo_url, "profile_url": profile_url}
            profiles.append(profile)

        return profiles

    def _crawl(self, stats):
        crawl_surnames_path = "analysis/surnames.txt"
        crawled_surnames_path = "output/crawled_surnames.txt"

        if not self.active:
            print("Crawler is inactive. Cannot crawl.")
            return

        with open(crawl_surnames_path, "r") as seed_file:
            self.surnames = [line.rstrip().lower() for line in seed_file]
            stats["surnames"] = len(self.surnames)

        if os.path.isfile(crawled_surnames_path):
            with open(crawled_surnames_path) as crawled_surnames_file:
                crawled_surnames = crawled_surnames_file.read().splitlines()
                for crawled_surname in crawled_surnames:
                    try:
                        stats["surnamesProcessed"] += 1
                        self.surnames.remove(crawled_surname.lower())
                    except ValueError:
                        # we crawled a surname that no longer exists in analysis/surnames.txt
                        pass

        with ThreadPoolExecutor(max_workers=12) as executor:
            for result in executor.map(self._searchDirectory, self.surnames):
                if result:
                    surname, content = result
                    profiles = self._parseHTML(content)
                    self.shipper.append("crawled_surnames.txt", surname)
                    for profile in profiles:
                        self.shipper.append("students.jsonl", json.dumps(profile))
                        self.profile_queue.put(profile)
                stats["surnamesProcessed"] += 1
