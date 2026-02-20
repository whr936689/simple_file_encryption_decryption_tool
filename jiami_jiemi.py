class FileProtector:
    def __init__(self,key):
        self.key=key%256       #右边的为传入参数，左边为实例化后的保有参数，求余防溢出
    def jiami(self,text,process_callback=None):    #传了半天把那啥更新进度条的函数传到了这里，这里是终点喵
        result=bytearray()
        total=len(text)
        for i,by in enumerate(text):
            result.append((by+self.key)%256)
            if(i%10000==0):
                process_callback(30+i/total*40)   #更新进度条
        return bytes(result)
    def jiemi(self,text,process_callback=None):
        result=bytearray()
        total = len(text)
        for i,by in enumerate(text):
            result.append((by-self.key)%256)
            if (i % 10000 == 0):
                process_callback(30+i/total*40)   #更新进度条
        return bytes(result)