"""
Professional PDF report generation for internal linking recommendations.
Designed for stakeholder delivery (clients, editors, content teams).
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime
import pandas as pd


def generate_pdf_report(links_df, site_url, output_path="internal_linking_report.pdf", metadata=None):
    """
    Generate professional PDF report from internal linking recommendations.
    
    Args:
        links_df: DataFrame with columns [from, to, anchor, sentence]
        site_url: Website URL analyzed
        output_path: Where to save PDF
        metadata: Dict with optional keys:
            - silhouette_score: Cluster cohesion metric
            - total_pages_crawled: Number of pages crawled
            - usable_pages: Number of pages with sufficient content
            - num_clusters: Number of semantic clusters
    """
    
    # Setup
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    # ====== TITLE PAGE ======
    story.append(Spacer(1, 0.5 * inch))
    title = Paragraph("Internal Linking Recommendations", title_style)
    story.append(title)
    
    subtitle = Paragraph(f"<b>Site:</b> {site_url}", styles['Normal'])
    story.append(subtitle)
    story.append(Spacer(1, 0.2 * inch))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    report_date = Paragraph(f"<b>Report Generated:</b> {date_str}", styles['Normal'])
    story.append(report_date)
    story.append(Spacer(1, 0.5 * inch))
    
    # ====== EXECUTIVE SUMMARY ======
    story.append(Paragraph("Executive Summary", heading_style))
    
    summary_text = f"""
    This report contains <b>{len(links_df)} actionable internal linking recommendations</b> 
    for {site_url}. Each recommendation is:
    <br/><br/>
    • <b>Semantic:</b> Based on topic relevance, not keyword matching<br/>
    • <b>Safe:</b> Anchors already exist in visible page content<br/>
    • <b>Audit-ready:</b> Includes source sentence for verification<br/>
    • <b>Google-compliant:</b> Follows SEO Starter Guide guidelines<br/>
    <br/>
    <b>Action Required:</b> Manual review and editorial judgment before implementation.
    This system recommends; humans approve.
    """
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # ====== METHODOLOGY ======
    story.append(Paragraph("Methodology", heading_style))
    
    methodology_text = """
    <b>1. Crawling & Content Extraction</b><br/>
    The system crawled all internal pages and extracted clean content 
    (excluding navigation, footer, scripts).<br/>
    <br/>
    <b>2. Semantic Clustering</b><br/>
    Pages were grouped by semantic similarity using sentence-transformers embeddings.
    Cluster cohesion is measured via silhouette score (higher = more topically coherent).<br/>
    <br/>
    <b>3. Pillar & Supporting Pages</b><br/>
    Within each cluster, the most comprehensive non-utility page was identified as the "pillar."
    Supporting pages link TO the pillar (not vice versa).<br/>
    <br/>
    <b>4. Anchor Selection</b><br/>
    For each supporting page, one natural anchor phrase is extracted from existing content
    using grammatical rules (noun phrases only). The anchor must overlap semantically with
    the target pillar page.<br/>
    <br/>
    <b>5. Safety Filters</b><br/>
    • No links from utility pages (privacy, terms, contact, etc.)<br/>
    • No self-links<br/>
    • One link per page per topic (to prevent over-optimization)<br/>
    • Anchors must be at least 2 words (avoids generic single-word anchors)<br/>
    """
    story.append(Paragraph(methodology_text, body_style))
    story.append(PageBreak())
    
    # ====== ANALYTICS ======
    if metadata:
        story.append(Paragraph("Analysis Metrics", heading_style))
        
        metrics_text = f"""
        <b>Crawl Statistics:</b><br/>
        • Total pages crawled: {metadata.get('total_pages_crawled', 'N/A')}<br/>
        • Pages with sufficient content (200+ words): {metadata.get('usable_pages', 'N/A')}<br/>
        • Semantic clusters identified: {metadata.get('num_clusters', 'N/A')}<br/>
        • Cluster cohesion (silhouette score): {metadata.get('silhouette_score', 'N/A'):.3f} 
        (0.3+ = acceptable, 0.5+ = good)<br/>
        <br/>
        """
        story.append(Paragraph(metrics_text, body_style))
        story.append(Spacer(1, 0.2 * inch))
    
    # ====== RECOMMENDATIONS TABLE ======
    story.append(Paragraph("Recommendations", heading_style))
    
    if len(links_df) == 0:
        story.append(Paragraph(
            "No internal linking opportunities found. This may indicate: "
            "few pages crawled, low content, or well-linked site.",
            body_style
        ))
    else:
        # Build table with better formatting (readable on PDF)
        # Layout: From Page | Anchor Text | Link To (separate rows for clarity)
        table_data = []
        
        for idx, (_, row) in enumerate(links_df.iterrows(), 1):
            from_page = row['from'].replace('https://', '').replace('http://', '').strip()
            to_page = row['to'].replace('https://', '').replace('http://', '').strip()
            anchor = row['anchor'].strip()
            sentence = row['sentence'].strip()
            
            # Format: Bold label + value for clarity
            from_cell = f"<b>From:</b> {from_page}"
            to_cell = f"<b>To:</b> {to_page}"
            anchor_cell = f"<b>Anchor:</b> {anchor}"
            context_cell = f"<b>Context:</b> {sentence[:120]}..."
            
            # Add recommendation number
            table_data.append([f"<b>Recommendation {idx}</b>", ""])
            table_data.append([from_cell, ""])
            table_data.append([anchor_cell, ""])
            table_data.append([to_cell, ""])
            table_data.append([context_cell, ""])
            table_data.append(["", ""])  # Spacer row
        
        # Create table with 2 columns (label column, value column)
        table = Table(table_data, colWidths=[6.5*inch, 0.5*inch])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Content styling
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Gridlines
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            
            # Alternating row colors for recommendation blocks
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
            
            # Recommendation number styling (bold header per item)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f4f8')),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ]))
        
        story.append(table)

    
    story.append(Spacer(1, 0.3 * inch))
    
    # ====== IMPLEMENTATION GUIDE ======
    story.append(PageBreak())
    story.append(Paragraph("Implementation Guide", heading_style))
    
    guide_text = """
    <b>Step 1: Review</b><br/>
    Read through all recommendations. Each row shows the source page, 
    the anchor text to use, and the target page to link to.<br/>
    <br/>
    <b>Step 2: Verify</b><br/>
    Check the "Context" column. The anchor phrase is pulled from the source page.
    Verify it appears in the sentence and makes sense in context.<br/>
    <br/>
    <b>Step 3: Edit (Optional)</b><br/>
    If the anchor text doesn't feel natural, you can use a synonym or related phrase.
    Example: "machine learning models" can become "ML models" or "deep learning."<br/>
    <br/>
    <b>Step 4: Implement</b><br/>
    Add the HTML anchor tag. Example:<br/>
    <font face="Courier" size="8">
    &lt;a href="https://target-page.com"&gt;anchor text&lt;/a&gt;
    </font><br/>
    <br/>
    <b>Step 5: Test</b><br/>
    After implementation, test:<br/>
    • Link is clickable and leads to the target page<br/>
    • Anchor text reads naturally in context<br/>
    • No duplicate links on the same page<br/>
    <br/>
    <b>Timing:</b> Implement links gradually (1-2 per day if possible).
    Sudden bulk linking can trigger spam filters.<br/>
    """
    story.append(Paragraph(guide_text, body_style))
    
    # ====== FOOTER ======
    story.append(Spacer(1, 0.3 * inch))
    footer_text = """
    <i>This report was generated by an automated Internal Linking AI Agent.
    All recommendations are suggestions only. Final decisions rest with
    editorial and SEO teams. For questions, contact your SEO partner.</i>
    """
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return output_path
