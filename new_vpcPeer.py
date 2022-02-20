'''
Created on November 2020

@author: dominickhernandez
'''
   
from pprint import pprint  
##  useful to 'pretty print, or pretty format' data-structures, that are nested or not.
import json, os     ## module for JSON data encoding and decoding.
from string import Template
## This is useful for modifying code using '$' prefixes for variables when constructing a new string from a given string.
import uuid         ## module to generate random unique id's.
import argparse  	## module to get command arguments from the user.
import ipaddress  	## module with many methods to create and control IPV4/IPv6 addresses and networks.

## Create banner upon execution.
banner = """ 
     ___        __  ___ ___ __     __  __  __   _____ 
|\ ||__ |  |   |__)|__ |__ |__)   /__`/  `|__)||__)|  
| \||___|/\|   |   |___|___|  \   .__/\__,|  \||   |  
                                                      

"""

Dependency = [
    'colorama',
    'gitpython',
    'netaddr',
    'python_terraform',
    'termcolor',
    ]
## Dependency is a list of strings based on the modules needed to run this program.

try: 
    ## The purpose of using try-except is to exit this program if it fails to import the packages listed in 'Dependency'.
    ## It will print two messages telling the user to install python packages listed in Dependency.
    from python_terraform import * ## A module to call the 'terraform' command.
    from termcolor import colored  ## A module for ANSII Color formatting output for terminals of specific type based on shell exported $TERM  
    from git import Repo           ## Modules to interact with git repos.
    from netaddr import IPNetwork  ## Modules to manipulate IPv4/IPv6 networks.
    import colorama                ## Makes ANSI escape character sequences for producing colored terminal text.

except ImportError:
    ## If a ImportError exception is encountered during the try block, 
    ## this will print a message telling the user to install the necessary modules.
    print()
    print('Install the following dependencies and try again:', 'red')
    print('sudo pip3 install -t /opt/python3/lib/python3.7/site-packages/')  ## Tells the user what to install:

    for dep in Dependency: ## Loop through the Dependency list as 'dep', telling the user each "- dep" they should install.
        print('- ' + dep)
        
    exit()

colorama.init()  ## Initialize colorama.

class Arguments(object):
    """
    Used for Arguments from the command line (--help gives usage).
    """
    ## When this class, 'Arguments' is called as a function, this '__init__()' function will be executed
    ## and will automatically 'return' a programming object of type 'Arguments'.
    ##
    ## Note that 'self' is a reference to the current instance of this class, and it
    ## exists before the instance is returned as an object for use outside of the class.
    ##
    ## The arguments defined are 'self', so '__init__()' knows what to initialize, and
    ## 'description' which is set by default to and empty string if not specified by the 
    ## function that called this.
    def __init__(self, description=''):
        """
        Default arguments for any job
        """
        ## Create '_parser' variable of the instance is an 'argparse.ArgumentParser' object.
        ## to contain CLI arguments and options provided, or defaults for those, as well as
        ## help strings for each argument.
        self._parser = argparse.ArgumentParser(description=description)

        ## PROGRAMMER NOTE: In the code below, there are no 'Positional Arguments'.
        ## Only optional arguments are defined here, along with their default and help strings.

        ## The following two lines should be deleted if they will not be needed again.
        # Positional Arguments
        # self._parser.add_argument('dc')

        # Optional Arguments
        self._parser.add_argument('-c',
                                  dest='cloud',
                                  default='',
                                  help='Cloud Environment')  ## create 'cloud' variable referenced later args.cloud .
        self._parser.add_argument('-r',
                                  dest='region',
                                  default='',
                                  help='Cloud Region')       ## create 'region' variable referenced later args.region .
        self._parser.add_argument('-cs',
                                  dest='cloud_secret',
                                  default='',
                                  help='Cloud Secret')       ## create 'cloud_secret' variable referenced later args.cloud_secret .
        self._parser.add_argument('-a',
                                  dest='app',
                                  default='',
                                  help='Application')        ## create 'app' variable referenced later args.app .
        self._parser.add_argument('-i',
                                  dest='ins',
                                  default='',
                                  help='Instance')           ## create 'ins' variable referenced later args.ins .
        self._parser.add_argument('-p', 
                                  dest='id',
                                  default='',
                                  help='Peer Identify')      ## create 'id' variable referenced later args.id .
        self._parser.add_argument('-s', 
                                  dest='subnet',
                                  default='',
                                  help='Peer Subnet')        ## create 'subnet' variable referenced later args.subnet .

        ## The following argument definition should be removed it will no longer be needed.
        # self._parser.add_argument('-l', 
        #                           dest='legacy',
        #                           action='store_true',
        #                           help='Legacy Configuration (only applicatable for AWS)')


    ## define a local method 'get' within this class, to provide external caller access to '_parser' from within this class.
    ## return private 'self._args' to a calling function.
    ##
    ## PROGRAMMER WARNING: This looks like either unfinished or vestigil code, as there is no use of the 
    ##   defined "access='read'".  However, if external programs import this code, this could exist to
    ##   prevent breaking that external code.
    def get(self, access='read'):
        """
        Get the arguments and verify them
        """
        self._args = self._parser.parse_args()  ## Define 'self._args' as an object to access the options stored in '_parser'.

        ## return caller access to class object '_args'. The single leading '_' indicates that by Python programming convention
        ##   this should be treated as a class private variable, even though the language itself does not enforce that.
        ##   This allows other portions of the program outside of the class to have coherent access to the CLI arguments.
        return self._args  

