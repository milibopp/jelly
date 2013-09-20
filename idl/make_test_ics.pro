
fout = "./ics_test.dat"

BoxX = 2.0D
BoxY = 1.5D

; Position and radius of "star" (which is really treasted as a spherical obstacle
; that can emit a wind)
StarX = 1.0D
StarY = 0.75D
StarR = 0.05D


;; properties of wind from star
V_outflow =   1.0
Rho_outflow = 1.5
u_outflow =   1.0

;; properties of background ISM
V_background =   2.0   
rho_background = 1.0
u_background =   1.0



d = 0.01D      ; desired mesh resolution


Nx = long(BoxX/d + 0.5)
Ny = long(BoxY/d + 0.5)

dx = BoxX/Nx
dy = BoxY/Ny

print, "cell volume=", dx*dy



; create a cartesian grid
 
N  = Nx * Ny
pos = fltarr(3, N)

count = 0L
for i=0L, Nx-1 do begin
   for j=0L, Ny-1 do begin
      pos(0, count) = (i+0.5) * dx
      pos(1, count) = (j+0.5) * dy
      count++
   endfor
endfor


;calculate distance from star

r = sqrt((pos(0,*) - StarX)^2 + (pos(1,*) - StarY)^2)

; find region outside of a shell with thickness 4d centered on the
; star surface

ind = where((r lt StarR-2.0*d) or (r gt StarR+2.0*d))

pos1 = fltarr(3, n_elements(ind))
vel1 = fltarr(3, n_elements(ind))

; filter out this region
pos1(0,*) = pos(0,ind)
pos1(1,*) = pos(1,ind)

; set the velocity of the backrgound
Vel1(0,*) = V_background







; create the rings of particles for treatment of the stellar surface

Nphi = long(2 * !Dpi * StarR / d + 1)

pos2 = fltarr(3, 4*Nphi)
vel2 = fltarr(3, 4*Nphi)

Vel2(0,*) = V_background  ; set the velocity in the outer parts, inner parts will be overwritten later

count = 0L
for i=0L, Nphi-1 do begin
   alpha = 2 *!PI * (i+0.5)/Nphi

   pos2(0, count) = StarX + cos(alpha) * (StarR + 1.5* d)
   pos2(1, count) = StarY + sin(alpha) * (StarR + 1.5* d)
   count++

   pos2(0, count) = StarX + cos(alpha) * (StarR + 0.5* d)
   pos2(1, count) = StarY + sin(alpha) * (StarR + 0.5* d)
   count++


   pos2(0, count) = StarX + cos(alpha) * (StarR - 0.5* d)
   pos2(1, count) = StarY + sin(alpha) * (StarR - 0.5* d)
   vel2(0, count) = V_outflow * cos(alpha)
   vel2(1, count) = V_outflow * sin(alpha) 
   count++

   pos2(0, count) = StarX + cos(alpha) * (StarR - 1.5* d)
   pos2(1, count) = StarY + sin(alpha) * (StarR - 1.5* d)
   vel2(0, count) = V_outflow * cos(alpha)
   vel2(1, count) = V_outflow * sin(alpha) 
   count++

endfor

; make a dot plot
window, xsize=1000, ysize=740
plot, pos1(0,*), pos1(1,*), psym=3
oplot, pos2(0,*), pos2(1,*), psym=3, color=255



;join the distributions together

N1 = n_elements(pos1(0,*))
N2 = n_elements(pos2(0,*)) 
N = N1 + N2

pos = fltarr(3,N)
vel = fltarr(3,N)
for j=0,1 do begin
   pos(j,0:N1-1) = pos1(j,*)
   pos(j,N1:*)   = pos2(j,*)
   vel(j,0:N1-1) = vel1(j,*)
   vel(j,N1:*)   = vel2(j,*)
endfor


; set temperature and density

u = fltarr(N)
rho = fltarr(N)
u(*) = u_background
rho(*) = rho_background




; create unique IDs from 1... N

id = lindgen(N)+1


; now we flag certain cells to be treated in a special way, to
; introduce the special boundaries


r = sqrt((pos(0,*)- StarX)^2 + (pos(1,*)- StarY)^2)

;; Set-up inflow nozzle
ind = where(pos(0,*) lt d)
Id(ind) +=  10000000                                  ;;; note:  BOUNDARY_REFL_FLUIDSIDE_MINID=10000000

;; make the next layer sticky
ind = where((pos(0,*) gt d) and (pos(0,*) lt 2*d))
Id(ind) +=  20000000                                  ;;; note:   BOUNDARY_STICKY_MINID=20000000



;; Set-up outflow region
ind = where(pos(0,*) gt (BoxX - d))
Id(ind) +=  10000000                                  ;;; note:  BOUNDARY_REFL_FLUIDSIDE_MINID=10000000

; make the next layer sticky
ind = where((pos(0,*) gt (BoxX - 2*d)) and (pos(0,*) lt (BoxX - 1*d)))
Id(ind) +=  20000000                                  ;;; note:   BOUNDARY_STICKY_MINID=20000000




;;; Set-up the star

ind = where(r lt StarR)

;; inside the star
Id(ind) +=  40000000                                 ;;;; note:   BOUNDARY_REFL_SOLIDSIDE_MINID=40000000
rho(ind) =  Rho_outflow
u(ind)    = U_outflow


;; set up cell layer on outer side of reflective boundary
ind = where((r gt StarR) and (r lt (StarR + d)))
Id(ind) +=  30000000                                 ;;;;  note:  BOUNDARY_REFL_FLUIDSIDE_MINID=30000000

; make the next layer sticky
ind = where((r gt StarR + d) and (r lt (StarR + 2*d)))
Id(ind) +=  20000000                                  ;;; note:   BOUNDARY_STICKY_MINID=20000000




; now shift the colums by half a cell in the third rows 
; from left and right. This is however not really necessary.
ind = where((pos(0,*) gt 2*d) and (pos(0,*) lt 3*d))
pos(1,ind) += 0.5*d


ind = where((pos(0,*) gt (BoxX - 3*d)) and (pos(0,*) lt (BoxX - 2*d)))
pos(1,ind) += 0.5*d



;;; Now write the IC file in Gadget's legacy file format

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

npart(0)    = N
npartall(0) = N

BoxSize=double(BoxX)
openw,1,fout,/f77_unformatted
writeu,1, npart,massarr,time,redshift,flag_sfr,flag_feedback,npartall,flag_cooling,num_files,BoxSize,la
writeu,1, pos
writeu,1, vel
writeu,1, id
writeu,1, rho
writeu,1, u
writeu,1, rho
close,1

print
print, "ICs have been written to:   ", fout
print

end


