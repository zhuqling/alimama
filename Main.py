# -*- coding:utf-8 -*-

import urllib
import urllib2
import cookielib
import re
import webbrowser
import json
import requests
#避免sslv3 alert handshake failure错误
import requests.packages.urllib3.util.ssl_
import warnings

#模拟登录淘宝+阿里妈妈类
class Taobao:
 
    #初始化方法
    def __init__(self):
        #避免sslv3 alert handshake failure错误
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
        #不显示警告
        warnings.filterwarnings("ignore")
        #登录的URL
        self.loginURL = "https://login.taobao.com/member/login.jhtml?style=mini&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true"
        #登录POST数据时发送的头部信息
        self.loginHeaders =  {
            'Host':'login.taobao.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
            'Referer' : 'https://login.taobao.com/member/login.jhtml?style=mini&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'Keep-Alive'
        }
        #Need to Set
        #用户名
        self.username = 'Your Username'
        #Need to Set
        #ua字符串，经过淘宝ua算法计算得出，包含了时间戳,浏览器,屏幕分辨率,随机数,鼠标移动,鼠标点击,其实还有键盘输入记录,鼠标移动的记录、点击的记录等等的信息
        self.ua = 'Your UA'
        #Need to Set
        #密码，在这里不能输入真实密码，淘宝对此密码进行了加密处理，256位，此处为加密后的密码
        self.password2 = 'Your Password'
        self.post = post = {
            'ua':self.ua,
            'TPL_checkcode':'',
            'CtrlVersion': '1,0,0,7',
            'TPL_password':'',
            'TPL_redirect_url':'http://login.taobao.com/member/taobaoke/login.htm?is_login=1',
            'TPL_username':self.username,
            'loginsite':'0',
            'newlogin':'0',
            'from':'tb',
            'fc':'default',
            'style':'default',
            'css_style':'',
            'tid':'XOR_1_000000000000000000000000000000_625C4720470A0A050976770A',
            'support':'000001',
            'loginType':'4',
            'minititle':'',
            'minipara':'',
            'umto':'NaN',
            'pstrong':'3',
            'llnick':'',
            'sign':'',
            'need_sign':'',
            'isIgnore':'',
            'full_redirect':'',
            'popid':'',
            'callback':'',
            'guf':'',
            'not_duplite_str':'',
            'need_user_id':'',
            'poy':'',
            'gvfdcname':'10',
            'gvfdcre':'',
            'from_encoding ':'',
            'sub':'',
            'TPL_password_2':self.password2,
            'loginASR':'1',
            'loginASRSuc':'1',
            'allp':'',
            'oslanguage':'zh-CN',
            'sr':'1366*768',
            'osVer':'windows|6.1',
            'naviVer':'firefox|35'
        }
        #登录代理（自行设置）
        self.proxyURL = 'http://120.193.146.97:843'
        self.proxy = urllib2.ProxyHandler({'http':self.proxyURL})
        #将POST的数据进行编码转换
        self.postData = urllib.urlencode(self.post)
        #设置cookie
        self.cookie = cookielib.LWPCookieJar()
        #设置cookie处理器
        self.cookieHandler = urllib2.HTTPCookieProcessor(self.cookie)
        #设置登录时用到的opener，它的open方法相当于urllib2.urlopen
        self.opener = urllib2.build_opener(self.cookieHandler,urllib2.HTTPHandler,self.proxy)
        #赋值J_HToken
        self.J_HToken = ''
        #urllib2：302处理实在没法用，只能改用requests
        self.newReq = requests.Session()
        #Need to Set
        #阿里妈妈第一次302跳转中sign_account参数
        self.sign_account = 'Your Alimama Sign_Account'
        #Need to Set
        #阿里妈妈展示位ID
        self.adzoneid = 'Your Adzone ID'
        #Need to Set
        #阿里妈妈站点ID
        self.siteid = 'Your Site ID'

        
 
    #得到是否需要输入验证码，这次请求的相应有时会不同，有时需要验证有时不需要
    def needCheckCode(self):
        #第一次登录获取验证码尝试，构建request
        request = urllib2.Request(self.loginURL,self.postData,self.loginHeaders)
        #得到第一次登录尝试的相应
        response = self.opener.open(request)
        #获取其中的内容
        content = response.read().decode('gbk')
        #获取状态吗
        status = response.getcode()
        #状态码为200，获取成功
        if status == 200:
            print u"获取请求成功"
            #\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801这六个字是请输入验证码的utf-8编码
            pattern = re.compile(u'\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801',re.S)
            result = re.search(pattern,content)
            #如果找到该字符，代表需要输入验证码
            if result:
                print u"此次安全验证异常，您需要输入验证码"
                return content
            #否则不需要
            else:
                #返回结果直接带有J_HToken字样，表明直接验证通过
                tokenPattern = re.compile('id="J_HToken" value="(.*?)"')
                tokenMatch = re.search(tokenPattern,content)
                if tokenMatch:
                    self.J_HToken = tokenMatch.group(1)
                    print u"此次安全验证通过，您这次不需要输入验证码"
                    return False
        else:
            print u"获取请求失败"
            return None


 
    #得到验证码图片
    def getCheckCode(self,page):
        #得到验证码的图片
        pattern = re.compile('<img id="J_StandardCode_m.*?data-src="(.*?)"',re.S)
        #匹配的结果
        matchResult = re.search(pattern,page)
        #已经匹配得到内容，并且验证码图片链接不为空
        if matchResult and matchResult.group(1):
            return matchResult.group(1)
        else:
            print u"没有找到验证码内容"
            return False

 
 
    #输入验证码，重新请求，如果验证成功，则返回J_HToken
    def loginWithCheckCode(self):
        #提示用户输入验证码
        checkcode = raw_input(u'请输入验证码:')
        #将验证码重新添加到post的数据中
        self.post['TPL_checkcode'] = checkcode
        #对post数据重新进行编码
        self.postData = urllib.urlencode(self.post)
        try:
            #再次构建请求，加入验证码之后的第二次登录尝试
            request = urllib2.Request(self.loginURL,self.postData,self.loginHeaders)
            #得到第一次登录尝试的相应
            response = self.opener.open(request)
            #获取其中的内容
            content = response.read().decode('gbk')
            #检测验证码错误的正则表达式，\u9a8c\u8bc1\u7801\u9519\u8bef 是验证码错误五个字的编码
            pattern = re.compile(u'\u9a8c\u8bc1\u7801\u9519\u8bef',re.S)
            result = re.search(pattern,content)
            #如果返回页面包括了，验证码错误五个字
            if result:
                print u"验证码输入错误"
                return False
            else:
                #返回结果直接带有J_HToken字样，说明验证码输入成功，成功跳转到了获取HToken的界面
                tokenPattern = re.compile('id="J_HToken" value="(.*?)"')
                tokenMatch = re.search(tokenPattern,content)
                #如果匹配成功，找到了J_HToken
                if tokenMatch:
                    print u"验证码输入正确"
                    self.J_HToken = tokenMatch.group(1)
                    return tokenMatch.group(1)
                else:
                    #匹配失败，J_Token获取失败
                    print u"J_Token获取失败"
                    return False
        except urllib2.HTTPError, e:
            print u"连接服务器出错，错误原因",e.reason
            return False
 

 
    #通过token获得st
    def getSTbyToken(self,token):
        tokenURL = 'https://passport.alipay.com/mini_apply_st.js?site=0&token=%s&callback=stCallback6' % token
        request = urllib2.Request(tokenURL)
        response = urllib2.urlopen(request)
        #处理st，获得用户淘宝主页的登录地址
        pattern = re.compile('{"st":"(.*?)"}',re.S)
        result = re.search(pattern,response.read())
        #如果成功匹配
        if result:
            print u"成功获取st码"
            #获取st的值
            st = result.group(1)
            return st
        else:
            print u"未匹配到st"
            return False


 
    #利用st码进行登录,获取重定向网址
    def loginByST(self,st,username):
        stURL = 'https://login.taobao.com/member/vst.htm?st=%s&TPL_username=%s' % (st,username)
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
            'Host':'login.taobao.com',
            'Connection' : 'Keep-Alive'
        }
        response = self.newReq.get(stURL,headers=headers,verify=False)
        content = response.text
        #检测结果，看是否登录成功
        pattern = re.compile('top.location = "(.*?)"',re.S)
        match = re.search(pattern,content)
        if match:
            print u"登录网址成功"
            location = match.group(1)
            return True
        else:
            print "登录失败"
            return False



    #阿里妈妈Sign，三次302重定向认证，urllib处理cookie根本用不了，只好改用requests，神清气爽    
    def loginOnAlimama(self): #return (type) void
        print u'阿里妈妈Sign开始'
        URL = 'http://www.alimama.com/membersvc/my.htm?domain=taobao&service=user_on_taobao&sign_account=' + self.sign_account
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
            'Connection' : 'Keep-Alive'
        }
        response = self.newReq.get(URL,headers=headers,verify=False)
        print u'阿里妈妈Sign结束'
        return 0
        

 
    #获得宝贝信息返回Json
    def getAuctionList(self): #return (type) json
        URL = 'http://pub.alimama.com/pubauc/searchAuctionList.json'
        data = {
            'spm':'a2320.7388781.a214tr8.d006.IGMump',
            'toPage':'1',
            'perPagesize':'40',
            't':'1443670734640',
            '_tb_token_':'dn05C3crepo',
            '_input_charset':'utf-8',
            #输入问题
            'q': raw_input(u"关键词：")
            }
        response = self.newReq.get(URL,params=data,verify=False)
        jsonda = response.json()
        return jsonda



    #获得宝贝佣金连接
    def getAuctionLink(self,auctionID): #return (type) string 
        URL = 'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid=%s&adzoneid=%s&siteid=%s&t=1443838678475&_tb_token_=bHI9Bztm1qo&_input_charset=utf-8' % (auctionID, self.adzoneid, self.siteid)
        response = self.newReq.get(URL,verify=False)
        jsonda = response.json()
        return jsonda['data']['shortLinkUrl']

    #输入关键字，返回（无中文）
    def printAuctionList(self):# return (type) void
        #得到商品Json列表
        jsondata = self.getAuctionList()
        print u'%-20s%-20s%-20s%-20s%-20s%-20s%-20s' % (u'商品名称',u'折扣',u'现价',u'收入比率',u'佣金',u'30天推广量',u'30天支出佣金')
        #遍历json输出
        for jsonvar in range(0,len(jsondata['data']['pagelist'])):
            jsontemp = jsondata['data']['pagelist'][jsonvar]
            print u'%-20s%-20s%-20s%-20s%-20s%-20s%-20s' % (jsontemp['title'].replace("<span class=H>","").replace("</span>",""),jsontemp['zkRate'],jsontemp['zkPrice'],str(jsontemp['commissionRatePercent']) + '%',jsontemp['calCommission'],jsontemp['totalNum'],jsontemp['totalFee'])
            #获得淘客链接
            print self.getAuctionLink(str(jsontemp['auctionId']))
        return 0

    #登陆完成后，阿里妈妈主过程
    def mainOfAlimama(self):# return (type) void
        while (raw_input(u'输入q退出：') != 'q'):
            self.printAuctionList()
        return 0
        


    #程序运行主干
    def main(self):
        #是否需要验证码，是则得到页面内容，不是则返回False
        needResult = self.needCheckCode()
        #请求获取失败，得到的结果是None
        if not needResult ==None:
            if not needResult == False:
                print u"您需要手动输入验证码"
                checkCode = self.getCheckCode(needResult)
                #得到了验证码的链接
                if not checkCode == False:
                    print u"验证码获取成功"
                    print u"请在浏览器中输入您看到的验证码"
                    webbrowser.open_new_tab(checkCode)
                    self.loginWithCheckCode()
                #验证码链接为空，无效验证码
                else:
                    print u"验证码获取失败，请重试"
            else:
                print u"不需要输入验证码"
        else:
            print u"请求登录页面失败，无法确认是否需要验证码"
 
 
        #判断token是否正常获取到
        if not self.J_HToken:
            print u"获取Token失败，请重试"
            return
        #获取st码
        st = self.getSTbyToken(self.J_HToken)
        #利用st进行登录
        result = self.loginByST(st,self.username)
        if result:
            #阿里妈妈Sign
            self.loginOnAlimama()
            self.mainOfAlimama()
        else:
            print u"登录失败"
 

if __name__ == '__main__' :
    taobao = Taobao()
    taobao.main()
