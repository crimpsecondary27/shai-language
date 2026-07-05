const fs = require('fs');
const path = require('path');

const arabicCommands = {
    '@نص': 'title',
    '@مسار': 'style',
    '@جسم': 'body',
    '@ر1': 'h1',
    '@ر2': 'h2',
    '@ر3': 'h3',
    '@ر4': 'h4',
    '@ر5': 'h5',
    '@ر6': 'h6',
    '@عنوان1': 'h1',
    '@فقرة': 'p',
    '@قائمة': 'ul',
    '@قائمة-غير-مرقمة': 'ul',
    '@عنصر': 'li',
    '@عنصر-قائمة': 'li',
    '@زر': 'button',
    '@جدول': 'table',
    '@رأس-جدول': 'thead',
    '@صف-جدول': 'tr',
    '@رأس-خلية': 'th',
    '@جسم-جدول': 'tbody',
    '@خلية-جدول': 'td',
    '@نموذج': 'form',
    '@تسمية': 'label',
    '@إدخال': 'input',
    '@فيديو': 'video',
    '@مصدر': 'source',
    '@قسم': 'div',
    '@نطاق': 'span',
    '@رابط': 'a',
    '@صورة': 'img',
    '@سطر-جديد': 'br',
    '@خط-فاصل': 'hr',
    '@غامق': 'strong',
    '@مائل': 'em',
    '@صغير': 'small',
    '@مسبق': 'pre',
    '@كود': 'code',
    '@اقتباس': 'blockquote',
    '@تنقل': 'nav',
    '@ترويسة': 'header',
    '@تذييل': 'footer',
    '@فصل': 'section',
    '@مقال': 'article',
    '@جانب': 'aside',
    '@رئيسي': 'main',
    '@شكل': 'figure',
    '@تسمية-شكل': 'figcaption',
    '@منطقة-نص': 'textarea',
    '@قائمة-منسدلة': 'select',
    '@خيار': 'option'
};

const englishCommands = {
    '@title': 'title',
    '@style': 'style',
    '@body': 'body',
    '@h1': 'h1',
    '@h2': 'h2',
    '@h3': 'h3',
    '@h4': 'h4',
    '@h5': 'h5',
    '@h6': 'h6',
    '@p': 'p',
    '@ul': 'ul',
    '@li': 'li',
    '@button': 'button',
    '@table': 'table',
    '@thead': 'thead',
    '@tr': 'tr',
    '@th': 'th',
    '@tbody': 'tbody',
    '@td': 'td',
    '@form': 'form',
    '@label': 'label',
    '@input': 'input',
    '@video': 'video',
    '@source': 'source',
    '@div': 'div',
    '@span': 'span',
    '@a': 'a',
    '@img': 'img',
    '@br': 'br',
    '@hr': 'hr',
    '@strong': 'strong',
    '@em': 'em',
    '@small': 'small',
    '@pre': 'pre',
    '@code': 'code',
    '@blockquote': 'blockquote',
    '@nav': 'nav',
    '@header': 'header',
    '@footer': 'footer',
    '@section': 'section',
    '@article': 'article',
    '@aside': 'aside',
    '@main': 'main',
    '@figure': 'figure',
    '@figcaption': 'figcaption',
    '@textarea': 'textarea',
    '@select': 'select',
    '@option': 'option'
};

const allCommands = { ...arabicCommands, ...englishCommands };
const headerTags = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']);
const genericTags = new Set([
    'div', 'span', 'a', 'strong', 'em', 'small', 'pre', 'code',
    'blockquote', 'nav', 'header', 'footer', 'section', 'article',
    'aside', 'main', 'figure', 'figcaption', 'textarea', 'select', 'option'
]);

const styleBlock = `  <style>
    body {
      font-family: Arial, sans-serif;
      background: white;
      color: black;
      padding: 30px;
      max-width: 900px;
      margin: 0 auto;
    }
    h1, h2, h3, h4, h5, h6 { color: black; }
    p { line-height: 1.6; margin: 12px 0; color: black; }
    a { color: blue; }
    ul { padding-left: 30px; }
    li { margin: 6px 0; }
    table { border-collapse: collapse; margin: 15px 0; }
    th, td { border: 1px solid black; padding: 8px; }
    th { background: white; font-weight: bold; }
    form { margin: 15px 0; }
    label { display: block; margin: 8px 0 4px; }
    input, textarea, select {
      border: 1px solid black;
      padding: 6px;
      margin-bottom: 10px;
      background: white;
      color: black;
    }
    button {
      background: white;
      color: black;
      border: 1px solid black;
      padding: 8px 16px;
      cursor: pointer;
    }
    button:hover { background: black; color: white; }
    pre, code { background: white; border: 1px solid black; padding: 8px; }
    blockquote { border-left: 3px solid black; padding-left: 12px; color: black; }
    hr { border: none; border-top: 1px solid black; }
  </style>`;

