program make_celldata
integer :: ierr, dummy
integer :: meshx, meshy, meshz, xi_meshx, xi_meshy, xi_meshz, n_cells, xi_n_cells, x, y, z, cell_idx
real*8, dimension(:) , allocatable :: neutral_frac, xi
real*4, dimension(:) , allocatable :: density, velocity!, ux, uy, uz
real*8, dimension(:), allocatable :: ux, uy, uz, rho !rho is the density in cm^-3
real*8, dimension(:), allocatable :: ux_c, uy_c, uz_c, rho_c
real*8 :: redshift, tmp
character(len=256) :: xfile, dfile, vfile, outfile
integer :: i, xd, yd, zd

!Cosmological constants
real*8, parameter :: h=0.7
real*8, parameter ::  H0=100.0*h
real*8, parameter ::  Omega0 = 0.27
real*8, parameter ::  OmegaB = 0.044
real*8, parameter ::  Mpc=1.e6*3.086e18
real*8, parameter :: tscale = 2.0/(3.0*sqrt(Omega0)*H0/Mpc*1.e5)
real*8, parameter :: rho_crit_0 = 9.2034676577211722e-30
real*8, parameter :: m_p=1.672661e-24 
real*8, parameter :: abu_he=0.074
real*8, parameter :: abu_h=1.0-abu_he
real*8, parameter :: abu_he_mass=0.24
real*8, parameter :: abu_h_mass=1.0-abu_he_mass
real*8, parameter :: mean_molecular = 1.0*abu_h + 4.0*abu_he
real*8, parameter :: lam = 1.0 - Omega0
real*4, parameter :: T4 = 1 !Temperature/10^4K
real*4, parameter :: Temp = 1e4 !Temperature in K
real*4, parameter :: Dnu = 1.0566e11*sqrt(T4) !Doppler width
real*8 :: velconvert
real*8 :: Hz !Redshift dependent Hubble parameter
real*8 :: dx, dy, dz

!Simulation parameters
integer :: n_box
real*8 :: boxsize
real*8 ::  LB
real*8 :: lscale
real*4  ::D_box

namelist /parameters/ xfile, dfile, vfile, redshift, outfile, &
        n_box, boxsize

!Read filenames and simluation paramters
open(unit=1, file='make_cell_data_parameters.txt', form='formatted', status='old')
read(1, nml=parameters, iostat=ierr)
close(1)

print*, 'Read parameters file'
print*, 'Redshift ', redshift
print*, 'xfile', xfile
print*, 'dfile', dfile
print*, 'vfile', vfile
print*, 'outfile', outfile
print*, 'n-box', n_box
print*, 'boxsize', boxsize

Hz = H0*sqrt(Omega0*(1.0+redshift)**3 + lam)
LB = boxsize/h
lscale = LB/dble(n_box)*Mpc
D_box = LB*1.e3

!Read ionized fractions, store in xi for now. Later in neutral_frac
print*, 'Reading neutral fractions...'
open(unit=2, file=xfile,status='old', form='unformatted')
read(2) xi_meshx, xi_meshy, xi_meshz
xi_n_cells = xi_meshx*xi_meshy*xi_meshz
allocate(xi(xi_n_cells))
read(2) (xi(i), i = 1, xi_n_cells)
close(2)
!neutral_frac = 1. - neutral_frac

!Read density
print*, 'Reading density...'
open(unit=2, file=dfile, status='old', form='unformatted', access='stream')
read(2) meshx, meshy, meshz
n_cells = meshx*meshy*meshz
allocate(density(n_cells))
read(2) (density(i), i = 1, n_cells)
close(2)

!Scale up xi to the same size as the density grid
allocate(neutral_frac(n_cells))
neutral_frac(:) = 0.
print*, 'Mean neutral frac. before scaling up:', sum(1.-xi)/xi_n_cells, ' sample:', 1.-xi(:3),&
' min:', minval(1.-xi), ' max:', maxval(1.-xi)
if (n_cells .ne. xi_n_cells) then
	print*, 'n_cells:', n_cells
	print*, 'xi_n_cells:', xi_n_cells
	print*, 'Scaling up xi to higher res...'
	do x = 1,xi_meshx
	  do y = 1,xi_meshx
		do z = 1,xi_meshx
		  xd = 2*x; yd = 2*y; zd = 2*z
		  tmp = 1. - xi((x-1)*xi_meshx*xi_meshx + (y-1)*xi_meshx+z)

		  neutral_frac( (xd-1)*meshx*meshx + (yd-1)*meshx + zd) = tmp   !000
		  neutral_frac( (xd-1)*meshx*meshx + (yd-1)*meshx + zd-1) = tmp !001
		  neutral_frac( (xd-1)*meshx*meshx + (yd-2)*meshx + zd) = tmp   !010
		  neutral_frac( (xd-1)*meshx*meshx + (yd-2)*meshx + zd-1) = tmp !011
		  neutral_frac( (xd-2)*meshx*meshx + (yd-1)*meshx + zd) = tmp   !100
		  neutral_frac( (xd-2)*meshx*meshx + (yd-1)*meshx + zd-1) = tmp !101
		  neutral_frac( (xd-2)*meshx*meshx + (yd-2)*meshx + zd) = tmp   !110
		  neutral_frac( (xd-2)*meshx*meshx + (yd-2)*meshx + zd-1) = tmp !111
		enddo
	  enddo
	enddo
