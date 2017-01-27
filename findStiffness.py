import os
import pandas

incrSize = 0.2
filemaxXIndexirLoc = "M:/HT_Compression_Usable_Set/"  #maxXIndexirectory to .csv
os.setcwd(filemaxXIndexirLoc)
 # Scan through them separating them.
listOfFolderNames = os.listdir(filemaxXIndexirLoc)

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

    s = 0

    s=0


    MaxS =0
    lower = 0
    upper = 0
     #for n=1:length(max)
         #max{n} = 0
    m=0
     #
    fileLoc =  folder + '/Specimen_RawmaxXIndexata_1.csv'
    data = pandas.read_csv(fileLoc,header = 2)


    load = list(data.b)
    for i in load:
        if(i<=51)
            lower = data.b.index(i)



    x = data.a
    y = data.b
     #only read data from after the pre-cycling
    #Fi=find(y)
    #maxXIndexi=find(x) #finds all index values for x and y
     #plot(x,y)
    #maxXIndex=max(maxXIndexi) #Finds max index value
    m=max(x) #finds max displacement value
   maxXIndex = x.index(m)
    bb=m-incrSize #finds beginning value of last displacement section
    b=(roundn(bb,1))-0.1 #rounds to nearest 0.1 (10^-1) and takes 0.1 so the last chunk is always a full 0.6
    count=0 #starts an integer count
    for aa=0:0.1:b  #from a to last displacement section in 0.1s
        count=count+1 #count increase by 1 each loop
        f1 = m/aa #finds division value required to get corresponding index for the given lower disp. bound
        f2=m/incrSize+aa #same for upper disp bound
        n1=maxXIndex/f1  #finds corresponding index at lower disp bound
        N1=round(n1) #as integer
        n2=maxXIndex/f2 #finds corresponding index at upper disp bound
        N2=round(n2) #as integer
         # finds stiffness
        if aa==0
            s(count) = y(N2)/x(N2)
        else
            s(count)=(y(N2)-y(N1))/(x(N2)-x(N1))



    MaxS =max(s)