## This defines function 'logger()' that is given a 'color' argument.
## This 'logger' function wraps a locally defined function '_logger', and returns that function address
## to the caller so that it can later use '_logger', giving it access to 'color.
##
##      The '_logger' function takes arguments 'header', data, and *args.  *args means a variable number of positional arguments.
##         - If given a dictionary datastructure called 'data', '_logger' will via 'pformat()' transform and format the dictionary
##           into a string.  Then it will further format that string via 'colored()', and then print it to standard output of the
##           program.
##         - Else, if given a string datastructure called 'data', '_logger', it will format that string via 'colored()', and then
##           print it to standard output of the program.
##
##  NOTE that every call to 'logger' will receive a different wrapped '_logger' function reference.  During execution, if the first caller 
##  sets color to red, and a second caller sets it to 'green', then the first caller's future uses of '_logger' will stay red.  
##  Likewise, the second caller's future use of '_logger', will format its own output as green.
def logger(color):
    """Log results"""
    def _logger(header, data, *args):
        if isinstance(data, dict) or isinstance(data, list):
            print(colored('\n[%s]\n' % header, color), pformat(data))
        elif isinstance(data, str):
            print(colored('[%s]' % header, color), data, *args)

    return _logger  ## This returns a unique wrapped function '_logger' to code that calls this.


log_i = logger('green')   ## log_i is a function reference to wrapped function '_logger' of 'logger', setting color to green.
log_w = logger('yellow')  ## log_w is a function reference to wrapped function '_logger' of 'logger', setting color to yellow.
log_e = logger('red')     ## log_e is a function reference to wrapped function '_logger' of 'logger', setting color to red.

## Create 'env' dictionary containing dictionaries with keywords of 'aws' and 'azure'.
##     - The 'aws' dictionary elements have keywords representing aws regions.  These are all initialized to empty strings.
##     - The 'azure' dictionary has one element with a keyword representing an azure region, and that is initialized with a hardcoded
##       IP address.  
env = {
    'aws': {
        'us-east-1': '',
        'us-east-2': '',
        'us-west-2': '',
},
    'azure': {
        # 'Region'  : 'Vnet NextHop'
        'central-us': '10.116.0.68',
    }
}

## Create 'sname' dictionary containing keyword:value pairs mapping either a cloud keyword to a cloud specific string value' or
## mapping a region keyword to a regin specific string value.
sname = {
    # Cloud
    'aws': 'aws',
    'azure': 'az',
    # Region
    'us-east-1': 'ue1',
    'us-east-2': 'ue2',
    'us-west-2': 'uw2',
    'central-us': 'cus',
}

## define function 'yesno_query().
##   This function prints to CLI standard output a given 'ask' string,
##   and then takes input that it converts to lower case, and then
##   uses the result of that to tell this program whether or not to
##   exit from execution.  It will repeat the question until it receives
##   an answer matching text strings that it looks for.
#    Then it will exit or not based on the answer.
## 
## PROGRAMMER WARNING: This function is structured to loop
## until it receives standard input that is case insensitive 
## of 'yes', 'y', 'no' or 'n', and that could be potentially never.
## If it looped through incorrect input, perhaps it would incorrectly act.
def yesno_query(ask, error):
    '''
    Query that will cancel script at no
    '''
    loop = True  ## Initialize boolian 'loop' as True.

    ##  While 'loop' remains True, keep executing this 'while' code block.
    while loop:	

        ## Using 'input()', get string input from STDIN (standard input), convert it 
        ## to lowercase, and use that to initialize string 'a' with that value.
        a = input(ask).lower()

        ## if 'a' is 'yes' or 'y':
        if a == 'yes' or a == 'y':
            loop = False  ## Set loop to False.  False will cause this 'while' code block to end. 
 
        ## if 'a' is 'no' or 'n':
        if a == 'no' or a == 'n':
            print()  ## print a newline with no visible text.

            ## call 'log_e' which is an '_logger' with 'red' configured.
            ## In the call, tell log_e to format/print two two supplied strings 
            log_e('Manual Exit', error)

            exit()  ## This causes the program to exit from execution.

## define function 'not_option_query(), to take arguments 'ask' and 'options'.
##  Loop taking standard input, and return that input as output if the input is 
##  not blank and is not already in the provided 'options'.
def not_option_query(ask, options):
    '''
    Query to make sure Answer is unique to option list
    '''
    loop = True  ## Initialize boolian 'loop' as True.

    ##  While 'loop' remains True, keep executing this 'while' code block.
    while loop:

        ## Using 'input()', get string input from STDIN (standard input), convert it 
        ## to lowercase, and use that to initialize string 'a' with that value.
        a = input(ask).lower()

        ## if 'a' is not an empty string, and 'a' is 'not in' (does not match) any of the given 'options',
        ## then set loop False so this 'while' loop will end.
        if a != '' and a not in options:
            answer = a  ## Initialize string 'answer' and copy the value of string 'a' into it.
            loop = False  ## Set loop to False.  False will cause this 'while' code block to end. 

        ## At this point, if loop was not set to False by the code above:
        if loop == True:
            print()  ## print a newline with no visible text.

            ## call 'log_e' which is an '_logger' with 'red' configured.
            ## In the call, tell log_e to format/print two two supplied strings 
            log_e('Unknown Response', 'Instance should be unique from below list')

            ## This 'for' loop will iterate through a sorted list of 'options' one at a time
            ## setting 'o' each time as it grabs a list element from 'options'.
            for o in sorted(options):
                print('- ' + o)  ## print a line with a hyphen followed by the current 'o' value.
            print()  ## print a blank line.

    return answer  ## return the 'answer' string to the caller.