else
	neutral_frac = 1. - xi
	deallocate(xi)
endif
print*, 'Mean neutral frac. after scaling up:', sum(neutral_frac)/size(neutral_frac), ' sample:', neutral_frac(:3),&
' min:', minval(neutral_frac), ' max:', maxval(neutral_frac)


!Convert density to cm^-3
allocate(rho(n_cells))
rho = dble(density) * rho_crit_0*Omega0*(dble(meshx)/dble(n_box))**3*(1.0+redshift)**3
rho = rho * OmegaB/Omega0/(mean_molecular*m_p)*abu_h
print*, 'Average density:', sum(rho)/n_cells, 'cm^-3'
print*, 'Minimum density:', minval(rho), 'cm^-3'
print*, 'Maximum density:', maxval(rho), 'cm^-3'

!Read velocity
print*, 'Reading velocity...'
allocate(velocity(3*n_cells))
open(unit=2, file=vfile, status='old', form='unformatted', access='stream')
read(2) meshx, meshy, meshz
read(2) (velocity(i), i = 1, n_cells*3)
close(2)


!Split velocity into x,y,z components
allocate(ux(n_cells))
allocate(uy(n_cells))
allocate(uz(n_cells))
ux = dble(velocity(1:n_cells:3))
uy = dble(velocity(2:n_cells:3))
uz = dble(velocity(3:n_cells:3))
deallocate(velocity)

!Convert velocity to km/s
velconvert = lscale/tscale*(1.0+redshift)/1.e5
ux = (velconvert*ux)/(dble(density)/8.)
uy = (velconvert*uy)/(dble(density)/8.)
uz = (velconvert*uz)/(dble(density)/8.)

print*, 'Mean velocity (magnitude):', sum(sqrt(ux*ux+uy*uy+uz*uz))/n_cells, 'km/s'

!Reshape to have z variying quickest
allocate(ux_c(n_cells))
allocate(uy_c(n_cells))
allocate(uz_c(n_cells))
allocate(rho_c(n_cells))
print*, 'Transposing...'
call reverse_order(ux, ux_c, meshx)
call reverse_order(uy, uy_c, meshx)
call reverse_order(uz, uz_c, meshx)
call reverse_order(rho*neutral_frac, rho_c, meshx)
print*, 'Mass-weighed mean ionization fraction:', 1-sum(rho_c)/sum(rho)
deallocate(ux)
deallocate(uy)
deallocate(uz)
deallocate(rho)
deallocate(neutral_frac)



!Calculate the expansion velocity, v = d*Hz
print*, 'Calculating Hubble flow...'
do x = 1,meshx
  do y = 1,meshy
    do z = 1,meshz
      dx = float((x-meshx/2))/float(meshx)*LB/(1.0+redshift)
      dy = float((y-meshy/2))/float(meshx)*LB/(1.0+redshift)
      dz = float((z-meshz/2))/float(meshx)*LB/(1.0+redshift)
      cell_idx = (x-1)*meshx*meshy + (y-1)*meshy + z
      ux_c(cell_idx) = ux_c(cell_idx) + dx*Hz
      uy_c(cell_idx) = uy_c(cell_idx) + dy*Hz
      uz_c(cell_idx) = uz_c(cell_idx) + dz*Hz
    enddo
  enddo
enddo


!Divide by thermal width, v1.0
ux_c = ux_c/(12.845*sqrt(T4))
uy_c = uy_c/(12.845*sqrt(T4))
uz_c = uz_c/(12.845*sqrt(T4))


!Write
print*, 'D_box:', dble(dble(d_box)/(1.0+redshift))
print*, 'Saving to file:', outfile
print*, 'n_cells is:', n_cells
open(2,file=outfile, form='unformatted', status='replace', action='write')
write(2) n_cells, dble(dble(d_box)/(1.0+redshift)), meshx, meshy, meshz
write(2) (int(0), i = 1, n_cells)
write(2) (real(rho_c(i)), i = 1, n_cells)
write(2) (real(Dnu), i = 1, n_cells) !v 1.0
write(2) (real(ux_c(i)), i = 1, n_cells)
write(2) (real(uy_c(i)), i = 1, n_cells)
write(2) (real(uz_c(i)), i = 1, n_cells)
close(2)

!Clean up
deallocate(density)
deallocate(ux_c)
deallocate(uy_c)
deallocate(uz_c)
deallocate(rho_c)

end program

!-----------------------------
!reverse an array from x,y,z-order to z,y,x-order
subroutine reverse_order(A, B, meshx)
implicit none
integer :: meshx, x,y,z, i
real*8, dimension(meshx**3), intent(in):: A
real*8, dimension(meshx**3), intent(out):: B

i = 1
do x = 1,meshx
  do y = 1,meshx
    do z = 1,meshx
      B(i) = A((z-1)*meshx*meshx+(y-1)*meshx+x)
      !B(i) = A(i)
      i = i+1
    enddo
  enddo
enddo

end subroutine
!-----------------------------
