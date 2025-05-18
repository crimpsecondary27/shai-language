class ShayRuntime {
  constructor() {
    console.log('Shai Runtime initialized');
  }

  execute(code) {
    try {
      // Convert Shai code to HTML
      let html = this.convertShaiToHtml(code);
      
      // Render the HTML with debug info
      console.log('Generated HTML:', html);
      document.body.innerHTML = html;
      
      // Fallback: If nothing rendered after 1 second, show raw HTML
      setTimeout(() => {
        if (document.body.textContent.trim() === '') {
          document.body.innerHTML = `
            <div style="padding:20px;background:#f0f0f0;color:#000">
              <h2>Rendering Failed - Showing Raw HTML</h2>
              <pre>${html.replace(/</g, '<')}</pre>
            </div>
          `;
        }
      }, 1000);
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
      if (line.startsWith('@مسار ')) {
        cssPath = line.substring(6).trim();
        console.log('Found CSS path:', cssPath);
        
        // Convert to absolute path if relative
        if (!cssPath.startsWith('http') && !cssPath.startsWith('/')) {
          try {
            cssPath = new URL(cssPath, window.location.href).href;
            console.log('Converted to absolute path:', cssPath);
          } catch (e) {
            console.error('Error converting CSS path:', e);
            document.body.innerHTML = `
              <div style="color: red; padding: 20px;">
                <h3>CSS Path Error</h3>
                <p>Invalid CSS path: ${cssPath}</p>
                <p>${e.message}</p>
              </div>
            `;
            return '';
          }
        }
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
      let cssLink = '';
      if (cssPath) {
        // Add default styles as fallback
        cssLink = `
  <style>
    /* Default fallback styles */
    body {
      background: #1e1e1e;
      color: white;
      font-family: Arial;
      padding: 20px;
    }
    h1 { color: #569cd6; }
    p { margin: 10px 0; }
  </style>
  <link rel="stylesheet" href="${cssPath}" onerror="
    console.error('Failed to load CSS:', this.href);
    const errorDiv = document.createElement('div');
    errorDiv.style.color = 'red';
    errorDiv.style.padding = '20px';
    errorDiv.innerHTML = 
      '<h3>Error loading CSS file</h3>' +
      '<p>Could not load: ' + this.href + '</p>' +
      '<p>Using default styles instead.</p>';
    document.body.prepend(errorDiv);
  ">`;
      } else {
        // Add default styles if no CSS specified
        cssLink = `
  <style>
    body {
      background: #1e1e1e;
      color: white;
      font-family: Arial;
      padding: 20px;
    }
    h1 { color: #569cd6; }
    p { margin: 10px 0; }
  </style>`;
      }
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
