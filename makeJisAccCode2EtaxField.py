# -*- coding: utf-8 -*-

import pdb
import dataset
import pprint
import json
# import pathlib
import sys, copy
import traceback


# dskacc=# select * from jis_account_a;
#  id | code |          name
# ----+------+------------------------
#   1 | 1000 | 流動資産
#   2 | 2000 | 固定資産
#   3 | 3000 | 繰延資産
#   4 | 4000 | 流動負債
#   5 | 5000 | 固定負債
#   6 | 6000 | 法令上の引当金
#   7 | 7000 | 資本
#   8 | 8000 | 経常損益
#   9 | 9000 | 特別損益及び未処分損益
# (9 行)


#= JIS X0406-1984 勘定科目コード 大分類コード 1桁 ⇒ e-Tax 2019年版の勘定科目コード（BScode10_2019.xlsxとPLcode10_2019.xlsx）
#   JIS 拡張版: 1..9 A..Z a..z
#   e-Tax 2019年版の勘定科目コード（BScode10_2019.xlsxとPLcode10_2019.xlsx）: [ 業種コード, 科目分類コード, 大分類コード ]
#       業種コード      := (例) 一般商工業: "10"
#       勘定科目区分    := (例) 資産: "A"
#       大分類コード    :=() 例) 流動資産: "1"
#
# メモ
#   1.貸借対照表
#     負債の部
#         賞与引当金
#           従業員賞与の未払計上額。
#         退職給付引当金
#           退職給付債務見込額および年金資産の評価に基づき必要額を計上。
#         その他の引当金
#           商法第287条ノ２の引当金をその名称を付して処理する。
#         特別法上の引当金
#           金融先物取引責任準備金
#             金融先物取引法第82条の規定による準備金。
#           証券取引責任準備金
#             証券取引法第65条の2第7項において準用する同法第51条の規定による準備金。
#=

JIS_2_ETAX2019_A = { # depth = 0 1 2 3 := 10A1-00010
    "10" : {    # 一般商工業
        # 1桁コード       業種コード         科目分類コード,     ETax Aコード
        "1"         : { "industry" : "10", "category" : "A", "cd" : "1"},  # 流動資産 ⇒ 資産, 流動資産
        "2"         : { "industry" : "10", "category" : "A", "cd" : "2"},  # 固定資産 ⇒ 資産, 固定資産
        "3"         : { "industry" : "10", "category" : "A", "cd" : "3"},  # 繰延資産 ⇒ 資産, 繰延資産
        "4"         : { "industry" : "10", "category" : "B", "cd" : "1"},  # 流動負債 ⇒ 負債, 流動負債
        "5"         : { "industry" : "10", "category" : "B", "cd" : "2"},  # 固定負債 ⇒ 負債, 固定負債
        "6"         : { "industry" : "10", "category" : "B", "cd" : "2"},  # 法令上の引当金 ⇒ 負債, 固定負債 ※その他の引当金　特別法上の引当金
        "7"         : { "industry" : "10", "category" : "C", "cd" : "1"},  # 資本 ⇒ 純資産の部, 株主資本
        
        "8"         : { "industry" : "10", "category" : "D", "cd" : "1"},  # （旧：経常損益）経常収益 ⇒ 営業活動による収益
        "a"         : { "industry" : "10", "category" : "E", "cd" : "1"},  # （旧：経常損益）経常費用 ⇒ 営業活動による費用・売上原価
        "c"         : { "industry" : "10", "category" : "E", "cd" : "2"},  # （旧：経常損益）経常費用 ⇒ 販売費及び一般管理費
        
        "9"         : { "industry" : "10", "category" : "D", "cd" : "3"},  # （旧：特別損益及び未処分損益）特別利益及び未処分利益   ⇒ 特別損益
        "b"         : { "industry" : "10", "category" : "E", "cd" : "4"},  # （旧：特別損益及び未処分損益）特別費用及び未処分費用　 ⇒ 特別損失
    }
}


