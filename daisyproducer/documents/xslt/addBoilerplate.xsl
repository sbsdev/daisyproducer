<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="2.0"
		xmlns="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">
  
  <xsl:output method="xml" encoding="utf-8" indent="no" 
	      doctype-public="-//NISO//DTD dtbook 2005-3//EN"
              doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />

  <xsl:template name="boilerplate">
    <level1>
      <h1>Zu diesem Buch</h1>
      <p>Dieses E-Book im DAISY-Format ist die ausschliesslich für die Nutzung durch seh- und lesebehinderte Menschen bestimmte zugängliche Version eines urheberrechtlich geschützten Werks. Sie können es im Rahmen des Urheberrechts persönlich nutzen, dürfen es aber nicht weiter verbreiten oder öffentlich zugänglich machen.</p>
      <xsl:if test="//dtb:meta[lower-case(@name)='prod:source']/@content = 'electronicData'">
	<p>Wir danken dem Verlag für die freundliche Bereitstellung der elektronischen Textdaten.</p>
      </xsl:if>
      <xsl:variable name="year" select="tokenize(//dtb:meta[lower-case(@name)='dc:date']/@content, '-')[1]"/>
      <p>Herstellung:<br/>SBS Schweizerische Bibliothek für Blinde, Seh- und Lesebehinderte, Zürich<br/><a href="http://www.sbs.ch" external="true">www.sbs.ch</a><br/><xsl:value-of select="concat('SBS ', $year)"/></p>
    </level1>
  </xsl:template>

  <!-- Add boilerplate text before the title page -->
  <xsl:template match="dtb:frontmatter//dtb:level1[@class='titlepage'][1]">
    <xsl:call-template name="boilerplate"/>
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Copy all other elements and attributes -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
