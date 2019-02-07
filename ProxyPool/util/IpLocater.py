# -*- coding: utf-8 -*-
import socket
import struct
import config

class IpLocater:
    #国内地区
    CHINA_AREA = ['省','中国','河北', '山东', '辽宁', '黑龙江', '吉林'
    , '甘肃', '青海', '河南', '江苏', '湖北', '湖南',
              '江西', '浙江', '广东', '云南', '福建',
              '台湾', '海南', '山西', '四川', '陕西',
              '贵州', '安徽', '重庆', '北京', '上海', '天津', '广西', '内蒙', '西藏', '新疆', '宁夏', '香港', '澳门']
    def __init__(self):
        self.ipdb = open(config.QQWRY_PATH, "rb")
        str = self.ipdb.read(8)
        (self.firstIndex, self.lastIndex) = struct.unpack('II', str)
        self.indexCount = int((self.lastIndex - self.firstIndex) / 7 + 1)
        # print self.getVersion(), u" 纪录总数: %d 条 "%(self.indexCount)

    def getVersion(self):
        s = self.getIpAddr(0xffffff00)
        return s

    def isDomestic(self,addr):
        for area in self.CHINA_AREA:
            if(area in addr):
                return True
        return False
    def getAreaAddr(self, offset=0):
        if offset:
            self.ipdb.seek(offset)
        str = self.ipdb.read(1)
        (byte,) = struct.unpack('B', str)
        if byte == 0x01 or byte == 0x02:
            p = self.getLong3()
            if p:
                return self.getString(p)
            else:
                return ""
        else:
            self.ipdb.seek(-1, 1)
            return self.getString(offset)

    def getAddr(self, offset, ip=0):
        self.ipdb.seek(offset + 4)
        countryAddr = ''
        areaAddr = ''
        str = self.ipdb.read(1)
        (byte,) = struct.unpack('B', str)
        if byte == 0x01:
            countryOffset = self.getLong3()
            self.ipdb.seek(countryOffset)
            str = self.ipdb.read(1)
            (b,) = struct.unpack('B', str)
            if b == 0x02:
                countryAddr = self.getString(self.getLong3())
                self.ipdb.seek(countryOffset + 4)
            else:
                countryAddr = self.getString(countryOffset)
            areaAddr = self.getAreaAddr()
        elif byte == 0x02:
            countryAddr = self.getString(self.getLong3())
            areaAddr = self.getAreaAddr(offset + 8)
        else:
            countryAddr = self.getString(offset + 4)
            areaAddr = self.getAreaAddr()
        return countryAddr + ',' + areaAddr

    def dump(self, first, last):
        if last > self.indexCount:
            last = self.indexCount
        for index in range(first, last):
            offset = self.firstIndex + index * 7
            self.ipdb.seek(offset)
            buf = self.ipdb.read(7)
            (ip, of1, of2) = struct.unpack("IHB", buf)
            address = self.getAddr(of1 + (of2 << 16))
            # 把GBK转为utf-8
            address = str(address, 'gbk').encode("utf-8")

    def setIpRange(self, index):
        offset = self.firstIndex + index * 7
        self.ipdb.seek(offset)
        buf = self.ipdb.read(7)
        (self.curStartIp, of1, of2) = struct.unpack("IHB", buf)
        self.curEndIpOffset = of1 + (of2 << 16)
        self.ipdb.seek(self.curEndIpOffset)
        buf = self.ipdb.read(4)
        (self.curEndIp,) = struct.unpack("I", buf)

    def getIpAddr(self, ip):
        L = 0
        R = self.indexCount - 1
        while L < R - 1:
            M = int((L + R) / 2)
            self.setIpRange(M)
            if ip == self.curStartIp:
                L = M
                break
            if ip > self.curStartIp:
                L = M
            else:
                R = M
        self.setIpRange(L)
        # version information, 255.255.255.X, urgy but useful
        if ip & 0xffffff00 == 0xffffff00:
            self.setIpRange(R)
        if self.curStartIp <= ip <= self.curEndIp:
            address = self.getAddr(self.curEndIpOffset)
            # 把GBK转为utf-8
            # 地址中,替换为_
            address = str(address).replace(',','_')
        else:
            address = str("未找到该IP的地址")
        return address

    def getIpRange(self, ip):
        self.getIpAddr(ip)
        range = self.ip2str(self.curStartIp) + ' - ' \
                + self.ip2str(self.curEndIp)
        return range

    def getString(self, offset=0):
        if offset:
            self.ipdb.seek(offset)
        str = b''
        ch = self.ipdb.read(1)
        (byte,) = struct.unpack('B', ch)
        while byte != 0:
            str += ch
            ch = self.ipdb.read(1)
            (byte,) = struct.unpack('B', ch)
        return str.decode('gbk')

    def ip2str(self, ip):
        return str(ip >> 24) + '.' + str((ip >> 16) & 0xff) + '.' + str((ip >> 8) & 0xff) + '.' + str(ip & 0xff)

    def str2ip(self, s):
        (ip,) = struct.unpack('I', socket.inet_aton(s))
        return ((ip >> 24) & 0xff) | ((ip & 0xff) << 24) | ((ip >> 8) & 0xff00) | ((ip & 0xff00) << 8)

    def getLong3(self, offset=0):
        if offset:
            self.ipdb.seek(offset)
        str = self.ipdb.read(3)
        (a, b) = struct.unpack('HB', str)
        return (b << 16) + a


if __name__ == '__main__':
    iplocater = IpLocater()
    addr = iplocater.getIpAddr(iplocater.str2ip('123.206.57.126'))
    print(addr)
