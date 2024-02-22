# -*- coding: utf-8 -*-

###
# @file: makeIndustryTable.py
# @require: pip install openpyxl dataset
# @version: 0.0.3, 2024.02.22
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


#=
# EDINET23業種
#=
Record_List = [
    { "code" : "10",   "name" : "一般商工業" },
    { "code" : "11",   "name" : "建設業" },
    { "code" : "12",   "name" : "銀行・信託業" },
    { "code" : "13",   "name" : "銀行・信託業(特定取引勘定設置銀行)" },
    { "code" : "14",   "name" : "建設保証業" },
    { "code" : "15",   "name" : "第一種金融商品取引業" },
    { "code" : "16",   "name" : "生命保険業" },
    { "code" : "17",   "name" : "損害保険業" },
    { "code" : "18",   "name" : "鉄道事業" },
    { "code" : "19",   "name" : "海運事業" },
    { "code" : "20",   "name" : "高速道路事業" },
    { "code" : "21",   "name" : "電気通信事業" },
    { "code" : "22",   "name" : "電気事業" },
    { "code" : "23",   "name" : "ガス事業" },
    { "code" : "24",   "name" : "資産流動化業" },
    { "code" : "25",   "name" : "投資運用業" },
    { "code" : "26",   "name" : "投資業" },
    { "code" : "27",   "name" : "特定金融業" },
    { "code" : "28",   "name" : "社会医療法人" },
    { "code" : "29",   "name" : "学校法人" },
    { "code" : "30",   "name" : "商品先物取引業" },
    { "code" : "31",   "name" : "リース事業" },
    { "code" : "32",   "name" : "投資信託受益証券" },
]


def makeIndustryTable(db, tableName, madeFlag):
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
            'industry_code',
        ])
    # rof

    print("done")


if __name__ == '__main__':
    # pdb.set_trace()
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    argc = len(argvs)  # 引数の個数

    if argc != 4:
        print('Usage: \n python makeIndustryTable.py "Database Connecting String" "Table Name" "Made Flag String"')
        print('E.g: \n python makeIndustryTable.py "postgresql://postgres:postgres@localhost:25432/dskacc" "industry" "2024.02.22"')
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
        makeIndustryTable(db, tableName, madeFlag)
    except Exception as e:
        traceback.print_exc()
        exit(1)
    # yrt

    exit(0)