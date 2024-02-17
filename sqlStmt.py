# -*- coding: utf-8 -*-


# = jis_account_a, b, c, d の結合 ⇒ jis_acc_cate_codes 作成
# TODO use SQLAlchemy expression
# =
STMT_ACC_JIS_CODES = """    
select 
    -- d はすべてのカラムが必要である
    d.level as level,
    d.etax_code as etax_code,
    d.code as code, 
    d.should_be_deducted as should_be_deducted,
    -- d.is_tax_related as is_tax_related
    a.name as aname, b.name as bname, c.name as cname, d.name as dname,
    a.id as a_id, b.id as b_id, c.id as c_id, d.id as d_id,
    a.code as a_code, b.code as b_code, c.code as c_code, d.code as d_code
from 
    jis_account_d as d 
left join jis_account_c as c on d.jisacc_c_id = c.id
left join jis_account_b as b on c.jisacc_b_id = b.id
left join jis_account_a as a on b.jisacc_a_id = a.id
order by d.code;
"""


STMT_ETAX_CODES = """
SELECT 
    e.id AS id,
    e.industry AS industry_code, i.industry_name AS industry_name,    
    e.classification AS classification,
    e.std_label_ja AS std_label_ja,
    -- e.ret_label_ja AS ret_label_ja,
    -- e.usage_cate_ja AS usage_cate_ja,
    -- e.namespace_prefix AS namespace_prefix,
    e.element_name AS element_name,
    
    e.acc_code AS acc_code,
    e.acc_cate AS acc_cate_code, c.name AS acc_cate_name

FROM 
    etax_account AS e
LEFT JOIN industry AS i ON e.industry = i.industry_code
LEFT JOIN etax_acc_cate AS c ON e.acc_cate = c.code
"""
