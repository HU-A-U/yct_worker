# -*- coding:utf-8 -*-
'''创建任务'''
import json
import random
import pickle
from handle_data import celery_app

from raven import Client

# from handle_data.rpyc_conn import rpycSer
from handle_data.save_to_mysql import Save_to_sql

cli = Client('https://6bc40853ade046ebb83077e956be04d2:d862bee828d848b6882ef875baedfe8c@sentry.cicjust.com//5')

# 建立redis连接池
import redis
from handle_data.celery_config import *

redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
r = redis.Redis(connection_pool=redis_pool)


# 建立rpyc连接
# import rpyc
# conn = rpyc.connect(rpyc_host,rpyc_port)

@celery_app.task(name='to_create')
def to_create(data_str):
    '''生产数据'''
    if not data_str:
        return
    # 将原始pickled的数据存入reids中
    # 随机生成一个数字，作为name
    name = str(random.random())
    value = data_str
    r.set(name, value, ex=3600)
    # 插入一条记录
    # save_to_product = Save_to_sql('product')
    # product_id = save_to_product.insert_new(data_str)

    # 根据返回的id res1，对数据进行解析，返回解析后的数据res2
    to_analysis.apply_async(args=[name], retry=True, queue='to_analysis', immutable=True)


@celery_app.task(name='to_analysis')
def to_analysis(name):
    # def to_analysis(data_str):
    '''解析数据'''

    # 从redis中获取值
    data = r.get(name)
    if isinstance(data, bytes):
        data_str = data.decode(encoding='utf-8')
    else:
        data_str = data
    # 进行数据解析
    analysis_data = Analysis_data(data_str, name)
    if not analysis_data:
        return

    # #将解析后的数据res2，插入数据库
    to_save.apply_async(args=[analysis_data], retry=True, queue='to_save', immutable=True)


@celery_app.task(name='to_save')
def to_save(data):
    '''消费数据'''
    # 将解析完的数据进行存库
    save_to_analysis = Save_to_sql('yctformdata')
    if data:
        is_del = data.pop('delete_set')
        if is_del:  # 判断是否删除记录
            save_to_analysis.del_set(data)
        else:
            save_to_analysis.insert_new(data)
    return data


