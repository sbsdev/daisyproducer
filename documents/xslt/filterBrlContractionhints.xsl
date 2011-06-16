<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">
  
  <xsl:output method="xml" encoding="utf-8" indent="yes" 
	      doctype-public="-//NISO//DTD dtbook 2005-3//EN"
              doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />

  <!-- Get rid of the brl namespace declaration in the dtbook node -->
  <xsl:template match="dtb:dtbook">
    <xsl:element name="{name()}" namespace="{namespace-uri()}">
      <xsl:apply-templates select="@*|*|text()|processing-instruction()|comment()" />
    </xsl:element>
  </xsl:template>

  <!-- Drop the brl:running-line elements without retaining their content -->
  <xsl:template match="brl:running-line"/>

  <!-- Drop the brl:toc-line elements without retaining their content -->
  <xsl:template match="brl:toc-line"/>

  <!-- Filter brl:when-braille elements -->
  <xsl:template match="brl:when-braille"/>

  <!-- Replace space inside num elements with non-breaking space -->
  <!-- FIXME: This should probably be in the dtbook2latex converter,
       but since that one dosn't know anything about num elements this
       template is here for now. -->
  <xsl:template match="brl:num//text()">
    <xsl:value-of select="translate(string(current()), ' ', ' ')"/>
  </xsl:template>

  <!-- Drop the brl:* elements while retaining their content -->
  <xsl:template match="brl:*">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- Drop the brl:* attributes -->
  <xsl:template match="@brl:*"/>

  <!-- Copy all other elements and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
