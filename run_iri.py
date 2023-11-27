import os
from ppgnss import gnss_time
bin = "./iri"
IRI_SRC_DIR = "../IRI-2020"
out_dir = "../IRI-2020/out"
year = 2016
bat_filename = os.path.join(IRI_SRC_DIR, "run_iri_bat_addon_%4d.sh"%year)
lines = list()
days = gnss_time.total_days(year)
for doy in range(1, days+1):
    for hour in range(0, 24):
        cmd = "%s %04d %2d %02d\n" % (bin, year, doy, hour)
        outfile = "IRI_%04d_%03d_%02d.TAB" %(year, doy, hour)
        # print(os.path.join(out_dir, outfile))
        # break
        if os.path.isfile(os.path.join(out_dir, outfile)):
            # print(cmd)
            continue
        else:
            print(os.path.join(out_dir, outfile))
            print(cmd)
            pass
        lines.append(cmd)
    # break

with open(bat_filename, "w") as fwrite:
    pass
    fwrite.writelines(lines)