# Genotype Imputation Workflow
The workflow is based around the [Michigan Imputation Server](https://imputationserver.sph.umich.edu/start.html#!pages/home) and the [Haplotype Reference Consortium](http://www.haplotype-reference-consortium.org/).
It uses publicly available scripts and tools to ease the preprocessing, uploading and downloading of the imputation results.

## Installation
Required tools:
- [python 3.x](https://www.python.org/)
- [requests](https://docs.python-requests.org/en/latest/)
- [perl](https://www.perl.org/)
- [plink](https://www.cog-genomics.org/plink/)
- [bcftools](https://samtools.github.io/bcftools/howtos/install.html)

All of the requirments can be installed with [conda](https://docs.conda.io/en/latest/).
Missing dependencies/packages can also be installed with [conda](https://docs.conda.io/en/latest/).

## Usage
The starting point for this workflow is a standard VCF file for which you want to impute genotypes. Often this is done in the context of a 
GWAS and genotyping arrays.

### Quality Control and Data Preparation
This part of the workflow is taken from [here](https://imputationserver.readthedocs.io/en/latest/prepare-your-data/). 
I have combined some of the steps to make the preprocessing more straightforward. 

1. Download [Will Rayners toolbox](https://www.well.ox.ac.uk/~wrayner/tools/) to prepare data:
    ```bash
    wget http://www.well.ox.ac.uk/~wrayner/tools/HRC-1000G-check-bim-v4.2.7.zip
    unzip HRC-1000G-check-bim-v4.2.7.zip
    rm HRC-1000G-check-bim-v4.2.7.zip
    ```

2. Download the HRC reference data:
    ```bash
    wget -O - ftp://ngs.sanger.ac.uk/production/hrc/HRC.r1-1/HRC.r1-1.GRCh37.wgs.mac5.sites.tab.gz | gunzip -c > HRC_reference.tab
    ```
3. Modify the `config.yaml` file so that the paths point to the right files.

4. Run `prepare_imputation.sh`. This script will compare your VCF file against the HRC reference and will remove variants that are not found in the reference. 
It will also check if the position and ref/alt assignment is correct and will remove SNPs otherwise. The script will create a seperate coordinate sorted vcf.gz file for each chromosome inside of the directory that you specified in the `config.yaml`
**!!! This script requires ~22 GB of RAM and will take around 15 minutes to finish!!!**

5. Now you can submit the VCF files created in step 4 to the [Michigan Imputation Server](https://imputationserver.sph.umich.edu/start.html#!pages/home). For that you have to [create an account](https://imputationserver.sph.umich.edu/index.html#!pages/register).
Afterwards you can either upload the VCF files manually via the web interface, or use the `submit_michigan_imputation.py` script.
If you chose to use the script, you need to install the __[Imputation Bot](https://imputationserver.readthedocs.io/en/latest/workshops/ASHG2020/Session5/)__.

6. After you download the results (if you use the Imputation Bot this will be done automatically) you can decrypt the files using the password that was sent to you via Email using the `decrypt_files.py` script.
    ```bash
   python decrypt_files.py -p "<password>" -i <directory_with_downloaded_zip_files> -o <output_directory>
   # e.g.
   python decrypt_files.py -p "STe)vMxd4asc3" -i job-20210920-157248-467/local/ -o decrypted_results
   ```
   The resulting directory looks like this:
   ```bash
    .
    ├── decrypted_results
    │ ├── chr_1
    │ │ ├── chr1.dose.vcf.gz
    │ │ └── chr1.info.gz
    │ └── chr_2
    │ │ ├── chr2.dose.vcf.gz
    │ │ └── chr2.info.gz
    │ └── chr_...
    │   ├── chr....dose.vcf.gz
    │   └── chr....info.gz
   ```

7. Optionally you can further filter the VCF file based on the estimated Imputation Accuracy (R-square) using this command:
    ```bash
    for i in {1..22}
    do
    echo ${i}
    bcftools filter -e 'INFO/R2<=0.9' -Oz -o chr${i}.filtered09.vcf.gz chr${i}.dose.vcf.gz
    done 
   ```  
   This will remove all SNPs from all autosomes with an imputation accuracy less than 0.9.
   After merging all autosomes together, e.g. using `bcftools concat`, the generated VCF can be used for further analysis. 