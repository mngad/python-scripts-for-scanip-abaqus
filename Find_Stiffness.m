clear all;
fileLoc = 'M:\Compression Tests\T2_CC1_15.2.16_Tofailure.is_comp_RawData\Specimen_RawData_1.csv'; %Directory to .csv
incrSize = 0.3;

%find limits of plot ie. > 50 N to max

fid = fopen(fileLoc);
tline = fgetl(fid);
i=0;
while ischar(tline)
    i=i+1;
    disp(tline);
    tline = fgetl(fid);
end
fclose(fid);
upper = num2str(i);
load = xlsread(fileLoc,strcat('B','1',':','B',upper));

for incr=1:i-2

    if(load(incr)<=51)
        lower = num2str(incr);
    end
     if(load(incr)<=5000)
         upper = num2str(incr);
     end
end

upper
lower
x = xlsread(fileLoc,strcat('A',lower,':','A',upper));
y = xlsread(fileLoc,strcat('B',lower,':','B',upper));
%only read data from after the pre-cycling
Fi=find(y);
Di=find(x);%finds all index values for x and y
plot(x,y)
D=max(Di);%Finds max index value
m=max(x);%finds max displacement value
bb=m-incrSize;%finds beginning value of last displacement section
b=(roundn(bb,-1))-0.1;%rounds to nearest 0.1 (10^-1) and takes 0.1 so the last chunk is always a full 0.6
count=0;%starts an integer count
for aa=0:0.1:b %from a to last displacement section in 0.1s
    count=count+1;%count increase by 1 each loop
    f1 = m/aa;%finds division value required to get corresponding index for the given lower disp. bound
    f2=m/incrSize+aa;%same for upper disp bound
    n1=D/f1; %finds corresponding index at lower disp bound
    N1=round(n1);%as integer
    n2=D/f2;%finds corresponding index at upper disp bound
    N2=round(n2);%as integer
    % finds stiffness
    if aa==0
        s(count) = y(N2)/x(N2);
    else
    s(count)=(y(N2)-y(N1))/(x(N2)-x(N1));
    end
end

MaxS =max(s)
