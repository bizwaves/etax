# -*- coding: utf-8 -*-

###
# @file: makeAccCateTable.py
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


#= acc_cate 勘定科目区分
# EDINETの勘定科目リストで使用されている勘定科目を財務諸表規則に基づき区分したもの。
#   select DISTINCT acc_cate from etax_account;
#   select DISTINCT acc_cate, substring(acc_code, 3, 2) from etax_account;
#   select DISTINCT acc_cate, etax_acc_cate, substring(acc_code, 3, 2) from etax_account;
#=
Acc_Cate_List = [
    { "code" : "-",    "name" : "-" },
    { "code" : "A",    "name" : "資産" },
    { "code" : "A1",   "name" : "流動資産" },
    { "code" : "A2a",  "name" : "固定資産" },
    { "code" : "A2a1", "name" : "有形固定資産" },
    { "code" : "A2a2", "name" : "無形固定資産" },
    { "code" : "A2b",  "name" : "投資その他の資産" },
    { "code" : "A3",   "name" : "繰延資産" },
    { "code" : "B",    "name" : "負債" },
    { "code" : "B1",   "name" : "流動負債" },
    { "code" : "B2",   "name" : "固定負債" },
    { "code" : "B3",   "name" : "特別法上の準備金等" },
    { "code" : "C",    "name" : "純資産" },
    { "code" : "C1a",  "name" : "資本金" },
    { "code" : "C1b",  "name" : "株主資本" },
    { "code" : "C1c",  "name" : "資本剰余金" },
    { "code" : "C1d",  "name" : "利益剰余金" },
    { "code" : "C2",   "name" : "評価・換算差額等" },
    { "code" : "C3",   "name" : "新株予約権" },
    { "code" : "D1",   "name" : "売上高" },
    { "code" : "E1",   "name" : "売上原価" },
    { "code" : "E2",   "name" : "販売費及び一般管理費" },
    { "code" : "E12",  "name" : "販売費及び一般管理費(売上原価)" },
    { "code" : "H",    "name" : "費用" },
    { "code" : "H3",   "name" : "営業外費用" },
    { "code" : "H4",   "name" : "特別損失" },
    { "code" : "F",    "name" : "損益" },
    { "code" : "G",    "name" : "収益" },
    { "code" : "G2",   "name" : "営業外収益" },
    { "code" : "G3",   "name" : "特別利益" },
    { "code" : "J1",   "name" : "その他" },
]


#= etax_acc_cate e-Tax対応勘定科目区分
# e-Taxの勘定科目を財務諸表規則に基づき区分したもの。
#   select DISTINCT etax_acc_cate from etax_account;
#   select DISTINCT etax_acc_cate, substring(acc_code, 3, 2) from etax_account;
#   select DISTINCT acc_cate, etax_acc_cate, substring(acc_code, 3, 2) from etax_account;
#=
Etax_Acc_Cate_List = [
    { "code" : "-",    "name" : "-" },
    { "code" : "A",    "name" : "資産" },
    { "code" : "A1",   "name" : "流動資産" },
    { "code" : "A2a",  "name" : "固定資産" },
    { "code" : "A2a1", "name" : "有形固定資産" },
    { "code" : "A2a2", "name" : "無形固定資産" },
    { "code" : "A2b",  "name" : "投資その他の資産" },
    { "code" : "A3",   "name" : "繰延資産" },
    { "code" : "B",    "name" : "負債" },
    { "code" : "B1",   "name" : "流動負債" },
    { "code" : "B2",   "name" : "固定負債" },
    { "code" : "B3",   "name" : "特別法上の準備金等" },
    { "code" : "C",    "name" : "純資産" },
    { "code" : "C1a",  "name" : "資本金" },
    { "code" : "C1b",  "name" : "株主資本" },
    { "code" : "C1c",  "name" : "資本剰余金" },
    { "code" : "C1d",  "name" : "利益剰余金" },
    { "code" : "C2",   "name" : "評価・換算差額等" },
    { "code" : "C3",   "name" : "新株予約権" },
    { "code" : "D1",   "name" : "売上高" },
    { "code" : "E1",   "name" : "売上原価" },
    { "code" : "E2",   "name" : "販売費及び一般管理費" },
    { "code" : "H3",   "name" : "営業外費用" },
    { "code" : "H4",   "name" : "特別損失" },    
    { "code" : "F",    "name" : "損益" },
    { "code" : "G2",   "name" : "営業外収益" },
    { "code" : "G3",   "name" : "特別利益" },
    { "code" : "J1",   "name" : "その他" },
]


def makeIndustryTable(db, tableName, racordList, madeFlag):
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    # Record_List を DB Table に upsert
    #
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    # pdb.set_trace()

    # データベース周りの準備
    table = db[tableName]

    # レコードをDB Tableに保存
    for data in racordList:
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

    if argc != 3:
        print('Usage: \n python makeAccCateTable.py "Database Connecting String" "Made Flag String"')
        print('E.g: \n python makeAccCateTable.py "postgresql://postgres:postgres@localhost:25432/dskacc" "2024.02.15"')
        exit(1)
    # fi

    dbConnStr = argvs[1]
    madeFlag = argvs[2]

    # データベースに接続
    try:
        db = dataset.connect(dbConnStr)
    except Exception as e:
        print("Error: {0}".format(e))
        exit(1)
    # yrt

    # do main work
    try:
        makeIndustryTable(db, "acc_cate", Acc_Cate_List, madeFlag)
        makeIndustryTable(db, "etax_acc_cate", Etax_Acc_Cate_List, madeFlag)
    except Exception as e:
        traceback.print_exc()
        exit(1)
    # yrt

    exit(0)