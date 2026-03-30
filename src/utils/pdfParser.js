// PDF parsing using pdf.js
import * as pdfjsLib from 'pdfjs-dist';
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';

// Configure worker — use local bundled worker (not CDN) for reliability
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

export const extractTextFromPDF = async (file) => {
  try {
    const arrayBuffer = await file.arrayBuffer();
    
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let fullText = '';
    
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      fullText += pageText + '\n';
    }
    
    if (!fullText.trim()) {
      return {
        success: false,
        error: 'No readable text found in PDF. The file may be scanned/image-based.'
      };
    }

    return {
      success: true,
      text: fullText.trim()
    };
  } catch (error) {
    console.error('PDF parsing error:', error);
    return {
      success: false,
      error: 'Failed to parse PDF: ' + error.message
    };
  }
};

// DOCX parsing — extracts text from xml inside the docx zip archive
const extractTextFromDOCX = async (file) => {
  try {
    const arrayBuffer = await file.arrayBuffer();
    
    // DOCX files are ZIP archives. We use the browser's DecompressionStream 
    // or fall back to manually finding the XML content.
    // The main document text lives in word/document.xml
    const uint8 = new Uint8Array(arrayBuffer);
    
    // Find the word/document.xml entry in the ZIP
    const xmlContent = await extractXmlFromZip(uint8, 'word/document.xml');
    
    if (!xmlContent) {
      return {
        success: false,
        error: 'Could not extract text from DOCX. The file may be corrupted.'
      };
    }

    // Parse the XML and extract text nodes
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlContent, 'application/xml');
    
    // Get all <w:t> text elements (the actual text content in DOCX)
    const textNodes = doc.getElementsByTagNameNS(
      'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 
      't'
    );
    
    let fullText = '';
    let lastParent = null;
    
    for (const node of textNodes) {
      // Detect paragraph boundaries for newlines
      const paragraph = node.closest('p') || findAncestor(node, 'w:p');
      if (paragraph && paragraph !== lastParent && fullText) {
        fullText += '\n';
      }
      lastParent = paragraph;
      fullText += node.textContent;
    }

    if (!fullText.trim()) {
      return {
        success: false,
        error: 'No readable text found in DOCX file.'
      };
    }

    return {
      success: true,
      text: fullText.trim()
    };
  } catch (error) {
    console.error('DOCX parsing error:', error);
    return {
      success: false,
      error: 'Failed to parse DOCX: ' + error.message
    };
  }
};

// Helper: find ancestor element by local name in XML
const findAncestor = (node, localName) => {
  let current = node.parentElement;
  while (current) {
    if (current.localName === localName.split(':').pop()) return current;
    current = current.parentElement;
  }
  return null;
};

// Minimal ZIP reader — extracts a single file from a ZIP archive (no external deps)
const extractXmlFromZip = async (uint8, targetPath) => {
  try {
    // Find end of central directory record
    let eocdOffset = -1;
    for (let i = uint8.length - 22; i >= 0; i--) {
      if (uint8[i] === 0x50 && uint8[i + 1] === 0x4b && 
          uint8[i + 2] === 0x05 && uint8[i + 3] === 0x06) {
        eocdOffset = i;
        break;
      }
    }
    
    if (eocdOffset === -1) return null;

    const view = new DataView(uint8.buffer, uint8.byteOffset, uint8.byteLength);
    const cdOffset = view.getUint32(eocdOffset + 16, true);
    const cdEntries = view.getUint16(eocdOffset + 10, true);

    let offset = cdOffset;
    
    for (let i = 0; i < cdEntries; i++) {
      // Central directory header signature check
      if (uint8[offset] !== 0x50 || uint8[offset + 1] !== 0x4b ||
          uint8[offset + 2] !== 0x01 || uint8[offset + 3] !== 0x02) break;

      const compMethod = view.getUint16(offset + 10, true);
      const compSize = view.getUint32(offset + 20, true);
      const uncompSize = view.getUint32(offset + 24, true);
      const nameLen = view.getUint16(offset + 28, true);
      const extraLen = view.getUint16(offset + 30, true);
      const commentLen = view.getUint16(offset + 32, true);
      const localHeaderOffset = view.getUint32(offset + 42, true);
      
      const nameBytes = uint8.slice(offset + 46, offset + 46 + nameLen);
      const fileName = new TextDecoder().decode(nameBytes);

      if (fileName === targetPath) {
        // Read local file header to find actual data start
        const localNameLen = view.getUint16(localHeaderOffset + 26, true);
        const localExtraLen = view.getUint16(localHeaderOffset + 28, true);
        const dataStart = localHeaderOffset + 30 + localNameLen + localExtraLen;
        const compressedData = uint8.slice(dataStart, dataStart + compSize);

        if (compMethod === 0) {
          // Stored (no compression)
          return new TextDecoder().decode(compressedData);
        } else if (compMethod === 8) {
          // Deflate — use DecompressionStream
          const ds = new DecompressionStream('raw');
          const writer = ds.writable.getWriter();
          writer.write(compressedData);
          writer.close();
          const reader = ds.readable.getReader();
          const chunks = [];
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
          }
          const totalLen = chunks.reduce((acc, c) => acc + c.length, 0);
          const result = new Uint8Array(totalLen);
          let pos = 0;
          for (const chunk of chunks) {
            result.set(chunk, pos);
            pos += chunk.length;
          }
          return new TextDecoder().decode(result);
        }
        return null;
      }

      offset += 46 + nameLen + extraLen + commentLen;
    }

    return null;
  } catch (error) {
    console.error('ZIP extraction error:', error);
    return null;
  }
};

export const extractTextFromFile = async (file) => {
  const fileType = file.type;
  const fileName = file.name.toLowerCase();
  
  try {
    // Handle PDF files
    if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
      return await extractTextFromPDF(file);
    }
    
    // Handle text-based files
    if (fileType.startsWith('text/') || fileName.endsWith('.txt')) {
      const text = await file.text();
      if (!text.trim()) {
        return { success: false, error: 'The file appears to be empty.' };
      }
      return { success: true, text: text.trim() };
    }
    
    // Handle DOCX files — proper XML extraction from ZIP archive
    if (fileType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
        fileName.endsWith('.docx')) {
      return await extractTextFromDOCX(file);
    }

    // Handle DOC files — limited support (legacy binary format)
    if (fileType === 'application/msword' || fileName.endsWith('.doc')) {
      return {
        success: false,
        error: 'Legacy .doc format is not supported. Please save as .docx or .pdf and try again.'
      };
    }
    
    return {
      success: false,
      error: 'Unsupported file type. Please upload PDF, DOCX, or TXT files.'
    };
  } catch (error) {
    console.error('File parsing error:', error);
    return {
      success: false,
      error: 'Failed to process file: ' + error.message
    };
  }
};