# dskacc=# select id, code, xcode, etax_code, name from jis_account_a order by xcode;
#  id | code | xcode | etax_code |          name
# ----+------+-------+-----------+------------------------
#   1 | 1000 | 1000  | 10A1      | 流動資産
#   2 | 2000 | 2000  | 10A2      | 固定資産
#   3 | 3000 | 3000  | 10A3      | 繰延資産
#   4 | 4000 | 4000  | 10B1      | 流動負債
#   5 | 5000 | 5000  | 10B2      | 固定負債
#   6 | 6000 | 6000  | 10B2      | 法令上の引当金
#   7 | 7000 | 7000  | 10C1      | 資本
#   8 | 8000 | 8000  | 10D1      | 経常収益
#   9 | 9000 | 9000  | 10D3      | 特別利益及び未処分利益
#  97 | 8000 | a000  | 10E1      | 経常費用1
#  98 | 9000 | b000  | 10E4      | 特別費用及び未処分費用
#  99 | 8000 | c000  | 10E2      | 経常費用2
# (12 行)

#= jis_account_a 2024.02.20 版
#   ! := 必須　Field
#   !! := key　Field
#   MADE := 非必須　Field, 従来アプリと互換性や管理しやすいために作成しているField　※関連データ修正する度に更新・チェックすること
#           尚、実際、同一データのMADE Fieldは複数の形式が存在し（例：code-n、code-s）、その選択は、データの利用目的やアプリに委ねる。
#   Unikue Fields: id, cd1 + cd2, code, xcode
#   備考: DB 上 Field Name は、互換性やTableの連結を保つためであり、変更はご慎重に検討の上、行うこと。
#=
JIS_2_ETAX2019_A_DATA = [ # depth = 0 1 2 3 := 10A1-00010
    #  !id        !industry              !code-1         !code-1      code-n          code-s            !etax-code-1    !etax-code-1  etax-code-s           !name                             note
    #  !! key !!  industry_code          part 1          part 2       MADE, num       MADE, ascii       part 1          part 2        MADE, str       
    # -------   ---------------------   -------------   ----------   --------------  ---------------   -------------   -----------   --------------------  -------------------------------   ----------------------------------    
    { "id": 1,  "industry_code": "10",  "cd1":   1,     "cd2":   0,  "code": 10000,  "xcode": "1000",  "etax_1": "A",  "etax_2": 1,  "etax_code": "10A1",  "name": "流動資産",                "note": "流動資産 ⇒ 資産, 流動資産" }, 
    { "id": 2,  "industry_code": "10",  "cd1":   2,     "cd2":   0,  "code": 20000,  "xcode": "2000",  "etax_1": "A",  "etax_2": 2,  "etax_code": "10A2",  "name": "固定資産",                "note": "固定資産 ⇒ 資産, 固定資産" }, 
    { "id": 3,  "industry_code": "10",  "cd1":   3,     "cd2":   0,  "code": 30000,  "xcode": "3000",  "etax_1": "A",  "etax_2": 3,  "etax_code": "10A3",  "name": "繰延資産",                "note": "繰延資産 ⇒ 資産, 繰延資産" }, 
    { "id": 4,  "industry_code": "10",  "cd1":   4,     "cd2":   0,  "code": 40000,  "xcode": "4000",  "etax_1": "B",  "etax_2": 1,  "etax_code": "10B1",  "name": "流動負債",                "note": "流動負債 ⇒ 負債, 流動負債" }, 
    { "id": 5,  "industry_code": "10",  "cd1":   5,     "cd2":   0,  "code": 50000,  "xcode": "5000",  "etax_1": "B",  "etax_2": 2,  "etax_code": "10B2",  "name": "固定負債",                "note": "固定負債 ⇒ 負債, 固定負債" }, 
    { "id": 6,  "industry_code": "10",  "cd1":   6,     "cd2":   0,  "code": 60000,  "xcode": "6000",  "etax_1": "B",  "etax_2": 2,  "etax_code": "10B2",  "name": "法令上の引当金",           "note": "法令上の引当金 ⇒ 負債, 固定負債 ※その他の引当金　特別法上の引当金" }, 
    { "id": 7,  "industry_code": "10",  "cd1":   7,     "cd2":   0,  "code": 70000,  "xcode": "7000",  "etax_1": "C",  "etax_2": 1,  "etax_code": "10C1",  "name": "資本",                    "note": "資本 ⇒ 純資産の部, 株主資本" }, 
    { "id": 8,  "industry_code": "10",  "cd1":   8,     "cd2":   0,  "code": 80000,  "xcode": "8000",  "etax_1": "D",  "etax_2": 1,  "etax_code": "10D1",  "name": "経常収益",                "note": "（旧：経常損益）経常収益 ⇒ 営業活動による収益" }, 
    { "id": 97, "industry_code": "10",  "cd1":   8,     "cd2":   1,  "code": 81000,  "xcode": "a000",  "etax_1": "E",  "etax_2": 1,  "etax_code": "10E1",  "name": "経常費用1",               "note": "（旧：経常損益）経常費用 ⇒ 営業活動による費用・売上原価" }, 
    { "id": 99, "industry_code": "10",  "cd1":   8,     "cd2":   2,  "code": 82000,  "xcode": "c000",  "etax_1": "E",  "etax_2": 2,  "etax_code": "10E2",  "name": "経常費用2",               "note": "（旧：経常損益）経常費用 ⇒ 販売費及び一般管理費" }, 
    { "id": 9,  "industry_code": "10",  "cd1":   9,     "cd2":   0,  "code": 90000,  "xcode": "9000",  "etax_1": "D",  "etax_2": 3,  "etax_code": "10D3",  "name": "特別利益及び未処分利益",   "note": "（旧：特別損益及び未処分損益）特別利益及び未処分利益 ⇒ 特別損益" }, 
    { "id": 98, "industry_code": "10",  "cd1":   9,     "cd2":   1,  "code": 91000,  "xcode": "b000",  "etax_1": "E",  "etax_2": 4,  "etax_code": "10E4",  "name": "特別費用及び未処分費用",   "note": "（旧：特別損益及び未処分損益）特別費用及び未処分費用 ⇒ 特別損失" },        
]


