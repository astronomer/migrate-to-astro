from git import Tag
from util.astro import astroClient
from util.software import softwareClient
from os.path import dirname, abspath
import sys
import json 
import os
import csv

'''
Generic Script to get the list of Dags along with Description, Pause Status and Tags associated with the Dag.
Execution Format: python3 getdaglist.py <target> wherein
    # <target>: Accepted Values Software or Astro
Output: 
It gets total number of Dags in a Deployment then generates DagDetails in CSV format with output file name output_dagdetails.csv
'''

def dir_check_create(path):

    '''
    Function to Check if Directory Exists and if Not Create the Directory
    '''

    try:    
        if not os.path.exists(path):
            os.makedirs(path)

    except Exception as e:
        print("Exception Occured while directory Check and Create Process for the Directory Path: " + path)
        print("EXCEPTION: " + str(e))

def get_total_dags_count(output_location,response):

    '''
    Function to parse the JSON output of DAG API response and to get total dags count in the deployment, 
    This is used as input to set Limit to further API call's to get the Dag Details for the total dag count.
        @output_location: location to generate a temp JSON file to get Dags details
        @response: JSON output of the API execution
    '''

    try:
        dir_check_create(output_location)

        with open(f"{output_location}/temp.json", "w") as outfile:
            outfile.write(response)

        f = open(f"{output_location}/temp.json")
                
        ##Returns JSON object as a dictionary
        data = json.load(f)

        totaldags_count = data['total_entries']

        f.close()

        return totaldags_count
        
    except Exception as e:
        print("Exception Occured while parsing the JSON to get the Total DAG Count")
        print("EXCEPTION: " + str(e))      


def parse_daglist_json(output_location,response,dagoffset):

    '''
    Function to parse the JSON output of DAG API response and generate a CSV file with required fields
        @output_location: location of the output csv file having Dag Details.
        @response: JSON output of the API execution
    '''

    try:
        dir_check_create(output_location)
        output_file= f"{output_location}/output_dagdetails.csv"

        with open(f"{output_location}/temp.json", "w") as outfile:
            outfile.write(response)

        f = open(f"{output_location}/temp.json")
                
        ##Returns JSON object as a dictionary
        data = json.load(f)

        ##Variable to ensure that header is only added in once while writing in an empty file
        headercount = 0

        for i in data['dags']:

            taglist= ""
            for j in i['tags']:
                taglist = taglist + j['name'] + ","

            header = ['DAGID','DESCRIPTION','IS_PAUSED','TAGS']
            data = [i['dag_id'],i['description'],i['is_paused'],taglist[:-1]]
            
            ##Writing Header into the Empty File and with First data record.
            if (headercount == 0) and (dagoffset == 0):
                with open(output_file,'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(header)
                    writer.writerow(data)
                    headercount = headercount +1

            ## Appending the Repo Data read from JSON to the CSV file. (HeaderCount not equal to 0)
            else:
                with open(output_file,'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(data)

        f.close()
        return True,output_file

    except Exception as e:
        print("Exception Occured while parsing the JSON to get the DAG List")
        print("EXCEPTION: " + str(e))      

def start_execution(output_location,target):

    '''
    Function to start execution of the get dag list utility.
        @output_location: location of the output csv file having Dag Details.
        @target: Command line argument passed by user, specifies whether to get Dag list from software or astro.
    '''
    
    try:

        if  (target == "astro") or (target == "software"):
            
            if target == "astro":
                client = astroClient()
                print(" INFO: Executing Utility for Astro")

            else:
                client = softwareClient()
                print(" INFO: Executing Utility for Software")

            '''
            Setting the Paramters for API Execution to get the Dag List.
            Daglimit - limit to fetch x number of Dags, Derived from the total dag present in the Deployment
            dagoffset - The number of items to skip before starting to collect the result set.

            So we start with offset as 0 and then fetch first 100 dags (API is limiting Dag Fetch to 100 only) thereafter set Offset as 100 and 
            fetch next set of 100 dags i.e. 101 to 200 and so on till the offset value is less then daglimit dervied from the deployment
            '''

            daglimit = 1
            dagoffset = 0

            totaldags_response = client.list_dags(daglimit,dagoffset)
            totaldags_count = get_total_dags_count(output_location,totaldags_response)
            print(" INFO: Total Dags in the " + target + " deployment is " + str(totaldags_count))

            
            while dagoffset <totaldags_count:
                response = client.list_dags(totaldags_count,dagoffset)
                execution_flag, output_file = parse_daglist_json(output_location,response,dagoffset)
                dagoffset = dagoffset + 100

            if execution_flag:
                print(" SUCCESS: DAG Details generated Successfully, Please refer the output file: "+ output_file)
            
    except Exception as e:
        print(" EXCEPTION: Got Exception while execution of this Utility")
        print(" EXCEPTION: " + str(e))

if __name__ == '__main__':

    try:
        output_location = dirname(dirname(abspath(__file__))) + "/dagutil/output"

        #Fetching the command line arguments
        target = sys.argv[1].lower().strip()
        start_execution(output_location,target)

    except IndexError:
        #Rasing an Exception in case one or more required command line arguments are missing
        print(" ERROR: Please Input correct set of input parameter to start the execution of utility to get list of Dags in Astronomer Software or Astro. \n Required format is python3 getdaglist.py <target>")
        print("     <target> can be software or astro")

    except Exception as e:
        #Exception to handle genric issues
        print(" EXCEPTION: Got Exception while execution of this Utility")
        print(" EXCEPTION: " + str(e))
