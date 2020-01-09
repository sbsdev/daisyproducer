<?xml version="1.0" encoding="utf-8"?>
<!-- NOTE: This is basically a copy of
     https://github.com/sbsdev/pipeline/blob/epub3-with-braille-rendition-script/modules/sbs/dtbook-to-ebook/src/main/resources/xml/xslt/addImageRefs.xsl
     -->
<xsl:stylesheet version="2.0"
                xmlns="http://www.daisy.org/z3986/2005/dtbook/"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"
                exclude-result-prefixes="dtb">

  <xsl:output method="xml" encoding="utf-8" indent="no"
              doctype-public="-//NISO//DTD dtbook 2005-3//EN"
              doctype-system="http://www.daisy.org/z3986/2005/dtbook-2005-3.dtd" />

  <!-- Add an imageref to the first prodnote inside an image group unless there
       are some existing elements within the same imggroup that actually have an
       imgref already -->
  <xsl:template match="dtb:imggroup//dtb:prodnote[1][not(../dtb:*[@imgref])]">
    <xsl:copy>
      <xsl:attribute name="imgref">
	<xsl:value-of select="preceding-sibling::dtb:img[1]/@id"/>
      </xsl:attribute>
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