JIS_2_ETAX2019_B_DATA = [ # depth = 4 := 10A1.0-0010   
    #  !id        !jisacc_a_id      !code-1         !code-1      code-n            code-s            !etax-code-1    etax-code-s             !should_be_deducted          !name                              note
    #  !! key !!                    part 1          part 2       MADE, num         MADE, ascii       part 1          MADE, str       
    # -------   ------------------- -------------   ----------   --------------    ---------------   -------------   ---------------------   ---------------------------  --------------------------------  ----------------------------------                        
    { "id": 11,  "jisacc_a_id": 1,  "cd1":   1,     "cd2":   0,  "code": 10100,   "xcode": "1100",  "etax_1": 0,    "etax_code": "10A10",  "should_be_deducted": False, "name": "当座資産",                "note": ".現金及び預金.現金" },    
    { "id": 12,  "jisacc_a_id": 1,  "cd1":   2,     "cd2":   0,  "code": 10200,   "xcode": "1200",  "etax_1": 0,    "etax_code": "10A10",  "should_be_deducted": False, "name": "たな卸資産",              "note": ".商品" },
    { "id": 14,  "jisacc_a_id": 1,  "cd1":   4,     "cd2":   0,  "code": 10400,   "xcode": "1400",  "etax_1": 0,    "etax_code": "10A10",  "should_be_deducted": False, "name": "その他の流動資産",         "note": ".前渡金" },
    { "id": 21,  "jisacc_a_id": 2,  "cd1":   1,     "cd2":   0,  "code": 20100,   "xcode": "2100",  "etax_1": 1,    "etax_code": "10A21",  "should_be_deducted": False, "name": "有形固定資産",            "note": ".建物" },
    { "id": 23,  "jisacc_a_id": 2,  "cd1":   3,     "cd2":   0,  "code": 20300,   "xcode": "2300",  "etax_1": 2,    "etax_code": "10A22",  "should_be_deducted": False, "name": "無形固定資産",            "note": ".特許権" },
    { "id": 26,  "jisacc_a_id": 2,  "cd1":   6,     "cd2":   0,  "code": 20600,   "xcode": "2600",  "etax_1": 3,    "etax_code": "10A23",  "should_be_deducted": False, "name": "投資その他の資産",        "note": ".出資金" },
    { "id": 31,  "jisacc_a_id": 3,  "cd1":   1,     "cd2":   0,  "code": 30100,   "xcode": "3100",  "etax_1": 0,    "etax_code": "10A30",  "should_be_deducted": False, "name": "繰延資産",                "note": ".創立費" },
    { "id": 41,  "jisacc_a_id": 4,  "cd1":   1,     "cd2":   0,  "code": 40100,   "xcode": "4100",  "etax_1": 0,    "etax_code": "10B10",  "should_be_deducted": False, "name": "短期債務",                "note": ".買掛金" },
    { "id": 43,  "jisacc_a_id": 4,  "cd1":   3,     "cd2":   0,  "code": 40300,   "xcode": "4300",  "etax_1": 0,    "etax_code": "10B10",  "should_be_deducted": False, "name": "引当金(流動性のもの)",     "note": ".修繕引当金" },
    { "id": 45,  "jisacc_a_id": 4,  "cd1":   5,     "cd2":   0,  "code": 40500,   "xcode": "4500",  "etax_1": 0,    "etax_code": "10B10",  "should_be_deducted": False, "name": "その他の流動負債",        "note": ".未払金" },
    { "id": 51,  "jisacc_a_id": 5,  "cd1":   1,     "cd2":   0,  "code": 50100,   "xcode": "5100",  "etax_1": 0,    "etax_code": "10B20",  "should_be_deducted": False, "name": "長期債務",                "note": ".社債" },
    { "id": 53,  "jisacc_a_id": 5,  "cd1":   3,     "cd2":   0,  "code": 50300,   "xcode": "5300",  "etax_1": 0,    "etax_code": "10B20",  "should_be_deducted": False, "name": "引当金(固定性のもの)",     "note": ".修繕引当金" },
    { "id": 61,  "jisacc_a_id": 6,  "cd1":   1,     "cd2":   0,  "code": 60100,   "xcode": "6100",  "etax_1": 0,    "etax_code": "10B20",  "should_be_deducted": False, "name": "商法第287条ノ2の引当金",   "note": ".商法第287条ノ２の引当金をその名称を付して処理する。" },
    { "id": 62,  "jisacc_a_id": 6,  "cd1":   2,     "cd2":   0,  "code": 60200,   "xcode": "6200",  "etax_1": 0,    "etax_code": "10B20",  "should_be_deducted": False, "name": "特別法上の準備金・引当金", "note": ".金融先物取引責任準備金" },
    { "id": 71,  "jisacc_a_id": 7,  "cd1":   1,     "cd2":   0,  "code": 70100,   "xcode": "7100",  "etax_1": 0,    "etax_code": "10C10",  "should_be_deducted": False, "name": "資本",                    "note": ".資本金" },
    { "id": 72,  "jisacc_a_id": 7,  "cd1":   2,     "cd2":   0,  "code": 70200,   "xcode": "7200",  "etax_1": 0,    "etax_code": "10C10",  "should_be_deducted": False, "name": "法定準備金",              "note": ".法定準備金" },
    { "id": 73,  "jisacc_a_id": 7,  "cd1":   3,     "cd2":   0,  "code": 70300,   "xcode": "7300",  "etax_1": 0,    "etax_code": "10C10",  "should_be_deducted": False, "name": "その他の剰余金",           "note": ".その他の剰余金" },
    { "id": 81,  "jisacc_a_id": 8,  "cd1":   1,     "cd2":   0,  "code": 80100,   "xcode": "8100",  "etax_1": 0,    "etax_code": "10D10",  "should_be_deducted": False, "name": "売上高",                    "note": ".売上高" },
    { "id": 86,  "jisacc_a_id": 8,  "cd1":   6,     "cd2":   0,  "code": 80600,   "xcode": "8600",  "etax_1": 0,    "etax_code": "10D10",  "should_be_deducted": False, "name": "営業外収益",                "note": ".営業外収益" },
    { "id": 91,  "jisacc_a_id": 9,  "cd1":   1,     "cd2":   0,  "code": 90100,   "xcode": "9100",  "etax_1": 0,    "etax_code": "10D30",  "should_be_deducted": False, "name": "特別利益",                  "note": ".特別利益" },
    { "id": 99,  "jisacc_a_id": 9,  "cd1":   9,     "cd2":   0,  "code": 90900,   "xcode": "9900",  "etax_1": 0,    "etax_code": "10D30",  "should_be_deducted": False, "name": "当期未処分利益(又は当期未処理損失)", "note": ".当期未処分利益" },
    { "id": 82,  "jisacc_a_id": 97, "cd1":   2,     "cd2":   0,  "code": 81200,   "xcode": "a200",  "etax_1": 0,    "etax_code": "10E10",  "should_be_deducted": False, "name": "売上原価",                  "note": ".売上原価" },
    { "id": 92,  "jisacc_a_id": 98, "cd1":   2,     "cd2":   0,  "code": 91200,   "xcode": "b200",  "etax_1": 0,    "etax_code": "10E40",  "should_be_deducted": False, "name": "特別損失",                  "note": ".特別損失" },
    { "id": 98,  "jisacc_a_id": 98, "cd1":   8,     "cd2":   0,  "code": 91800,   "xcode": "b800",  "etax_1": 0,    "etax_code": "10E40",  "should_be_deducted": False, "name": "法人税及び住民税",          "note": ".法人税" },
    { "id": 83,  "jisacc_a_id": 99, "cd1":   3,     "cd2":   0,  "code": 82300,   "xcode": "c300",  "etax_1": 0,    "etax_code": "10E20",  "should_be_deducted": False, "name": "販売費及び一般管理費",      "note": ".広告宣伝費" },
    { "id": 88,  "jisacc_a_id": 99, "cd1":   8,     "cd2":   0,  "code": 82800,   "xcode": "c800",  "etax_1": 0,    "etax_code": "10E20",  "should_be_deducted": False, "name": "営業外費用",                "note": ".営業外費用" },
]



