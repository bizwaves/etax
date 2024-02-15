# -*- coding: utf-8 -*-

###
# @file: makeIndustryTable.py
# @require: pip install openpyxl dataset
# @version: 0.0.2, 2024.02.15
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
    { "industry_code" : "10",   "industry_name" : "一般商工業" },
    { "industry_code" : "11",   "industry_name" : "建設業" },
    { "industry_code" : "12",   "industry_name" : "銀行・信託業" },
    { "industry_code" : "13",   "industry_name" : "銀行・信託業(特定取引勘定設置銀行)" },
    { "industry_code" : "14",   "industry_name" : "建設保証業" },
    { "industry_code" : "15",   "industry_name" : "第一種金融商品取引業" },
    { "industry_code" : "16",   "industry_name" : "生命保険業" },
    { "industry_code" : "17",   "industry_name" : "損害保険業" },
    { "industry_code" : "18",   "industry_name" : "鉄道事業" },
    { "industry_code" : "19",   "industry_name" : "海運事業" },
    { "industry_code" : "20",   "industry_name" : "高速道路事業" },
    { "industry_code" : "21",   "industry_name" : "電気通信事業" },
    { "industry_code" : "22",   "industry_name" : "電気事業" },
    { "industry_code" : "23",   "industry_name" : "ガス事業" },
    { "industry_code" : "24",   "industry_name" : "資産流動化業" },
    { "industry_code" : "25",   "industry_name" : "投資運用業" },
    { "industry_code" : "26",   "industry_name" : "投資業" },
    { "industry_code" : "27",   "industry_name" : "特定金融業" },
    { "industry_code" : "28",   "industry_name" : "社会医療法人" },
    { "industry_code" : "29",   "industry_name" : "学校法人" },
    { "industry_code" : "30",   "industry_name" : "商品先物取引業" },
    { "industry_code" : "31",   "industry_name" : "リース事業" },
    { "industry_code" : "32",   "industry_name" : "投資信託受益証券" },
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
        print('E.g: \n python makeIndustryTable.py "postgresql://postgres:postgres@localhost:25432/dskacc" "industry" "2024.02.13"')
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