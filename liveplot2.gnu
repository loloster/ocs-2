# Greg Ziegan (grz5)
# Matt Prosser (mep99)
# Plotting format file. Is reread to refresh live plot

reset
set terminal wxt size 1300,600
set multiplot layout 3,1 title "MMO-3"
set tmargin 2

### Plot OSC1 '65440'
set title "OSC1"
unset key
stats 'plot.dat' using 1 name "X"
set xlabel "time (ms)"
set ylabel "Modulation Value"
if (X_max < 2000) {
    set autoscale x
} else {
    set xrange [X_max-2000:X_max]
}
set yrange [-40000:40000] 
plot "<(grep 65440 plot.dat)" using 1:3 with lines
###

### Plot OSC2 '65441'
set title "OSC2"
unset key
set xlabel "time (ms)"
set ylabel "Modulation Value"
if (X_max < 2000) {
    set autoscale x
} else {
    set xrange [X_max-2000:X_max]
}
set yrange [-40000:40000] 
plot "<(grep 65441 plot.dat)" using 1:3 with lines
###

### Plot OSC3 '65442'
set title "OSC3"
unset key
stats 'plot.dat' using 1 name "X"
set xlabel "time (ms)"
set ylabel "Modulation Value"
if (X_max < 2000) {
    set autoscale x
} else {
    set xrange [X_max-2000:X_max]
}
set yrange [-40000:40000] 
plot "<(grep 65442 plot.dat)" using 1:3 with lines
###

unset multiplot
pause 0.001  # stepsize
reread
