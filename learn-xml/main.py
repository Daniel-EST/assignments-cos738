from typing import TextIO
import os
import xml.sax
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
import xml.dom.minidom


FILE_PATH = f"./data/raw/cf79.xml"
TITLES_PATH = f"./data/parsed/titulos.xml"
AUTHORS_PATH = f"./data/parsed/autores.xml"


class AuthorHandler(XMLGenerator):
    """Handles Authors using SAX parser and saves to a file."""
    def __init__(self, out: TextIO, encoding: str = "utf-8"):
        super().__init__(out, encoding)
        self.current_element = None

    def startDocument(self):
        super().startDocument()
        super().startElement("AUTHORS", {})
        self._write("\n")
    
    def startElement(self, name: str, attrs: AttributesImpl) -> None:
        self.current_element = name
        if name == "AUTHOR":
            super().startElement(name, attrs)
        
    def characters(self, content: str) -> None:
        if self.current_element == "AUTHOR":
            super().characters(content)
    
    def endElement(self, name: str) -> None:
        self.current_element = name
        if name == "AUTHOR":
            if self._pending_start_element:
                self._write('/>\n')
                self._pending_start_element = False
            else:
                self._write('</%s>\n' % name)
    
    def endDocument(self):
        super().endElement("AUTHORS")
        super().endDocument()


if __name__ == "__main__":
    # Parses AUTHOR using SAX.
    print(AUTHORS_PATH)
    with open(AUTHORS_PATH, 'w') as file:
        xml.sax.parse(FILE_PATH, handler=AuthorHandler(file))
    
    # Parses TITLE using DOM (minidom).
    with xml.dom.minidom.parse(FILE_PATH) as doc:
        titles = [title.childNodes[0].nodeValue for title in doc.getElementsByTagName("TITLE")]

    with open(TITLES_PATH, 'w') as file:
        doc = xml.dom.minidom.Document()
        root = doc.createElement("TITLES")
        doc.appendChild(root)

        for title in titles:
            temp_child = doc.createElement("TITLE")
            root.appendChild(temp_child)

            text = doc.createTextNode(title.strip())
            temp_child.appendChild(text)

        doc.writexml(file, newl="\n", encoding="utf-8")
