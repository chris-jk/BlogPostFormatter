import os
import pypandoc
import markdown
import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import html2text

def markdown_to_rtf(markdown_text):
    """Convert markdown text to RTF format with enhanced styling"""
    try:
        # Convert markdown to HTML with essential extensions
        html = markdown.markdown(markdown_text, extensions=['extra'])
        
        # RTF Header with optimized styling
        rtf_header = [
            r"{\rtf1\ansi\ansicpg1252\cocoartf2761",
            r"\cocoatextscaling0\cocoaplatform0",
            r"{\fonttbl",
            r"\f0\fswiss\fcharset0 Helvetica;",
            r"\f1\fswiss\fcharset0 Helvetica-Bold;",
            r"}",
            r"{\colortbl;\red0\green0\blue0;}",
            r"\paperw12240\paperh15840",
            r"\margl1440\margr1440",
            r"\vieww12000\viewh15000\viewkind0",
            r"\pard\tx720\pardeftab720\partightenfactor0",
            r"\f0\fs24",
        ]
        
        rtf = '\n'.join(rtf_header)
        
        # Convert HTML to RTF
        rtf_body = html
        
        # Headers with improved spacing
        rtf_body = re.sub(r'<h1>(.*?)</h1>', r'\\f1\\fs36\\b \1\\f0\\b0\\fs24\\par\\par', rtf_body)
        rtf_body = re.sub(r'<h2>(.*?)</h2>', r'\\f1\\fs32\\b \1\\f0\\b0\\fs24\\par\\par', rtf_body)
        rtf_body = re.sub(r'<h3>(.*?)</h3>', r'\\f1\\fs28\\b \1\\f0\\b0\\fs24\\par\\par', rtf_body)
        
        # Lists with proper bullets using RTF bullet
        rtf_body = re.sub(r'<ul>', r'\\par', rtf_body)
        rtf_body = re.sub(r'</ul>', r'\\par', rtf_body)
        rtf_body = re.sub(r'<li>(.*?)</li>', r'\\fi-360\\li720 {\\bullet} \1\\par', rtf_body)
        
        # Paragraphs with proper spacing
        rtf_body = re.sub(r'<p>(.*?)</p>', r'\1\\par\\par', rtf_body)
        
        # Inline formatting
        rtf_body = re.sub(r'<strong>(.*?)</strong>', r'\\b \1\\b0 ', rtf_body)
        rtf_body = re.sub(r'<em>(.*?)</em>', r'\\i \1\\i0 ', rtf_body)
        
        # Clean up HTML tags
        rtf_body = re.sub(r'<[^>]+>', '', rtf_body)
        
        # Replace problematic characters
        replacements = {
            '•': '{\\bullet}',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '–': '-',
            '—': '--',
            '\u2022': '{\\bullet}',  # Unicode bullet
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201C': '"',  # Left double quote
            '\u201D': '"',  # Right double quote
        }
        
        for old, new in replacements.items():
            rtf_body = rtf_body.replace(old, new)
        
        # Add content and close RTF
        rtf += rtf_body + "\n}"
        
        return rtf
        
    except Exception as e:
        print(f"Error in RTF conversion: {str(e)}")
        return str(e)

def enhance_rtf_formatting(rtf_content):
    """Enhance the RTF formatting with custom styling"""
    # Add custom font table
    font_table = (
        r"{\fonttbl"
        r"{\f0\fswiss\fcharset0 Helvetica-Bold;}"
        r"{\f1\fswiss\fcharset0 Helvetica;}"
        r"{\f2\fmodern\fcharset0 Menlo-Regular;}"
        r"}"
    )
    
    # Replace default font table
    rtf_content = re.sub(r'{\fonttbl.*?}', font_table, rtf_content)
    
    # Enhance heading styles
    rtf_content = re.sub(r'\\f0\\fs48', r'\\f0\\fs40\\b', rtf_content)  # H1
    rtf_content = re.sub(r'\\f0\\fs36', r'\\f0\\fs32\\b', rtf_content)  # H2
    rtf_content = re.sub(r'\\f0\\fs28', r'\\f0\\fs28\\b', rtf_content)  # H3
    
    return rtf_content

