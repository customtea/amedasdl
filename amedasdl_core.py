import json
from enum import Enum
import datetime
import requests
import time
import typing
from pathlib import Path

__author__ = 'customtea (https://github.com/customtea/)'
__version__ = '1.0.0'

class AmedasError(BaseException): pass

AMEDAS_BASEURL = "https://www.data.jma.go.jp/obd/stats/etrn/view/"

class AmedasDataType(str, Enum):
    """AMeDAS Site Support Data Type
    """
    ANNUAL      = "annually_#SPEC#"
    THREEMONTH  = "3monthly_#SPEC#1"
    ALLMONTH    = "monthly_#SPEC#3"
    YEARMONTH   = "monthly_#SPEC#1"
    TENDAYS     = "10daily_#SPEC#1"
    FIVEDAYS    = "mb5daily_#SPEC#1"
    DAY         = "daily_#SPEC#1"
    HOUR        = "hourly_#SPEC#1"
    TENMINUTES  = "10min_#SPEC#1"
    
    def s(self):
        """Spec 's'

        Returns
        -------
        str
            url_spec is s
        """
        v = self.value
        return v.replace("#SPEC#", "s")

    def a(self):
        """Spec 'a'

        Returns
        -------
        str
            url_spec is a
        """
        v = self.value
        return v.replace("#SPEC#", "a")


