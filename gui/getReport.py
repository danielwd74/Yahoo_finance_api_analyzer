import os
import pandas as pd

#helper function
def getReport(optiontype, dataframe, ticker_input, date_input):
    return_string = ''
    return_string += ("///////////////////////////////////////////////////\n")
    return_string += (f"{optiontype} REPORT FOR TICKER {ticker_input} ON DATE {date_input}\n\n")
    total_volume = dataframe['volume'].sum()
    return_string += ("Total volume: " + str(total_volume) + "\n")
    total_calls = dataframe['contractSymbol'].count()
    return_string += ("Total options: " + str(total_calls) + "\n")
    #Bought at or below bid dataframe slice
    atOrBelowBid = dataframe.loc[(dataframe['lastPrice'] <= dataframe['bid'])]
    atOrBelowBid_totalVolume = atOrBelowBid['volume'].sum()
    return_string += ("Bought at or below bid volume sum: " + str(atOrBelowBid_totalVolume) + '\n')
    return_string += ("Percentage of total: " + str(round(atOrBelowBid_totalVolume / total_volume * 100, 2)) + "%\n")

    #Bought at or above ask dataframe slice
    atOrAboveAsk = dataframe.loc[(dataframe['lastPrice'] >= dataframe['ask'])]
    atOrAboveAsk_totalVolume = atOrAboveAsk['volume'].sum()
    return_string += ("Bought at or above ask volume sum: " + str(atOrAboveAsk_totalVolume)+ '\n')
    return_string += ("Percentage of total: " + str(round(atOrAboveAsk_totalVolume / total_volume * 100, 2)) + "%\n")
    
    #Bought between market (at price between bid and ask)
    betweenTheMarket = dataframe.loc[(dataframe['lastPrice'] > dataframe['bid']) & (dataframe['lastPrice'] < dataframe['ask'])]
    betweenTheMarket_totalVolume = betweenTheMarket['volume'].sum()
    return_string += ("Bought between market (at price between bid and ask) volume sum: " + str(betweenTheMarket_totalVolume)+ '\n')
    return_string += ("Percentage of total: " + str(round(betweenTheMarket_totalVolume / total_volume * 100, 2)) + "%\n")            
    return_string += ("///////////////////////////////////////////////////\n")

    return return_string

def get_report_data(date_input, ticker_input, option_type):
    #date_input = str(input("Please enter a date in format mm/dd/yyyy or Q to quit: "))
    file_date = str(date_input)
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
        return E
    else:
        file_name = file_date + "_" + ticker_input
        if option_type == False:
            try:
                file_name = "call_options/" + file_name + "_C.csv"
                print("FILE NAME: ", file_name)
                calls_dataframe = pd.read_csv(file_name, sep=',')
            except:
                return (f'ERROR: Ticker {ticker_input} does not exist, cannot open file')
            else:
                return getReport("Calls", calls_dataframe, ticker_input, date_input)
        elif option_type == True:
            try:
                file_name = "put_options/" + file_name + "_P.csv"
                print("FILE NAME: ", file_name)
                puts_dataframe = pd.read_csv(file_name, sep=',')
            except:
                return (f'ERROR: Ticker {ticker_input} does not exist, cannot open file') 
            else:
                return getReport("Puts", puts_dataframe, ticker_input, date_input)
        else:
            return "Could not get option choice"