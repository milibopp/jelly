# Notes on AREPO usage

## Configuration file

Config.sh in the Arepo directory needs to be changed and Arepo recompiled in certain situations:

- Change of any compiler flags, obviously
- Change of domain box size

## Initial conditions

- Never use zero as a cell ID, it causes the derefinement subroutines to crash,
  since they internally set the ID of removed cells to zero


# Open questions

- Is any manual control of domain decomposition required?
- How do you change dimensionality?
