%--------------------------------------------------------------------------
%   Matlab Program:    Rotate_ISQ-file_to_tiff_stack
%   Author:            Martin Preutenborbeck (mnmp)
%   Last Updated:      11/08/2015
%   Supervisor:        Al Jones, Richard Hall, Sophie Williams;
%
%   Purpose: To rotate (optional) and convert an ISQ file which has been 
%   exported from a Scanco CT-scanner, into a stack of TIFF image files.
%   
%   Update record:      First created 07/05/2015 v0
%   Update record:      Update by Fernando Zapata 11/08/2015 v1.0
%--------------------------------------------------------------------------
%   Modified by Fernando Zapata
%   Added the functionality of rescaling images in the 0 - 255 scale
%   and save the files in 8-bit tiff files for posterior use with scanIP
%--------------------------------------------------------------------------


function Rotate_ISQ_2_TIFF_(filename,rotangle,rescaling)
% filename:  Name of the ISQ file without file extension
% rotangle:  Angle of rotation (without rotation rotangle=0)
% rescaling: Rescale files to 0 - 255 scale and save as tiff files (true or
% false)
% example:   Rotate_ISQ_2_TIFF_('X0001325',10,true)
% change Par.rotaxis for different axis

%--------------------------------------------------------------------------
% Parameter Init
%--------------------------------------------------------------------------
Par.filenameISQ=sprintf('%s.ISQ',filename);
Par.deg=rotangle;
Par.rotaxis=1; % if 0 then rotation on x-axis (takes longer) else y-axis
% Par.slope=1.42830896e+03; % only valid for XtremeCT 18/05/15
% Par.intercept=-3.54631012e+02;


% Hounsfield (HU) values which are registered range from 0 - maximum
% This is the maximum HU value for the iMBE micro-CT/XtremeCT machine
maximum = 32767;  

[Hinfo]=read_isq_header(Par);
Par.data_offset=double(Hinfo.data_offset)+1;
Par.ydim=double(Hinfo.dimx_p);
Par.xdim=double(Hinfo.dimy_p);
Par.zdim=double(Hinfo.dimz_p);
Par.res=double(Hinfo.slice_thickness_um)*0.001;
Par.muscale=double(Hinfo.mu_scaling);

%--------------------------------------------------------------------------
% Create folder for new files
%--------------------------------------------------------------------------

foldername = sprintf('%s_new',filename);
mkdir (foldername);

%--------------------------------------------------------------------------
% Load Image
%--------------------------------------------------------------------------

[x1,x2]=rotate_coordinates(Par);
for i=0:1:(Par.zdim-1)
    Par.i=i;
    
    if Par.deg==0
        I=isq_load(Par);
    elseif Par.rotaxis==0
        I=isq_load_rotate_x(Par,x1,x2);
    else
        I=isq_load_rotate_y(Par,x1,x2);
    end
    
%--------------------------------------------------------------------------
% Write new files in designated folder
%--------------------------------------------------------------------------
   if rescaling == true
        for oj=1:Par.xdim
                for oi=1:Par.ydim
                    if I(oj, oi) < 0   % values less than zero considered to be noise
                        I(oj, oi) = 0;
                    else
                        I(oj, oi) = ( double(I(oj, oi))  / double(maximum) ) * 255.0;
                    end
                end
        end
        I = flipdim(I,2);
        I = rot90(I,1);
        filenameout = sprintf('%s/%s_%g.tiff', foldername, filename,i);
        fprintf('%g/%g\n', i, Par.zdim); % for info in Matlab
        imwrite(uint8(I), filenameout,'tiff'); % safe output file
        %dicomwrite(I, filenameout);
   else
        %I=double(I)*(Par.slope)/Par.muscale+(Par.intercept); % [mgHA/ccm]
        %I=double(I)*(5.004933e-01)-1000; % [HU] for XtremeCT 20/05/15
        filenameout = sprintf('%s/%s_%g.tiff', foldername, filename,i);
        fprintf('%g/%g\n', i, Par.zdim); % for info in Matlab
        imwrite(uint16(I), filenameout,'tiff'); % safe output file
        %dicomwrite(I, filenameout);
   end
end

%--------------------------------------------------------------------------
end

%--------------------------------------------------------------------------
% for earlier versions of matlab that lack the rad2deg and deg2rad functions
%--------------------------------------------------------------------------
function y = rad2deg(x)
y = x * 180/pi;
end

function y = deg2rad(x)
y = x * pi/180;
end
%--------------------------------------------------------------------------


function I=isq_load_rotate_x(Par,x1,x2)
%--------------------------------------------------------------------------
% Rotate & Open  ISQ-image
%--------------------------------------------------------------------------
fid=fopen(Par.filenameISQ,'r');

I=int16(zeros(Par.ydim,Par.xdim));
n=1;
for j=1:Par.ydim
   if x1(n+Par.ydim*Par.i)<round(Par.zdim) && x2(n+Par.ydim*Par.i)<round(Par.ydim) % that it doesnt excites matrix dimension ydim zdim
     fseek(fid, (x2(n+Par.ydim*Par.i)-1)*2 + ((x1(n+Par.ydim*Par.i)-1)*Par.xdim*Par.ydim)*2 + Par.data_offset*512 ,'bof');
     I(j,:)=[ fread(fid, Par.xdim ,'*int16', (Par.ydim-1)*2) ]'; % read all x on y coordinate   
   end
   n=n+1;
end
fclose(fid);
%--------------------------------------------------------------------------
end