def makeJisA2EtaxField(db, industry, tableName, madeFlag):
    #= JIS_2_ETAX2019_A_DATA を jis_account_a に upsert する
    table = db[tableName]
    
    for record in JIS_2_ETAX2019_A_DATA:
        pprint.pprint(record)
        
        #= Do Some assert of Fields especially MADE Fields
        # 1) A code is nn000 ※2024.02.20 仮仕様
        assert(record["code"] % 1000 == 0)
        # 2) A xcode is "a000", length is 4
        assert(record["xcode"][:1] in "1234567890abcdefghijklmnopqrstuvwxyz")
        assert(record["xcode"][1:] == "000")
        assert(len(record["xcode"]) == 4)
        # 3) etax_code is industry_code + etax_1 + str(etax_2), length is 4
        assert(len(record["etax_code"]) == 4)
        assert(record["etax_code"][:3] == record["industry_code"] + record["etax_1"])
        assert(record["etax_code"][3:] == str(record["etax_2"]))
        # 4) TODO etax_code is exists in Table etax_account Field acc_code
        #    TODO id を etax_account Field jis_code に記入する ※2024.02.20 検討中: D時 のみ　か [A, B, C, D] すべてに記入するか
        #    dskacc=# select id, title_item, industry, depth, acc_cate, acc_code, etax_acc_ja from etax_account;
        #     id  | title_item | industry | depth | acc_cate | acc_code  |    etax_acc_ja
        #     ------+------------+----------+-------+----------+-----------+--------------------
        #         1 | t          | 10       |     0 | -        | -         | 貸借対照表
        #         2 | f          | 10       |     1 | -        | -         | 貸借対照表
        #         3 | f          | 10       |     1 | -        | -         | 貸借対照表
        #         4 | t          | 10       |     2 | A        | 10A000010 | 資産の部
        #         5 | t          | 10       |     3 | A1       | 10A100010 | 流動資産
        #         6 | f          | 10       |     4 | A1       | 10A100020 | 現金及び預金
        #         7 | f          | 10       |     4 | A1       | 10A100030 | 受取手形及び売掛金
        #         8 | f          | 10       |     5 | A1       | 10A100040 | 貸倒引当金
        
        record[ "made_flag" ] = madeFlag
        table.upsert(record, ['id'])
    #rof
    
    print("JIS_2_ETAX2019_A_DATA を jis_account_a に upsert した。")
 
 
 
