#!/usr/bin/env python3

import base64
import sys
import requests
import urllib3
import os

urllib3.disable_warnings()

def auth_headers(username, password):
    #return 'Basic ' + base64.encodestring('%s:%s' % (username, password))[:-1]
    st = '%s:%s' % (username, password)
    return 'Basic ' + base64.b64encode(st.encode()).decode("utf-8")


usernameAndApiToken = "<Your Jenkins API token>"
userName = "<your username>"

# ciURL = sys.argv[1]
ciURL = os.environ['JENKINS_URL']+"/"
keepbuilds = 6
data = {'json': '%7B%7D', 'Submit': "Yes", }
headers = {'Authorization': auth_headers(userName, usernameAndApiToken)}


def getCIDetails(CIURL):
    r = requests.get(url=CIURL, headers=headers, verify=False)
    jobList = r.json()
    return jobList


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
    r = requests.post(url=JenkinsEndPoint, data=data, headers=headers, verify=False)
    responseCode = r
    print(JenkinsEndPoint+" ==> Delete response Code:" + str(responseCode))


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
