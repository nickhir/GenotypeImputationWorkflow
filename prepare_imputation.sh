#!/bin/sh
set -e

# Script to perform data preperation for michigan imputation server, based on this: https://imputationserver.readthedocs.io/en/latest/prepare-your-data/
# REQUIRES ~22GB of RAM

# include parse_yaml function
. parse_yaml.sh

# read yaml file
eval $(parse_yaml config.yaml "config_")

# access yaml content
in_vcf=$config_config_input_vcf_file
output_dir=$config_config_output_directory_preprocesing
HRC_reference_panel=$config_config_HRC_reference
HRC_1000G_check_script=$config_config_HRC_1000G_check_script
plink_exe=$config_config_plink_exe
plink_dir=$config_config_plink_dir
bcftools_exe=$config_config_bcftools_exe

# make directory if it doesnt exist already
if [[ ! -e "${output_dir}" ]]; then
    mkdir -p "${output_dir}"
fi

# VCF TO PLINK. GENERATE UNIQUE MISSING IDS
${plink_exe} --double-id --set-missing-var-ids @:#[b37]\$1,\$2 --make-bed --out tmp_plink --vcf ${in_vcf}

# CREATE FREQUENCY TABLE
${plink_exe} --freq --bfile tmp_plink --out tmp_plink

# RUN THE COMPARISON SCRIPT
perl ${HRC_1000G_check_script} -b tmp_plink.bim -f tmp_plink.frq -r ${HRC_reference_panel} -h -n 
PATH=$PATH:$plink_dir
# THE COMPARISON SCRIPT CREATS A BASH FILE TO FIX THE PROBLEMS.
# THE BASH FILE ASSUMES THAT PLINK IS IN YOUR PATH. MAKE SURE IT IS:
bash Run-plink.sh
for i in {1..22}
do
echo ${i}
${plink_exe} --bfile tmp_plink-updated-chr${i} --recode vcf --out ${output_dir}/chr${i}
${bcftools_exe} sort ${output_dir}/chr${i}.vcf -Oz -o ${output_dir}/chr${i}.vcf.gz
done

rm *tmp*
rm Run-plink.sh
rm ${output_dir}/chr*vcf ${output_dir}/chr*log ${output_dir}/chr*nosex