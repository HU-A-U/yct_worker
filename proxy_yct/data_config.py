class Config(object):
    YCT_TASK={'project':'yct',
              'version':1,
              'zzmc':'',
              'zzjg':'',
              'catch_key_words':{'yct_no':'','register_no':'','app_no':'','zzxs':'','zzjg':''},
              'catch_url':{'/namedeclare/easy/before_apply':'','/bizhallnz_yctnew/main':'','/bizhallnz_yctnew/apply/save_info':'',
'/bizhallnz_yctnew/apply/investor/ajax/save':'','/bizhallnz_yctnew/apply/member/ajax_save_member':'','/yct_other/police/saveInputPolice':'','/yct_other/tax/saveInputTax2':'','/yct_other/tax/saveInputTax1':'','/yct_other/tax/saveInputTax3':'','/yct_other/tax/saveInputTax4':'','/yct_other/bank/saveInputBank':''},
              'catch_pic':'/uc/oauth2.0/getImage.do',
    'database':'yct_server',
    'datatable':'yct_1',
              'not_over':{'/bizhallnz_yctnew/apply/member/ajax_save_member':'','/bizhallnz_yctnew/apply/investor/ajax/save':''}}

#根据字段的提取判断出应该是哪个datatalbe
