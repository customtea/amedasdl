from amedasdl_core import Amedas, AmedasNode, AmedasDataType, AmedasType
import typing
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import datetime

__author__ = 'customtea (https://github.com/customtea/)'
__version__ = '1.0.0'

table_infos = {
    AmedasDataType.TENMINUTES : { "tablename" : "tablefix1", "tablenum" : 0, },
    AmedasDataType.HOUR : { "tablename" : "tablefix1", "tablenum" : 0, }
}

csv_headers: dict[AmedasDataType, dict[AmedasType, list[str]]] = {
    AmedasDataType.TENMINUTES:{
        AmedasType.KAN : ["時分","現地気圧(hPa)","海面気圧(hPa)","降水量(mm)","気温(℃)","相対湿度(％)","平均風速(m/s)","平均風向","最大瞬間風速(m/s)","最大瞬間風向","日照時間(分)"],
        AmedasType.AUTO4 : ["時分","降水量(mm)","気温(℃)","相対湿度（%）","平均風速(m/s)","平均風向","最大瞬間風速(m/s)","最大瞬間風向","日照時間(分)"],
        AmedasType.AUTO3: [],   # ToDo
        AmedasType.AUTORAIN: [],# ToDo
        AmedasType.AUTOSNOW: [] # ToDo
    },
    AmedasDataType.HOUR:{
        AmedasType.KAN : ["時","現地気圧(hPa)","海面気圧(hPa)","降水量(mm)","気温(℃)","露点温度(℃)","蒸気圧(hPa)","湿度(％)","風速(m/s)","風向","日照時間(h)","全天日射量(MJ/m^2)","降雪(cm)","積雪(cm)", "天気記号", "雲量", "視程(km)"],
        AmedasType.AUTO4 : ["時","降水量(mm)","気温(℃)","露点温度(℃)","蒸気圧(hPa)","湿度(％)","平均風速(m/s)","風向","日照時間(h)","降雪(cm)","積雪(cm)"],
        AmedasType.AUTO3: [],   # ToDo
        AmedasType.AUTORAIN: [],# ToDo
        AmedasType.AUTOSNOW: [] # ToDo
    }
}

parse_header_nums: dict[AmedasDataType, dict[AmedasType, int]] = {
    AmedasDataType.TENMINUTES:{
        AmedasType.KAN : 2,
        AmedasType.AUTO4: 3,
        AmedasType.AUTO3: 0,    # ToDo
        AmedasType.AUTORAIN: 0, # ToDo
        AmedasType.AUTOSNOW: 0  # ToDo
    },
    AmedasDataType.HOUR:{
        AmedasType.KAN : 2,
        AmedasType.AUTO4: 2,
        AmedasType.AUTO3: 0,    # ToDo
        AmedasType.AUTORAIN: 0, # ToDo
        AmedasType.AUTOSNOW: 0  # ToDo
    }
}

def is_exception_data(raw_data: str):
    if ")" in raw_data or "]" in raw_data or "///" in raw_data or "×" in raw_data or "#" in raw_data:
        return True
    return False


class AMeDASNode(AmedasNode):
    def __check_support_dtype(self, dtype: AmedasDataType):
        return dtype is AmedasDataType.TENMINUTES or dtype is AmedasDataType.HOUR
    
    def save(self, outtype:str, dtype: AmedasDataType, date: datetime.date):
        if outtype == "csv":
            self.save_csv(dtype, date)
        elif outtype == "html":
            self.save_html(dtype, date)
        else:
            print(f"Not Support Output Format {outtype}")

    def save_csv(self, dtype: AmedasDataType, date: datetime.date):
        if not self.__check_support_dtype(dtype):
            print(f"Not Support {dtype.name} for csv output")
            return
        dpath = self.gen_savepath(date)
        filename = Path(self.gen_filename(dtype, date) + ".csv")
        dpath.mkdir(parents=True, exist_ok=True)
        savepath = dpath / filename
        html = self.download(dtype, date)
        
        tb_name = table_infos[dtype]["tablename"]
        tb_numer = table_infos[dtype]["tablenum"]
        headernum = parse_header_nums[dtype][self._obstype]
        header = csv_headers[dtype][self._obstype]
        if len(header) == 0:
            print("[Info] This Header Type is not Implement")
        table = self.parse_table_to_list(html, tb_name, headernum, tb_numer)

        csv_file = open(savepath, 'wt', newline = '', encoding = 'utf-8')
        table.insert(0, header)
        csv_write = csv.writer(csv_file)
        csv_write.writerows(table)
        csv_file.close()

    def parse_table_to_list(self, html: str, table_name: str, ignore_lines: int = 2, table_number:int = 0) -> typing.List[typing.List[str]]:
        """Extract 2dim table from HTML text

        Parameters
        ----------
        html : str
            HTML Source
        table_name : str
            Target Table Name
        ignore_lines : int, optional
            html table header count, by default 2
        table_number : int, optional
            table number (if multi table in one page), by default 0

        Returns
        -------
        typing.List[typing.List[str]]
            2dim table data
        """
        table_data = []
        soup = BeautifulSoup(html, "html.parser")
        table = soup.findAll(id=table_name)[0]
        trs = table.findAll("tr")
        for row_num, tr in enumerate(trs):
            row_data = []
            if row_num < ignore_lines:
                continue
            else:
                for col_num, cell in enumerate(tr.findAll(['td', 'th'])):
                    raw_cell = cell.get_text()
                    row_data.append(raw_cell)
            table_data.append(row_data)
        return table_data

class AMeDAS(Amedas):
    def load(self, d: dict):
        for key, value in d.items():
            self.amedas_nodes[key] = AMeDASNode.load(value)
    
    def prepare_fuzzyfinder(self):
        sug_list = []
        name2id = {}
        for am in self.amedas_nodes.values():
            name = f"{am._group_name}{am._name}"
            sug_list.append(name)
            name2id[name] = am._oid
        return sug_list, name2id




if __name__ == '__main__':
    ame = AMeDAS()
    hiroshima = ame.search_name("広島")
    # print(hiroshima)
    import datetime
    dt = datetime.datetime.now() - datetime.timedelta(days=1)
    # hiroshima.save_csv(AmedasDataType.TenMinutes, dt)
