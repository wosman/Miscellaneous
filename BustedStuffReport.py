#Importing required libraries
import urllib2
import logging
import re
import datetime
from xmlrpclib import ServerProxy as Server
import sys

# Functions for printing ASCII-art ticks and crosses into the console

def introprint():
    print " "
    print "###########################################"
    print "#                                         #"
    print "#   Welcome to the Busted Stuff Report!   #"
    print "#     'A robot for Content Managers'      #"
    print "#                 :-D                     #"
    print "#    Let's begin scanning your pages!     #"
    print "#                                         #"
    print "###########################################"
    print " "
    print "Scanning begins!"
    print " "

def tickprint():
    print "\n"
    print "               /       "
    print "              /        "
    print "             /         "
    print "            /          "
    print "    \      /           "
    print "     \    /            "
    print "      \  /             "
    print "       \/              "
    print "\n"

def crossprint():
    print "\n"
    print "     \       /       "
    print "      \     /        "
    print "       \   /         "
    print "        \ /          "
    print "         X           "
    print "        / \          "
    print "       /   \         "
    print "      /     \        "
    print "     /       \       "
    print "\n"

# Checking that all the arguments were entered on the command line, exiting with a message if not.
def checkstart():
    if len(sys.argv) != 5:
        argumentsnotset = 'One or more arguments were not passed. \nUsage is like so: \nPython BustedStuffReport.py http://CONFLUENCESERVERNAME USERNAME PASSWORD CONFLUENCE-SPACENAME'
        print argumentsnotset
        sys.exit(1)	

# Setting up logging format to set log file AND HTML report filename, time stamping ON
checkstart()
logfilename = "BustedStuffLogFile.log"
logging.basicConfig(filename=logfilename,filemode='w',level=logging.INFO,format='%(asctime)s %(message)s')
htmlreportname = "Busted_Stuff_Report.html"
introprint() #prints introduction text in ASCII art square

# Setting up HTML report header and footer
# HTML header content:
header = """
<html>
<head><title>Busted Stuff Report</title></head>
<body>
<h1>Busted Stuff Report</h1>
<i>Compiled on: """

# Setting up timestamp for HTML report
datestamp = datetime.date.today().strftime("%A %d. %B %Y")
timestamp = datetime.datetime.now().strftime("%I:%M%p")

# Writing HTML header to file:
with open(htmlreportname, 'w') as f:
    f.write(header)
    f.write(datestamp)
    f.write(", at ")
    f.write(timestamp)
    f.write(""" UTC</i>""")

# HTML footer content:
footer = """<br><br><b>Ending Busted Stuff testing. 
<br><br>Thanks for using the Busted Stuff Report!</b></body></html>"""

# List of general varables in use
# e is a variable that catches HTTP error codes that come back
response = "A string to catch the HTML data from the URL location"
html = "."
sessionduration = 0
linktesttotal = 0
errorcount = 0

# Setting up the regex strings that will be scanned on each page. 
# These are specific text strings found in Confluence errors, that show up in the source of the page. 
bustedloginregex = re.compile("<title>Log In")
bustedlinkregex = re.compile("error\">&#91;")
createlinkregex = re.compile("createlink")
bustedimageregex = re.compile("Unable to render embedded object")
bustedmacroregex = re.compile("Unknown macro")
bustedmacroregex2 = re.compile("Error rendering macro")
bustedjiraissuesregex = re.compile("error\">jiraissues\:")
bustedincluderegex = re.compile("The page.*does not exist")
bustedincluderegex2 = re.compile("The included page could not be found.")

tuplelist = [(bustedloginregex,' failed login.',' a login error was returned.'), (bustedlinkregex,' broken links.',' a broken internal link was found.'), (createlinkregex,' red create links.',' a red create link was found.'), (bustedimageregex,' broken graphics.',' a broken graphic was found.'), (bustedmacroregex,' uninstalled macros.',' an uninstalled macro reference was found.'), (bustedmacroregex2,' general macro errors.',' a general macro error was found.'), (bustedjiraissuesregex,' JIRA Issues Macro errors.',' a JIRA Issues Macro error was found.'), (bustedincluderegex,' busted excerpt-includes.',' an excerpt-include is busted or hidden from the logged-in user.'), (bustedincluderegex2,' busted page includes.',' an included page is busted or hidden from the logged-in user.')]

