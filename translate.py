import xmltodict
from json2html import *
import os
import json
from glob import glob

class Translate:
    #ns = {"igsn": "http://igsn.org/schema/kernel-v.1.0", "gesep": "http://www.gesep.org/coreMetadata"}
    def __init__(self, xmldir, htmldir):
        self.xml_dir = xmldir
        self.html_dir = htmldir
        self.sitemap = []

    def parseXMLs(self):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        xmlfiles_dir = os.path.join(root_dir, self.xml_dir)
        xmlfiles = [y for x in os.walk(xmlfiles_dir) for y in glob(os.path.join(x[0], '*.xml'))]
        for xmlfile in xmlfiles:
            json_dict = None
            jsonld = None
            with open(xmlfile) as fd:
                json_raw = xmltodict.parse(fd.read())
                json_raw = json.loads(json.dumps(json_raw))
                if 'cores' in xmlfile:
                    json_dict, jsonld = self.convert_core_hole(json_raw)
                elif 'samples' in xmlfile:
                    json_dict, jsonld = self.convert_sample(json_raw)
                elif 'sections' in xmlfile:
                    json_dict, jsonld = self.convert_section(json_raw)
                else: # TODO site?
                    pass

            # TODO generate and write html file and then append the path to the sitemap list
            html = self.generate_html(json_dict, jsonld)
            html_path = xmlfile.replace(self.xml_dir, self.html_dir)
            #with open(html_path, "w") as file:
                #file.write(str(html))
            #self.sitemap.append(html_path)

    def convert_core_hole(self, raw):
        jsondict = None
        jsonld = None
        core = raw.get('core')
        #context = core.get('@xmlns')
        core_id = core.get('@ID')
        coreDetails = core.get('coreDetails')
        hole = core.get('hole')
        hole_id = hole.get('@ID')

        return jsondict, jsonld

    def convert_sample(self, raw):
        jsondict = None
        jsonld = None
        core = raw.get('sample')

        return jsondict, jsonld

    def convert_section(self, raw):
        jsondict = None
        jsonld = None
        section = raw.get('sample')

        return jsondict, jsonld

    def generate_html(self, json_dict, jsonld):
        js = '<script type="application/ld+json">{}</script>'.format(jsonld)
        html_sub = json2html.convert(json=json_dict,
                                     table_attributes="id=\"igsn-table\" class=\"table table-bordered table-hover\"")
        html_1 = '<html><head>' + js + '</head>'
        html_2 = '<body>' + html_sub + '</body></html>'
        html = html_1 + html_2
        return html

    def generate_sitemap(self):
        return None