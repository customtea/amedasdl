import sys
import argparse
from dateutil.relativedelta import relativedelta
from amedasdl_adv import AMeDAS, AMeDASNode, AmedasDataType
import datetime
import typing

__author__ = 'customtea (https://github.com/customtea/)'
__version__ = '0.1.0'
__program__ = 'amedasdl'
def version():
    return f'{__program__} ver:{__version__} Created By {__author__}'



def datetime_range(start: datetime.datetime, stop: datetime.datetime, step: relativedelta = relativedelta(days=1)) -> typing.Iterator[datetime.datetime]:
    """ datetime型を1日ずつ進める
    for文でrangeの代わりに使う事ができる

    Parameters
    ----------
    start : dt.datetime
        最初の日付
    stop : dt.datetime
        最後の日付
    step : relativedelta, optional
        進める時間数日数, by default relativedelta(days=1)

    Yields
    -------
    Iterator[tp.Iterator[dt.datetime]]
        [description]
    """
    current = start
    while current < stop:
        yield current
        current += step


def getOption():
    parser = argparse.ArgumentParser(
        description="""
Notes:
    [WARNING] AMeDAS Data CANNOT download same day's
""",
    )
    loc_select_group = parser.add_argument_group("ObsSelect")
    loc_select_group = parser.add_mutually_exclusive_group(required=True)
    loc_select_group.add_argument("--search",
                        type=str,
                        metavar="Location Name for Search",
                        default=False,
                        help="観測地点名を検索する")
    loc_select_group.add_argument("--isearch",
                        type=str,
                        metavar="Location Name for Search",
                        default=False,
                        help="観測地点名を逐次検索する対話インターフェス")
    loc_select_group.add_argument('-n', '--name',
                                    nargs="?",
                                    type=str,
                                    metavar="LocationName",
                                    default=None, 
                                    help='観測地点名 カンマ区切り（スペース不可）で複数指定可能')
    loc_select_group.add_argument('-i','--oid',
                                    nargs="?",
                                    type=str,
                                    metavar="Observation ID",
                                    default=None,
                                    help="観測地点番号 カンマ区切り（スペース不可）で複数指定可能")

    output_format_group = parser.add_argument_group("Format")
    output_format_group.add_argument("-o", "--output",
                                        nargs="?",
                                        type=str,
                                        metavar="Output Format",
                                        default="csv",
                                        help="出力形式 [csv, html]")

    data_type_group = parser.add_argument_group("Data Type Group")
    data_type_group.add_argument("-t", "--dtype",
                                    nargs="?",
                                    type=str,
                                    metavar="DataType",
                                    default="TenMinutes",
                                    help="取得するデータの種類 [Annual, ThreeMonth, AllMonth, YearMonth, TenDays, FiceDays, Day, Hour,TenMinutes] カンマ区切り（スペース不可）で複数指定可能")

    parser.add_argument('-s', '--start',
                        type=str,
                        metavar="StartDate",
                        default=None,
                        help='開始日時  YYYYMMDD形式')
    parser.add_argument('-e','--end',
                        type=str,
                        metavar="EndDate",
                        default=None,
                        help='終了日時  YYYYMMDD形式')
    parser.add_argument('-l','--list',
                        action='store_true',
                        default=None,
                        help='観測地点一覧を出力')


    parser.add_argument('--version', action='version', version=version())
    return parser.parse_args()


if __name__ == '__main__':
    ams = AMeDAS()
    locations: list[AMeDASNode] = []
    data_types: list[AmedasDataType] = []
    
    opt = getOption()
    if opt.list:
        for a in ams.list():
            print(a)
        sys.exit(0)
    
    if opt.search:
        try:
            from fuzzyfinder import fuzzyfinder
            suglist, name2id = ams.prepare_fuzzyfinder()
            suggestions = fuzzyfinder(opt.search, suglist)
            # print(list(suggestions))
            for sug in suggestions:
                print(f"ID:{name2id[sug]}    {sug}")
        except ImportError:
            print("Searching Exact Match Mode. If install fuzzyfinder with pip, it will be Support Fuzzy Search")
            r = ams.search_name(opt.search)
            print(r)
        sys.exit(0)

    if opt.isearch:
        try:
            from fuzzyfinder import fuzzyfinder
        except ImportError:
            print("install fuzzyfinder with pip")
            sys.exit(1)
        suglist, name2id = ams.prepare_fuzzyfinder()
        keyword = opt.isearch
        while True:
            suggestions = list(fuzzyfinder(keyword, suglist))
            for sug in suggestions:
                print(f"ID:{name2id[sug]}    {sug}")
            if len(suggestions) == 1:
                break
            else:
                new_keyword = input(f"> {keyword}")
                keyword += new_keyword.strip()
            target = suggestions[0]
            toid = name2id[target]
        yn = input("Download This Location Data? y/n  ")
        if yn == "y":
            locations.append(ams.search_oid(toid))
            pass
        else:
            sys.exit()
    
    if opt.name:
        sname = opt.name.split(",")
        # print(sname)
        for name in sname:
            a = ams.search_name(name)
            if a is None:
                print(f"Not Found Name {name}")
            else:
                locations.append(a)

    if opt.oid:
        soid = opt.oid.split(",")
        # print(soid)
        for oid in soid:
            a = ams.search_oid(oid)
            if a is None:
                print(f"Not Found ID:{oid}")
            else:
                locations.append(a)

    if opt.dtype:
        sdytpe = opt.dtype.split(",")
        for t in sdytpe:
            try:
                dtype = AmedasDataType[t.upper()]
            except KeyError:
                print(f"Not Support Data Tyep of {t}")
            data_types.append(dtype)

    if opt.start:
        dt_start = datetime.datetime.strptime(opt.start, "%Y%m%d")
    else:
        start = input("StartDate(YYYYMMDD): ")
        dt_start = datetime.datetime.strptime(start, "%Y%m%d")

    if opt.end:
        dt_end = datetime.datetime.strptime(opt.end, "%Y%m%d")
    else:
        end = input("EndDate(YYYYMMDD)    : ")
        dt_end = datetime.datetime.strptime(end, "%Y%m%d")
    
    output_format = opt.output

    for dt_current in datetime_range(dt_start, dt_end):
        for a in locations:
            for d in data_types:
                a.save(output_format, d, dt_current)
