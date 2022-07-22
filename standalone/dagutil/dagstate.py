from util.astro import astroClient
from util.software import softwareClient
from os.path import dirname, abspath
import sys

'''
Script Execution
Info Generic Script to Pause Unpause Airflow Dags based on the requested action and list of Dags Provided. Configured to work for both Astronomer Software and Astro.

Execution format python3 dagstate.py <target> <action> <daglist> wherein
    # <target>: Accepted Values Software or Astro
    # <action> : Pause or Unpause Dags
    # <daglist> : Text file name, having list of dags with one line for each dag in input folder.Example daglist.txt
    # sample command: python3 dagstate.py astro unpause daglist.txt 
    # sample command: python3 dagstate.py software pause daglist.txt
'''

def get_dag_list(input_location,inputfilename,action):

    '''
        Desc: Function to get the daglist from the input file name in the input location

        @input_location: location to look for the dag list file. Default location /input folder
        @input_filename: file name along with extension to be used as input, it is provided by user.
        @action: Action to be performed, values pause to pause the Dags, unpause to unpause the dags
    '''

    try:
        print(" INFO: Getting List of Dags for the " + action + " operation")
        daglist = []
        with open(f"{input_location}/"+inputfilename) as f:
            while True:
                line = f.readline().strip()
                if not line: 
                    break            
                daglist.append(line)
        
        print(" INFO: Got the following DagId's " + str(daglist))
        return daglist

    except Exception as e:
        print("Got Exception while Fetching the Dag List from " + inputfilename)
        print(str(e))

def start_execution(input_location,inputfilename,target,action):

    '''
        Desc: Function to start the execution process to pause or unpause the Dags for the target i.e. Astronomer Software or Astro.

        @input_location: location to look for the dag list file. Default location /input folder.
        @input_filename: file name along with extension to be used as input, it is provided by user.
        @target: Command line argument passed by user, specifies whether to perfom action in software or astro.
        @action: Action to be performed, values pause to pause the Dags, unpause to unpause the dags
    '''

    try:

        if  (target == "astro") or (target == "software"):
            
            if target == "astro":
                client = astroClient()
                print(" INFO: Executing Utility for Astro")

            else:
                client = softwareClient()
                print(" INFO: Executing Utility for Software")
            
            if (action == "unpause") or (action == "pause"):
                
                if action == "unpause":
                    pause_flag = False
                else:
                    pause_flag = True

                daglist = get_dag_list(input_location,inputfilename,action)

                for dagid in daglist:

                    if dagid == "astronomer_monitoring_dag":
                        print("ERROR: Dag with dag_id astronomer_monitoring_dag cannot be paused or unpaused")

                    else:
                        status = client.pause_unpausedags(dagid, pause_flag)
                        print(status)

            else:
                print(" ERROR: Please input the correct parameter to pause/unpause the Dag, Parameter accepted for action are pause or unpause.")

        else:
            print(" ERROR: Please input the correct parameter to pause/unpause the Dag, Parameter accepted for target are software or astro.")

    except Exception as e:
        print(" EXCEPTION: Got Exception while execution of this Utility")
        print(" EXCEPTION: " + str(e))
        
if __name__ == '__main__':

    try:
        input_location = dirname(dirname(abspath(__file__))) + "/dagutil/input"

        #Fetching the command line arguments
        target = sys.argv[1].lower().strip()
        action = sys.argv[2].lower().strip()
        inputfilename = sys.argv[3].lower().strip()
        
        start_execution(input_location,inputfilename,target,action)

    except IndexError:
        #Rasing an Exception in case one or more required command line arguments are missing
        print(" ERROR: Please Input correct set of input parameter to start the execution of utility to pause/unpause Dags in Astronomer Software or Astro. \n Required format is python3 dagstate.py <target> <action> <daglist> ")
        print("     <target> can be software or astro")
        print("     <action> can be pause or unpause")
        print("     <daglist> can be a text file in input folder")

    except Exception as e:
        #Exception to handle genric issues
        print(" EXCEPTION: Got Exception while execution of this Utility")
        print(" EXCEPTION: " + str(e))
