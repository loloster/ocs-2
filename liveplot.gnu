# Greg Ziegan (grz5)
# Matt Prosser (mep99)
# Plotting format file. Is reread to refresh live plot

reset
#set terminal xvt size 1300,600
set terminal wxt size 1300,600
#set terminal xterm
#set terminal dumb
set multiplot layout 3,1 title "MMO-3"
set tmargin 2
### Plot x1, y1
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
#plot "plot.dat" using 1:2 with lines, "plot.dat" using 1:5 with lines
plot "plot.dat" using 1:2 with lines
###

unset multiplot
#pause 0.01  # stepsize
reread