def basic_markdown_to_rtf(markdown_text):
    """Fallback basic markdown to RTF converter"""
    # First convert markdown to HTML
    html = markdown.markdown(markdown_text)
    
    # Basic RTF header with more complete styling
    rtf = [
        r"{\rtf1\ansi\ansicpg1252\cocoartf2639\cocoatextscaling0",
        r"{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\froman\fcharset0 TimesNewRoman;}",
        r"{\colortbl;\red0\green0\blue0;\red0\green0\blue255;}",
        r"\paperw12240\paperh15840\margl1440\margr1440\vieww12000\viewh15000\viewkind0",
        r"\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0",
        r"\f0\fs24\fsmilli12200"
    ]
    rtf = '\n'.join(rtf)
    
    # Convert HTML to RTF
    rtf_body = html
    
    # Headers
    rtf_body = re.sub(r'<h1>(.*?)</h1>', r'\\par\\f1\\fs36\\b \1\\b0\\fs24\\f0\\par\n', rtf_body)
    rtf_body = re.sub(r'<h2>(.*?)</h2>', r'\\par\\f1\\fs32\\b \1\\b0\\fs24\\f0\\par\n', rtf_body)
    rtf_body = re.sub(r'<h3>(.*?)</h3>', r'\\par\\f1\\fs28\\b \1\\b0\\fs24\\f0\\par\n', rtf_body)
    
    # Paragraphs
    rtf_body = re.sub(r'<p>(.*?)</p>', r'\\par \1\\par\n', rtf_body)
    
    # Lists
    rtf_body = re.sub(r'<ul>(.*?)</ul>', r'\\par \1\\par\n', rtf_body)
    rtf_body = re.sub(r'<li>(.*?)</li>', r'\\par • \1', rtf_body)
    
    # Inline formatting
    rtf_body = re.sub(r'<strong>(.*?)</strong>', r'\\b \1\\b0 ', rtf_body)
    rtf_body = re.sub(r'<em>(.*?)</em>', r'\\i \1\\i0 ', rtf_body)
    rtf_body = re.sub(r'<code>(.*?)</code>', r'\\f1 \1\\f0 ', rtf_body)
    
    # Links
    rtf_body = re.sub(r'<a href="(.*?)">(.*?)</a>', r'\\cf2\\ul \2\\cf1\\ulnone', rtf_body)
    
    # Clean up any remaining HTML tags
    rtf_body = re.sub(r'<[^>]+>', '', rtf_body)
    
    # Escape special characters
    rtf_body = rtf_body.replace('\\', '\\\\')
    rtf_body = rtf_body.replace('{', '\\{')
    rtf_body = rtf_body.replace('}', '\\}')
    
    # Fix double escaping of RTF commands
    rtf_body = rtf_body.replace('\\\\par', '\\par')
    rtf_body = rtf_body.replace('\\\\b', '\\b')
    rtf_body = rtf_body.replace('\\\\i', '\\i')
    rtf_body = rtf_body.replace('\\\\f', '\\f')
    rtf_body = rtf_body.replace('\\\\fs', '\\fs')
    
    # Add converted body and close RTF
    rtf += rtf_body + "\n}"
    
    return rtf

def markdown_to_docx(markdown_text):
    """Convert markdown text to DOCX format"""
    # Convert markdown to HTML first
    html = markdown.markdown(markdown_text)
    
    # Create a new document
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    style.font.name = 'Helvetica'
    style.font.size = Pt(11)
    
    # Convert HTML to plain text while preserving basic formatting
    h = html2text.HTML2Text()
    h.body_width = 0  # Disable wrapping
    text = h.handle(html)
    
    # Process the text line by line
    current_list = None
    for line in text.split('\n'):
        if line.startswith('# '):  # H1
            p = doc.add_paragraph()
            run = p.add_run(line[2:])
            run.font.size = Pt(20)
            run.font.bold = True
            p.space_after = Pt(12)
        elif line.startswith('## '):  # H2
            p = doc.add_paragraph()
            run = p.add_run(line[3:])
            run.font.size = Pt(16)
            run.font.bold = True
            p.space_after = Pt(10)
        elif line.startswith('### '):  # H3
            p = doc.add_paragraph()
            run = p.add_run(line[4:])
            run.font.size = Pt(14)
            run.font.bold = True
            p.space_after = Pt(8)
        elif line.startswith('* '):  # List items
            if current_list is None:
                current_list = doc.add_paragraph()
            p = current_list.add_run('\n• ' + line[2:])
        elif line.strip() == '':  # Empty line
            current_list = None
            doc.add_paragraph()
        else:  # Regular paragraph
            current_list = None
            p = doc.add_paragraph(line)
            p.space_after = Pt(10)
    
    return doc

def save_as_docx(doc, filename):
    """Save the document as DOCX"""
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc.save(filename)