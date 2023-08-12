import urllib.request
import urllib.parse

def CtoK(temp):
    return temp+273.15

class Flir:
    def __init__(self, baseURL='http://192.168.100.6/'):
        self.baseURL = baseURL

    def setResource(self,resource,value):
        return urllib.request.urlopen(self.baseURL+'res.php',urllib.parse.urlencode({'action':'set','resource':resource,'value':value}).encode("utf-8")).read()

    def getResource(self,resource):
        return urllib.request.urlopen(self.baseURL+'res.php',urllib.parse.urlencode({'action':'get','resource':resource}).encode("utf-8")).read()

    def setIRMode(self):
        self.setResource('.image.sysimg.fusion.fusionData.fusionMode',1)
        self.setResource('.image.sysimg.fusion.fusionData.useLevelSpan',1)

    def setVisualMode(self):
        self.setResource('.image.sysimg.fusion.fusionData.fusionMode',1)
        self.setResource('.image.sysimg.fusion.fusionData.useLevelSpan',0)

    def setMSXMode(self):
        self.setResource('.image.sysimg.fusion.fusionData.fusionMode',3)

    def setTemperatureRange(self,minTemp, maxTemp):
        self.setResource('.image.contadj.adjMode', 'manual')
        self.setResource('.image.sysimg.basicImgData.extraInfo.lowT',CtoK(minTemp))
        self.setResource('.image.sysimg.basicImgData.extraInfo.highT',CtoK(maxTemp))

    def showOverlay(self,show=True):
        if show:
            self.setResource('.resmon.config.hideGraphics','false')
        else:
            self.setResource('.resmon.config.hideGraphics','true')

    def light(self,on=True):
        if on:
            self.setResource('.system.vcam.torch','true')
        else:
            self.setResource('.system.vcam.torch','false')

    def setPalette(self, palette):
        # iron.pal, bw.pal, rainbow.pal
        self.setResource('.image.sysimage.palette.readFile',palette)

    def getBox(self,boxNumber):
        ret = {}
        bns = str(boxNumber)
        ret['boxNumber']=boxNumber
        #for field in ('active','avgT','avgValid','x','y','width','height','medianT','medianValid','minT','minValid','minX','minY','maxT','maxValid','maxX','maxY'):
        for field in ('active','avgT','minT','maxT'):
            ret[field] =self.getResource('.image.sysimg.measureFuncs.mbox.'+bns+'.'+field).decode('utf8')
            if field == 'active' and ret[field] == '"false"':
                break
        return ret

    def getBoxes(self):
        ret = []
        for i in range(1,7):
            ret.append(self.getBox(i))
        return ret

    def getMaxTemp(self):
        #NOTE. DO NOT CHANGE BOX NUMBER IN ADMIN PAGE!
        #      If Max temperature is represented weird, SET THE BOX RANGE ClOSE TO BABY
        resource = self.getResource('.image.sysimg.measureFuncs.mbox.'+'1'+'.'+'maxT').decode('utf8')
        # print(f"[{self.__class__.__name__}] type : {type(resource)}")
        # print(f"[{self.__class__.__name__}] len  : {len(resource)}")
        # print(f"[{self.__class__.__name__}] len  : {list(resource)}")
        if resource != None:
            if isinstance(resource, str):
                if len(resource) > 8: # -> "35.002C"
                    return resource[1:7]
            else:
                return ""
        else:
            return ""