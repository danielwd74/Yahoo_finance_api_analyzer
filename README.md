config2.py gathers informations from yahoo finance API and stores that data into a csv after manipulating dates from UNIX to regular mm/dd/yyyy HH:MM times and stores the information into seperate folders, getsummary.py gets summary data of certain options volume / total options volume based off 3 logical cases (see below) and also generates a report off that data which is stored into a text file with timestamp as well as ticker type
1) ((lastprice > bid) AND (lastprice < ask))
2) (lastprice <= bid)
3) (lastprice >= ask)