def makeJisB2EtaxField(db, industry, tableName, madeFlag):
    #= JIS_2_ETAX2019_B_DATA を jis_account_b に upsert する
    table = db[tableName]
    
    for record in JIS_2_ETAX2019_B_DATA:
        print("record:")
        pprint.pprint(record)
        # pdb.set_trace()
        #= Do Some assert of Fields especially MADE Fields
        a_recs = list(db[ "jis_account_a" ].find( id = record[ "jisacc_a_id" ]))
        assert( len(a_recs) == 1 )
        a_rec = a_recs[0]
        print("parent A record:")
        pprint.pprint(a_rec)
        # 1) B code is nnn00 ※2024.02.20 仮仕様
        assert(record["code"] % 100 == 0)
        # 2) B xcode is "aa00", length is 4
        assert(record["xcode"][:1] in "1234567890abcdefghijklmnopqrstuvwxyz")
        assert(record["xcode"][1:2] in "1234567890abcdefghijklmnopqrstuvwxyz")
        assert(record["xcode"][2:] == "00")
        assert(len(record["xcode"]) == 4)
        # 3) etax_code is industry_code + etax_1 + str(etax_2), length is 5
        assert(len(record["etax_code"]) == 5)
        assert(record["etax_code"][:4] == a_rec["etax_code"])
        assert(record["etax_code"][4:] == str(record["etax_1"]))
        # 4) TODO etax_code is exists in Table etax_account Field acc_code
        #    TODO id を etax_account Field jis_code に記入する ※2024.02.20 検討中: D時 のみ　か [A, B, C, D] すべてに記入するか
        
        record[ "made_flag" ] = madeFlag
        table.upsert(record, ['id'])
    #rof
    
    print("JIS_2_ETAX2019_A_DATA を jis_account_b に upsert した。")    
    
    