def Analysis_data(data_str, name):
    # 数据解析
    data_dict = pickle.loads(eval(data_str))

    # 过滤 js,css,png,gif,jpg 的数据
    for end_name in ['.js', '.css', '.png', '.jpg', '.gif','.ico']:
        if end_name in data_dict.get('to_server'):
            return
    request = data_dict.get('request')
    response = data_dict.get('response')
    parameters_dict = {}
    try:
        request_form = request.urlencoded_form
        if request_form:
            for item in request_form.items():
                parameters_dict[item[0]] = item[1]
        else:
            json_data = request.text
            parameters_dict = json.loads(json_data)

    except Exception as e:
        parameters_dict = {}

    parameters = handel_parameter(parameters_dict, data_dict.get('to_server'))
    if not parameters:
        return

    # 区分不同页面的form
    page_name = filter_step(data_dict.get('to_server'))
    analysis_data = {
        'product_id': name,
        'customer_id': '',
        'methods': request.method,
        'web_name': data_dict.get('web_name'),
        'to_server': data_dict.get('to_server'),
        'time_circle': data_dict.get('time_circle'),
        'parameters': parameters,
        'pageName': page_name,
        'anync': '',
        'isSynchronous': '0',
        'delete_set': False
    }
    to_server = data_dict.get('to_server')

    #过滤无用请求
    unuse_urls = [
        'http://yct.sh.gov.cn/namedeclare','http://yct.sh.gov.cn/portal_yct',
        'http://yct.sh.gov.cn/favicon.ico',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/generateCsrfToken',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/loadAcceptSite',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/showDescription',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/establish/edit_yct',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/register',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/edit',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/entity_type',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/to_member_info',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/revert',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/main',
        'http://yct.sh.gov.cn/bizhallnz_yctnew/index'
    ]
    for url in unuse_urls:
        if url in to_server:
            return

    # apply_form的保存，会产生公司名称和yctAppNo
    if 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info' in to_server:
        registerAppNo = parameters_dict.get('registerAppNo', '')
        yctAppNo = parameters_dict.get("yctAppNo", '') or parameters_dict.get('yctSocialUnit.yctAppNo', '')
        etpsName = parameters_dict.get('etpsApp.etpsName', '')
        # 将registerAppNo对应公司名称和yctAppNo对应公司名称，暂存到redis
        r.mset({registerAppNo: etpsName, yctAppNo: etpsName})
        analysis_data['registerAppNo'] = registerAppNo
        analysis_data['yctAppNo'] = yctAppNo
        analysis_data['etpsName'] = etpsName
        analysis_data['to_server'] = 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info'

    # 针对股东或成员的保存
    elif to_server in ['http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/save',
                       'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_save_member']:
        registerAppNo = parameters_dict.get('appNo') or parameters_dict.get('etpsMember.appNo')  # 注册公司对应的唯一的appNo
        gdNo = response.text  # 股东对应的编号
        analysis_data['customer_id'] = gdNo
        analysis_data['registerAppNo'] = registerAppNo
        if r.get(registerAppNo):
            analysis_data['etpsName'] = r.get(registerAppNo).decode(encoding='utf-8') if isinstance(
                r.get(registerAppNo), bytes) else r.get(registerAppNo)
            analysis_data['yctAppNo'] = ''  # 股东没有yctAppNo，置为空

    # 针对股东的删除
    elif 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/delete' in to_server:
        from urllib import parse
        params = parse.parse_qs(parse.urlparse(to_server).query)
        gdNo = params.get('id', [])[0]
        registerAppNo = params.get('appNo', [])[0]
        analysis_data['customer_id'] = gdNo
        analysis_data['registerAppNo'] = registerAppNo
        analysis_data['delete_set'] = True

    # 针对成员的删除
    elif 'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_delete_member' in to_server:
        from urllib import parse
        params = parse.parse_qs(parse.urlparse(to_server).query)
        gdNo = params.get('id', [])[0]
        analysis_data['customer_id'] = gdNo
        analysis_data['delete_set'] = True

    # 针对其他的form的保存，前提是appNo对应apply_form已经存在库里
    else:
        yctAppNo = parameters_dict.get("yctAppNo", '') or parameters_dict.get("yctSocialUnit.yctAppNo", '')
        registerAppNo = parameters_dict.get("registerAppNo", '') or parameters_dict.get('appNo') or parameters_dict.get('etpsMember.appNo')
        if yctAppNo or registerAppNo:
            if r.get(yctAppNo):
                analysis_data['registerAppNo'] = ''
                analysis_data['yctAppNo'] = yctAppNo
                analysis_data['etpsName'] = r.get(yctAppNo).decode(encoding='utf-8') if isinstance(r.get(yctAppNo),bytes) else r.get(yctAppNo)
            elif r.get(registerAppNo):
                analysis_data['yctAppNo'] = ''
                analysis_data['registerAppNo'] = registerAppNo
                analysis_data['etpsName'] = r.get(registerAppNo).decode(encoding='utf-8') if isinstance(
                    r.get(registerAppNo), bytes) else r.get(registerAppNo)

    return analysis_data


form_url_dict = {
    'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/save_info': 'apply_form',
    'http://yct.sh.gov.cn/yct_other/social/saveSocial': 'socialForm',
    'http://yct.sh.gov.cn/yct_other/police/saveInputPolice': 'policeform',
    'http://yct.sh.gov.cn/yct_other/tax/saveInputTax1': 'tax1form',
    'http://yct.sh.gov.cn/yct_other/tax/saveInputTax2': 'tax2form',
    'http://yct.sh.gov.cn/yct_other/tax/saveInputTax3': 'tax3form',
    'http://yct.sh.gov.cn/yct_other/tax/saveInputTax4': 'tax4form',
    'http://yct.sh.gov.cn/yct_other/bank/saveInputBank': 'bankform',

    'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_save_member': 'memberform',
    'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_delete_member': 'memberform',

    'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/save': 'gdform',
    'http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/delete': 'gdform'
}


