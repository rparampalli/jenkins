#!/usr/bin/env python

#Works on python 2.7 only
import base64
import json
import urllib
from urlparse import urlparse
import os
import httplib
import ssl


def auth_headers(username, password):
    #return 'Basic ' + base64.encodestring('%s:%s' % (username, password))[:-1]
    st = '%s:%s' % (username, password)
    return 'Basic ' + base64.b64encode(st)


usernameAndApiToken = "<Jenkins API Token for the username>"
userName = "<jenkins username>"
keepbuilds = 6

ciURL = os.environ['JENKINS_URL']+"/"
data = {'json': '%7B%7D', 'Submit': "Yes", }
headers = {'Authorization': auth_headers(userName, usernameAndApiToken),
           'content-type': 'application/x-www-form-urlencoded',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}


def getCIDetails(CIURL):
    #r = requests.get(url=CIURL, headers=headers, verify=False)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    conn = httplib.HTTPSConnection(urlparse(CIURL).netloc, context=ctx)
    conn.request("GET", urlparse(CIURL).path,"", headers)
    resp = conn.getresponse()
    joblist = json.loads(resp.read())
    return joblist


def checkBuildCount(jobURL, numJobsToKeep):
    bNumber = set()
    ciBuildsJson = getCIDetails(jobURL+"api/json")
    for y in ciBuildsJson['builds']:
        bNumber.add(y.get('number'))

    if len(bNumber) > numJobsToKeep:
        bDeleteCount = len(bNumber) - numJobsToKeep
        bDeleteCounter = 0
        for buildNumber in sorted(bNumber):
            print("Number of builds to Delete "+str(bDeleteCount) + " Total builds count "+str(len(bNumber)) +
                  " Total builds to keep " + str(numJobsToKeep)+" Build URL to delete " + jobURL+str(buildNumber))
            bDeleteCounter = bDeleteCounter+1
            deleteBuilds(jobURL, buildNumber)
            if bDeleteCounter == bDeleteCount:
                print ("Done Deleting builds " + jobURL +
                       " " + str(bDeleteCounter)+" builds")
                break
    else:
        print("Nothing to delete "+jobURL+" Build count is " +
              str(len(bNumber)) + " and keep count is "+str(numJobsToKeep))


def deleteBuilds(jobURL, buiNumber):
    data = {'json': '%7B%7D', 'Submit': "Yes", }
    headers = {'Authorization': auth_headers(userName, usernameAndApiToken)}
    CommandToExecute = "/doDelete"
    JenkinsEndPoint = jobURL+str(buiNumber)+CommandToExecute
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
   
    conn = httplib.HTTPSConnection(urlparse(JenkinsEndPoint).netloc, context=ctx)
    conn.request("POST", urlparse(JenkinsEndPoint).path, urllib.urlencode(data), headers)
    resp = conn.getresponse()
    responsecode = resp.status
    print(JenkinsEndPoint+" ==> Delete response Code:" + str(responsecode))


if __name__ == '__main__':
    ciJOBS = getCIDetails(ciURL+"api/json")
    for target_list in ciJOBS["jobs"]:
        if "udson.maven.MavenModuleSet" in target_list.get("_class") or "hudson.model.FreeStyleProject" in target_list.get("_class") or "org.jenkinsci.plugins.workflow.job.WorkflowJob" in target_list.get("_class"):
            checkBuildCount(target_list.get("url"), keepbuilds)
        if "jenkins.branch.OrganizationFolder" in target_list.get("_class"):
            # print(target_list.get("url"))
            secLayerJobs = getCIDetails(target_list.get("url")+"api/json")
            for tsecond_target_list in secLayerJobs["jobs"]:
                # print("======>"+tsecond_target_list.get("url"))
                thLayerJobs = getCIDetails(
                    tsecond_target_list.get("url")+"api/json")
                for target_list3 in thLayerJobs["jobs"]:
                    # print("=====> "+target_list3.get("url"))
                    checkBuildCount(target_list3.get("url"), keepbuilds)
