set -e

mkdir -p .cache
cd .cache

odoo_versions=(
15.0.20240701
16.0.20240701
17.0.20240701
)
for odoo_version in ${odoo_versions[@]}
do
    odoo_major_version=${odoo_version:0:4}
    odoo_file_name=odoo_$odoo_version.zip
    if [ ! -f $odoo_file_name ]; then
        echo "Download $odoo_file_name"
        wget --no-clobber https://nightly.odoo.com/$odoo_major_version/nightly/src/$odoo_file_name
        unzip $odoo_file_name
    fi
done