function I=isq_load_rotate_y(Par,x1,x2)
fid=fopen(Par.filenameISQ,'r');

I=int16(zeros(Par.ydim,Par.xdim));
n=1;
for j=1:Par.xdim
   if x1(n+Par.xdim*Par.i)<round(Par.zdim) && x2(n+Par.xdim*Par.i)<round(Par.xdim) % that it doesnt excites matrix dimension ydim zdim
     fseek(fid, ((x2(n+Par.xdim*Par.i)-1)*Par.ydim*2)+ ((x1(n+Par.xdim*Par.i)-1)*Par.xdim*Par.ydim)*2+ Par.data_offset*512 ,'bof');
     I(:,j)=[fread(fid,Par.ydim,'*int16')]';% read all x on y coordinate   
   end
   n=n+1;
end
fclose(fid);
%--------------------------------------------------------------------------
end


function I=isq_load(Par)
fid=fopen(Par.filenameISQ,'r'); % binary image file (ISQ)
fseek(fid, (Par.i*Par.xdim*Par.ydim*2) + Par.data_offset*512 ,'bof');
I=fread (fid,[Par.ydim,Par.ydim],'*int16');
fclose(fid);
%--------------------------------------------------------------------------
end


function [x1,x2]=rotate_coordinates(Par)
%--------------------------------------------------------------------------
% Calculate new Pixel coordinates: Transform into polar
% coordinate system, rotate, transform back into cartesian system;
%--------------------------------------------------------------------------
rotcoordinates=zeros(Par.ydim*Par.zdim, 2);
rotpoint=[ceil((Par.zdim+1)/2),ceil((Par.ydim+1)/2)]; %(y/x)Set point of rotation
m=1;
for i=1:Par.zdim
    i1=i-rotpoint(1);
    for j=1:Par.ydim
        [t,r]=cart2pol(i1,j-rotpoint(2));  %convert from cartesian to polar --distance x y from rotation point
        t1=rad2deg(t)+Par.deg;  %Convert radians to degree and add rotated degree value
        t=deg2rad(t1);  %Convert degree to radians
        [y,x]=pol2cart(t,r);  %Convert to Cartesian Coordinates
        rotcoordinates(m,:)=[round(y+rotpoint(1)), round(x+rotpoint(2))]; % new rotated coordinates(y/x)
        m=m+1;
    end
end
rotcoordinates(find(rotcoordinates < 1))=1; % values smaller 1 are set to 1 (imaginary)
x1=rotcoordinates(:,1);
x2=rotcoordinates(:,2);
%--------------------------------------------------------------------------
end


function [Hinfo]=read_isq_header(Par)
%--------------------------------------------------------------------------
% Reads  ISQ-Header from Scanco XtremeCT
%--------------------------------------------------------------------------
fid=fopen(Par.filenameISQ,'r'); % binary RAW ISQ  offset for ISQ header?512*6

Hinfo.check16=fread (fid,[1,16],'*char');
Hinfo.data_type=fread (fid,1,'*int32');
Hinfo.nr_of_bytes=fread (fid,1,'*int32');   %/* either one of them */ 
Hinfo.nr_of_blocks=fread (fid,1,'*int32');   %/* or both, but min. of 1 */ 
Hinfo.patient_index=fread (fid,1,'*int32');  %/* 1 block = 512 bytes */ 
Hinfo.scanner_id=fread (fid,1,'*int32');
Hinfo.creation_date2=fread (fid,[1,2],'*int32');
%fseek(fid,[44],'bof');
Hinfo.dimx_p=fread (fid,1,'*int32'); 
Hinfo.dimy_p=fread (fid,1,'*int32'); 
Hinfo.dimz_p=fread (fid,1,'*int32'); 
Hinfo.dimx_um=fread (fid,1,'*int32'); 
Hinfo.dimy_um=fread (fid,1,'*int32'); 
Hinfo.dimz_um=fread (fid,1,'*int32'); 
Hinfo.slice_thickness_um=fread (fid,1,'*int32'); 
Hinfo.slice_increment_um=fread (fid,1,'*int32'); 
Hinfo.slice_1_pos_um=fread (fid,1,'*int32'); 
Hinfo.min_data_value=fread (fid,1,'*int32'); 
Hinfo.max_data_value=fread (fid,1,'*int32'); 
Hinfo.mu_scaling=fread (fid,1,'*int32');  %/* p(x,y,z)/mu_scaling = value [1/cm] */ 
Hinfo.nr_of_samples=fread (fid,1,'*int32'); 
Hinfo.nr_of_projections=fread (fid,1,'*int32') ;
Hinfo.scandist_um=fread (fid,1,'*int32'); 
Hinfo.scanner_type=fread (fid,1,'*int32'); 
Hinfo.sampletime_us=fread (fid,1,'*int32') ;
Hinfo.index_measurement=fread (fid,1,'*int32'); 
Hinfo.site=fread (fid,1,'*int32');  %/* Coded value */ 
Hinfo.reference_line_um=fread (fid,1,'*int32');  
Hinfo.recon_alg=fread (fid,1,'*int32');  %/* Coded value */ 
Hinfo.name40=fread (fid,[1,40],'*char'); 
Hinfo.energy=fread (fid,1,'*int32');  %/*V */ 
Hinfo.intensity=fread (fid,1,'*int32');  % /* uA */ 
Hinfo.fill83=fread (fid,83,'*int32'); 
Hinfo.data_offset=fread (fid,1,'*int32'); %/* in 512-byte-blocks */
fclose(fid);
%--------------------------------------------------------------------------
end