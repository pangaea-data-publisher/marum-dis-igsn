import logging
import pathlib

import xmltodict
from json2html import *
import os
import json
from glob import glob
import xml.etree.cElementTree as ET
import datetime

class Translate:
    #ns = {"igsn": "http://igsn.org/schema/kernel-v.1.0", "gesep": "http://www.gesep.org/coreMetadata"}
    def __init__(self, domain, xmldir, htmldir):
        self.domain = domain
        self.xml_dir = xmldir
        self.html_dir = htmldir
        self.sitemap = []
        self.root_folder = None
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.root_folder = os.path.basename(self.root_path)
        self.logger = logging.getLogger(self.__class__.__name__)

    def parseXMLs(self):
        xmlfiles_dir = os.path.join(self.root_path, self.xml_dir)
        xmlfiles = [y for x in os.walk(xmlfiles_dir) for y in glob(os.path.join(x[0], '*.xml'))]
        for xmlfile in xmlfiles:
            json_dict = None
            jsonld = None
            with open(xmlfile) as fd:
                json_raw = xmltodict.parse(fd.read())
                json_raw = json.loads(json.dumps(json_raw))
                if 'cores' in xmlfile:
                    resource_type =' http://vocabulary.odm2.org/specimentype/core'
                    pass
                    #json_dict, jsonld = self.convert_core_hole(json_raw) # TODO jsonld
                elif 'samples' in xmlfile:
                    resource_type ='http://pid.geoscience.gov.au/def/voc/ga/sampletype/borehole_specimen'
                    json_dict, jsonld = self.convert_sample_section(resource_type,json_raw)
                elif 'sections' in xmlfile:
                    resource_type = 'http://vocabulary.odm2.org/specimentype/coreSection'
                    json_dict, jsonld = self.convert_sample_section(resource_type,json_raw)
                else: # TODO site?
                    pass

            if json_dict and jsonld:
                # TODO generate and write html file and then append the path to the sitemap list (include server:port)
                html = self.generate_html(json_dict, jsonld)
                html_file_path = xmlfile.replace(self.xml_dir, self.html_dir)
                html_file_path = html_file_path.replace('.xml', '.html')

                sub_folder = os.path.dirname(html_file_path)
                if not os.path.exists(sub_folder):
                    os.makedirs(sub_folder)
                    self.logger.debug('Creating html files sub-dir - {}'.format(sub_folder))
                with open(html_file_path, "w") as file:
                    file.write(str(html))
                    sitemap_path = os.path.relpath(html_file_path)
                    self.sitemap.append(sitemap_path) #pages\357\samples\357_70_C_1_1_5030293.html

        self.logger.info('Total html files generated - {}'.format(len(self.sitemap)))

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

    def convert_sample_section(self, resource_type, raw):
        jsonld = {}
        sample = raw.get('sample')
        context_igsn_main = "https://raw.githubusercontent.com/IGSN/igsn-json/master/schema.igsn.org/json/registration/v0.1/context.jsonld"
        jsonld["@context"] = context_igsn_main
        jsonld["@id"] = sample.get('dislink')
        jsonld["additionalType"] = resource_type
        jsonld["igsn"] = 'http://hdl.handle.net/'+sample.get('sampleNumber').get('#text')
        jsonld["registrant"] = {"name": sample.get('registrant').get('registrantName')}

        related = []
        rel_identifiers = sample.get('relatedResourceIdentifiers').get('relatedIdentifier')
        if isinstance(rel_identifiers, dict): # only one relation exists, so convert into a list
            # example {'@relatedIdentifierType': 'handle', '@relationType': 'IsPartOf', '#text': '10273/IBCR0357ESJ0001'}
            rel_identifiers = [rel_identifiers]
        for r in rel_identifiers:
            iden = r.get('#text')
            identype = r.get('@relationType')
            relation = r.get('@relatedIdentifierType')
            related.append({"identifier": {"id": iden, "kind": relation}, "relationship": identype})
        jsonld["related"] = related

        ele = sample.get('log').get('logElement')
        logtype = ele.get('@event')
        timestamp = ele.get('@timeStamp')
        comment = ele.get('@comment')
        jsonld["log"] = {"type": logtype, "timestamp": timestamp, "comment": comment}
        return sample, jsonld

    def generate_html(self, json_dict, jsonld):
        js = '<script type="application/ld+json">{}</script>'.format(json.dumps(jsonld))
        html_sub = json2html.convert(json=json_dict)
        html_1 = '<html><head>' + js + '</head>'
        html_2 = '<body>' + html_sub + '</body></html>'
        html = html_1 + html_2
        return html

    def generate_sitemap(self):
        root = ET.Element('urlset')
        #root.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        #root.attrib['xsi:schemaLocation'] = "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
        root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
        for site in self.sitemap:
            site_root = site.replace('\\', '/')
            dt = datetime.datetime.now().strftime("%Y-%m-%d")
            doc = ET.SubElement(root, "url")
            html_page_url ='{}{}/{}'.format(self.domain, self.root_folder, site_root)
            ET.SubElement(doc, "loc").text = html_page_url
            ET.SubElement(doc, "lastmod").text = dt
            #ET.SubElement(doc, "changefreq").text = "weekly"
            #ET.SubElement(doc, "priority").text = "1.0"
        tree = ET.ElementTree(root)
        tree.write('sitemap.xml', encoding='utf-8', xml_declaration=True)