function extractCommand(line) {
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

function compileShaiToHTML(shaiCode) {
    const lines = shaiCode.split('\n');
    const out = ['<!DOCTYPE html>', '<html>', '<head>'];
    let inBody = false;
    let inList = false;
    let inTable = false;
    let inTableHead = false;
    let inTableBody = false;
    let inForm = false;
    let inVideo = false;

    for (const rawLine of lines) {
        const line = rawLine.trim();

        if (!line || line.startsWith('#')) continue;

        if (line === '@body' || line === '@جسم') {
            out.push('</head>');
            out.push('<body>');
            inBody = true;
            continue;
        }

        const { command, content, attrs } = extractCommand(line);

        if (command === '@title' || command === '@نص') {
            out.push(`  <title>${content}</title>`);
            continue;
        }

        if (command === '@style' || command === '@مسار') {
            out.push(`  <link rel="stylesheet" href="${content}">`);
            continue;
        }

        if (!inBody) continue;

        const tag = allCommands[command];

        if (!tag) {
            out.push(`  <p>${line}</p>`);
            continue;
        }

        if (headerTags.has(tag)) {
            if (inList) { out.push('  </ul>'); inList = false; }
            if (inTable) {
                if (inTableHead) { out.push('    </thead>'); inTableHead = false; }
                if (inTableBody) { out.push('    </tbody>'); inTableBody = false; }
                out.push('  </table>'); inTable = false;
            }
            out.push(`  <${tag}>${content}</${tag}>`);
        } else if (tag === 'p') {
            out.push(`  <p>${content}</p>`);
        } else if (tag === 'ul') {
            if (inList) out.push('  </ul>');
            out.push('  <ul>');
            inList = true;
        } else if (tag === 'li') {
            if (!inList) { out.push('  <ul>'); inList = true; }
            out.push(`    <li>${content}</li>`);
        } else if (tag === 'table') {
            if (inList) { out.push('  </ul>'); inList = false; }
            out.push('  <table border="1">');
            inTable = true;
        } else if (tag === 'thead') {
            out.push('    <thead>');
            inTableHead = true;
        } else if (tag === 'tbody') {
            if (inTableHead) { out.push('    </thead>'); inTableHead = false; }
            out.push('    <tbody>');
            inTableBody = true;
        } else if (tag === 'tr') {
            if (inTableHead || inTableBody) out.push('      <tr>');
        } else if (tag === 'th') {
            out.push(`        <th>${content}</th>`);
        } else if (tag === 'td') {
            out.push(`        <td>${content}</td>`);
        } else if (tag === 'form') {
            out.push('  <form>');
            inForm = true;
        } else if (tag === 'label') {
            out.push(`    <label ${attrs}>${content}</label>`);
        } else if (tag === 'input') {
            out.push(`    <input ${attrs}>`);
        } else if (tag === 'button') {
            if (content.includes('@onclick="')) {
                const parts = content.split('@onclick="');
                const buttonText = parts[0].trim();
                const onclick = parts[1].replace(/"/g, '');
                out.push(`  <button onclick="${onclick}">${buttonText}</button>`);
            } else {
                out.push(`  <button ${attrs}>${content}</button>`);
            }
        } else if (tag === 'video') {
            out.push(`  <video ${attrs}>`);
            inVideo = true;
        } else if (tag === 'source') {
            out.push(`    <source ${attrs}>`);
        } else if (tag === 'br') {
            out.push('  <br>');
        } else if (tag === 'hr') {
            out.push('  <hr>');
        } else if (tag === 'img') {
            out.push(`  <img ${attrs}>`);
        } else if (genericTags.has(tag)) {
            if (attrs) {
                out.push(`  <${tag} ${attrs}>${content}</${tag}>`);
            } else {
                out.push(`  <${tag}>${content}</${tag}>`);
            }
        }
    }

    if (inList) out.push('  </ul>');
    if (inTableHead) out.push('    </thead>');
    if (inTableBody) out.push('    </tbody>');
    if (inTable) out.push('  </table>');
    if (inForm) out.push('  </form>');
    if (inVideo) out.push('  </video>');

    if (!inBody) {
        out.push('</head>');
        out.push('<body>');
        out.push('  <h1>Missing @body section</h1>');
    }

    out.push(styleBlock);
    out.push('</body>');
    out.push('</html>');

    return out.join('\n');
}

function compileShay(inputFile, outputFile) {
    try {
        if (!fs.existsSync(inputFile)) {
            console.error(`Error: Input file not found: ${inputFile}`);
            return false;
        }

        const shaiContent = fs.readFileSync(inputFile, 'utf8');
        console.log(`Compiling: ${inputFile}`);

        const htmlContent = compileShaiToHTML(shaiContent);

        const outputDir = path.dirname(outputFile);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        fs.writeFileSync(outputFile, htmlContent, 'utf8');
        console.log(`Successfully compiled to: ${outputFile}`);

        return true;
    } catch (error) {
        console.error(`Compilation failed: ${error.message}`);
        return false;
    }
}

if (require.main === module) {
    if (process.argv.length !== 4) {
        console.log('Usage: node shay-compiler.js <input.shai> <output.html>');
        console.log('Example: node shay-compiler.js example.shai index.html');
        process.exit(1);
    }

    const inputFile = process.argv[2];
    const outputFile = process.argv[3];

    const success = compileShay(inputFile, outputFile);
    process.exit(success ? 0 : 1);
}

module.exports = { compileShay, compileShaiToHTML };
