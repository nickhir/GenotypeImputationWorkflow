### THIS SCRIPT USES THE IMPUTATIONBOT TO SUBMIT OUR IMPUTATION JOB TO THE SERVER AND DOWNLOAD THE RESULTS.
### BEFORE YOU CAN RUN THIS SCRIPT, YOU HAVE TO PROPERLY SET UP THE IMPUTATION BOT, WHICH IS SHOWN HERE:
### https://imputationserver.readthedocs.io/en/latest/workshops/ASHG2020/Session5/

import subprocess
import os
import requests
import json
import time
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


# imputation server url
url = 'https://imputationserver.sph.umich.edu/api/v2'
token = config["config"]["token"]
# There should only be vcf files in that directory.
vcf_dir = config["config"]["output_directory_preprocesing"]
vcfs = listdir_fullpath(vcf_dir)

imputation_bot_exe = config["config"]["imputation_bot_exe"]

# add token to header (see Authentication)
headers = {'X-Auth-Token': token}

data = {
    'refpanel': 'hrc-r1.1',
    'population': 'eur',
    "mode": "imputation",
    "phasing": "eagle",
    "build": config["config"]["genome_build"],
    "r2Filter": config["config"]["r2Filter"]
}

# submit new job
# open the files
files = [("files", open(i, "rb")) for i in vcfs[3:5]]
print("Submitting Job")
r = requests.post(url + "/jobs/submit/minimac4", files=files, data=data, headers=headers)

if r.status_code != 200:
    print(r.json()['message'])
    raise Exception('POST /jobs/submit/minimac4 {}'.format(r.status_code))

# print message
job_id = (r.json()['id'])
print(f"Job was sucessfully submitted with id: {job_id}")

while True:
    # monitor the job status, as soon as it starts running execute the download command.
    r = requests.get(f"{url}/jobs/{job_id}", headers=headers)

    if r.status_code != 200:
        print(r.json()["message"])
        print("Continuing")
        continue

    # r -> True -> job is running
    # r -> False -> job is not running yet
    if r:
        print("Job started running. Downloading it as soon as it finishes")
        subprocess.run(f"{imputation_bot_exe} download {job_id}", shell=True)
        print(
            f"Encrypted zip files are located in {job_id} directory. The password necessary to decrypt the file was sent to the email you registered with")

        exit()
    else:
        subprocess.run(f"{imputation_bot_exe} jobs", shell=True)
        print("Job is still in the queuing.")
        time.sleep(45)