def handel_parameter(parameter_dict, url):
    '''拼接参数'''
    parameters = {}
    from handle_data.data_mapping import big_dict, gdlx, qylx, nsrlx, cyzw, fplx, szlx, skfws, chiefProvId, chiefCityId, \
        chiefDistrictId
    step_name = filter_step(url)
    if step_name == 'gdform':
        parameters.update(
            gdxm=parameter_dict.get('personInvtSet', [{}])[0].get('personName', ''),  # 姓名
            gdsfz=parameter_dict.get('personInvtSet', [{}])[0].get('cetfId', ''),  # 身份证
            gddz=parameter_dict.get('address', ''),  # 地址
            gdrj=parameter_dict.get('cptl', ''),  # 认缴金额
            czqx=parameter_dict.get('deadlineDate', ''),  # 出资期限
            gdlx=gdlx.get(parameter_dict.get('entityTypeId', ''), ''),  # 股东类型
        )
    else:
        maping_dict = big_dict.get(step_name)
        if maping_dict:
            for k, v in maping_dict.items():
                if v == 'qylx':
                    parameters[v] = qylx.get(parameter_dict.get(k, ''), '')
                elif v == 'nsrlx':
                    parameters[v] = nsrlx.get(parameter_dict.get(k, ''), '')
                elif v == 'cyzw':
                    parameters[v] = cyzw.get(parameter_dict.get(k, ''), '')
                elif v == 'fplx':
                    parameters[v] = fplx.get(parameter_dict.get(k, ''), '')
                elif v == 'szlx':
                    parameters[v] = szlx.get(parameter_dict.get(k, ''), '')
                elif v == 'skfws':
                    parameters[v] = skfws.get(parameter_dict.get(k, ''), '')
                elif k == 'frdz':
                    parameters[k] = chiefProvId.get(parameter_dict.get(v[0], ''), '') \
                                    + chiefCityId.get(parameter_dict.get(v[1], ''), '') \
                                    + chiefDistrictId.get(parameter_dict.get(v[2], ''), '')
                elif k == 'zcdz':
                    parameters[k] = parameter_dict.get(v, '')
                else:
                    parameters[v] = parameter_dict.get(k, '')
        # else:
        #     return json.dumps(parameter_dict)

    return json.dumps(parameters)


def filter_step(to_server):
    if not to_server:
        return
    pageName = ''
    for url, form_name in form_url_dict.items():
        if url in to_server:
            pageName = form_name
            break
    return pageName


