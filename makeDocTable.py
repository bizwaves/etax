# -*- coding: utf-8 -*-

###
# @file: makeDocTable.py
# @require: pip install openpyxl dataset
# @version: 0.0.1, 2024.02.13
# @author: H. Nakano nakano-h@bitwaves.org
# @url: https://www.bitwaves.org/
###

import pdb
import dataset
import pprint
import json
import pathlib
import sys
import traceback
from openpyxl import load_workbook, workbook

Record_List = [
    {
        "name"      : "bs.acc-cate-code.etax.acc",  # !! ID, Key 1
        "variation" : "all",  # !! Varriant, Key 2
        "version"   : "2019",  # !! Version, Key 3
        "localfile" : "in-data/BScodeall_2019.xlsx",  # Download されたファイル
        "sheet"     : "貸借対照表　勘定科目コード表(2019年版)",  # Excel Sheet Name Or Sheet Number (0, 1, 2, ...) 書き方は要検討
        "table"     : "etax_account",  # o.p.t お勧め Database Table Name
        "parser"    : "eTaxAccCode.py",  # 解析・DB Loadプログラム
        "writer"    : "",  # 作成プログラム
        "curl"      : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/1/BScodeall_2019.xlsx",  # Download URL
        "url"       : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho4_zaihyo_taishaku_02.htm",  # o.p.t 解説ページ
        "desc"      : "ホーム > 利用可能手続一覧 > 財務諸表のＣＳＶ形式データの作成方法 > 財務諸表（貸借対照表）の勘定科目コード表及び標準フォーム（令和2年4月１日以後提出分）",  # o.p.t Description
    },
    {
        "name"      : "bs.acc-cate-code.etax.acc",
        "variation" : "10",
        "version"   : "2019",
        "localfile" : "in-data/BScode10_2019.xlsx",
        "sheet"     : "貸借対照表　勘定科目コード表(2019年版)",
        "table"     : "etax_account",
        "parser"    : "eTaxAccCode.py",
        "writer"    : "",
        "curl"      : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/1/BScode10_2019.xlsx",
        "url"       : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho4_zaihyo_taishaku_02.htm",
        "desc"      : "ホーム > 利用可能手続一覧 > 財務諸表のＣＳＶ形式データの作成方法 > 財務諸表（貸借対照表）の勘定科目コード表及び標準フォーム（令和2年4月１日以後提出分）",
    },
    {
        "name"      : "bs.standard-form.etax.acc",
        "variation" : "10",
        "version"   : "2019",
        "localfile" : "in-data/HOT010_3.0_BS_10.xlsx",
        "sheet"     : "HOT010_3.0_BS_一般商工業",
        "table"     : "",
        "parser"    : "",
        "writer"    : "makeeTaxStdForm.py",
        "curl"      : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/1/HOT010_3.0_BS_10.xlsx",
        "url"       : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho4_zaihyo_taishaku_02.htm",
        "desc"      : "ホーム > 利用可能手続一覧 > 財務諸表のＣＳＶ形式データの作成方法 > 財務諸表（貸借対照表）の勘定科目コード表及び標準フォーム（令和2年4月１日以後提出分）",
    },
    {
        "name"      : "pl.acc-cate-code.etax.acc",
        "variation" : "all",
        "version"   : "2019",
        "localfile" : "in-data/PLcodeall_2019.xlsx",
        "sheet"     : "損益計算書　勘定科目コード表(2019年版)",
        "table"     : "etax_account",
        "parser"    : "eTaxAccCode.py",
        "writer"    : "",
        "curl"      : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/2/PLcodeall_2019.xlsx",
        "url"       : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho4_zaihyo_soneki_02.htm",
        "desc"      : "ホーム > 利用可能手続一覧 > 財務諸表のＣＳＶ形式データの作成方法 > 財務諸表（損益計算書）の勘定科目コード表及び標準フォーム（令和2年4月１日以後提出分）",
    },
    {
        "name"      : "pl.acc-cate-code.etax.acc",
        "variation" : "10",
        "version"   : "2019",
        "localfile" : "in-data/PLcode10_2019.xlsx",
        "sheet"     : "損益計算書　勘定科目コード表(2019年版)",
        "table"     : "etax_account",
        "parser"    : "eTaxAccCode.py",
        "writer"    : "",
        "curl"      : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/2/PLcode10_2019.xlsx",
        "url"       : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho4_zaihyo_soneki_02.htm",
        "desc"      : "ホーム > 利用可能手続一覧 > 財務諸表のＣＳＶ形式データの作成方法 > 財務諸表（損益計算書）の勘定科目コード表及び標準フォーム（令和2年4月１日以後提出分）",
    },
    {
        "name"      : "pl.standard-form.etax.acc",
        "variation" : "10",
        "version"   : "2019",
        "localfile" : "in-data/HOT010_3.0_PL_10.xlsx",
        "sheet"     : "HOT010_3.0_PL_一般商工業",
        "table"     : "",
        "parser"    : "",
        "writer"    : "eTaxAccCode.py",
        "curl"      : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho3/1/HOT010_3.0_BS_10.xlsx",
        "url"       : "https://www.e-tax.nta.go.jp/hojin/gimuka/csv_jyoho4_zaihyo_soneki_02.htm",
        "desc"      : "ホーム > 利用可能手続一覧 > 財務諸表のＣＳＶ形式データの作成方法 > 財務諸表（損益計算書）の勘定科目コード表及び標準フォーム（令和2年4月１日以後提出分）",
    },
]


def makeDocTable(db, tableName, madeFlag):
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    # Record_List を DB Table に upsert
    #
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    # pdb.set_trace()

    # データベース周りの準備
    table = db[tableName]

    # レコードをDB Tableに保存
    for data in Record_List:
        data["made_flag"] = madeFlag    # 今回作成・修正に示すフラグ

        pprint.pprint(data)

        table.upsert(data, keys=[
            'name', 'variation', 'version'
        ])
    # rof

    print("done")


if __name__ == '__main__':
    # pdb.set_trace()
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    argc = len(argvs)  # 引数の個数

    if argc != 4:
        print('Usage: \n python makeDocTable.py "Database Connecting String" "Table Name" "Made Flag String"')
        print('E.g: \n python makeDocTable.py "postgresql://postgres:postgres@localhost:25432/dskacc" "spec_file" "2024.02.22"')
        exit(1)
    # fi

    dbConnStr = argvs[1]
    tableName = argvs[2]
    madeFlag = argvs[3]

    # データベースに接続
    try:
        db = dataset.connect(dbConnStr)
    except Exception as e:
        print("Error: {0}".format(e))
        exit(1)
    # yrt

    # do main work
    try:
        makeDocTable(db, tableName, madeFlag)
    except Exception as e:
        traceback.print_exc()
        exit(1)
    # yrt

    exit(0)