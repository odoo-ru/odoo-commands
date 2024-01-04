set -e

mkdir -p .cache
cd .cache

odoo_versions=(
11.0.20201201
12.0.20211011
13.0.20230607
)
for odoo_version in ${odoo_versions[@]}
do
    odoo_major_version=${odoo_version:0:4}
    odoo_file_name=odoo_$odoo_version.zip
    echo $odoo_file_name
    if [ ! -f $odoo_file_name ]; then
        wget --no-clobber https://nightly.odoo.com/$odoo_major_version/nightly/src/$odoo_file_name
        unzip $odoo_file_name
    fi
done