## define function 'not_option_verify(), to take arguments 'info', 'options', 'arg', and 'ask'.
##     If the info is empty or already known in 'options':
##        then tell the user the 'arg' is 'Argument invalid'.
##     If info is still empty, call function 'not_option_query()' to 'ask' the user for a new arg, and return.
##     Else return the info that was given to this function.
def not_option_verify(info, options, arg, ask):
    '''
    Validate Argument is unique to option list
    If false, user will be prompted via "not_option_query"
    '''

    ##  If 'info' is not empty, and 'info' is already in 'options':
    if info != '' and info in options:
        ## call 'log_e' which is an '_logger' with 'red' configured.
        ## In the call, tell log_e to format/print two two supplied strings 
        log_e(arg, 'Argument invalid')

        ## Call not_option_query(), and when it finishes, take its output and return that.
        return not_option_query(ask, options)

    ##  If 'info' is empty:
    if info == '':
        ## Call not_option_query(), and when it finishes, take its output and return that.
        return not_option_query(ask, options)

    ## Else return the given 'info' to the caller
    else:
        return info 

## define function 'option_query(), to take arguments 'ask' and 'options'.
##  Loop taking standard input, and return that input as output if the input matches
##  any element in the 'options' list.
##  If it did not find that the input, print the options list for the user to choose
##  their answer from.
## 
def option_query(ask, options):
    '''
    Query to make sure Answer is in option list
    '''

    loop = True  ## Initialize boolian 'loop' as True.

    ##  While 'loop' remains True, keep executing this 'while' code block.
    while loop:

        ## Using 'input()', get string input from STDIN (standard input), convert it 
        ## to lowercase, and use that to initialize string 'a' with that value.
        a = input(ask).lower()

        ## if 'a' is matches any element 'in' the given 'options',
        ## then initialize 'answer' and copy the user input into it, then set loop False so this
        ## 'while' loop will end.
        if a in options:
            answer = a
            loop = False

        ## If 'loop' is True, indicating that the above clause did not find a matching option.
        if loop == True:
            print()  ## print a blank line.

            ## call 'log_e' which is an '_logger' with 'red' configured.
            ## In the call, tell log_e to format/print two two supplied strings 
            log_e('Unknown Response', 'Please choose from list below:')

            ## This 'for' loop will iterate through a sorted list of 'options' one at a time
            ## setting 'o' each time as it grabs a list element from 'options'.
            for o in sorted(options):
                print('- ' + o)  ## print a line with a hyphen followed by the current 'o' value.

            print()  ## print a blank line.

    return answer  ## return the 'answer' string to the caller.

## define function 'option_verify(), to take arguments 'info', 'options', 'arg', and 'ask'.
##     If the 'info' is not empty and not already known in 'options':
##        then tell the user the 'arg' is 'Argument invalid'.
##     If the 'info' is not in the options 
##        and call function 'option_query()' to 'ask' the user for a new arg.
##     Else return the info that was given to this function.
def option_verify(info, options, arg, ask):
    '''
    Validate Argument is in option list
    If false, user will be prompted via "option_query"
    '''
    ##  If 'info' is not empty, and 'info' is 'not in' 'options':
    if info != '' and info not in options:
        ## call 'log_e' which is an '_logger' with 'red' configured.
        ## In the call, tell log_e to format/print two two supplied strings 
        log_e(arg, 'Argument invalid')

    ## if 'info' is 'not in' 'options':
    if info not in options:
        ## Call option_query(), and when it finishes, take its output and return that.
        return option_query(ask, options)
    ## Else return the given 'info' to the caller
    else:
        return info 

## define function 'simple_query(), to take argument 'ask'.
## In a 'while' loop, keep taking input from the user until non empty input is provided.
## return a lowercase representaion of the user input.
def simple_query(ask):
    '''
    Query for raw answer
    No validation
    '''
    loop = True  ## Initialize boolian 'loop' as True.

    ##  Loop continuously until an answer is returned.
    while loop:
        ## Using 'input()', get string input from STDIN (standard input), convert it 
        ## to lowercase, and use that to initialize string 'answer' with that value.
        answer = input(ask).lower()

        ## If answer is not empty, return it.
        if answer != '':
            return answer

## define function 'simple_verify(), to take arguments 'info' and 'ask'.
## If 'info' is empty, call 'simple_query()' and return what it returned.
## Else return the 'info' that was provided.  This will be a user supplied answer string.
def simple_verify(info, ask):
    '''
    Validate Argument is set
    If empty, user will be prompted via "simple_query"
    '''
    if info == '':
        return simple_query(ask)
    else:
        return info 

