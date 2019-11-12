class TimeParser:
    def __init__(self, time):
        #[1234, 1245, 1259, 2244, 2245] / HHMM
        self.time = time
        # end of sleep exception
        if len(self.time)%2 : self.time.append('9999')
        self.idx = len(time) - 2


    # [2359, 0031, 0033] -> [2359, 2431, 2433]
    def calculateNextDay(self):
        if len(self.time) <= 2:
                return
            
        if int(self.time[-1]) - int(self.time[0]) < 0:
            for i in range(len(self.time)-1, -1, -1):
                if self.time[i] < '2359':
                    self.time[i] = str(int(self.time[i]) + 2400)
                else:
                    return


    # remove duplicated time
    def calculateDupTime(self):
        if len(self.time) <= 2 or self.idx < 2:
            return

        if int(self.time[self.idx])-int(self.time[self.idx-1]) <= 1:
            self.time.pop(self.idx)
            self.time.pop(self.idx-1)
        self.idx -= 2

        self.calculateDupTime()


    def timeParsing(self):
        for i in range(1, len(self.time)-1, 2):
            self.time[i] = self.time[i].replace(self.time[i], self.time[i] + '/')

        return ''.join(self.time)


    def getTime(self):
        return self.time


t = TimeParser(['1234','2345','2345','2347','2355','2377','2388'])
print(t.getTime())
t.calculateNextDay()
print(t.getTime())
t.calculateDupTime()
print(t.getTime())
print(t.timeParsing())
print(t.getTime())
