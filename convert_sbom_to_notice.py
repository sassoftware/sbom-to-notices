import json
import sys
import os

license_texts = {}
exclusions = []
additions = {}
overrides = {}

def get_license(spdx):
    if spdx in license_texts:
        return license_texts[spdx]
    try:
        text = open('custom-license-data/%s.html'%spdx).read()
        license_texts[spdx] = text
        return text
    except:
        pass
    try:
        text = open('license-list-data/html/%s.html'%spdx).read()
        license_texts[spdx] = text
        return text
    except:
        return "<p>The licenses for the above packages could not be found.</p>"



def read_bom(filename):
    data = json.loads(open(filename, 'r').read())
    return data["components"]


def get_component_licenses(components, override):
    results = {}

    # Load the override file into three data structures depending on the action.
    if override:
        for l in open(override).readlines():
            a,b,c,d = l.strip().split(',', 3)
            if b == 'hide':
                exclusions.append(a)
            elif b == 'add':
                additions[a] = (b,c,d.strip('"'))
            else:
                overrides[a] = (b,c,d.strip('"'))

    # Iterate over all components in sbom.
    for component in components:
        name = component['name']
        version = component['version']
        license = "Missing"
        extra = ""
        if name in overrides:
            license = overrides[name][1]
            extra = overrides[name][2]
        elif name in additions:
            license = additions[name][1]
            extra = additions[name][2]
            additions[name] = "done",additions[name][1], additions[name][2] #mark addition as replaced
        elif "licenses" in component and component['licenses']:
            license = ""
            if "expression" in component['licenses'][0]:
                license = component['licenses'][0]['expression']
            else:
                for sublicense in component['licenses']:
                    license += " AND "
                    if 'id' in sublicense['license']:
                        license += sublicense['license']['id']
                    elif 'name' in sublicense['license']:
                        license += sublicense['license']['name']
                license = license[5:]

        results[(name, version)] = license, extra
    
    # For any 'add' items that didn't show up, add them now.
    for component in additions:
        if additions[component][0] != 'done':
           results[(component,None)] = additions[component][1], additions[component][2]

    return results


def html_output(results, title):
    unique_licenses = {}

    output = "<html><head>"
    output += """
<style>
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
</style>
"""
    output += "</head><body>"
    output += "<h1>Third Party Licenses and Information</h1>"
    output += "<p>This page contains information regarding any third party code included with your software, including applicable third party software notices and/or additional terms and conditions.</p>"
    output += "<h2>%s</h2>"%title
    output += "<table ><tr><th>Name</th><th>License</th><th>Additional Information</th></tr>"
    #output += "<table ><tr><th>Name</th><th>Version</th><th>License</th></tr>"
    for name, version in sorted(component_licenses.keys()):
        exclude = False
        for ex in exclusions:
            if ex in name:
                exclude= True
        if exclude:
              continue
        license, extra = component_licenses[(name, version)]
        if " AND " or " OR " in license:
            _license = license.replace(" AND ", " _ ").replace(" OR ", " _ ").replace("(","").replace(")","")
            for l in _license.split(" _ "):
                if l not in unique_licenses:
                    unique_licenses[l] = []
                if name not in unique_licenses[l]:
                    unique_licenses[l].append(name)
                #unique_licenses[l].append("%s:%s"%(name, version))
        else:
            if license not in unique_licenses:
                unique_licenses[license] = []
            if name not in unique_licenses[license]:
                unique_licenses[license].append(name)
            #unique_licenses[license].append("%s:%s"%(name, version))
        output += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(name, license, extra)
        #output += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(name, version, license)
    output += "</table>"
    for l in sorted(unique_licenses.keys()):
        output += "<hr /><div><h2>%s</h2><ul>"%l
        for item in sorted(unique_licenses[l]):
            output += "<li>%s</li>"%item
        output += "</ul>%s</div>"%get_license(l)
    output += "</body></html>"

    return output



if __name__ == "__main__":
    if not os.path.isdir('license-list-data'):
        print("Didn't find license-list-data. Use `git clone https://github.com/spdx/license-list-data` to download.")
        sys.exit(1)

    filename = sys.argv[1]
    override = None
    if len(sys.argv) > 1:
        override = sys.argv[2]
    components = read_bom(filename)
    component_licenses = get_component_licenses(components, override)
    out = open(filename+".html", 'w')
    out.write(html_output(component_licenses, filename))
