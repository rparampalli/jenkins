# jenkins
Jenkins related scritps and notes

Jenkins backup Script

Jenkins cleanup scripts that work in Python 2.7 and Python 3

# Groovy script to kill hung build jobs
```
def build = Jenkins.instance.getItemByFullName("jobName").getBuildByNumber(jobNumber)
build.doStop()
build.doKill()
```
