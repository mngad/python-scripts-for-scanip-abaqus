import os
import pandas
import pyperclip as pc
import re

def findStiffness(segSize, incrSize):
    fileDir = "M:/HT_Compression_3+post/"  #maxXIndexirectory to .csv
    allRes = ''
    os.chdir(fileDir)
     # Scan through them separating them.
    listOfFolderNames = os.listdir(fileDir)

     #find limits of plot ie. > 50 N to max
    for folder in listOfFolderNames:
        Fi=0
        maxXIndexi=0 #finds all index values for x and y
         #plot(x,y)
        maxXIndex=0 #Finds max index value
        m=0 #finds max displacement value
        bb=0 #finds beginning value of last displacement section
        b=0 #rounds to nearest 0.1 (10^-1) and takes 0.1 so the last chunk is always a full 0.6
        count=0 #starts an integer count
         #from a to last displacement section in 0.1s

        f1 = 0 #finds division value required to get corresponding index for the given lower disp. bound
        f2=0 #same for upper disp bound
        n1=0  #finds corresponding index at lower disp bound
        N1=0 #as integer
        n2=0 #finds corresponding index at upper disp bound
        N2=0 #as integer
         # finds stiffness

        s =[]
        MaxS =0
        lower = 0
        upper = 0
         #for n=1:length(max)
             #max{n} = 0
        m=0
         #
        fileLoc =  folder + '/Specimen_RawData_1.csv'
        data = pandas.read_csv(fileLoc,header = 1)

        countr =0
        load = list(data['(N)'])
        for i in load:
            if(i<=51):
                lower = countr
            countr = countr + 1

        xdata = data['(mm)']
        ydata = data['(N)']
        x = xdata.tolist()
        y = ydata.tolist()
        x = x[lower:]
        y = y[lower:]
        xmin = x[0]
        ymin = y[0]
        fail = False
        for i in range(len(x)):
            #print('oldx = ' +str(x[i]))
            diff =  x[i] - xmin
            x[i] = diff
           # print('x = ' +str(x[i]))
        count=0 #starts an integer count
        aa = int(len(x)/4)
        #print(len(x))
        while aa < (len(x)-(segSize+incrSize)):
            #print(count)
            s.append((y[aa + segSize]-y[aa])/(x[aa+segSize]-x[aa]))
            #print(str(aa) + ', ' + str(s[count]))
            count=count+1 #count increase by 1 each loop
            aa = aa +incrSize

        MaxS =max(s)
        if(MaxS>s[-1:]):
            fail = True
        Mindex = s.index(max(s))
        allRes = allRes + str(segSize) + ', ' + folder[:-16] + ', ' + str(MaxS) + ', fail = ' + str(fail) +  '\n'
        #print(folder)

    print(allRes)
    pc.copy(allRes)
    return(allRes)
    #print('Results copies to clipboard')


findStiffness(20,1)
