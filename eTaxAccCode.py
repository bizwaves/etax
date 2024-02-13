# -*- coding: utf-8 -*-

###
# @file: eTaxAccCode.py
# @require: pip install openpyxl dataset requests
# @usage: eTaxAccCode.ps1 参照。（ご準備：Download Url 等は Table spec_file に登録済 ※ makeDocTable.py 参考）
# @version: 0.0.1, 2024.02.13
# @author: H. Nakano, nakano-h@bitwaves.org
# @url: https://www.bitwaves.org/
###

import pdb
import dataset
import pprint
import json
import requests
import pathlib
import sys
import traceback
from openpyxl import load_workbook, Workbook

Field_Dict = {  # Row 2 : Row 3 ⇒ DB Field Name
    '0': {'name': 'industry',            'desc': '業種'},  # Industry
    "1": {'name': 'classification',      'desc': '科目分類'}, # Subject classification
    "2": {'name': 'std_label_ja',        'desc': '標準ラベル（日本語）'}, # Standard label (Japanese)
    "3": {'name': 'ret_label_ja',        'desc': '冗長ラベル（日本語）'}, # Redundant label (Japanese)
    "4": {'name': 'std_label_en',        'desc': '標準ラベル（英語）'}, # Standard label (English)
    "5": {'name': 'ret_label_en',        'desc': '冗長ラベル（英語）'}, # Redundant label (English)
    "15": {'name': 'depth',               'desc': 'depth'},  # depth
    "16": {'name': 'title_item',          'desc': 'タイトル項目'},  # Title item
    "17": {'name': 'total_usage_cate',    'desc': '合計（用途区分）'}, # Total (usage category)
    "18": {'name': 'account_category',    'desc': '勘定科目区分'},  # Account category
    "19": {'name': 'ac_cate_code',        'desc': '勘定科目コード'}, # Account category code
    "20": {'name': 'etax_acc_ja',         'desc': 'e-Tax対応勘定科目（日本語）'}, # e-Tax compatible accounts (Japanese)
    "21": {'name': 'etax_acc_en',         'desc': 'e-Tax対応勘定科目（英語）'}, # e-Tax compatible account (English)
    "22": {'name': 'etax_acc_cate',       'desc': 'e-Tax勘定科目区分'}, # e-tax account category
}


def readXlsToTable(db, name, variation, version, tableName, madeFlag):
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    # e-tax 勘定科目コード表 excel ファイルを読み込んで、Database Table に upsert する
    #   ※ ローカルファイルが存在しない場合は自動的ダウンロードする
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    # pdb.set_trace()

    # DB Table spec_file からファイル名等を取得する
    tbl_spec_file = db['spec_file']
    spec_file = tbl_spec_file.find_one(name = name, variation = variation, version = version)
    assert(spec_file is not None)
    pprint.pprint(spec_file)
    
    localfile = spec_file['localfile']
    sheetName = spec_file['sheet']
    table = spec_file['table']
    

    assert(localfile is not None and len(localfile) > 0)
    assert(sheetName is not None and len(sheetName) > 0)
    assert(table is not None and len(table) > 0)
    
    
    xlsFile = pathlib.Path(localfile)
    
    # test parent  directory of local file exists or not
    if not xlsFile.parent.is_dir():
        print("Error: {} is not a directory or not exists.".format(xlsFile.parent.absolute()))
        exit(1)
    # fi

    if not xlsFile.is_file():
        # ファイルをダウンロードする
        curl = spec_file['curl']
        print(f"{xlsFile.name} not exists, Downloading {curl} to {xlsFile.absolute()}")
        assert(curl is not None and len(curl) > 0)
        response = requests.get(curl)
        if response.status_code == 200:
            with open(xlsFile, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Error: Failed to download the file. Status code: {response.status_code}")
            # ↓ is_file check で exit しているので、ここで exit しない
        #fi
    else:
        print(f"{xlsFile.name} exists.")
    # fi

    if not xlsFile.is_file():
        print("Error: {} is not a file or not exists.".format(xlsFile.absolute()))
        exit(1)
    # fi
    
    # 拡張子チェック
    if not xlsFile.suffix.lower() in ['.xls', '.xlsx', '.xlsm']:
        print(
            "Error: The extension of the input file must be in ['.xls', '.xlsx', '.xlsm' ]")
        exit(1)
    # fi
    
    # Excel ファイルを読み込む
    wb = load_workbook(filename=xlsFile.as_posix(), data_only=True)
    ws = wb[sheetName]

    title = ws["A1"].value  # 貸借対照表　勘定科目コード表（2019年版）
    print(title)

    # ヘッダー行を読み出してフィールドリストを作成
    # ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22']
    headers = [cell.value for cell in ws[2]]
    print("headers: {0}".format(headers))

    desc_headers = [cell.value for cell in ws[3]]       # ['業種',
    print("desc_headers: {0}".format(desc_headers))

    # do some test
    assert (len(headers) == 23)
    assert (headers[0] == "0")
    assert (desc_headers[0] == '業種')

    # データベース周りの準備
    table = db[tableName]

    # Row 4 以降のデータ行を読み出し、レコードとしてDB Tableに保存
    for row in ws.iter_rows(min_row=4, values_only=True):
        record = dict(zip(headers, row))    # {'0': '一般商工業',

        # Field_Dict を適用し、DB 登録用レコードを作る
        data = {}
        for key in Field_Dict:
            data[Field_Dict[key]['name']] = record[key]
        # for

        data["jis_code"] = ""           # 【ペンディング】jis-code table へのリンク ※検討中だが、とりあえず空欄を作っておく

        # 元出処（Unique Key Fields）
        data["spec_name"] = name
        data["spec_variation"] = variation
        data["spec_version"] = version
        
        data["made_flag"] = madeFlag    # 今回作成・修正に示すフラグ

        pprint.pprint(data)

        table.upsert(data, keys=[
            'industry', 'classification', 'std_label_ja', 'ret_label_ja', 'depth', 'title_item', 'account_category',  # 合っているか？
            'ac_cate_code',
            "spec_name", "spec_variation", "spec_version"
        ])
    # rof

    print("done")


if __name__ == '__main__':
    # pdb.set_trace()
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    argc = len(argvs)  # 引数の個数

    if argc != 7:
        print('Usage: \n python eTaxAccCode.py "doc_file.name" "doc_file.variation" "doc_file.version" "Database Connecting String" "Table Nane" "Made Flag String"')
        print('Usage: \n python eTaxAccCode.py "bs.acc-cate-code.etax.acc" "all" "2019" "postgresql://postgres:postgres@localhost:25432/dskacc" "etax_account" "2014.02.13"')
        exit(1)
    # fi

    name = argvs[1]
    variation = argvs[2]
    version = argvs[3]
    dbConnStr = argvs[4]
    tableName = argvs[5]
    madeFlag = argvs[6]

    # データベースに接続
    try:
        db = dataset.connect(dbConnStr)
    except Exception as e:
        print("Error: {0}".format(e))
        exit(1)
    # yrt

    try:
        readXlsToTable(db, name, variation, version, tableName, madeFlag)
    except Exception as e:
        traceback.print_exc()
    # yrt
    
    exit(0)
