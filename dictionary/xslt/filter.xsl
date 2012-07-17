<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="2.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">
  
  <xsl:param name="contraction" select="2"/>
  
  <xsl:output method="xml" encoding="utf-8" indent="yes"
    doctype-public="-//NISO//DTD dtbook 2005-3//EN"
    doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />
  
  <xsl:strip-space elements="brl:select"/>
  
  <!-- Drop a, i.e. urls, etc as they will be shown in grade 0 anyway -->
  <xsl:template match="dtb:a"/>
  
  <!-- Drop the abbr elements -->
  <xsl:template match="dtb:abbr"/>
  
  <!-- Drop the num elements -->
  <xsl:template match="brl:num"/>
  
  <!-- Drop brl:literals -->
  <xsl:template match="brl:literal"/>
  
  <!-- Drop text which is not meant for Braille anyway -->
  <xsl:template match="brl:otherwise"/>
  
  <!-- Drop names with mixed capitalization -->
  <xsl:template match="brl:name[matches(string(.), '\p{Ll}\p{Lu}')]"/>
  
  <!-- Drop foreign and downgraded words -->
  <xsl:template match="*[not(lang('de'))]"/>
  <xsl:template match="*[@brl:grade and number(@brl:grade) &lt; $contraction]"/>

  <!-- Copy all other nodes and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