## define function 'identify_cloud(), to take arguments 'args' and 'info'.
##   It sets info['cloud'] based on the output of 'option_verify()'.
## The 'return' from this function is implied to be 'None', as no return is
## explicitly defined here.
def identify_cloud(args, info):
    '''
    Identify Cloud Environment
    '''
    ask = 'Specify Cloud Environment: '  ## Initialize 'ask' string

    ## Initialize or overwrite the list element 'cloud' of the given 'info' list.
    ## set the value of 'cloud' within info to the output provided by
    ## 'option_verify()'.  
    ##
    ## Note that below, the 'info' keyword supplied to a function is not the same object as 'info' dictionary that 
    ## is defined in main().
    ##
    ## When supplying arguments to 'option_verify()', set the keyword arguments as follows:
    ##    For the 'info' keyword argument, take args.cloud that was derived from CLI input arguments, and
    ##        change any uppercase to lowercase. Then initialize the 'info' keyword to that value.
    ##    Set the 'options' keyword argument to an iterable object of type dict_keys (a dictionary view object),
    ##        from which the values of the keys or list elements can be extracted as strings.  In this code 
    ##        those strings would be 'aws' and 'azure'.
    ##    For the 'arg' keyword argument, simply set it to '-c'.
    ##    For the 'ask' keyword argument, simply set it to the hard coded local value of 'ask'.
    info['cloud'] = option_verify(info = args.cloud.lower(), 
                           options = env.keys(),
                           arg = '-c', 
                           ask = ask)

## define function 'identify_region(), to take arguments 'args' and 'info'.
##   It sets info['region'] based on the output of 'option_verify()'.
## The 'return' from this function is implied to be 'None', as no return is
## explicitly defined here.
def identify_region(args, info):
    '''
    Identify Cloud Region
    '''
    ask = 'Specify Cloud Region: '  ## Initialize 'ask' string

    ## Initialize or overwrite the list element 'region' of the given 'info' list.
    ## set the value of 'region' within info to the output provided by
    ## 'option_verify()'.  
    ##
    ## Note that below, the 'info' keyword supplied to a function is not the same object as 'info' dictionary that 
    ## is defined in main().
    ##
    ## set 
    ## When supplying arguments to 'option_verify()', set the keyword arguments as follows:
    ##    For the 'info' keyword argument, take args.region that was derived from CLI input arguments, and
    ##        change any uppercase to lowercase. Then initialize the 'info' keyword to that value.
    ## 
    ##    To set the 'options' keyword argument:
    ##        - First get the string value of global dictionary 'info' at element 'cloud'.
    ##        - Then use that value as a key into the 'env' dictionary to obtain a reference to a dictionary that was
    ##          placed there with that key. 
    ##        - Then call the keys() method of that dictionary to create a dict_key dynamic
    ##          view object for that dictionary.
    ##        - Set argument keyword 'options' equal to the dict_key object that was created.
    ##
    ##    For the 'arg' keyword argument, simply set it to '-c'.
    ## 
    ##    For the 'ask' keyword argument, simply set it to the hard coded local value of 'ask'.
    info['region'] = option_verify(info = args.region.lower(), 
                            options = env[info['cloud']].keys(),
                            arg = '-r', 
                            ask = ask)
    ## If info dictionary at ['cloud'] is equal to the string 'azure':
    if info['cloud'] == 'azure':
        ## Initialize info dictionary at ['next_hop'] to be the
        ## First get the value of the info dictionary at ['cloud'] keyword.
        ##     Using that string value as a key into the env dictionary, obtain the env values at that key.
        ##         The env values will be a list containing dictionaries.  This code takes index 0 of that list
        ##         to obtain only the first dictionary from that list.    
        ## Take the dictionary obtained from env and initialize dictionary info at ['next_hop'] to that value.
        info['next_hop'] = list(env[info['cloud']].values())[0]
        
## define function 'identify_cloud_secret(), to take arguments 'args' and 'info'.
##     If info['cloud'] is 'azure', 
##         It sets info['secret'] as follows:
##             Initialize the 'ask' string by taking the string 'Specify ',
##             and adding to that a string returned from colored() formatted in green.
##             that string is obtained from info['cloud'] after using the str.upper() method
##             to convert the found value to uppercase. Then another string ' Secret: ' is added
##             to that.
##     Else, it sets info['secret'] to be an empty string.

## The 'return' from this function is implied to be 'None', as no return is
## explicitly defined here.
def identify_cloud_secret(args, info):
    '''
    For Azure, ask for Cloud Secret
    '''
    ask = 'Specify '+colored(info['cloud'].upper(), "green")+' Secret: '
    if info['cloud'] == 'azure':
        secret = simple_verify(info = args.cloud_secret, 
                               ask = ask)
    else:
        secret = ''
    info['cloud_secret'] = secret

