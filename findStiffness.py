import os
import pandas
import pyperclip as pc
incrSize = 0.01
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

    for i in range(len(x)):
        #print('oldx = ' +str(x[i]))
        diff =  x[i] - xmin
        x[i] = diff
       # print('x = ' +str(x[i]))






    m=max(x) #finds max displacement value
    maxXIndex = x.index(m)
    bb=m-incrSize #finds beginning value of last displacement section
    b=(round(bb,2))-incrSize #rounds to nearest 0.1 (10^-1) and takes 0.1 so the last chunk is always a full 0.6
    count=0 #starts an integer count
    aa = 0
    #print('m = ' + str(m))
    #print('bb = ' + str(bb))
    #print('round(bb,1) = ' + str(round(bb,2)))
    #print('b = ' + str(b))
    while aa < b:
        f1 = m/aa #finds division value required to get corresponding index for the given lower disp. bound
        f2=m/incrSize+aa #same for upper disp bound
        n1=maxXIndex/f1  #finds corresponding index at lower disp bound
        N1=int(round(n1)) #as integer
        n2=maxXIndex/f2 #finds corresponding index at upper disp bound
        N2=int(round(n2)) #as integer
         # finds stiffness
        if aa==0:
            s.append(0)
        else:
            s.append((y[N2]-y[N1])/(x[N2]-x[N1]))
        aa = aa + 0.0005
        #print(str(aa) + ', ' + str(s[count]))
        count=count+1 #count increase by 1 each loop


    MaxS =max(s)
    allRes = allRes + folder[:-16] + ', ' + str(MaxS) + '\n'
    #print(folder)

print(allRes)
pc.copy(allRes)
print('Results copies to clipboard')
