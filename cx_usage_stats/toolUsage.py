import getpass
import json
import platform
import socket
import sys
import requests
import time

# Disable urllib3 warning when https is used with self-signed certificate
requests.packages.urllib3.disable_warnings()

# Default settings
http_timeout = 2

def my_ip():
    """
    Function that finds local IPv4 address
    
    Parameters: None
    Returns: Local IPv4 address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.0.0.8', 1027))
    except socket.error:
        return None
    return s.getsockname()[0]

def my_ipv6():
    """
    Function that finds local IPv6 address
    
    Parameters: None
    Returns: Local IPv6 address
    """
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect(('2001:db8::', 1027))
    except socket.error:
        return None
    return s.getsockname()[0]

def my_timezone():
    """
    Function that finds local timezone
    
    Parameters: None
    Returns: Returns local timezone as a string formatted as UTC, UTC-1.0, or UCT+2.0
    """

    if time.daylight:
        offset = 0-(time.altzone / 3600.0)
    else:
        offset = 0-(time.timezone / 3600.0)

    if offset > 0:
        timezone = "UTC+" + str(offset)
    elif offset == 0:
        timezone = "UTC"
    elif offset < 0:
        timezone = "UTC-" + str(offset)
    return timezone

def anonymous_string(string, retainCharacterCount):
    """
    Function anonymouses the input string by only retaining the first and last
    characters in the string. All other characters are replaced with a .
    The number of characters that are retained are specified as a input variable.
    
    Parameters:
    string - input string that are to be anonymoused
    retainCharacterCount - number of characters that are retained in the beginning and end of string

    Returns: Anonymoused string
    """
    stringLength = len(string)
    stringStart = string[:retainCharacterCount]
    stringEnd = string[(stringLength-retainCharacterCount):]
    stringMiddle = ""
    for _ in range(0,stringLength-(2*retainCharacterCount)):
        stringMiddle = stringMiddle + "."
    newString = stringStart + stringMiddle + stringEnd
    return newString

def submit_usage_data(tool_name, url="NaN", usage_information = {}, statistic_information = {}):
    """
    Function that submits usage information to the URL provided as input.

    The following information are captured before submission:
    - Script Name (input variable)
    - Timestamp
    - Local timezone
    - Execution mode
    - Local IPv4 and IPv6 address
    - Local hostname (anonymoused)
    - Username (anonymoused)
    - Commandline arguments during script execution
    - Python version
    - Operating System Type (macOS, Linux, Windows, etc.)
    - Operating System Version
    
    Parameters:
    tool_name - string containing tool name
    url - url which the usage data should be posted to
    usage_information - dictionary to report various usage information
    statistic_information - dictionary to report various statistical information

    Returns:
    Dictionary with usage data. The key "upload_status" will indicate whether the usage
    where successfully submitted
    """
    # Gather usage data 
    usageData = {}
    usageData["scriptName"] = tool_name
    usageData["timeStamp"] = int(time.time())
    usageData["timezone"] = my_timezone()
    usageData["ipAddr"] = my_ip()
    usageData["ip6Addr"] = my_ipv6()
    usageData["hostname"] = anonymous_string(platform.node(), 3)
    usageData["username"] = anonymous_string(getpass.getuser(), 2)
    usageData["commandLine"] = sys.argv
    usageData["pythonVersion"] = platform.python_version()
    usageData["operatingSystem"] = platform.system()
    if usageData["operatingSystem"] == "Darwin":
        usageData["operatingSystemVersion"] = platform.mac_ver()[0]
    elif usageData["operatingSystem"] == "Linux":
        try:
            usageData["operatingSystemVersion"] = "%s (%s)" % (platform.linux_distribution()[0], platform.linux_distribution()[1])
        except AttributeError:
            usageData["operatingSystemVersion"] = "NaN"
    else:
        usageData["operatingSystemVersion"] = "NaN"
    usageData["usage"] = usage_information
    usageData["statistics"] = statistic_information

    # Print information
    #print(json.dumps(usageData))

    # Submit usage data
    if url == "NaN":
        usageData["upload_status"] = "Skipped, no URL provided"
    else:
        try:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            payload = json.dumps(usageData)
            http_post = requests.post(url, data=payload, headers=headers, verify=False, timeout=http_timeout)
            if http_post.status_code != 200:
                usageData["upload_status"] = "Error, HTTP return-code %s" % http_post.status_code
            else:
                usageData["upload_status"] = "Success"
        except requests.exceptions.Timeout:
            usageData["upload_status"] = "Error, HTTP timeout"
        except requests.exceptions.ConnectionError:
            usageData["upload_status"] = "Error, HTTP connection error"

    return(usageData)