## define function 'existing_instances(), to take argument 'app'.
## The function compares the given 'app' string with the names of all files 
## or directories that are in the current file-system directory except '.' and '..'.
## 
## For every matching directory/file found, it appends to the 'ins' list, a substring 
## that is taken from the matched directory entry name.
##
## It will return the 'ins' list that will either be empty or contain the
## substrings. 
##
## PROGRAMMER WARNING:
## Depending on how unique the app string might be, and how 'ins' is used,
## this could be buggy.
##
## Note that the matching method used, could in theory match a directory that is for a different app.
## This could happen if a directory is found within the current directory where this program 
## executes, but only if the app string matches a substring of any portion of that directory name.
##     - Elsewhere in the code, the directory names are set to be of the form:
##         f"{app}_{cloud}_{region}_{ins}"
##     - app is  in the 0th underscore delimited position, and represents the app name.
##     - ins is  in the 4th underscore delimited position, and represents the app instance name supplied
##       as input.
##     - If in practice, this is a real issue, The matching method could be altered 
##       to compare 'app' with only the text of the 0th underscore delimited position.
def existing_instances(app):
    '''
    Indentify existing instances 
    for specified Application
    '''
    ins = []  ## Initialize 'ins' to be an empty list

    ## Using 'os.listdir()' method list current directory contents, except '.' and '..'.
    ## In a 'for' loop, iterate over the output of 'listdir()' as object 'p'.
    for p in os.listdir():
        ## If the value of the given app variable is found to match any portion of 'p',
        ## either matching entirely or matching a substring:
        ##   Take the value of p, which it assumes to be a string containing at least 3 '_'
        ##   characters.  Use the str.split() method to split the string into a list using
        ##   '_' as a delimiting character.  Then take the 4th item from that list and
        ##   append that item to the 'ins' list.
        if app in p:
            ins.append(p.split("_")[3])
    return(ins)


## define function 'identify_name(), to take arguments 'args', 'info'.
##  Create peer_name and store it in directory info{} at key 'peer_name'
def identify_name(args, info):
    '''
    Create Peer Name: <app>_<cloud>_<region>_<instance>_<unique_id>
    '''
    # cloud/region Short Name
    cloud = sname[info['cloud']]   ## Create 'cloud' string and initialize it from 'sname[]' at key('info{}' at 'cloud'). 
    region = sname[info['region']] ## Create 'region' string and initialize it from 'sname[]' at key('info{}' at 'region'). 

    # identify S3 Bucket name that holds remote state for AWS TGW or Azure Transit 
    if info['cloud'] == 'aws':                        ## If 'info{}' at 'cloud' equals string 'aws':
        info['state'] = cloud + '_' + region + '_tgw' ## Set 'info{}' at key 'state' to f"cloud_{region}_tgw"
    if info['cloud'] == 'azure':                        ## If 'info{}' at 'cloud' equals string 'azure':
        info['state'] = cloud + '_' + region + '_transit' ## Set 'info{}' at key 'state' to f"cloud_{region}_transit"

    # identify Application
    ask = 'Specify Application: '  ## Create 'ask' string

    ## Create the 'app' string and initialize it with the answer
    ## it obtains from simple_verify.
    ## For the call to simple_verify:
    ##     - The keyword argument 'info' is set to the value obtained from a value found from:
    ##       - Taking the CLI argument 'app' string
    ##       - Converting it to a lower case string
    ##       - Stripping off leading and trailing white spaces.
    ##     - The keyword argument 'ask' is set to the local string 'ask' 
    app = simple_verify(info = args.app.lower().strip(), ask = ask)

    # pulls list of all existing Instances for specified Application
    exist_ins = existing_instances(app+'_'+cloud+'_'+region)

    # identify App Instance and confirm it is unique for App
    ask = 'Specify Application Instance: '
    ins = not_option_verify(info = args.ins.lower().strip(), 
                        options = exist_ins,
                        arg = '-i', 
                        ask = ask)
    # build Perr Name by App/Cloud/Region/Instance
    ## Note that peer_name will be used for naming a directory that will be created,
    ## therefore, it must be unique.  The following original code is commented out
    ## and replaced with instructions below to create a unique id, and use it as part of peer_name.
    ## info['peer_name'] = app+'_'+cloud+'_'+region+'_'+ins

    ## Create string 'unique_id' and initialize it to a unique id hex value as a bytes,
    ## and convert those to a string
    unique_id = str(uuid.uuid4().hex) 

    ## Initialize info{} at key 'peer_name' as formatted in 'f string' below.
    info['peer_name'] = f'{app}_{cloud}_{region}_{ins}_{unique_id}'

## define function 'get_info(), to take argument 'opt'.
## return a list that either a dictionary containing peer information, or an empty list.
def get_info(opt):
    '''
    Pull Information from Static Peer List
    Pull Options:
        peer
        id
        subnet
    '''
    ## In a 'with' context block, open file 'peer_list.json' as object 'f'.
    with open('peer_list.json', 'r') as f:
        r = []  ## Initialize 'r' as an empty list
        p = json.load(f)  ## Create dictionary 'p', initialized with output of json.load() method
                          ## this reads json formatted data from file object 'f'.
                          ## If this read fails, there will be an uncaught exception and the program will abend.
        ## In a for loop:
        ## Iterate through p Keys and Values.  On each loop iteration put the key in 'a', and the value in 'b'.
        for a, b in p.items():
            ## If the value of 'opt' equals 'peer':
            if opt == 'peer':
                r.append(a)  ## Append 'a', the key into the 'r[]' list.
                return(r)    ## return the 'r[]' list.

            ## In the event that this function has not yet done a return, append 'b{}' dictionary to the 'r[]' list.
            r.append(b[opt])

        return(r) ## return the 'r[]' list, if the function has not already done a return.

