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

class AmedasType(str, Enum):
    AUTO4       = "auto4"
    AUTO3       = "auto3"
    KAN         = "Kan"
    AUTORAIN    = "autorain"
    AUTOSNOW    = "autosnow"

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
    def __init__(self, oid: str, prec_no: str, block_no: str, name: str, group_name: str, lat: str, long: str, elev: str, obstype:str) -> None:
        """Init

        Parameters
        ----------
        oid : str
            Observation ID
        prec_no : str
            District Number
        block_no : str
            Block Number (uniq)
        name : str
            Name
        group_name : str
            District Group Name
        lat : str
            Latitude
        long : str
            Longitude
        elev : str
            Elevation
        obstype: str
            Observation Type
            
        Attributes
        ----------
        _oid : int or None
            Observation ID
        _prec_no : str
            District Number
        _block_no : str
            Block Number (uniq)
        _name : str
            Name
        _group_name : str
            District Group Name
        _lat : float
            Latitude
        _long : float
            Longitude
        _elev : float
            Elevation
        _url_spec: str
            URL Spec
        """
        if oid is not None:
            self._oid = int(oid)
        else:
            self._oid = None
        self._prec_no = prec_no
        self._block_no = block_no
        self._name = name
        self._group_name = group_name
        self._lat = float(lat)
        self._long = float(long)
        self._elev = float(elev)
        self._obstype = AmedasType(obstype)
        self._url_spec = None

        if self._block_no != "NoRegist":
            if int(self._block_no) < 10000:
                self._url_part = "a"
            else:
                self._url_part = "s"
    
    def __str__(self) -> str:
        return f"{self._oid} : {self._name}"
    
    @classmethod
    def load(cls, d: dict):
        oid = d["oid"]
        prec_no = d["prec_no"]
        block_no = d["block_no"]
        name = d["name"]
        gname = d["group_name"]
        lat = d["lat"]
        long = d["long"]
        elev = d["elev"]
        if not "obstype" in d:
            obstype = "Kan"
        else:
            obstype = d["obstype"]
        return cls(oid, prec_no, block_no, name, gname, lat, long, elev, obstype)
    
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
        if self._block_no == "NoRegist":
            raise AmedasError("This Observation still not registed reference json. Please Create Issue for Github Repository")
        url = AMEDAS_BASEURL
        if self._url_spec == "a":
            url += dtype.a()
        else:
            url += dtype.s()
        url += ".php?"
        url += "prec_no=" + self._prec_no
        url += "&block_no=" + self._block_no
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
        droot = Path(f"./data/{self._block_no}_{self._group_name}_{self._name}")
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
        return f"{date.strftime('%Y%m%d')}_{self._block_no}_{dtype.name}"
    

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
            if ams._block_no == blockno:
                return ams

    def search_name(self, name):
        for ams in self.amedas_nodes.values():
            if ams._name == name:
                return ams


if __name__ == '__main__':
    ams = Amedas()
    r = ams.search_oid("67437")
    print(r)
    dt = datetime.datetime.now() - datetime.timedelta(days=1)
    print(r.url(AmedasDataType.TENMINUTES, dt))
