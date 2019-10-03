<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="2.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"	
		xmlns:brl="http://www.daisy.org/z3986/2009/braille/"
		exclude-result-prefixes="dtb brl">

  <xsl:output method="text" encoding="utf-8" indent="no" />

  <xsl:template match="text()">
    <xsl:value-of select="string(.)"/>
  </xsl:template>
  
</xsl:stylesheet>
