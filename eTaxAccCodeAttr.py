# -*- coding: utf-8 -*-

###
# @file: eTaxAccCodeAttr.py
# @require: pip install openpyxl dataset
# @version: 0.0.1, 2024.02.13
# @author: H. Nakano nakano-h@bitwaves.org
# @url: https://www.bitwaves.org/
###

import pdb
import dataset
import pprint
import json
import sys
import traceback


numCodeList = []  # check 用
dskCodeList = []  # check 用

#              0  1  2  3  4    5  6  7  8  9  depth
#              ↓  ↓  ↓  ↓  ↓    ↓  ↓  ↓  ↓  ↓
lastLevels = [ 0, 0, 0, 0, 0,   0, 0, 0, 0, 0 ]     #  depth 0.. のレベル追跡,  各要素は、空は 0, 有効な値は 1..n
maxLevels  = [ 0, 0, 0, 0, 0,   0, 0, 0, 0, 0 ]     #  レベル最大値の記憶
lastDepth = 0   # 最後に処理した depth

industryStruct = {}

#= 
#                     0  1  2   3    4   5     6   7  8  9
PrefixedindustryStruct = {
 '10': {'max_level': [2, 3, 18, 131, 64, 131,  39, 6, 0, 0]},
 '11': {'max_level': [2, 2, 13, 22,  14, 8,    2,  0, 0, 0]},
 '12': {'max_level': [2, 2, 8,  31,  18, 2,    4,  0, 0, 0]},
 '13': {'max_level': [2, 2, 8,  31,  18, 2,    4,  0, 0, 0]},
 '14': {'max_level': [2, 2, 11, 10,  13, 10,   4,  0, 0, 0]},
 '15': {'max_level': [2, 2, 13, 9,   19, 8,    2,  0, 0, 0]},
 '16': {'max_level': [2, 2, 9,  26,  19, 5,    1,  0, 0, 0]},
 '17': {'max_level': [2, 2, 8,  20,  21, 3,    1,  0, 0, 0]},
 '18': {'max_level': [2, 2, 18, 10,  18, 11,   8,  0, 0, 0]},
 '19': {'max_level': [2, 2, 19, 16,  15, 13,   4,  0, 0, 0]},
 '20': {'max_level': [2, 2, 13, 11,  20, 10,   11, 4, 0, 0]},
 '21': {'max_level': [2, 2, 11, 11,  17, 14,   20, 2, 0, 0]},
 '22': {'max_level': [2, 2, 15, 4,   25, 15,   2,  3, 0, 0]},
 '23': {'max_level': [2, 2, 20, 8,   18, 14,   3,  0, 0, 0]},
 '24': {'max_level': [2, 2, 16, 4,   14, 11,   8,  3, 0, 0]},
 '25': {'max_level': [2, 2, 12, 11,  12, 7,    2,  0, 0, 0]},
 '26': {'max_level': [2, 2, 15, 10,  14, 14,   3,  3, 0, 0]},
 '27': {'max_level': [2, 2, 11, 6,   15, 11,   4,  0, 0, 0]},
 '28': {'max_level': [2, 2, 10, 3,   11, 11,   4,  0, 0, 0]},
 '29': {'max_level': [2, 2, 10, 5,   14, 17,   4,  0, 0, 0]},
 '30': {'max_level': [2, 2, 11, 30,  25, 19,   4,  0, 0, 0]},
 '31': {'max_level': [2, 2, 13, 8,   25, 17,   11, 4, 0, 0]},
 '32': {'max_level': [2, 2, 20, 18,  48, 6,    0,  0, 0, 0]} 
 }

industryCounts = {}
   

def layerEncodeDsk(industry, level, maxDepth = 8):
    #= layer情報 max_level から DSK コードを生成する
    #             0  1  2       3    4    5     6  7  8  9      depth
    # [ in]  10  [2, 3, 18,     131, 64, 131,  39, 6, 0, 0]     industry level
    # [out]  10   Hi Lo ASCII   02h  02h 02h   02h Lo - -       ASCII: 1 := A, 2 := B ... 26 := Z 
    #             ※ depth = 8, 9 は、無視する
    #=
    # pdb.set_trace()
    
    # 1) industry ⇒ 02d
    n = int(industry)
    indu = f'{n:02d}'
    
    # 2) depth 0, 1 ⇒ bit 3-2, bit 1-0
    hi = level[0]
    low = level[1]
    n = hi << 2 | low
    s1 = f'{n:01x}'
    
    # 3) depth 2 ⇒ ASCII A..Z (1 := A, 2 := B ... 26 := Z)
    n = level[2]
    s2A = chr(n + 64) # A.. 
    
    # 4) depth 3..6 ⇒ 02h
    s3 = f'{level[3]:02x}'
    s4 = f'{level[4]:02x}'
    s5 = f'{level[5]:02x}'
    s6 = f'{level[6]:02x}'
    
    # 5) depth 7 ⇒ bit 3-0
    hi = 0 # !保留 
    low = level[7]
    n = hi << 4 | low
    s7 = f'{n:01x}'
    
    strCode = f'{indu}{s1}{s2A}{s3}{s4}{s5}{s6}{s7}'
            
    return strCode


