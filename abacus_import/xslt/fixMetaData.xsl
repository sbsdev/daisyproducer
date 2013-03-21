<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		exclude-result-prefixes="dtb">
  
  <xsl:param name="date"/>
  <xsl:param name="identifier"/>
  <xsl:param name="production_source"/>

  <xsl:output method="xml" encoding="utf-8" indent="no"
    doctype-public="-//NISO//DTD dtbook 2005-3//EN"
    doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />
  
  <!-- Override the date -->
  <xsl:template match="//dtb:meta[@name = 'dc:Date']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$date"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override dc:Identifier and dtb:uid -->
  <xsl:template match="//dtb:meta[@name = 'dc:Identifier' or @name = 'dtb:uid']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$identifier"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override prod:source -->
  <xsl:template match="//dtb:meta[@name = 'prod:source']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$production_source"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Insert a missing prod:source -->
  <xsl:template match="dtb:head[not(dtb:meta[@name = 'prod:source'])]">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:element name="meta" namespace="http://www.daisy.org/z3986/2005/dtbook/">
	<xsl:attribute name="name">
	  <xsl:value-of select="'prod:source'"/>
	</xsl:attribute>
	<xsl:attribute name="content">
	  <xsl:value-of select="$production_source"/>
	</xsl:attribute>
      </xsl:element>
    </xsl:copy>
  </xsl:template>

  <!-- Copy all other nodes and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
