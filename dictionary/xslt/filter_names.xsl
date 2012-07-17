<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">
  
  <xsl:output method="xml" encoding="utf-8" indent="yes" 
	      doctype-public="-//NISO//DTD dtbook 2005-3//EN"
              doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />
  
  <!-- Drop the homograph, name and place elements as they are handled separately-->
  <xsl:template match="brl:homograph|brl:name|brl:place"/>
  
  <!-- Make sure the first/last words in running-line and toc-line elements are
       not joined with other words -->
  <xsl:template match="brl:running-line|brl:toc-line">
    <xsl:copy>
      <xsl:text> </xsl:text>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:text> </xsl:text>
    </xsl:copy>
  </xsl:template>

  <!-- Copy all other nodes and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
