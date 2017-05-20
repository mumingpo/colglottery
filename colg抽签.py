import hashlib
from html.parser import HTMLParser
from urllib import request

def main():
    a = colgnames('http://bbs.colg.cn/thread-6274315-', 28, '-1.html')
    check(a.namescorelist, 'MM1')

class colgnames(HTMLParser):
    def __init__(self, url1, numofpages, url2):
        self.inposttag = False
        self.layerofdiv = 0
        self.innametag = False
        self.inscoreboardtag = False
        self.inscoretag = False
        self.inscoreamounttag = False
        self.namescorelist = []
        self.name = ''
        self.scorename = ''
        self.scores = {}
        for i in range(numofpages):
            HTMLParser.__init__(self)
            html = None
            with request.urlopen(url1 + str(i+1) + url2) as f:
                html = f.read().decode('UTF-8')
            self.feed(html)
            del html
            print('Page {} has completed processing.'.format(i+1))
    def handle_starttag(self, tag, attributes):
        if not self.inposttag:
            if tag == 'div' and attributes[0][0] == 'id' and attributes[0][1][:5] == 'post_':
                self.inposttag = True
        else:
            if tag == 'div':
                self.layerofdiv += 1
            if not self.innametag and tag == 'a' and ('class', 'xw1') in attributes:
                self.innametag = True
            elif not self.inscoreboardtag:
                if tag == 'table' and ('class', 'ratl') in attributes:
                    self.inscoreboardtag = True
            else:
                if not self.inscoretag:
                    if tag == 'th' and ('class', 'xw1') in attributes:
                        self.inscoretag = True
                elif not self.inscoreamounttag:
                    if tag == 'i':
                        self.inscoreamounttag = True         
    def handle_endtag(self, tag):
        if self.inposttag:
            if tag == 'div':
                if self.layerofdiv == 0:
                    self.inposttag = False
                    if self.name: self.namescorelist.append((self.name, self.scores))
                    self.name = ''
                    self.scorename = ''
                    self.scores = {}
                else:
                    self.layerofdiv -= 1
            elif self.innametag:
                if tag == 'a':
                    self.innametag = False
            elif self.inscoreboardtag:
                if self.inscoretag:
                    if self.inscoreamounttag:
                        if tag == 'i': 
                            self.inscoreamounttag = False
                    elif tag == 'th':
                        self.inscoretag = False
                elif tag == 'tbody':
                    self.inscoreboardtag == False
    def handle_data(self, data):
        if self.innametag:
            self.name = data
        elif self.inscoretag:
            if self.inscoreamounttag:
                if self.scorename in set(['可用积分', '水滴', '存在感']):
                    self.scores[self.scorename] = int(data.strip('+ \n'))
            else:
                self.scorename = data.strip(' \n')

#def 转换(名字): return sum([int(hashlib.md5(bytearray([i.encode(encoding = 'utf-16-le')[0] for i in (名字.strip() + 'KoishiMeow>v<' + 'MM1')])).hexdigest()[[0, 3, 5, 7, 9, 11, 13][j]], 16) << (j * 4) for j in range(7)]) * 10000 >> 28
def nametoscore(name, hashseed):
    distr = {
        50: [{'可用积分': 120}],##特大吉
        600: [{'可用积分': 60}],##大吉
        4500: [{'可用积分': 30}],##吉
        7500: [{'可用积分': 20}],##小吉
        ##7500: [{'可用积分': 10}],##平
        8500: [{'可用积分': 20, '水滴': -20}, {'可用积分': -20, '水滴': 20}],##小凶
        9500: [{'可用积分': 30, '水滴': -30}, {'可用积分': -30, '水滴': 30}],##凶
        9950: [{'可用积分': 60, '水滴': -60}, {'可用积分': -60, '水滴': 60}],##大凶
        10000: [{'可用积分': -120, '水滴': -120, '存在感': 1}, {'可用积分': 120, '水滴': -120}, {'可用积分': -120, '水滴': 120}]##特大凶
        }
    distrkeys = [50, 600, 4500, 7500, 8500, 9500, 9950, 10000]
    hashdata = name.strip() + 'KoishiMeow>v<' + hashseed
    hashdatamd5 = hashlib.md5(bytearray([i.encode(encoding = 'utf-16-le')[0] for i in hashdata])).hexdigest()
    namevalue = 0
    for i in range(7):
        namevalue += int(hashdatamd5[[0, 3, 5, 7, 9, 11, 13][i]], 16) << (i * 4)
    namevalue *= 10000
    namevalue >>= 28
    for i in distrkeys:
        if namevalue <= i:
            return distr[i]

def check(namescorelist, hashseed):
    for i in namescorelist:
        name = i[0]
        scoregiven = i[1]
        shouldget = nametoscore(name, hashseed)
        if scoregiven not in shouldget:
            print('{}:\n    所得:{}\n    应得:{}'.format(name, scoregiven, '或'.join([str(j) for j in shouldget])))

if __name__ == '__main__':
    main()