import os
import xml.etree.cElementTree as ET
from xml.dom import minidom
import requests


class Input:

    # Takes a xml file that was created from a test station and a maintainable station key.
    # Once the xml file gets validated by maintainable --
    # it will get unpacked and displayed in the standard format on the maintainable site
    @staticmethod
    def insert(station, local_filename):
        # functional relay example:'a85bb732'
        # Station Example: 'a2bc48c7'
        # file example: 'C:/Users/mgrischy/Desktop/test.xml'

        with open(local_filename, "rb") as f:
            remote_filename = os.path.basename(local_filename)
            file_type = "text/xml"

            response = requests.post('https://secure.maintainabletest.com/api/v1/uploads.xml',
                                     headers={'X-Maintainable-Relay-Key': 'a85bb732'},
                                     data={'station[api_key]': station},
                                     files={'upload[uploaded_file]': (remote_filename, f, file_type)}
                                     )
            assert (response.status_code == requests.codes.created), response


class Etree(object):

    # Creates the basic structure and xml file
    # create_root_summary is the only method that is needed to create a Maintainable upload
    # A Maintainable upload can not be made without create_root_summary
    # This should only be called once
    # Duplicates can not be uploaded
    @staticmethod
    def create_root_summary(part_number, serial_number, operation, status, started_at, ended_at):
        root = ET.Element("test_report")
        uuts = ET.SubElement(root, "uuts")
        uut = ET.SubElement(uuts, "uut")

        summary = ET.SubElement(uut, "summary")
        ET.SubElement(summary, "part_number").text = part_number
        ET.SubElement(summary, "serial_number").text = serial_number
        ET.SubElement(summary, "status").text = status
        ET.SubElement(summary, "started_at").text = started_at
        ET.SubElement(summary, "ended_at").text = ended_at
        ET.SubElement(summary, "operation").text = operation

        tree = ET.ElementTree(root)
        tree.write("items2.xml")

    # I don't think we will need this method
    @staticmethod
    def test(name, status):
        tree = ET.parse("items2.xml")
        root2 = tree.getroot()

        for u in root2.iter('uut'):
            uut = u
        tests = ET.SubElement(uut, 'tests')
        test = ET.SubElement(tests, 'test')
        ET.SubElement(test, "name").text = name
        ET.SubElement(test, "status").text = status

        tree2 = ET.ElementTree(root2)
        tree2.write("items2.xml")

    # The measurements method will take an object instead of individual variables
    # This is done so a test station can input multiple or nested measurements
    @staticmethod
    def measurements(obj):

        tree = ET.parse("items2.xml")
        root2 = tree.getroot()

        for u in root2.iter('uut'):
            uut = u
        tests = ET.SubElement(uut, 'tests')
        test = ET.SubElement(tests, 'test')

        for i in obj:
            test_name = obj[i]["test_name"]
            test_status = obj[i]["test_status"]
            name = obj[i]["name"]
            status = obj[i]["status"]
            measured = obj[i]["measured"]

            ET.SubElement(test, "name").text = test_name
            ET.SubElement(test, "status").text = test_status
            measurements = ET.SubElement(test, 'measurements')
            measurement = ET.SubElement(measurements, 'measurement')
            ET.SubElement(measurement, "name").text = name
            ET.SubElement(measurement, "status").text = status
            ET.SubElement(measurement, "measured").text = measured

            tree2 = ET.ElementTree(root2)
            tree2.write("items2.xml")

    # message method is used to write notes for a specific product.
    @staticmethod
    def message(name, status, txt):
        tree = ET.parse("items2.xml")
        root2 = tree.getroot()

        for u in root2.iter('uut'):
            uut = u
        tests = ET.SubElement(uut, 'tests')
        test = ET.SubElement(tests, 'test')
        ET.SubElement(test, "name").text = name
        ET.SubElement(test, "status").text = status
        message = ET.SubElement(test, 'message')
        ET.SubElement(message, "text").text = txt

        tree2 = ET.ElementTree(root2)
        tree2.write("items2.xml")

    # takes a test property name and Dictionary obj to add multiple property names and values
    @staticmethod
    def properties(property_group_name, obj):
        tree = ET.parse("items2.xml")
        root2 = tree.getroot()

        for u in root2.iter('uut'):
            uut = u
        property_groups = ET.SubElement(uut, 'property_groups')
        property_group = ET.SubElement(property_groups, 'property_group')
        ET.SubElement(property_group, "name").text = property_group_name
        properties = ET.SubElement(property_group, 'properties')
        property = ET.SubElement(properties, 'property')
        for i in obj:
            name = obj["name"]
            value = obj["value"]
            ET.SubElement(property, "name").text = name
            ET.SubElement(property, "value").text = value

        tree2 = ET.ElementTree(root2)
        tree2.write("items2.xml")

    @staticmethod
    def pretty():
        tree = ET.parse("items2.xml")
        root2 = tree.getroot()
        xmlstr = minidom.parseString(ET.tostring(root2, 'utf-8')).toprettyxml(indent=" ")
        with open("items2.xml", "w") as f:
            f.write(xmlstr)


# create_root_summary(part_number, serial_number, operation, status, started_at, ended_at)
Etree.create_root_summary("31-001197-03-01", "113710008404", "Functional", "Pass", "2019-01-02 13:45:35",
                          "2019-01-02 13:52:50")
# test(name, status)
Etree.test("UUT Setup", "Passed")
# measurements(name, status, measured)
Etree.measurements(
    {1: {"test_name": "fn", "test_status": "Passed", "name": "Successful", "status": "Passed", "measured": "2"},
     2: {"test_name": "fn", "test_status": "Passed", "name": "Successful", "status": "Passed", "measured": "3"}})
# message(name, status, text)
Etree.message("test", "Passed", "This is only a test")
# properties(name, value)
Etree.properties("Configuration Sector", {"name": "RDR", "value": "5", "name": "RDR", "value": "5"})
# # reformat file to be readable
Etree.pretty()
# uploads a xml file to maintainable to be unpacked by to a station
# Input.insert("a2bc48c7", "items2.xml")
