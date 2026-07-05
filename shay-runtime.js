class ShayRuntime {
  constructor() {
    this.commandMap = {
      '@title': 'title', '@نص': 'title',
      '@style': 'style', '@مسار': 'style',
      '@body': 'body', '@جسم': 'body',
      '@h1': 'h1', '@ر1': 'h1',
      '@h2': 'h2', '@ر2': 'h2',
      '@h3': 'h3', '@ر3': 'h3',
      '@h4': 'h4', '@ر4': 'h4',
      '@h5': 'h5', '@ر5': 'h5',
      '@h6': 'h6', '@ر6': 'h6',
      '@p': 'p', '@فقرة': 'p',
      '@ul': 'ul', '@قائمة': 'ul',
      '@li': 'li', '@عنصر': 'li',
      '@table': 'table', '@جدول': 'table',
      '@thead': 'thead', '@رأس-جدول': 'thead',
      '@tr': 'tr', '@صف-جدول': 'tr',
      '@th': 'th', '@رأس-خلية': 'th',
      '@tbody': 'tbody', '@جسم-جدول': 'tbody',
      '@td': 'td', '@خلية-جدول': 'td',
      '@form': 'form', '@نموذج': 'form',
      '@label': 'label', '@تسمية': 'label',
      '@input': 'input', '@إدخال': 'input',
      '@button': 'button', '@زر': 'button',
      '@video': 'video', '@فيديو': 'video',
      '@source': 'source', '@مصدر': 'source',
      '@div': 'div', '@قسم': 'div',
      '@span': 'span', '@نطاق': 'span',
      '@a': 'a', '@رابط': 'a',
      '@img': 'img', '@صورة': 'img',
      '@br': 'br', '@سطر-جديد': 'br',
      '@hr': 'hr', '@خط-فاصل': 'hr',
      '@strong': 'strong', '@غامق': 'strong',
      '@em': 'em', '@مائل': 'em',
      '@small': 'small', '@صغير': 'small',
      '@pre': 'pre', '@مسبق': 'pre',
      '@code': 'code', '@كود': 'code',
      '@blockquote': 'blockquote', '@اقتباس': 'blockquote',
      '@nav': 'nav', '@تنقل': 'nav',
      '@header': 'header', '@ترويسة': 'header',
      '@footer': 'footer', '@تذييل': 'footer',
      '@section': 'section', '@فصل': 'section',
      '@article': 'article', '@مقال': 'article',
      '@aside': 'aside', '@جانب': 'aside',
      '@main': 'main', '@رئيسي': 'main',
      '@figure': 'figure', '@شكل': 'figure',
      '@figcaption': 'figcaption', '@تسمية-شكل': 'figcaption',
      '@textarea': 'textarea', '@منطقة-نص': 'textarea',
      '@select': 'select', '@قائمة-منسدلة': 'select',
      '@option': 'option', '@خيار': 'option'
    };
    this.headerTags = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']);
    this.genericTags = new Set([
      'div', 'span', 'a', 'strong', 'em', 'small', 'pre', 'code',
      'blockquote', 'nav', 'header', 'footer', 'section', 'article',
      'aside', 'main', 'figure', 'figcaption', 'textarea', 'select', 'option'
    ]);
    this.bodyMarkers = new Set(['@body', '@جسم']);
  }

  execute(code) {
    try {
      const result = this.compile(code);
      document.title = result.title;

      let styleEl = document.getElementById('shai-runtime-style');
      if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = 'shai-runtime-style';
        document.head.appendChild(styleEl);
      }
      styleEl.textContent = this.defaultStyles();

      if (result.cssPath) {
        let linkEl = document.getElementById('shai-runtime-link');
        if (!linkEl) {
          linkEl = document.createElement('link');
          linkEl.id = 'shai-runtime-link';
          linkEl.rel = 'stylesheet';
          document.head.appendChild(linkEl);
        }
        linkEl.href = result.cssPath;
      }

      document.body.innerHTML = result.body;
    } catch (e) {
      document.body.innerHTML = `<div style="color:red;padding:20px"><h2>Shai Runtime Error</h2><pre>${this.escape(e.stack || e.message)}</pre></div>`;
    }
  }

  escape(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  extractCommand(line) {
    if (!line.startsWith('@')) return { command: '', content: line, attrs: '' };

    const spaceIndex = line.indexOf(' ');
    const bracketIndex = line.indexOf('[');

    if (bracketIndex !== -1 && (spaceIndex === -1 || bracketIndex <= spaceIndex)) {
      const command = line.substring(0, bracketIndex).trimEnd();
      const endBracket = line.indexOf(']', bracketIndex);
      if (endBracket !== -1) {
        const attrs = line.substring(bracketIndex + 1, endBracket);
        const content = line.substring(endBracket + 1).trim();
        return { command, content, attrs };
      }
      return { command, content: '', attrs: '' };
    }

    if (spaceIndex !== -1) {
      const command = line.substring(0, spaceIndex);
      const rest = line.substring(spaceIndex + 1).trim();
      if (rest.startsWith('[')) {
        const endBracket = rest.indexOf(']');
        if (endBracket !== -1) {
          const attrs = rest.substring(1, endBracket);
          const content = rest.substring(endBracket + 1).trim();
          return { command, content, attrs };
        }
      }
      return { command, content: rest, attrs: '' };
    }

    return { command: line, content: '', attrs: '' };
  }

  resolvePath(p) {
    if (!p) return '';
    if (p.startsWith('http') || p.startsWith('/')) return p;
    try {
      return new URL(p, window.location.href).href;
    } catch (e) {
      return p;
    }
  }

  compile(code) {
    const lines = code.split('\n');
    let title = 'Shai Page';
    let cssPath = '';
    let inBody = false;
    let inList = false;
    let inTable = false;
    let inTableHead = false;
    let inTableBody = false;
    let inForm = false;
    let inVideo = false;
    const out = [];

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line || line.startsWith('#')) continue;

      if (this.bodyMarkers.has(line)) {
        inBody = true;
        continue;
      }

      const { command, content, attrs } = this.extractCommand(line);

      if (command === '@title' || command === '@نص') {
        title = content;
        continue;
      }

      if (command === '@style' || command === '@مسار') {
        cssPath = this.resolvePath(content);
        continue;
      }

      if (!inBody) continue;

      const tag = this.commandMap[command];

      if (!tag) {
        out.push(`<p>${this.escape(line)}</p>`);
        continue;
      }

      if (this.headerTags.has(tag)) {
        if (inList) { out.push('</ul>'); inList = false; }
        if (inTable) {
          if (inTableHead) { out.push('</thead>'); inTableHead = false; }
          if (inTableBody) { out.push('</tbody>'); inTableBody = false; }
          out.push('</table>'); inTable = false;
        }
        out.push(`<${tag}>${this.escape(content)}</${tag}>`);
      } else if (tag === 'p') {
        out.push(`<p>${this.escape(content)}</p>`);
      } else if (tag === 'ul') {
        if (inList) out.push('</ul>');
        out.push('<ul>');
        inList = true;
      } else if (tag === 'li') {
        if (!inList) { out.push('<ul>'); inList = true; }
        out.push(`<li>${this.escape(content)}</li>`);
      } else if (tag === 'table') {
        if (inList) { out.push('</ul>'); inList = false; }
        out.push('<table border="1">');
        inTable = true;
      } else if (tag === 'thead') {
        out.push('<thead>');
        inTableHead = true;
      } else if (tag === 'tbody') {
        if (inTableHead) { out.push('</thead>'); inTableHead = false; }
        out.push('<tbody>');
        inTableBody = true;
      } else if (tag === 'tr') {
        if (inTableHead || inTableBody) out.push('<tr>');
      } else if (tag === 'th') {
        out.push(`<th>${this.escape(content)}</th>`);
      } else if (tag === 'td') {
        out.push(`<td>${this.escape(content)}</td>`);
      } else if (tag === 'form') {
        out.push('<form>');
        inForm = true;
      } else if (tag === 'label') {
        out.push(`<label ${attrs}>${this.escape(content)}</label>`);
      } else if (tag === 'input') {
        out.push(`<input ${attrs}>`);
      } else if (tag === 'button') {
        if (content.includes('@onclick=')) {
          const parts = content.split('@onclick=');
          const buttonText = parts[0].trim();
          const onclick = parts[1].replace(/"/g, '');
          out.push(`<button onclick="${onclick}">${this.escape(buttonText)}</button>`);
        } else {
          out.push(`<button ${attrs}>${this.escape(content)}</button>`);
        }
      } else if (tag === 'video') {
        out.push(`<video ${attrs}>`);
        inVideo = true;
      } else if (tag === 'source') {
        out.push(`<source ${attrs}>`);
      } else if (tag === 'br') {
        out.push('<br>');
      } else if (tag === 'hr') {
        out.push('<hr>');
      } else if (tag === 'img') {
        out.push(`<img ${attrs}>`);
      } else if (this.genericTags.has(tag)) {
        if (attrs) {
          out.push(`<${tag} ${attrs}>${this.escape(content)}</${tag}>`);
        } else {
          out.push(`<${tag}>${this.escape(content)}</${tag}>`);
        }
      }
    }

    if (inList) out.push('</ul>');
    if (inTableHead) out.push('</thead>');
    if (inTableBody) out.push('</tbody>');
    if (inTable) out.push('</table>');
    if (inForm) out.push('</form>');
    if (inVideo) out.push('</video>');

    if (!inBody) out.push('<h1>Missing @body section</h1>');

    return { title, cssPath, body: out.join('\n') };
  }

  defaultStyles() {
    return `
body { font-family: Arial, sans-serif; padding: 20px; background: white; color: black; }
h1, h2, h3, h4, h5, h6 { color: black; }
p { margin: 10px 0; line-height: 1.6; color: black; }
a { color: blue; }
ul { padding-left: 30px; }
li { margin: 6px 0; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th, td { border: 1px solid black; padding: 8px; }
form { margin: 15px 0; }
label { display: block; margin: 8px 0 4px; }
input, textarea, select { padding: 6px; width: 100%; box-sizing: border-box; margin-bottom: 10px; border: 1px solid black; background: white; color: black; }
button { padding: 8px 16px; cursor: pointer; background: white; color: black; border: 1px solid black; }
button:hover { background: black; color: white; }
pre, code { background: white; border: 1px solid black; padding: 8px; }
blockquote { border-left: 3px solid black; padding-left: 12px; }
hr { border: none; border-top: 1px solid black; }
video { max-width: 100%; }
`;
  }
}
