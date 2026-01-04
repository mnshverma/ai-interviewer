// PDF parsing using pdf.js (will be installed via npm)
export const extractTextFromPDF = async (file) => {
  try {
    // For PDF files, we'll use pdf.js library
    // This is a placeholder - actual implementation will use pdf.js
    const arrayBuffer = await file.arrayBuffer();
    
    // Dynamic import of pdf.js
    const pdfjsLib = await import('pdfjs-dist');
    pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;
    
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let fullText = '';
    
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map(item => item.str).join(' ');
      fullText += pageText + '\n';
    }
    
    return {
      success: true,
      text: fullText.trim()
    };
  } catch (error) {
    console.error('PDF parsing error:', error);
    return {
      success: false,
      error: error.message
    };
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
    
    // Handle text-based files (txt, docx as text)
    if (fileType.startsWith('text/') || fileName.endsWith('.txt')) {
      const text = await file.text();
      return {
        success: true,
        text: text.trim()
      };
    }
    
    // Handle DOCX (basic text extraction)
    if (fileType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || fileName.endsWith('.docx')) {
      // For DOCX, we'll try to read as text (limited support without a library)
      const text = await file.text();
      return {
        success: true,
        text: text.trim()
      };
    }
    
    return {
      success: false,
      error: 'Unsupported file type. Please upload PDF or TXT files.'
    };
  } catch (error) {
    console.error('File parsing error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};