## define function 'identify_subnet(), to take arguments 'args', and 'info'.
def identify_subnet(args, info):
    '''
    Identify Peer Subnet
    Confirms Peer Subnet is not already used
    '''
    ask = 'Specify Subnet: '  ## Create and initialize string 'ask'.
    loop = True  ## Create and set boolian variable 'loop' to True

    ## Create variable subnet, and initialize it to the return value of
    ##  not_option_verify to ask the user to specify subnet information.
    ##   - info keyword argument is set equal to locercase args.subset.
    ##   - options keyword argument is set equal to the return value of
    ##     get_info for 'subset.
    ##   - arg keyword argument is set to '-s'
    ##   - ask keyword argument is set to 'ask' that is defined above.
    subnet = not_option_verify(info = args.subnet.lower(), 
                options = get_info('subnet'),
                arg = '-s', 
                ask = ask)
    ## Starts a 'while True' loop.
    while loop:
        # Confirm the Subnet Provided is valid
        ## In a try-except block, call ipaddress.ip_network() method for the 'subnet'
        ##    ip_network obtains an IPv4 or IPv6 object depending on given IP address.
        ## If ip_network() did not encounter an exception, 'loop' is set to False so the
        ## while loop can exit.
        try:
            ipaddress.ip_network(subnet)
            loop = False
        except:  ## If any exception is encountered:

            ## call 'log_e' which is an '_logger' with 'red' configured.
            ## In the call, tell log_e to format/print two two supplied strings 
            log_e('Subnet Incorrect', 'Please provide valid Subnet.')

            ## Set 'subnet' from output of not_option_query() that asks the user for 'subnet'.
            subnet = not_option_query(ask, get_info('subnet')) 

        # Confirm Subnet is not overlaping any other existing Subnets Configured
        ## in a for loop, iterate through the return values from get_info('subnet'), setting 's' to the element 
        ## returned each time.
        for s in get_info('subnet'):

            ## If IP address of 'subnet' matches the IP address of 's', there is an overlap.
            ##     It obtains those addresses from netaddr.IPNetowrk() method):
            if IPNetwork(subnet).ip in IPNetwork(s):
  
                ## call 'log_e' which is an '_logger' with 'red' configured.
                ## In the call, tell log_e to format/print the given string and f-string.
                ## the f-string uses variable substitution to fill in {subnet} and {s} placeholders.
                log_e('Subnet Overlap', f'{subnet} is part of {s}.')

                ## Ask the user for the subnet.
                ## Set new subset variable to the output of not_option_query().
                subnet = not_option_query(ask, get_info('subnet'))
                loop = True  ## set loop to True so the while loop will continue.

            ## Else continue.  The continue directive tells the Python Interpreter to jump to the
            ## top of the while loop and continue execution from there.
            else:
                continue        

    ## set directory 'info{}' at 'peer_subnet' to 'subnet'.
    info['peer_subnet'] = subnet

## define function 'identify_peer(), to take arguments 'args', and 'info'.
## it sets info['peer_id']
def identify_peer(args, info):
    '''
    Identify Peer ID
    Confirms Peer ID is not already used
    '''
    ask = 'Specify Peer Identity: '  ## Create 'ask' string

    ## Create 'id' string initialized with output of 'not_option_verify()'
    ## to validate that 'id' is unique.
    ##     - set info keword argument to lowercase args.id.
    ##     - set options keword argument to output of get_info('id') 
    ##       that returns peer information.
    ##     - set arg keword argument to '-p'
    ##     - set ask keword argument to ask
    id = not_option_verify(info = args.id.lower(), 
                        options = get_info('id'),
                        arg = '-p', 
                        ask = ask)
    ## set dictionary 'info{}' at 'peer_id' to 'id'.
    info['peer_id'] = id

## define function 'identify' to take arguments 'args', and 'info'.
##  - Call the identify* functions that are defined above.
##  - Format and print peer information
##  - Ask whether or not to proceed
def identify(args, info):
    '''
    Identify Peer Information
    '''
    ## With 'args' and 'info' arguments, call the identify* functions.
    identify_cloud(args, info)
    identify_region(args, info)
    identify_cloud_secret(args, info)
    identify_name(args, info)
    identify_subnet(args, info)
    identify_peer(args, info)

    print()  ## print a blank line

    ## use colored() to take the string given, format it as green, 
    ## and give that text to print() 
    print(colored('[Peer Information]', 'green')) 

    ## The items() method returns key,value pairs during each loop iteration.
    for key, value in info.items():
        ## Create list 'l' and initialize it to the following strings.
        l = ['cloud', 'region', 'peer_name', 'peer_subnet', 'peer_id']

        ## if the current 'key' is found in list 'l':
        if key in l:
            ## Print an f-string comprised of:
            ##   - key.title(), which takes the value of key and transforms it so that each word is titlecased.
            ##     so words start with uppercased characters and all remaining cased characters have lower case.
            ##   - a ':'
            ##   - the value of 'value'
            print(f'{key.title()}: {value}')  ## print 

    ## set 'ask' and 'error' strings and ask yesno_query
    ask = '\nProceed with Above Information? '
    error = 'Rerun with correct information.'
    yesno_query(ask, error)  ## ask the user whether to proceed or not.

