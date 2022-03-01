import os
import pandas as pd

def getReport(file, dataframe, ticker_input, date_input):
    file.write("///////////////////////////////////////////////////\n")
    file.write(f"REPORT FOR TICKER {ticker_input} ON DATE {date_input}\n\n")
    total_volume = dataframe['volume'].sum()
    file.write("Total volume: " + str(total_volume) + "\n")
    total_calls = dataframe['contractSymbol'].count()
    file.write("Total options: " + str(total_calls) + "\n")
    #Bought at or below bid dataframe slice
    atOrBelowBid = dataframe.loc[(dataframe['lastPrice'] <= dataframe['bid'])]
    atOrBelowBid_totalVolume = atOrBelowBid['volume'].sum()
    file.write("Bought at or below bid volume sum: " + str(atOrBelowBid_totalVolume) + '\n')
    file.write("Percentage of total: " + str(round(atOrBelowBid_totalVolume / total_volume * 100, 2)) + "%\n")

    #Bought at or above ask dataframe slice
    atOrAboveAsk = dataframe.loc[(dataframe['lastPrice'] >= dataframe['ask'])]
    atOrAboveAsk_totalVolume = atOrAboveAsk['volume'].sum()
    file.write("Bought at or above ask volume sum: " + str(atOrAboveAsk_totalVolume)+ '\n')
    file.write("Percentage of total: " + str(round(atOrAboveAsk_totalVolume / total_volume * 100, 2)) + "%\n")
    
    #Bought between market (at price between bid and ask)
    betweenTheMarket = dataframe.loc[(dataframe['lastPrice'] > dataframe['bid']) & (dataframe['lastPrice'] < dataframe['ask'])]
    betweenTheMarket_totalVolume = betweenTheMarket['volume'].sum()
    file.write("Bought between market (at price between bid and ask) volume sum: " + str(betweenTheMarket_totalVolume)+ '\n')
    file.write("Percentage of total: " + str(round(betweenTheMarket_totalVolume / total_volume * 100, 2)) + "%\n")            
    file.write("///////////////////////////////////////////////////\n")

while True:
    date_input = str(input("Please enter a date in format mm/dd/yyyy or Q to quit: "))
    if date_input == 'Q':
        break
    date_input_array = date_input.split("/")
    if (len(date_input_array[0]) == 1):
        date_input_array[0] = "0" + date_input_array[0]
    if (len(date_input_array[1]) == 1):
        date_input_array[1] = "0" + date_input_array[1]
    file_date = date_input_array[2] + "-" + date_input_array[0] + "-" + date_input_array[1]
    dateExists = False
    try:
        for file_name in os.listdir('call_options/'):
            if file_date in file_name:
                dateExists = True
                break
        for file_name in os.listdir('put_options/'):
            if file_date in file_name:
                dateExists = True
                break
        if (dateExists == False): raise Exception("-----------------------\nERROR: Date does not exist in files, please try another date\n-----------------------")
    except Exception as E:
        print(E)
    else:
        while True:
            ticker_input = str(input("Please enter a ticker you want to parse or Q to quit: "))
            if ticker_input == 'Q':
                break
            option_type = str(input("Do you want to explore call options? (Y/y) or (N/n) for puts: "))
            file_name = file_date + "_" + ticker_input
            if option_type == 'Y' or option_type == 'y':
                try:
                    file_name = "call_options/" + file_name + "_C.csv"
                    calls_dataframe = pd.read_csv(file_name, sep=',')
                except:
                    print(f'-----------------------\nERROR: Ticker {ticker_input} does not exist, cannot open file\n-----------------------')
                else:
                    with open('generated_reports/' + file_name[:-4] + '_REPORT.txt', 'w') as new_f:
                        getReport(new_f, calls_dataframe, ticker_input, date_input)
                    new_f.close()
            else:
                try:
                    file_name = "put_options/" + file_name + "_P.csv"
                    puts_dataframe = pd.read_csv(file_name, sep=',')
                except:
                    print(f'ERROR: Ticker {ticker_input} does not exist, cannot open file') 
                else:
                    with open('generated_reports/' + file_name[:-4] + '_REPORT.txt', 'w') as new_f:
                        getReport(new_f, puts_dataframe, ticker_input, date_input)
                    new_f.close()
#for f in os.listdir(calls):
#    file = 'call_options/' + f
#    if os.path.isfile(file):
#        file