
fout = "./test.dat"

nn = 16L
N  = nn^2

pos = fltarr(3, N)


BoxSize = 2.0D

for i=0L, nn-1 do begin
    for j=0L, nn-1 do begin
        pos(0, i * nn + j) = double(i) / double(nn) * BoxSize
        pos(1, i * nn + j) = double(j) / double(nn) * BoxSize
        pos(2, i * nn + j) = 0.0
    endfor
endfor


npart=lonarr(6)	
massarr=dblarr(6)
time=0.0D
redshift=0.0D
flag_sfr=0L
flag_feedback=0L
npartall=lonarr(6)	
flag_cooling= 0L
num_files= 1L
BoxSize = 0.0D

bytesleft=120
la=intarr(bytesleft/2)

npart(0) = N
npartall(0) = N

massarr(0) = 1.0/N

id = lindgen(N)+1

vel = fltarr(3, N)
u = fltarr(N)
u(*) = 1.0
rho = fltarr(N)


openw,1,fout,/f77_unformatted
writeu,1, npart,massarr,time,redshift,flag_sfr,flag_feedback,npartall,flag_cooling,num_files,BoxSize,la
writeu,1, pos
writeu,1, vel
writeu,1, id
writeu,1, u
writeu,1, rho
close,1

end