## define function 'pull_template' to take argument 'info'.
## Returns string data from Template after it makes instructed text substitutions.
def pull_template(info):
    '''
    Pull Terraform Template for AWS/Azure Peers
    '''
    ## In a 'with' context block open file: f'peer_templates/{info['cloud']}_peer_LATEST' as file object 'f'
    with open('peer_templates/' + info['cloud'] + '_peer_LATEST', 'r') as f:
        ## create a 't' object from class 'Template', telling it to read the contents of 'f' from the file.
        t = Template(f.read())

        ## Create string 'data' with return value of t.substitute(info) where it will
        ## make text substitutions based on the contents of 'info'.
        ## Template uses '$' prefixed variables to know which text to substitute.
        data = t.substitute(info)
           
        return data  ## return 'data' to the caller.

## define function 'create_peer_tf(), to take argument 'info'.
## It creates a Terraform Config File with peer_name.
def create_peer_tf(info):
    '''
    Create New Peer Directory & Config File
    '''
    tf = pull_template(info)  ## Create tf initialized to the output of pull_template(info) 
    name = info['peer_name']  ## Create string 'name' with value of 'info{}' at 'peer_name'.

    ## The following two commented out code lines should be removed if they will never be needed again.
    # app = name.split('_')[0]
    # inst = name.split('_')[3]

    ## If the value of 'name' is the pathname of a directory:
    if os.path.isdir(name):
        print()  ## print() a blank line

        ## call 'log_e' which is an '_logger' with 'red' configured.
        ## In the call, tell log_e to format/print supplied string and following f-string
        log_e('Error', f'{name} Already Exists')

        print('\tPlease rerun with unique Peer Name')  ## Tell the user to rerun the command.
        exit()  ## exit the program with a 0 which typically means the program succeeded.

    ## call 'log_i' which is an '_logger' with 'green' configured.
    ## In the call, tell log_e to format/print supplied string and following f-string
    log_i('Info', f"Creating Terraform Config File for '{name}'")

    ## Moved mkdir into a try-except block with no finally clause.
    try:
        os.mkdir(name)
    except (OSError, PermissionError, IsADirectoryError) as e:
        log_e(f'Error: Could not directory {name} for Terraform Config file. Error: {e}')
        ## PROGRAMMER QUESTION: Should this instead be given a non-zero return code to indicate CLI failure?
        exit(0)  
     
    ## Create and initialize string 'file' to be a path to the file, such that the directory name and file-name 
    ## are the same, except that the file-name will have a '.tf' suffix appended to it.
    file = os.path.join(name, name + '.tf')

    ## Moved the open and write into a try-except block with no finally clause.
    try:
        with open(file, 'w') as f:
            f.write(tf)
    except (OSError, PermissionError, IsADirectoryError) as e:
        log_e(f'Error: Could not write Terraform Config file: {file}. Error: {e}')
        ## PROGRAMMER QUESTION: Should this instead be given a non-zero return code to indicate CLI failure?
        exit(0)  

    ## call 'log_i' which is an '_logger' with 'green' configured.
    ## In the call, tell log_e to format/print the two supplied strings
    log_i('Info', "Terraform Config File Created")

## define function 'terraform(), to take arguments 'path', and 'secret'.
## Creates a Terraform object.
## Applies plan
def terraform(path, secret):
    '''
    Utilize Terraform to push new Peer Config
    '''
    ## Create 'tf' object from class 'Terraform' initialized with keyword argument 'working_dir' = 'path' .
    tf = Terraform(working_dir=path)

    ## call 'log_i' which is an '_logger' with 'green' configured.
    ## In the call, tell log_e to format/print the two supplied strings
    log_i('Terraform', "Initialize Configuration")
    print()  ## print() blank line.

    tf.init(capture_output=False)  ## tell Terraform to not print standard output or standard error.
    print() ## print blank line.

    log_i('Terraform', "Configuration Initialized")  ## print given message in green

    ## take user input, after printing the message in green
    input('\nPress '+colored("[ENTER]", "green")+' to Continue to Terraform Plan\n')
    log_i('Terraform', "Plan Configuration")  ## print given message in green
    print() ## print blank line.

    ## creates an execution plan, setting 'client_secret' variable to secret.
    tf.plan(capture_output=False, var={'client_secret':secret})

    log_i('Terraform', "Plan Complete")    ## print given message in green

    ## print given message in yellow
    print(colored('\n***Confirm there are no errors on Terraform Plan***\n', 'yellow'))

    ## Create and initialize 'ask' and 'error' strings to send to yes_no_query()
    ask = 'Do you want to continue to Terraform Apply? '
    error = 'Terraform Config has been created but not applied'
    yesno_query(ask, error)  ## Ask the user to Terraform Apply or not.

    log_i('Terraform', "Apply Configuration")  ## print given message in green
    print() ## print blank line.

    ## Apply terraform changes, skipping confirmation approval.  Do not print to stdout stderr
    ## set variable 'client_secret' to 'secret'.
    tf.apply(skip_plan=True, capture_output=False, var={'client_secret':secret})
    print() ## print blank line.

    log_i('Terraform', "Configuration Applied")  ## print given message in green