def makeJisA2EtaxField_old(db, industry, tableName, madeFlag):
    # jis_account_a データを読み込む
    table = db[tableName]
    
    rows = table.all()
    
    for row in rows:
        pprint.pprint(row)  # OrderedDict([('id', 1), ('code', 1000), ('name', '流動資産')])
        
        xcode = row['xcode'] if row['xcode'] is not None else str(row['code'])
        mycode  = xcode[:1] # 1桁コード, 1..9 A..Z a..z 拡張版
        
        indusCodeDict = JIS_2_ETAX2019_A[industry]
        assert(indusCodeDict is not None)
        
        etaxCode = indusCodeDict[mycode]
        assert(etaxCode is not None)
        pprint.pprint(etaxCode)
      
        record = copy.deepcopy(row)
        record["xcode"] = xcode          # !! Str型の拡張版に変換
        record["etax_code"] = f'{etaxCode["industry"]}{etaxCode["category"]}{etaxCode["cd"]}' # e-Tax 2019年版の勘定科目コード
        record[ "made_flag" ] = madeFlag
        pprint.pprint(record)
        
        table.update(record, ['id'])
        
        #= 初期のみ実行: xcode a000 b000 作成
        # if mycode == "8":
        #     #= "9" （旧：経常損益）経常費用 レコードを作成する
        #     mycode  = "a"
        #     etaxCode = indusCodeDict[mycode]
        #     assert(etaxCode is not None)
        #     pprint.pprint(etaxCode)            
            
        #     record = copy.deepcopy(row)
        #     record["xcode"] = f'{mycode}000' # !! Str型の拡張版に変換
        #     record["etax_code"] = f'{etaxCode["industry"]}{etaxCode["category"]}{etaxCode["cd"]}' # e-Tax 2019年版の勘定科目コード
        #     record[ "made_flag" ] = madeFlag
            
        #     record["id"] = 97
        #     pprint.pprint(record)
        #     table.upsert(record, ['id', 'xcode'])
        # #fi
        # if mycode == "8":
        #     #= "9" （旧：経常損益）経常費用 レコードを作成する
        #     mycode  = "c"
        #     etaxCode = indusCodeDict[mycode]
        #     assert(etaxCode is not None)
        #     pprint.pprint(etaxCode)            
            
        #     record = copy.deepcopy(row)
        #     record["xcode"] = f'{mycode}000' # !! Str型の拡張版に変換
        #     record["etax_code"] = f'{etaxCode["industry"]}{etaxCode["category"]}{etaxCode["cd"]}' # e-Tax 2019年版の勘定科目コード
        #     record[ "made_flag" ] = madeFlag
            
        #     record["id"] = 99
        #     pprint.pprint(record)
        #     table.upsert(record, ['id', 'xcode'])
        # #fi
        # if mycode == "9":
        #     #= "9" （旧：特別損益及び未処分損益）
        #     mycode  = "b"
        #     etaxCode = indusCodeDict[mycode]
        #     assert(etaxCode is not None)
        #     pprint.pprint(etaxCode)            
            
        #     record = copy.deepcopy(row)
        #     record["xcode"] = f'{mycode}000' # !! Str型の拡張版に変換
        #     record["etax_code"] = f'{etaxCode["industry"]}{etaxCode["category"]}{etaxCode["cd"]}' # e-Tax 2019年版の勘定科目コード
        #     record[ "made_flag" ] = madeFlag
            
        #     record["id"] = 98
        #     pprint.pprint(record)
        #     table.upsert(record, ['id', 'xcode'])
        # #fi
                
    #rof
    