# Setting Confluence URL, Space, username and password.
server = sys.argv[1]
conf_user = sys.argv[2]
conf_pwd = sys.argv[3]
conf_space = sys.argv[4]
with open(htmlreportname, 'a') as f:
    f.write("<br><i>Scanning URL:<b> ")
    f.write(server)
    f.write("</b> and SPACE:<b> ")
    f.write(conf_space)
    f.write("</b></i><br>")
    f.write("<br><b>The following stuff is busted.</b> ;-)<br>")

# Access the site via XML-RPC to retrieve the list of all pages in the space (once-off action)
s = Server(server + "/rpc/xmlrpc")
s = s.confluence1
token = s.login(conf_user,conf_pwd)
# this is a "dictionary" (spaceindex)
spaceindex = s.getPages(token, conf_space)
s.logout(token)

def downloadpage(site_address):
    # Conditional block that tries to access the URL and catches HTTP Error codes sent back.
    try: 
        response = urllib2.urlopen(site_address)
        html = response.read()
    #BEGIN HTTP error finder block
    except urllib2.HTTPError, e:
    # e.code is just the numerical HTTP error code from the server. i.e. 404
        print "Error", e.code, "was detected."
	crossprint()
	with open(htmlreportname, 'a') as f:
	    f.write('For page:')
	    f.write('<a href=\"')
	    f.write(site_address)
	    f.write('\" </a>')
            f.write("Error", e.code, "was detected.")
        errorcode = e.code
        errorloggystring = 'Error', errorcode, 'from', 
        logging.info(errorloggystring)
        errorcount = errorcount + 1
    # e.read is the HTML source of the 404 page. Line below prints that to console.
        print e.read() 
    #END HTTP error finder block
    return html

def regexfunction(html, coolregex, testname, errormessage, site_address):
    # Search for Busted Stuff (error codes in page sources)
    print "Testing for%s" %testname
    errormatch = coolregex.search(html)
    if errormatch: # This shows a list of the characters that matched.
        print 'Error found: ', errormatch.group()
        errorloggystring = 'Error: ', errormatch.group(), 'found.'
        logging.info(errorloggystring)
	with open(htmlreportname, 'a') as f:
	    f.write("<br>For page: ") 
	    f.write("<a href=\"")
	    f.write(site_address)
	    f.write('\">')
	    f.write(site_address)
	    f.write('</a>')
            f.write('%s' %errormessage)
	crossprint()
	return False
    else:
        errorloggystring = 'Passed.'
	print errorloggystring
        logging.info(errorloggystring)
	tickprint()
	return True

# MAIN PROGRAM LOOP

# Loop to print every url in the spaceindex
for page_summary in spaceindex:
    site_address = page_summary['url']
    #Putting in an initial log entry to show that we're trying the given URL.
    initloggystring = "Accessing", site_address
    logging.info(initloggystring)
    print "Accessing", site_address
    linktesttotal += 1
    html = downloadpage(site_address)
    for coolregex, testname, errormessage in tuplelist:
        if not regexfunction(html, coolregex, testname, errormessage, site_address):
		errorcount += 1
    # WINDUP FUNCTION 
    # This records the outcome of the ping to the log, if it seemed successful.
    if html == ".": winduploggystring = "Page content was not retrieved for", site_address
    if html != ".": winduploggystring = "Actions completed on", site_address  
    logging.info(winduploggystring)
    print "Actions completed on", site_address
    html = "."

# (endFOR MAIN PROGRAM)


# This sends summary information to the console and seals off entries in the log file.

print " "
print "Ending Busted Stuff testing. Thanks for using the Busted Stuff Report!\n"
scansummary = linktesttotal, "link(s) were tested.", errorcount, "error(s) were found."
print linktesttotal, "link(s) were tested.", errorcount, "error(s) were found."
print "Busted Stuff was recorded in the HTML report:", htmlreportname
print "And in the logfile:", logfilename
summarytotal = (linktesttotal, "link(s) were tested.", errorcount, "error(s) were found.")

with open(htmlreportname, 'a') as f:
    f.write("<br><i>If there's no links above, then no errors were found! See the .log file for a detailed record of the scan.</i>")
    f.write(footer)