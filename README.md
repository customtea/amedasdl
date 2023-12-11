# AMeDAS Downloader
気象庁のAMeDASデータをページをスクレイピングしてデータを取得するプログラム

## Require
- requests
- beautifulsoup4
- relativedelta
- (fuzzyfinder)

## Files
- amedasdl.py
  - CUI
  - CSVをデフォルトで出力する
  ```
  usage: amedasdl.py [-h] (--search Location Name for Search | --isearch Location Name for Search | -n [LocationName] | -i [Observation ID]) [-o [Output Format]] [-t [DataType]]
                    [-s StartDate] [-e EndDate] [-l] [--version]

  Notes: [WARNING] AMeDAS Data CANNOT download same day's

  options:
    -h, --help            show this help message and exit
    --search Location Name for Search
                          観測地点名を検索する
    --isearch Location Name for Search
                          観測地点名を逐次検索する対話インターフェス
    -n [LocationName], --name [LocationName]
                          観測地点名 カンマ区切り（スペース不可）で複数指定可能
    -i [Observation ID], --oid [Observation ID]
                          観測地点番号 カンマ区切り（スペース不可）で複数指定可能
    -s StartDate, --start StartDate
                          開始日時 YYYYMMDD形式
    -e EndDate, --end EndDate
                          終了日時 YYYYMMDD形式
    -l, --list            観測地点一覧を出力
    --version             show program's version number and exit

  Format:
    -o [Output Format], --output [Output Format]
                          出力形式 [csv, html]

  Data Type Group:
    -t [DataType], --dtype [DataType]
                          取得するデータの種類 [Annual, ThreeMonth, AllMonth, YearMonth, TenDays, FiceDays, Day, Hour,TenMinutes] カンマ区切り（スペース不可）で複数指定可能
  ```
  - 複数の箇所もまとめて指定できる
  - fuzzyfinderが入っていると気象観測一覧を検索できる
    - あんまり需要は無いと思う，やりたかっただけ
    - 無くても警告が出るだけで，ただの完全一致で検索してくれる

- amedasdl_core.py
  - URLの生成などの基本的な部分が書かれている
  - これ単体でも実行できるが，HTML形式での保存しか対応していない

- amedasdl_adv.py
  - 上のcoreにページ内のtableを検索してcsvとして保存するための機能を追加したもの
  - `bs4`が入っていないと動かない

- amedas.json
  - AMeDASデータの公開ページのURL生成に必要な情報が入っている
  - 緯度経度などは要らないけど，公開されてたので入っている
  - `obstype`は観測方式？だが，これによって表示されるページのフォーマットが異なるっぽい
    - csv変換のために必要
  
- amedas_json.py
  - 上の`amedas.json`を単にpythonのモジュール化しただけ
  - ファイルをうまくPATHに突っ込むのがめんどくさかったので，モジュール化した
    - モジュールの場合は実行されるファイルのある場所からの相対パスとなるため