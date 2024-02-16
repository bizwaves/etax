# -*- coding: utf-8 -*-


from .sqlStmt import STMT_ACC_JIS_CODES


def jis_acc_cate_codes(db):
    # = jis_acc_cate_codes 作成
    # { level, code, aname.., a_id.., a_code.., ..., names: [] }
    # =
    rc = db.query(STMT_ACC_JIS_CODES)
    rc = list(rc)

    acc_codes = []

    for row in rc:
        code = row['code']
        aname = row['aname']
        bname = row['bname']
        cname = row['cname']
        dname = row['dname']

        ch_code = list(f"{code:02d}")   # ['1', '1', '1', '1']
        # print(ch_code, aname, bname, cname, dname)

        # = code に応じて names を作成
        #   A000　AB00 ABC0 ABCD
        # =
        names = []
        level = '-'  # A, B, C, D
        assert (ch_code[0] != '0')

        if ch_code[-1] == '0':
            if ch_code[-2] == '0':
                if ch_code[-3] == '0':
                    names = [aname]
                    level = 'A'
                else:
                    names = [aname, bname]
                    level = 'B'
                # fi
            else:
                level = 'C'
                names = [aname, bname, cname]
            # fi
        else:
            names = [aname, bname, cname, dname]
            level = 'D'
        # fi

        ro = row.copy()

        if 'level' in ro:
            # d.level がある時、それが正しいかどうかをチェック ※ ↓ --make_level 参考
            assert (ro['level'] == level)
        else:
            # 初期、d.level がない時、または、d.level を 更新・修正したい時に使う
            ro['level'] = level
        # fi

        ro['names'] = names
        acc_codes.append(ro)
    # efor

    return acc_codes


def make_jis_level(db, rc):
    table = db['jis_account_d']
    for r in rc:
        code = r['code']
        level = r['level']
        table.update({'code': code, 'level': level}, ['code'])
    # efor
