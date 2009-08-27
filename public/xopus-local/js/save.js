function mySaveFunction(uri, xmldoc) {
    var response = HTTPTools.postXML(get_save_url(), xmldoc, "UTF-8");
    return true;
}
IO.setSaveXMLFunction(mySaveFunction);