def layerDecodeDsk(dskCode, maxDepth = 8):
    # [IN] '10 a P 0101 0000 0'
    #                     11 1
    #       01 2 3 4567 8901 2
    #                     
    industry = int(dskCode[0:2])
    
    layer = [ 0, 0, 0, 0, 0,   0, 0, 0, 0, 0 ]
    s1 = int(dskCode[2], 16)
    hi = s1 >> 2
    low = s1 & 0x03
    layer[0] = hi
    layer[1] = low
    
    s2A = dskCode[3]
    n = ord(s2A) - 64
    layer[2] = n
    
    s3 = int(dskCode[4:6], 16)
    s4 = int(dskCode[6:8], 16)
    s5 = int(dskCode[8:10], 16)
    s6 = int(dskCode[10:12], 16)
    layer[3] = s3
    layer[4] = s4
    layer[5] = s5
    layer[6] = s6
    
    s7 = int(dskCode[12], 16)
    hi = s7 >> 4
    low = s7 & 0x0f
    
    # hi 保留
    layer[7] = low
    
    return str(industry), layer


def layerEncodeNum(industry, level, maxDepth = 8):
    #= layer情報 max_level から Numbers コードを生成する
    #             0  1  2   3    4   5     6   7  8  9   depth
    # [ in]  10  [2, 3, 18, 131, 64, 131,  39, 6, 0, 0]  industry level
    # [out]  10   -  -  2d  3d   2d 3d     2d  1d -  -   Numbers Code 例: 10A210310 | 100100201005011 | 減価償却累計額、船舶
    #             ※ depth = 8, 9 は、無視する
    #=
    n = int(industry)
    m = 0
    for i in range(0, maxDepth):    # 0..maxDepth-1
        ev = level[i]
        if i == 7:
            m += ev                  # 7桁目 ⇒ 1桁 小計 1桁
        elif i == 6:
            m += ev * 10             # 6桁目 ⇒ 2桁 小計 3桁
        elif i == 5:
            m += ev * 1000           # 5桁目 ⇒ 3桁 小計 6桁
        elif i == 4: 
            m += ev * 1000000        # 4桁目 ⇒ 2桁 小計 8桁
        elif i == 3:
            m += ev * 100000000      # 3桁目 ⇒ 3桁 小計 11桁
        elif i == 2:
            m += ev * 100000000000   # 2桁目 ⇒ 2桁 小計 13桁
        elif i == 1:
            m += ev * 10000000000000  # 1桁目 ⇒ 1桁 小計 14桁
        elif i == 0:
            m += ev * 100000000000000 # 0桁目 ⇒ 1桁 小計 15桁
        #fi
    #rof
    m += n * 1000000000000000  # industry ⇒ 2桁 小計 15桁
            
    return m
    

def layerDecodeNum(numCode, maxDepth = 8):
    # pdb.set_trace()
    m = int(numCode)

    industry = m // 1000000000000000
    m -= industry * 1000000000000000
    
    layer = [ 0, 0, 0, 0, 0,   0, 0, 0, 0, 0 ]
    
    layer[0] = m // 100000000000000
    m -= layer[0] * 100000000000000
    layer[1] = m // 10000000000000
    m -= layer[1] * 10000000000000
    layer[2] = m // 100000000000
    m -= layer[2] * 100000000000
    layer[3] = m // 100000000
    m -= layer[3] * 100000000
    layer[4] = m // 1000000
    m -= layer[4] * 1000000
    layer[5] = m // 1000
    m -= layer[5] * 1000
    layer[6] = m // 10
    m -= layer[6] * 10
    layer[7] = m
    
    return str(industry), layer


