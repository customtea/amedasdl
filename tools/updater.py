import requests
import time
from bs4 import BeautifulSoup
import urllib.parse
import json
from parse_node import ObsPoint, parse_node_html
from pathlib import Path


def get_group(key):
    BASEURL = "https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture.php?prec_no="
    url = BASEURL + key
    print(url)
    response = requests.get(url)
    time.sleep(1)
    response.encoding = "utf-8"
    html = response.text
    return html

def parse_group_html(html):
    group_d = {}
    soup = BeautifulSoup(html, "html.parser")
    map = soup.findAll("map")[0]
    for area in map.findAll("area"):
        href = urllib.parse.urlparse(area["href"])
        if not "prefecture.php" in href.path:
            continue
            # print(area["href"])
        # print(area)
        querry = urllib.parse.parse_qs(href.query)
        # print(querry)
        group_d[querry["prec_no"][0]] = area["alt"]
    return group_d


def stage1():
    ALLGROUP = "https://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php"
    response = requests.get(ALLGROUP)
    time.sleep(1)
    response.encoding = "utf-8"
    html = response.text

    with open("all_group.html", "w") as f:
        f.write(html)
    
    return html


def stage2(html):
    group_d = parse_group_html(html)
    
    with open("group.json", "w") as f:
        json.dump(group_d, f, indent=4, ensure_ascii=False)

    return group_d


def stage3(group_d):
    Path("./group/").mkdir(exist_ok=True)
    for key, name in group_d.items():
        html = get_group(key)
        with open(f"./group/{key}_{name}.html", "w") as f:
            f.write(html)

def stage4(group_d):
    amedas_d: dict[str, ObsPoint] = {}

    for num, name in group_d.items():
        with open(f"./group/{num}_{name}.html") as f:
            html = f.read()
            tmpd = parse_node_html(html, group_d)
            amedas_d.update(tmpd)
    
    td = {}
    for k, a in amedas_d.items():
        td[k] = a.dict()
    
    with open("amedas.json", "w") as f:
        json.dump(td, f, indent=4, ensure_ascii=False)
    
    with open("amedas_json.py", "w") as f:
        f.write("amedas_json = ")
        f.write(json.dumps(td, ensure_ascii=False))

def update_all():
    print("STAGE1 -- Get group List --")
    html = stage1()
    print("STAGE2 -- Parse group List --")
    group_d = stage2(html)
    print("STAGE3 -- Get each group Node List --")
    stage3(group_d)
    print("STAGE4 -- Parse each group Node List --")
    stage4(group_d)
    print("Update Complete")

if __name__ == '__main__':
    update_all()