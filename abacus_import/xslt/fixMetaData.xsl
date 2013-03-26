<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		exclude-result-prefixes="dtb">
  
  <xsl:param name="author"/>
  <xsl:param name="date"/>
  <xsl:param name="description"/>
  <xsl:param name="identifier"/>
  <xsl:param name="language"/>
  <xsl:param name="production_series"/>
  <xsl:param name="production_series_number"/>
  <xsl:param name="production_source"/>
  <xsl:param name="publisher"/>
  <xsl:param name="rights"/>
  <xsl:param name="source"/>
  <xsl:param name="source_date"/>
  <xsl:param name="source_edition"/>
  <xsl:param name="source_publisher"/>
  <xsl:param name="source_rights"/>
  <xsl:param name="subject"/>
  <xsl:param name="title"/>

  <xsl:output method="xml" encoding="utf-8" indent="no"
    doctype-public="-//NISO//DTD dtbook 2005-3//EN"
    doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />
  
  <!-- Override the author -->
  <xsl:template match="//dtb:meta[@name = 'dc:Creator']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$author"/>
    </xsl:attribute>
    <!-- Don't touch the docauthor as it might contain inline markup
         such as brl:* -->
  </xsl:template>

  <!-- Override the date -->
  <xsl:template match="//dtb:meta[@name = 'dc:Date']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$date"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override the description -->
  <xsl:template match="//dtb:meta[@name = 'dc:Description']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$description"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override dc:Identifier and dtb:uid -->
  <xsl:template match="//dtb:meta[@name = 'dc:Identifier' or @name = 'dtb:uid']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$identifier"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override the language -->
  <xsl:template match="//dtb:meta[@name = 'dc:Language']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$language"/>
    </xsl:attribute>
  </xsl:template>

  <!-- update the root xml:lang tag -->
  <xsl:template match="/dtb:dtbook/@xml:lang">
    <xsl:attribute name="xml:lang">
      <xsl:value-of select="$language"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override production_series -->
  <xsl:template match="//dtb:meta[@name = 'prod:series']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$production_series"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override production_series_number -->
  <xsl:template match="//dtb:meta[@name = 'prod:seriesNumber']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$production_series_number"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override production_source -->
  <xsl:template match="//dtb:meta[@name = 'prod:source']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$production_source"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override publisher -->
  <xsl:template match="//dtb:meta[@name = 'dc:Publisher']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$publisher"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override rights -->
  <xsl:template match="//dtb:meta[@name = 'dc:Rights']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$rights"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override the ISBN -->
  <xsl:template match="//dtb:meta[@name = 'dc:Source']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$source"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override source_date -->
  <xsl:template match="//dtb:meta[@name = 'dtb:sourceDate']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$source_date"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override the source_edition -->
  <xsl:template match="//dtb:meta[@name = 'dtb:sourceEdition']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$source_edition"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override the source_publisher -->
  <xsl:template match="//dtb:meta[@name = 'dtb:sourcePublisher']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$source_publisher"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override source_rights -->
  <xsl:template match="//dtb:meta[@name = 'dtb:sourceRights']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$source_rights"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override subject -->
  <xsl:template match="//dtb:meta[@name = 'dc:Subject']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$subject"/>
    </xsl:attribute>
  </xsl:template>

  <!-- Override the title -->
  <xsl:template match="//dtb:meta[@name = 'dc:Title']/@content">
    <xsl:attribute name="content">
      <xsl:value-of select="$title"/>
    </xsl:attribute>
    <!-- Don't touch the doctitle as it might contain inline markup
         such as brl:* -->
  </xsl:template>

  <!-- Insert a missing production_series -->
  <xsl:template match="dtb:head[not(dtb:meta[@name = 'prod:series'])]">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:element name="meta" namespace="http://www.daisy.org/z3986/2005/dtbook/">
	<xsl:attribute name="name">
	  <xsl:value-of select="'prod:series'"/>
	</xsl:attribute>
	<xsl:attribute name="content">
	  <xsl:value-of select="$production_series"/>
	</xsl:attribute>
      </xsl:element>
    </xsl:copy>
  </xsl:template>

  <!-- Insert a missing production_series_number -->
  <xsl:template match="dtb:head[not(dtb:meta[@name = 'prod:seriesNumber'])]">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:element name="meta" namespace="http://www.daisy.org/z3986/2005/dtbook/">
	<xsl:attribute name="name">
	  <xsl:value-of select="'prod:seriesNumber'"/>
	</xsl:attribute>
	<xsl:attribute name="content">
	  <xsl:value-of select="$production_series_number"/>
	</xsl:attribute>
      </xsl:element>
    </xsl:copy>
  </xsl:template>

  <!-- Insert a missing production_source -->
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
