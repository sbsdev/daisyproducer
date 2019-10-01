<?xml version="1.0" encoding="utf-8"?>

<!-- When a dtbook document only contains level1 we would like to
render it a bit more compactly in large print, i.e. do not put each h1
on a recto page. The same holds if the h2 are all empty.

This stylesheet determines whether a document qualifies for compact
style rendering. If it does it returns "true". Otherwise it will
return "false". -->

<xsl:stylesheet version="2.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:dtb="http://www.daisy.org/z3986/2005/dtbook/"
		xmlns:my="http://my-functions"
		exclude-result-prefixes="dtb">

  <xsl:output method="text" encoding="utf-8" indent="no" />

  <xsl:template match="/*">
    <xsl:choose>
      <xsl:when test="dtb:book/dtb:bodymatter//dtb:h2[normalize-space(.)]">
	<xsl:text>false</xsl:text>
      </xsl:when>
      <xsl:otherwise>
      	<xsl:text>true</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