if __name__ == '__main__':
    # pdb.set_trace()
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    argc = len(argvs)  # 引数の個数

    if argc != 5:
        print('Usage: \n python makeJisAccCode2EtaxField.py "Database Connecting String" "industry" "a | b | c | d" "Made Flag String"')
        print('E.g: \n python makeJisAccCode2EtaxField.py "postgresql://postgres:postgres@localhost:25432/dskacc" "10" "a" "2024.02.19"')
        exit(1)
    # fi

    dbConnStr = argvs[1]
    industry = argvs[2]
    tableFix = argvs[3]
    madeFlag = argvs[4]
    
    assert(tableFix in [ "a", "b", "c", "d" ])
    tableName  = f'jis_account_{tableFix}'

    # データベースに接続
    try:
        db = dataset.connect(dbConnStr)
    except Exception as e:
        print("Error: {0}".format(e))
        exit(1)
    # yrt

    # do main work
    try:
        if tableFix  == "a":
           makeJisA2EtaxField(db, industry, tableName, madeFlag)
        elif tableFix  == "b":
           makeJisB2EtaxField(db, industry, tableName, madeFlag)
        else:
            raise ValueError('invalid fix')
        #fi
    #ryt
        
       
       
    except Exception as e:
        traceback.print_exc()
        exit(1)
    # yrt

    exit(0)