def makeAccCodeAttr(db, tableName, industry, madeFlag):
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    # Record_List を 加工し DB Table に upsert
    #
    # = +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    global lastLevels, lastDepth, maxLevels, numCodeList, dskCodeList, industryCounts, industryStruct, PrefixedindustryStruct
    # pdb.set_trace()
    
    # reset
    lastLevels = [ 0, 0, 0, 0, 0,   0, 0, 0, 0, 0 ]
    maxLevels  = [ 0, 0, 0, 0, 0,   0, 0, 0, 0, 0 ]
    lastDepth = 0

    # データベース周りの準備
    table = db[tableName]
    
    # find the record
    Record_List = table.find(industry = industry, order_by = [ 'industry', 'id' ])

    # レコードをDB Tableに保存
    for data in Record_List:
        data["made_flag"] = madeFlag    # 今回作成・修正に示すフラグ

        depth = data["depth"]   # int, 0..
        
        #= lastDepth と比較し、当レコードの levels lastLevels を更新
        if depth < lastDepth:
            # pdb.set_trace()
            # assert depth == lastDepth - 1
            # 遡るもの: 当該 depth 以降のレベルを 0 にする
            for i in range(depth, len(lastLevels)):     # depth .. len(lastLevels) - 1
                if i < depth:
                    pass
                elif i == depth:
                    lastLevels[i] += 1
                    if lastLevels[i] > maxLevels[i]:
                        maxLevels[i] = lastLevels[i]
                    #fi
                elif i > depth:
                    lastLevels[i] = 0
                    if lastLevels[i] > maxLevels[i]:
                        maxLevels[i] = lastLevels[i]
                    #fi
                #fi
            # rof
        elif depth == lastDepth:
            # pdb.set_trace()
            lastLevels[depth] += 1
            if lastLevels[depth] > maxLevels[depth]:
                maxLevels[depth] = lastLevels[depth]
            #fi
        elif depth > lastDepth:
            # pdb.set_trace()
            if not depth == lastDepth + 1:
                print(f"Error: depth: {depth}, lastDepth: {lastDepth}")
                pprint.pprint(data)
            #fi
            assert depth == lastDepth + 1
            lastLevels[depth] = 1
            if lastLevels[depth] > maxLevels[depth]:
                maxLevels[depth] = lastLevels[depth]
            #fi
        #fi
        
        # pdb.set_trace()
        # print(f"-------\nid: {data['id']}, Old lastDepth: {lastDepth}")
        lastDepth = depth
        # print(f"New lastDepth: {lastDepth}")
        # pprint.pprint(lastLevels)
        pprint.pprint(maxLevels)

        level_code = layerEncodeNum(industry, lastLevels, 8)
        print(f"layerDecodeNum: {level_code}")
        
        #  復元テスト
        # pdb.set_trace()
        indus, layer = layerDecodeNum(level_code, 8)
        assert(indus == industry)
        for i in range(0, len(layer)):
            if not layer[i] == lastLevels[i]:
                pdb.set_trace()
            assert(layer[i] == lastLevels[i])
        
        assert not level_code in numCodeList
        numCodeList.append(level_code)
        
        dskCode = layerEncodeDsk(industry, lastLevels, 8)
        print(f"layerDecodeDsk: {dskCode}")
        
        # 復元テスト
        d_indus, d_layer = layerDecodeDsk(dskCode, 8)
        assert(d_indus == industry)
        for i in range(0, len(d_layer)):
            if not d_layer[i] == lastLevels[i]:
                pdb.set_trace()
            assert(d_layer[i] == lastLevels[i])
        
        assert not dskCode in dskCodeList
        dskCodeList.append(dskCode)
        
        data["level_code"] = level_code
        data["dsk_code"] = dskCode
        
        if not industry in industryCounts:
            industryCounts[industry] = 1    # !! 1 からスタート
        else:
            industryCounts[industry] += 1
        #fi
        
        data["indu_code"] = industryCounts[industry] # industry-code UI 上入力用の勘定科目コードとして利用予定
        
        # pprint.pprint(data)

        table.upsert(data, keys=[
            'id',
        ])
    # rof

    # maxLevels の clone を返す
    maxlevs = maxLevels.copy()
    return maxlevs


if __name__ == '__main__':
    # pdb.set_trace()
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得
    argc = len(argvs)  # 引数の個数

    if argc != 4:
        print('Usage: \n python eTaxAccCodeAttr.py "Database Connecting String" "Table Name" "Made Flag String"')
        print('E.g: \n python eTaxAccCodeAttr.py "postgresql://postgres:postgres@localhost:25432/dskacc" "etax_account" "2024.02.22" ')
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

    industryCounts = {}
    numCodeList = []    # reset
    dskCodeList = []    # reset

    industry = db['industry']
    for data in industry:
        pprint.pprint(data)
        
        code = data['code']
        name = data['name']
        
        try:
            maxlevs = makeAccCodeAttr(db, tableName, code, madeFlag)
        except Exception as e:
            traceback.print_exc()
            exit(1)
        # yrt
  
        industryStruct[code] = {
            "max_level" : maxlevs,
        }        
    # rof

    print("numCodeList:")
    print(numCodeList)
    print("dskCodeList:")
    print(dskCodeList)
    print("industryStruct:")
    pprint.pprint(industryStruct)
    print("done")

    
    
    exit(0)