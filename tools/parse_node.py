import json
from bs4 import BeautifulSoup
import urllib.parse


class ObsPoint():
    def __init__(self, aors, bk_no, ch, ch_kn, lat_d, lat_m, lon_d, lon_m, height, f_pre, f_wsp, f_tem, f_sun, f_snc, f_hum, ed_y, ed_m, ed_d, bikou1, bikou2, bikou3, bikou4, bikou5)-> None:
        self.prec_no = ""
        self.block_no = bk_no
        self.obstype = aors
        self.name = ch
        self.yomi = ch_kn
        self.group_name = ""
        self.lat_d = lat_d
        self.lat_m = lat_m
        self.lon_d = lon_d
        self.lon_m = lon_m
        self.elev = height
        self.rain = int(f_pre)
        self.wind = int(f_wsp)
        self.temp = int(f_tem)
        self.sun = int(f_sun)
        self.snow = int(f_snc)
        self.hum = int(f_hum)
        self.ed_y = int(ed_y)
        self.ed_m = int(ed_m)
        self.ed_d = int(ed_d)
        self.bikou1 = bikou1
        self.bikou2 = bikou2
        self.bikou3 = bikou3
        self.bikou4 = bikou4
        self.bikou5 = bikou5
        
    def __str__(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)
    
    def dict(self):
        return self.__dict__
        
def parse_mouseover_js(text: str):
    prefix = "javascript:viewPoint("
    sufix = ");"
    t = text.removeprefix(prefix)
    t = t.removesuffix(sufix)
    ss = t.split(",")
    ss = list(map(lambda x: x.replace("'", ""),ss))
    d = ObsPoint(*ss)
    return d


def parse_node_html(html, group_d):
    tmp_d = {}
    soup = BeautifulSoup(html, "html.parser")
    map = soup.findAll("map")[0]
    for area in map.findAll("area"):
        href = urllib.parse.urlparse(area["href"])
        mouseover_js = area.get("onmouseover")
        if mouseover_js is None:
            continue
        if "prefecture.php" in href.path:
            continue
            # print(area["href"])
        # print(area)
        querry = urllib.parse.parse_qs(href.query)
        # print(querry)
        # print(mouseover_js)
        node = parse_mouseover_js(mouseover_js)
        prec_no = querry["prec_no"][0]
        node.prec_no = prec_no
        node.group_name = group_d[prec_no]
        yomi = fix_yomi(int(node.block_no))
        if not yomi is None:
            node.yomi = yomi
        # print(node)
        key = f"{node.prec_no}{node.block_no}"
        tmp_d[key] = node
    return tmp_d


def fix_yomi(bk_no):
    if bk_no == 47401:
        return 'ワッカナイ'
    if (bk_no == 47412):
        return 'サッポロ'
    if (bk_no == 47421):
        return 'スッツ'
    if (bk_no == 47433):
        return 'クッチャン'
    if (bk_no == 47520):
        return 'シンジョウ'
    if (bk_no == 47648):
        return 'チョウシ'
    if (bk_no == 47662):
        return 'トウキョウ'
    if (bk_no == 47678):
        return 'ハチジョウジマ'
    if (bk_no == 47684):
        return 'ヨッカイチ'
    if (bk_no == 47746):
        return 'トットリ'
    if (bk_no == 47759):
        return 'キョウト'
    if (bk_no == 47829):
        return 'ミヤコノジョウ'
    return None


def main():
    amedas_d: dict[str, ObsPoint] = {}
    group_d: dict[str, str] = {}
    with open("group.json")as f:
        group_d = json.load(f)

    for num, name in group_d.items():
        with open(f"./group/{num}_{name}.html") as f:
            html = f.read()
            parse_node_html(html, group_d)
    
    td = {}
    for k, a in amedas_d.items():
        td[k] = a.dict()
    
    with open("amedas.json", "w") as f:
        json.dump(td, f, indent=4, ensure_ascii=False)
    
    with open("amedas_json.py", "w") as f:
        f.write("amedas_json = ")
        f.write(json.dumps(td, ensure_ascii=False))



if __name__ == '__main__':
    main()