class AmedasNode():
    """Amedas Node
    """
    def __init__(self, obstype, prec_no, block_no, name, yomi, group_name, lat_d, lat_m, lon_d, lon_m, elev, rain, wind, temp, sun, snow, hum, ed_y, ed_m, ed_d, bikou1, bikou2, bikou3, bikou4, bikou5) -> None:
        self.prec_no = prec_no
        self.block_no = block_no
        self.obstype = obstype
        self.name = name
        self.yomi = yomi
        self.group_name = group_name
        self.lat_d = lat_d
        self.lat_m = lat_m
        self.lon_d = lon_d
        self.lon_m = lon_m
        self.elev = elev
        self.rain = int(rain)
        self.wind = int(wind)
        self.temp = int(temp)
        self.sun = int(sun)
        self.snow = int(snow)
        self.hum = int(hum)
        self.ed_y = int(ed_y)
        self.ed_m = int(ed_m)
        self.ed_d = int(ed_d)
        self.bikou1 = bikou1
        self.bikou2 = bikou2
        self.bikou3 = bikou3
        self.bikou4 = bikou4
        self.bikou5 = bikou5

    
    def __str__(self) -> str:
        return f"{self.prec_no}{self.block_no} : {self.name} {self.yomi}"
    
    def print_detail(self):
        print(f"Location Name   :   {self.name} （{self.yomi}）")
        print(f"Group Name      :   {self.group_name}")
        print(f"Prec Number     :   {self.prec_no}")
        print(f"Block Number    :   {self.block_no}")
        if self.obstype == "a":
            print("Observation Type:   AMeDAS")
        elif self.obstype == "s":
            print("Observation Type:   Weather Station")
        print(f"Coordinate Lat  :   N  {self.lat_d}° {self.lat_m}′")
        print(f"Coordinate Long :   E {self.lon_d}° {self.lon_m}′")
        print(f"Elevation       :   {self.elev}m")
        print(f"Obs Temperature :   {self.temp}")
        print(f"Obs Rain        :   {self.rain}")
        print(f"Obs WindSpeed   :   {self.wind}")
        print(f"Obs Humid       :   {self.hum}")
        print(f"Obs Sun         :   {self.sun}")
        print(f"Obs Snow        :   {self.snow}")
        if self.ed_y == 9999 or self.ed_m == 9999 or self.ed_d == 9999:
            print("State           :   Continue")
        else:
            print(f"State           :   Stop at {self.ed_y}/{self.ed_m}/{self.ed_d}")
        if self.bikou1:
            print(f"Note1           :   {self.bikou1}")
        if self.bikou2:
            print(f"Note2           :   {self.bikou2}")
        if self.bikou3:
            print(f"Note3           :   {self.bikou3}")
        if self.bikou4:
            print(f"Note4           :   {self.bikou4}")
        if self.bikou5:
            print(f"Note5           :   {self.bikou5}")
    
    @classmethod
    def load(cls, d: dict):
        tlist = []
        for key in ["obstype", "prec_no", "block_no", "name", "yomi", "group_name", "lat_d", "lat_m", "lon_d", "lon_m", "elev", "rain", "wind", "temp", "sun", "snow", "hum", "ed_y", "ed_m", "ed_d", "bikou1", "bikou2", "bikou3", "bikou4", "bikou5" ]:
            tlist.append(d[key])

        return cls(*tlist)
    
    def url(self, dtype: AmedasDataType, date: datetime.date) -> str:
        """Generate Access URL

        Parameters
        ----------
        dtype : AmedasDataType
            Data Type
        date : datetime.date
            Target Date

        Returns
        -------
        str
            url string

        Raises
        ------
        AMeDASError
            NOT Use today in date
        """ 
        if not self.__valid_date(date):
            raise AmedasError("[WARNING] NOT Use today in date")
        if self.block_no == "NoRegist":
            raise AmedasError("This Observation still not registed reference json. Please Create Issue for Github Repository")
        url = AMEDAS_BASEURL
        if self.obstype == "a":
            url += dtype.a()
        else:
            url += dtype.s()
        url += ".php?"
        url += "prec_no=" + self.prec_no
        url += "&block_no=" + self.block_no
        url += "&year=" + str(date.year)
        url += "&month=" + date.strftime("%m")
        url += "&day=" + date.strftime("%d")
        url += "&view="
        return url
    
    def __valid_date(self, date:datetime.date) -> bool:
        """valid date

        Parameters
        ----------
        date : datetime.date
            date

        Returns
        -------
        bool
            if between one day True
        """
        thdt = datetime.datetime.now() - datetime.timedelta(days=1)
        thdt = thdt.replace(hour=23, minute=59, second=59, microsecond=0)
        return date < thdt
    
    def __internal_download(self, url: str) -> str:
        """internal download

        Parameters
        ----------
        url : str
            url

        Returns
        -------
        str
            html text

        Raises
        ------
        AMeDASError
            Any Error
        """
        try:
            time.sleep(1) # Force Requset Rate Limit
            response = requests.get(url)
            response.encoding = "utf-8"
            html = response.text
        except Exception as e:
            raise AmedasError(e)
        return html
    
    def download(self, dtype: AmedasDataType, date: datetime.date) -> str:
        """download data

        Parameters
        ----------
        dtype : AmedasDataType
            Data Type
        date : datetime.date
            Target Date

        Returns
        -------
        str
            HTML text
        """
        url = self.url(dtype, date)
        print(f"DownloadURL : {url}")
        html = self.__internal_download(url)
        return html
    
    def gen_savepath(self, date: datetime.date) -> Path:
        """generate save dir name

        Parameters
        ----------
        date : datetime.date
            date

        Returns
        -------
        pathlib.Path
            dirpath
        """
        droot = Path(f"./data/{self.block_no}_{self.group_name}_{self.name}")
        year_dir = Path(date.strftime("%Y"))
        month_dir = Path(date.strftime("%m"))
        day_dir = Path(date.strftime("%d"))
        dpath = droot / year_dir / month_dir
        return dpath
    
    def gen_filename(self, dtype:AmedasDataType, date: datetime.date) -> str:
        """generate save file name

        Parameters
        ----------
        date : datetime.date
            date

        Returns
        -------
        str
            file name
        """
        return f"{date.strftime('%Y%m%d')}_{self.block_no}_{dtype.name}"
    

    def save_html(self, dtype: AmedasDataType, date: datetime.date) -> None:
        """save data for HTML File

        Parameters
        ----------
        dtype : AmedasDataType
            Data Type
        date : datetime.date
            date
        """
        dpath = self.gen_savepath(date)
        filename = Path(self.gen_filename(dtype, date) + ".html")
        dpath.mkdir(parents=True, exist_ok=True)
        savepath = dpath / filename
        html = self.download(dtype, date)
        with open(savepath, "w") as f:
            f.write(html)


class Amedas():
    amedas_nodes: typing.Dict[str, AmedasNode] = {}
    def __init__(self) -> None:
        import amedas_json
        self.load(amedas_json.amedas_json)
        # with open("./amedas.json") as f:
        #     amedas_d = json.load(f)
        #     self.load(amedas_d)
    
    def load(self, d:dict):
        for key, value in d.items():
            self.amedas_nodes[key] = AmedasNode.load(value)
    
    def list(self):
        return list(self.amedas_nodes.values())
    
    def search_oid(self, oid):
        return self.amedas_nodes.get(oid)

    def search_blockno(self, blockno):
        for ams in self.amedas_nodes.values():
            if ams.block_no == blockno:
                return ams

    def search_name(self, name):
        for ams in self.amedas_nodes.values():
            if ams.name == name:
                return ams


if __name__ == '__main__':
    ams = Amedas()
    r = ams.search_blockno("47765")
    print(r)
    dt = datetime.datetime.now() - datetime.timedelta(days=1)
    print(r.url(AmedasDataType.TENMINUTES, dt))
    print(r.print_detail())
