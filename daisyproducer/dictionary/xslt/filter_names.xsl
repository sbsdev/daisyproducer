<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="2.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">
  
  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  
  <!-- Drop the homograph, name and place elements as they are handled separately-->
  <xsl:template match="brl:homograph|brl:name|brl:place">
    <xsl:text> </xsl:text>
  </xsl:template>
  
  <!-- Drop hyphens immediately before a homograph, a name or a place -->
  <xsl:template match="text()[ends-with(., '-') and following-sibling::*[1][self::brl:homograph or self::brl:name or self::brl:place]]">
    <xsl:value-of select="substring(., 1, string-length(.)-1)"/>
  </xsl:template>

  <!-- Drop hyphens immediately after a homograph, a name or a place -->
  <xsl:template match="text()[starts-with(., '-') and preceding-sibling::*[1][self::brl:homograph or self::brl:name or self::brl:place]]">
    <xsl:value-of select="substring(., 2)"/>
  </xsl:template>

  <!-- Make sure the first/last words in running-line and toc-line elements are
       not joined with other words -->
  <xsl:template match="brl:running-line|brl:toc-line">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:text> </xsl:text>
      <xsl:apply-templates select="node()"/>
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
