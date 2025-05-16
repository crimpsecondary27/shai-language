class ShayRuntime {
  constructor() {
    console.log('Shai Runtime initialized');
  }

  execute(code) {
    try {
      // Convert Shai code to HTML
      let html = this.convertShaiToHtml(code);
      
      // Render the HTML
      document.body.innerHTML = html;
    } catch (e) {
      console.error('Execution error:', e);
      document.body.innerHTML = `
        <div style="color: red; padding: 20px;">
          <h2>Shai Runtime Error</h2>
          <pre>${e.stack}</pre>
        </div>
      `;
    }
  }

  convertShaiToHtml(code) {
    // Split into lines and process each one
    let lines = code.split('\n');
    let html = '';
    let currentTag = null;
    let currentAttrs = '';
    
    const arabicTags = {
      '@نص': 'title',
      '@جسم': 'body',
      '@عنوان1': 'h1',
      '@فقرة': 'p',
      '@قائمة-غير-مرقمة': 'ul',
      '@عنصر-قائمة': 'li',
      '@جدول': 'table',
      '@رأس-جدول': 'thead',
      '@صف-جدول': 'tr',
      '@رأس-خلية': 'th',
      '@جسم-جدول': 'tbody',
      '@خلية-جدول': 'td',
      '@نموذج': 'form',
      '@تسمية': 'label',
      '@إدخال': 'input',
      '@زر': 'button',
      '@فيديو': 'video',
      '@مصدر': 'source'
    };

    let cssPath = '';
    
    // First pass to find CSS path
    for (let line of lines) {
      line = line.trim();
      if (line.startsWith('@مسار')) {
        cssPath = line.split(' ')[1];
        break;
      }
    }

    // Second pass to process other tags
    for (let line of lines) {
      line = line.trim();
      if (!line || line.startsWith('@مسار')) continue;

      // Check for Shai tag
      const tagMatch = line.match(/^(@\S+)/);
      if (tagMatch) {
        const shaiTag = tagMatch[1];
        const content = line.slice(tagMatch[0].length).trim();
        
        if (arabicTags[shaiTag]) {
          // Handle attributes
          const attrMatch = content.match(/\[(.*?)\]/);
          let tagContent = attrMatch ? content.slice(0, attrMatch.index).trim() : content;
          let attrs = attrMatch ? attrMatch[1] : '';
          
          // Convert to HTML
          html += `<${arabicTags[shaiTag]}${attrs ? ' ' + attrs : ''}>${tagContent}</${arabicTags[shaiTag]}>`;
        }
      }
    }

    // Wrap in basic HTML structure if needed
    if (!html.includes('<html>')) {
      let cssLink = cssPath ? `<link rel="stylesheet" href="${cssPath}">` : '';
      html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Shai App</title>
  ${cssLink}
</head>
${html}
</html>`;
    }

    return html;
  }
}