if __name__ == '__main__':
    # res = to_product.apply_async(args=(1, 2), routing_key='product')
    # print(res.status)
    # to_analysis('0.6844667690124796')
    # step = filter_step('http://yct.sh.gov.cn/yct_other')
    # print(step)
    # res = to_product('{"a":"qwe"}')
    # print(res.get())
    string = b'\x80\x03}q\x00(X\x07\x00\x00\x00requestq\x01cmitmproxy.http\nHTTPRequest\nq\x02)\x81q\x03}q\x04(X\x04\x00\x00\x00dataq\x05cmitmproxy.net.http.request\nRequestData\nq\x06)\x81q\x07}q\x08(X\x11\x00\x00\x00first_line_formatq\tX\x08\x00\x00\x00relativeq\nX\x06\x00\x00\x00methodq\x0bC\x04POSTq\x0cX\x06\x00\x00\x00schemeq\rC\x04httpq\x0eX\x04\x00\x00\x00hostq\x0fC\ryct.sh.gov.cnq\x10X\x04\x00\x00\x00portq\x11KPX\x04\x00\x00\x00pathq\x12CR/bizhallnz_yctnew/apply/investor/ajax/delete?id=-846397&appNo=0000000120190506A017q\x13X\x0c\x00\x00\x00http_versionq\x14C\x08HTTP/1.1q\x15X\x07\x00\x00\x00headersq\x16cmitmproxy.net.http.headers\nHeaders\nq\x17)\x81q\x18}q\x19X\x06\x00\x00\x00fieldsq\x1a(C\x04Hostq\x1bC\ryct.sh.gov.cnq\x1c\x86q\x1dC\nUser-Agentq\x1eCRMozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0q\x1f\x86q C\x06Acceptq!C\x17text/plain, */*; q=0.01q"\x86q#C\x0fAccept-Languageq$C;zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2q%\x86q&C\x0fAccept-Encodingq\'C\rgzip, deflateq(\x86q)C\x07Refererq*C\xb1http://yct.sh.gov.cn/bizhallnz_yctnew/apply/establish/edit_yct?loginStatus=LOGIN_STATUS_PORTAL_OTHER&registerAppNo=0000000120190506A017&yctAppNo=ca422073c42947a6a86b576b0b798819q+\x86q,C\x10X-Requested-Withq-C\x0eXMLHttpRequestq.\x86q/C\nConnectionq0C\nkeep-aliveq1\x86q2C\x06Cookieq3C\xc0JSESSIONID=rBtPMABQXQni4zRYYUi8Z0QLlgM6vUkt9B4A; JSESSIONID=rBtPMABQXQmybnaU7k_X50njn_tVIVtPlzEA; BIGipServerGSJ-YCT-pool1=810490796.20480.0000; BIGipServerGSJ-INT-YCT-WEB=273617324.20480.0000q4\x86q5C\x0eContent-Lengthq6C\x010q7\x86q8tq9sbX\x07\x00\x00\x00contentq:C\x00q;X\x0f\x00\x00\x00timestamp_startq<GA\xd7B}\xa5\xa7\xd3\x95X\r\x00\x00\x00timestamp_endq=GA\xd7B}\xa5\xa8%\xf2ubX\t\x00\x00\x00is_replayq>\x89X\x06\x00\x00\x00streamq?NubX\x0b\x00\x00\x00time_circleq@X\x13\x00\x00\x002019-06-19 16:47:18qAX\x08\x00\x00\x00web_nameqBX\r\x00\x00\x00yct.sh.gov.cnqCX\t\x00\x00\x00to_serverqDXf\x00\x00\x00http://yct.sh.gov.cn/bizhallnz_yctnew/apply/investor/ajax/delete?id=-846397&appNo=0000000120190506A017qEX\x08\x00\x00\x00responseqFcmitmproxy.http\nHTTPResponse\nqG)\x81qH}qI(h\x05cmitmproxy.net.http.response\nResponseData\nqJ)\x81qK}qL(h\x14C\x08HTTP/1.1qMX\x0b\x00\x00\x00status_codeqNK\xc8X\x06\x00\x00\x00reasonqOC\x02OKqPh\x16h\x17)\x81qQ}qRh\x1a(C\x04DateqSC\x1dWed, 19 Jun 2019 08:47:55 GMTqT\x86qUC\x0cContent-TypeqVC\x17text/html;charset=UTF-8qW\x86qXC\x0eContent-LengthqYh7\x86qZC\x06Serverq[C\x06******q\\\x86q]C\x06Pragmaq^C\x08no-cacheq_\x86q`C\x07ExpiresqaC\x1dThu, 01 Jan 1970 00:00:00 GMTqb\x86qcC\rCache-ControlqdC\x12no-cache, no-storeqe\x86qfC\x0eAccept-CharsetqgBT\x07\x00\x00big5, big5-hkscs, compound_text, euc-jp, euc-kr, gb18030, gb2312, gbk, ibm-thai, ibm00858, ibm01140, ibm01141, ibm01142, ibm01143, ibm01144, ibm01145, ibm01146, ibm01147, ibm01148, ibm01149, ibm037, ibm1026, ibm1047, ibm273, ibm277, ibm278, ibm280, ibm284, ibm285, ibm297, ibm420, ibm424, ibm437, ibm500, ibm775, ibm850, ibm852, ibm855, ibm857, ibm860, ibm861, ibm862, ibm863, ibm864, ibm865, ibm866, ibm868, ibm869, ibm870, ibm871, ibm918, iso-2022-cn, iso-2022-jp, iso-2022-jp-2, iso-2022-kr, iso-8859-1, iso-8859-13, iso-8859-15, iso-8859-2, iso-8859-3, iso-8859-4, iso-8859-5, iso-8859-6, iso-8859-7, iso-8859-8, iso-8859-9, jis_x0201, jis_x0212-1990, koi8-r, koi8-u, shift_jis, tis-620, us-ascii, utf-16, utf-16be, utf-16le, utf-32, utf-32be, utf-32le, utf-8, windows-1250, windows-1251, windows-1252, windows-1253, windows-1254, windows-1255, windows-1256, windows-1257, windows-1258, windows-31j, x-big5-hkscs-2001, x-big5-solaris, x-euc-jp-linux, x-euc-tw, x-eucjp-open, x-ibm1006, x-ibm1025, x-ibm1046, x-ibm1097, x-ibm1098, x-ibm1112, x-ibm1122, x-ibm1123, x-ibm1124, x-ibm1364, x-ibm1381, x-ibm1383, x-ibm33722, x-ibm737, x-ibm833, x-ibm834, x-ibm856, x-ibm874, x-ibm875, x-ibm921, x-ibm922, x-ibm930, x-ibm933, x-ibm935, x-ibm937, x-ibm939, x-ibm942, x-ibm942c, x-ibm943, x-ibm943c, x-ibm948, x-ibm949, x-ibm949c, x-ibm950, x-ibm964, x-ibm970, x-iscii91, x-iso-2022-cn-cns, x-iso-2022-cn-gb, x-iso-8859-11, x-jis0208, x-jisautodetect, x-johab, x-macarabic, x-maccentraleurope, x-maccroatian, x-maccyrillic, x-macdingbat, x-macgreek, x-machebrew, x-maciceland, x-macroman, x-macromania, x-macsymbol, x-macthai, x-macturkish, x-macukraine, x-ms932_0213, x-ms950-hkscs, x-ms950-hkscs-xp, x-mswin-936, x-pck, x-sjis_0213, x-utf-16le-bom, x-utf-32be-bom, x-utf-32le-bom, x-windows-50220, x-windows-50221, x-windows-874, x-windows-949, x-windows-950, x-windows-iso2022jpqh\x86qiC\rAccept-RangesqjC\x05bytesqk\x86qltqmsbh:h;h<GA\xd7B}\xa5\xad\x19"h=GA\xd7B}\xa5\xae Subh>\x89h?Nubu.'
    # string = b'\x80\x03}q\x00(X\x07\x00\x00\x00requestq\x01cmitmproxy.http\nHTTPRequest\nq\x02)\x81q\x03}q\x04(X\x04\x00\x00\x00dataq\x05cmitmproxy.net.http.request\nRequestData\nq\x06)\x81q\x07}q\x08(X\x11\x00\x00\x00first_line_formatq\tX\x08\x00\x00\x00relativeq\nX\x06\x00\x00\x00methodq\x0bC\x04POSTq\x0cX\x06\x00\x00\x00schemeq\rC\x04httpq\x0eX\x04\x00\x00\x00hostq\x0fC\ryct.sh.gov.cnq\x10X\x04\x00\x00\x00portq\x11KPX\x04\x00\x00\x00pathq\x12C=/bizhallnz_yctnew/apply/member/ajax_delete_member?id=-1104621q\x13X\x0c\x00\x00\x00http_versionq\x14C\x08HTTP/1.1q\x15X\x07\x00\x00\x00headersq\x16cmitmproxy.net.http.headers\nHeaders\nq\x17)\x81q\x18}q\x19X\x06\x00\x00\x00fieldsq\x1a(C\x04Hostq\x1bC\ryct.sh.gov.cnq\x1c\x86q\x1dC\nUser-Agentq\x1eCRMozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0q\x1f\x86q C\x06Acceptq!C\x17text/plain, */*; q=0.01q"\x86q#C\x0fAccept-Languageq$C;zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2q%\x86q&C\x0fAccept-Encodingq\'C\rgzip, deflateq(\x86q)C\x07Refererq*C\xb1http://yct.sh.gov.cn/bizhallnz_yctnew/apply/establish/edit_yct?loginStatus=LOGIN_STATUS_PORTAL_OTHER&registerAppNo=0000000120190506A017&yctAppNo=ca422073c42947a6a86b576b0b798819q+\x86q,C\x10X-Requested-Withq-C\x0eXMLHttpRequestq.\x86q/C\nConnectionq0C\nkeep-aliveq1\x86q2C\x06Cookieq3C\xc0JSESSIONID=rBtPMABQXQni4zRYYUi8Z0QLlgM6vUkt9B4A; JSESSIONID=rBtPMABQXQmybnaU7k_X50njn_tVIVtPlzEA; BIGipServerGSJ-YCT-pool1=810490796.20480.0000; BIGipServerGSJ-INT-YCT-WEB=273617324.20480.0000q4\x86q5C\x0eContent-Lengthq6C\x010q7\x86q8tq9sbX\x07\x00\x00\x00contentq:C\x00q;X\x0f\x00\x00\x00timestamp_startq<GA\xd7B\x80\x02\xdc\x1d\xb0X\r\x00\x00\x00timestamp_endq=GA\xd7B\x80\x02\xdc\x90\xafubX\t\x00\x00\x00is_replayq>\x89X\x06\x00\x00\x00streamq?NubX\x0b\x00\x00\x00time_circleq@X\x13\x00\x00\x002019-06-19 17:27:39qAX\x08\x00\x00\x00web_nameqBX\r\x00\x00\x00yct.sh.gov.cnqCX\t\x00\x00\x00to_serverqDXQ\x00\x00\x00http://yct.sh.gov.cn/bizhallnz_yctnew/apply/member/ajax_delete_member?id=-1104621qEX\x08\x00\x00\x00responseqFcmitmproxy.http\nHTTPResponse\nqG)\x81qH}qI(h\x05cmitmproxy.net.http.response\nResponseData\nqJ)\x81qK}qL(h\x14C\x08HTTP/1.1qMX\x0b\x00\x00\x00status_codeqNK\xc8X\x06\x00\x00\x00reasonqOC\x02OKqPh\x16h\x17)\x81qQ}qRh\x1a(C\x04DateqSC\x1dWed, 19 Jun 2019 09:28:16 GMTqT\x86qUC\x0cContent-TypeqVC\x17text/html;charset=UTF-8qW\x86qXC\x0eContent-LengthqYh7\x86qZC\x06Serverq[C\x06******q\\\x86q]C\x06Pragmaq^C\x08no-cacheq_\x86q`C\x07ExpiresqaC\x1dThu, 01 Jan 1970 00:00:00 GMTqb\x86qcC\rCache-ControlqdC\x12no-cache, no-storeqe\x86qfC\x0eAccept-CharsetqgBT\x07\x00\x00big5, big5-hkscs, compound_text, euc-jp, euc-kr, gb18030, gb2312, gbk, ibm-thai, ibm00858, ibm01140, ibm01141, ibm01142, ibm01143, ibm01144, ibm01145, ibm01146, ibm01147, ibm01148, ibm01149, ibm037, ibm1026, ibm1047, ibm273, ibm277, ibm278, ibm280, ibm284, ibm285, ibm297, ibm420, ibm424, ibm437, ibm500, ibm775, ibm850, ibm852, ibm855, ibm857, ibm860, ibm861, ibm862, ibm863, ibm864, ibm865, ibm866, ibm868, ibm869, ibm870, ibm871, ibm918, iso-2022-cn, iso-2022-jp, iso-2022-jp-2, iso-2022-kr, iso-8859-1, iso-8859-13, iso-8859-15, iso-8859-2, iso-8859-3, iso-8859-4, iso-8859-5, iso-8859-6, iso-8859-7, iso-8859-8, iso-8859-9, jis_x0201, jis_x0212-1990, koi8-r, koi8-u, shift_jis, tis-620, us-ascii, utf-16, utf-16be, utf-16le, utf-32, utf-32be, utf-32le, utf-8, windows-1250, windows-1251, windows-1252, windows-1253, windows-1254, windows-1255, windows-1256, windows-1257, windows-1258, windows-31j, x-big5-hkscs-2001, x-big5-solaris, x-euc-jp-linux, x-euc-tw, x-eucjp-open, x-ibm1006, x-ibm1025, x-ibm1046, x-ibm1097, x-ibm1098, x-ibm1112, x-ibm1122, x-ibm1123, x-ibm1124, x-ibm1364, x-ibm1381, x-ibm1383, x-ibm33722, x-ibm737, x-ibm833, x-ibm834, x-ibm856, x-ibm874, x-ibm875, x-ibm921, x-ibm922, x-ibm930, x-ibm933, x-ibm935, x-ibm937, x-ibm939, x-ibm942, x-ibm942c, x-ibm943, x-ibm943c, x-ibm948, x-ibm949, x-ibm949c, x-ibm950, x-ibm964, x-ibm970, x-iscii91, x-iso-2022-cn-cns, x-iso-2022-cn-gb, x-iso-8859-11, x-jis0208, x-jisautodetect, x-johab, x-macarabic, x-maccentraleurope, x-maccroatian, x-maccyrillic, x-macdingbat, x-macgreek, x-machebrew, x-maciceland, x-macroman, x-macromania, x-macsymbol, x-macthai, x-macturkish, x-macukraine, x-ms932_0213, x-ms950-hkscs, x-ms950-hkscs-xp, x-mswin-936, x-pck, x-sjis_0213, x-utf-16le-bom, x-utf-32be-bom, x-utf-32le-bom, x-windows-50220, x-windows-50221, x-windows-874, x-windows-949, x-windows-950, x-windows-iso2022jpqh\x86qiC\rAccept-RangesqjC\x05bytesqk\x86qltqmsbh:h;h<GA\xd7B\x80\x02\xde\xdc\x1ah=GA\xd7B\x80\x02\xdf\xca!ubh>\x89h?Nubu.'
    a = Analysis_data(string, '0.9094022512644758')
