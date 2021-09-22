### AFTER RUNNING `submit_michigan_imputation.py` YOU CAN USE THIS SCRIPT TO DECRYPT ALL IMPUTED VCF FILES
###

import subprocess
import argparse
import os
import re

def cmdline_args():
    # Make parser object
    p = argparse.ArgumentParser()

    p.add_argument("-p", "--password", type=str, required=True,
                   help="Password to decrypt the vcf files. It should have been sent to the email you used to sign up for the michigan imputation server.")

    p.add_argument("-i", "--input", type=str, required=True,
                   help="Path to the directory with the encrpyted files. Probability something like: job-20210920-063234-183/local/")
    p.add_argument("-o", "--output", type=str, required=True,
                   help="Path to the directory where the decrypted files should be."
                        "Insde that directory there will be one directory per chromosome.")

    return (p.parse_args())


if __name__ == '__main__':
    args = cmdline_args()
    password = args.password
    in_dir = args.input
    out = args.output
    if not os.path.isdir(out):
        os.makedirs(out)

    files = os.listdir(in_dir)
    for file in files:
        name = re.sub("\.zip", "", file)
        in_path = os.path.join(in_dir, file)
        out_path = os.path.join(out, name)

        if not os.path.isdir(out_path):
            os.makedirs(out_path)

        subprocess.run(fr"unzip -P '{password}' -d {out_path} {in_path} ", shell=True)