## define function 'add_info(), to take arguments 'peer', 'id', and 'subnet'.
## - reads peer_info from file, 
## - updates peer info 
## - writes the peer id and subnet info to file peer_list.json
def add_info(peer, id, subnet):
    '''
    Add new Peer to Static Peer List
    '''
    ## in a 'with' context, open file 'peer_list.json' read_only as object 'f':
    with open('peer_list.json', 'r') as f:
        ## Create and initialize dictionary p with returned json formatted structure from json.load of file f.
        p = json.load(f)  

        p[peer] = {'id': id, 'subnet': subnet}  ## set dictionary 'p{}' at peer to the given dictionary, containing id and subnet.

    ## in a 'with' context, open file 'peer_list.json' writable as object 'f':
    with open('peer_list.json', 'w') as f:
        json.dump(p, f)  ## transform dictionary 'p{}' into json formatted text, and write it to file 'f'.

## Define function 'update_permissions() to take argument 'peer'.
## This walks through 'peer' directory tree and sets permissions of everything to '-rwxr--r--'.
def update_permissions(peer):

    os.chmod(peer, 0o774)  ## use os.chmod method to set file permissions of 'peer' to octal 744 '-rwxr--r--'.

    ## call os.walk(peer) to build topdown tree of the directory structure at 'peer'
    ## It returns a tupple with (dirpath, dirnames, filenames)
    ## iterate through the output in sub loops.
    for root, dirs, files in os.walk(peer):
        ## loop through the directory names.
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o774)  ## set permissions to '-rwxr--r--'.
        ## loop through the filenames.
        for f in files:
            os.chmod(os.path.join(root, f), 0o774)  ## set permissions to '-rwxr--r--'.

## Define function 'git()' to take argument name.
## For a repo in the current directory:
## Ask the user all the appropriate questions to know whether or not to:
##     - do: git status
##     - do: git add
##     - do: git status
##     - do: git commit
##     - do: git push
def git(name):
    '''
    Stage New Peer and Peer_List
    Commit/Push Changes to External BitBucket
    '''
    ## Print the given green message, and wait until the user hits [ENTER]
    input('\nPress '+colored("[ENTER]", "green")+' to Continue to update GIT\n')

    ## Create object 'repo' and initialize it with 'Repo' class
    ## with the current directory as an argument to represent the repository path.
    repo = Repo(os.getcwd())  ## repo is an object pointing to a git repository

    ##  The next two commented lines should be removed if they will not be needed again.
    # repo_url = repo.git.remote('-v').split("\t")[1].split(" ")[0]
    # branch = repo.git.status().split("\n")[0].split(" ")[2]

    log_i('GIT', "Pre Status")  ## print given message in green

    ## the next line should be removed if it will not be needed again.
    # print(repo.git.checkout(b='origin/python_creation_peer'))

    print(repo.git.status())  ## Execute 'git.status()' and print the result
    log_i('GIT', 'Staging New Peer')  ## print given message in green

    ## print the output of repo.git.add(name) plus repo.git.add('peer_list.json').
    print(repo.git.add(name)+repo.git.add('peer_list.json'))
    log_i('GIT', "Post Status")  ## print given message in green

    print(repo.git.status())  ## Execute 'git.status()' and print the result

    ## print the given message in yellow asking the user to confirm.
    ## then prepare 'ask' and 'error' to take an answer from the user.
    print(colored('Confirm new Folder and File are ready to be committed', "yellow"))
    ask = '\nDo you want to Commit Changes? '
    error = 'Terraform Config has been applied but version control not updated'
    yesno_query(ask, error)

    log_i('GIT', 'Performing Commit')  ## print given message in green

    ## call git commit on 'name', and print the output.
    print(repo.git.commit(m="Cloud Peer '%s' Add" % name))
    print() ## print a blank line.
    log_i('GIT', 'Pushing to External BitBucket.  Enter Passphrase if needed.')  ## print given message in green

    ## call git push, and print its output.
    print(repo.git.push())

def main():  ## This defines the main() function.

    # Description for Job
    description = 'Create AWS/Azure Peering Utilizing Terrafrom'  ## Create and initialize string 'description'
    # Pull Arguments
    args = Arguments(description)  ## Create object 'args', to obtain and contain parse CLI arguments and options.

    ## reassign the args variable to the output of args.get() which gives this function indirect access
    ## to the 'private by convention' variables that are within the object instance.
    args = args.get()
             
    info = {}  ## Create empty 'info{}' dictionary 

    ## In a try-except block:
    try:
        print(banner)  ## Print the banner that is defined at the top of this program.

        identify(args, info)  ## print peer info, and ask whether or not to proceed.

        create_peer_tf(info) ## Creates a Terraform Config File with peer_name.

        ## Creates a Terraform Config File and Applies plan
        terraform(path   = info['peer_name'],
                secret = info['cloud_secret'])

        ### Updates a Terraform Config File with peer_name and info.
        add_info(peer = info['peer_name'],
                id = info['peer_id'],
                subnet = info['peer_subnet'])

        ## update file permissions of directory tree that was created for peer_name to '-rwxr--r--'.
        update_permissions(info['peer_name'])

        ## call git() to add/commit/push the current directory as the given repo
        git(name = info['peer_name'])

    ## The next line that is commented out looks like a debug message.
    # pprint(info)

    ## If the user causes a Keyboard Interrupt, print a blank line. 
    except KeyboardInterrupt:
        print()


## If the program is executed as a script, the following call to main() will be executed.
## Otherwise, if some other Python program imports this code, then main() will not be executed.
if __name__ == '__main__':
    main()
