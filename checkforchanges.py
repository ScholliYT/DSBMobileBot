import subprocess
import os
import json
import collections
import unicodedata
import shutil

def recursively_default_dict():
    return collections.defaultdict(recursively_default_dict)

pwd = os.getcwd()
new_file = "json/new_data.json"
f = open(new_file, "w") #create new temp file
f.close()
bashCommand = "docker run --name dsbmobile-data-scraper --rm -it -v " + pwd +"/"+new_file+":/app/json/groupedtables.json dsbmobile-data-scraper"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print(output)

print("\nchekcing for changes in data\n")

with open(new_file) as f_new:
    data_new = json.load(f_new)

with open("json/groupedtables.json") as f_old:
    data_old = json.load(f_old)


newdata = recursively_default_dict()
for day in data_new:
    if day in data_old:
        print("found day in old: " + day)
        for classname in data_new[day]:
            if classname in data_old[day]:
                for sub in data_new[day][classname]:
                    if not sub in data_old[day][classname]: # substitucion is not in old data
                        if classname in newdata[day]:
                            newdata[day][classname].append(sub)
                        else:
                            newdata[day][classname] = [sub]
            else:
                newdata[day][classname] = data_new[day][classname]
    else:
        print("new day: " + day)
        newdata[day] = data_new[day]
print("changes:")
print(newdata)

print("saving changes to file")
# export as utf-8 encoded json file
with open("json/changes.json", "w", encoding='utf8') as outfile:
    json.dump(newdata, outfile, indent = 4, ensure_ascii=False)

print("overwriting groupedtables.json with current data")
os.rename(new_file, "json/groupedtables.json")
