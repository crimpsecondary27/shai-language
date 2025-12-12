const fs = require('fs');
const path = require('path');

function compileShaiToHTML(shaiCode) {
    let lines = shaiCode.split('\n');
    let html = '<!DOCTYPE html>\n<html>\n<head>\n';
    let inBody = false;
    let inList = false;
    let inTable = false;
    let inTableHead = false;
    let inTableBody = false;
    let inForm = false;
    let inVideo = false;
    let title = 'Shai Page';
    let cssFile = '';
    
    const arabicCommands = {
        '@نص': 'title',
        '@مسار': 'style',
        '@جسم': 'body',
        '@ر1': 'h1',
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
        '@مصدر': 'source'
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
        '@button': 'button'
    };
    
    function extractCommand(line) {
        if (!line.startsWith('@')) return {command: '', content: line, attrs: ''};
        
        let command = '';
        let content = '';
        let attrs = '';
        
        const spaceIndex = line.indexOf(' ');
        const bracketIndex = line.indexOf('[');
        
        if (bracketIndex !== -1 && (spaceIndex === -1 || bracketIndex < spaceIndex)) {
            command = line.substring(0, bracketIndex);
            const endBracket = line.indexOf(']', bracketIndex);
            if (endBracket !== -1) {
                attrs = line.substring(bracketIndex + 1, endBracket);
                content = line.substring(endBracket + 1).trim();
            }
        } else if (spaceIndex !== -1) {
            command = line.substring(0, spaceIndex);
            content = line.substring(spaceIndex + 1).trim();
        } else {
            command = line;
        }
        
        return {command, content, attrs};
    }
    
    for (let line of lines) {
        let trimmed = line.trim();
        
        if (!trimmed || trimmed.startsWith('#')) continue;
        
        if (trimmed === '@body' || trimmed === '@جسم') {
            html += '</head>\n<body>\n';
            inBody = true;
            continue;
        }
        
        const {command, content, attrs} = extractCommand(trimmed);
        
        if (command === '@title' || command === '@نص') {
            title = content;
            html += `  <title>${title}</title>\n`;
        }
        else if (command === '@style' || command === '@مسار') {
            cssFile = content;
            html += `  <link rel="stylesheet" href="${cssFile}">\n`;
        }
        else if (inBody) {
            const allCommands = {...arabicCommands, ...englishCommands};
            const htmlTag = allCommands[command];
            
            if (htmlTag) {
                if (htmlTag === 'h1') {
                    if (inList) { html += '  </ul>\n'; inList = false; }
                    if (inTable) { 
                        if (inTableHead) { html += '    </thead>\n'; inTableHead = false; }
                        if (inTableBody) { html += '    </tbody>\n'; inTableBody = false; }
                        html += '  </table>\n'; inTable = false; 
                    }
                    html += `  <h1>${content}</h1>\n`;
                }
                else if (htmlTag === 'p') {
                    html += `  <p>${content}</p>\n`;
                }
                else if (htmlTag === 'ul') {
                    if (inList) html += '  </ul>\n';
                    html += '  <ul>\n';
                    inList = true;
                }
                else if (htmlTag === 'li') {
                    if (!inList) {
                        html += '  <ul>\n';
                        inList = true;
                    }
                    html += `    <li>${content}</li>\n`;
                }
                else if (htmlTag === 'table') {
                    if (inList) { html += '  </ul>\n'; inList = false; }
                    html += '  <table border="1">\n';
                    inTable = true;
                }
                else if (htmlTag === 'thead') {
                    html += '    <thead>\n';
                    inTableHead = true;
                }
                else if (htmlTag === 'tbody') {
                    if (inTableHead) {
                        html += '    </thead>\n';
                        inTableHead = false;
                    }
                    html += '    <tbody>\n';
                    inTableBody = true;
                }
                else if (htmlTag === 'tr') {
                    if (inTableHead || inTableBody) {
                        html += '      <tr>\n';
                    }
                }
                else if (htmlTag === 'th') {
                    html += `        <th>${content}</th>\n`;
                }
                else if (htmlTag === 'td') {
                    html += `        <td>${content}</td>\n`;
                }
                else if (htmlTag === 'form') {
                    html += '  <form>\n';
                    inForm = true;
                }
                else if (htmlTag === 'label') {
                    html += `    <label ${attrs}>${content}</label>\n`;
                }
                else if (htmlTag === 'input') {
                    html += `    <input ${attrs}>\n`;
                }
                else if (htmlTag === 'button') {
                    if (content.includes('@onclick="')) {
                        const parts = content.split('@onclick="');
                        const buttonText = parts[0].trim();
                        const onclick = parts[1].replace(/"/g, '');
                        html += `  <button onclick="${onclick}">${buttonText}</button>\n`;
                    } else {
                        html += `  <button ${attrs}>${content}</button>\n`;
                    }
                }
                else if (htmlTag === 'video') {
                    html += `  <video ${attrs}>\n`;
                    inVideo = true;
                }
                else if (htmlTag === 'source') {
                    html += `    <source ${attrs}>\n`;
                }
            } else if (trimmed) {
                if (trimmed.includes('متصفحك لا يدعم تشغيل الفيديو')) {
                    if (inVideo) {
                        html += '    ' + trimmed + '\n';
                        html += '  </video>\n';
                        inVideo = false;
                    }
                } else {
                    html += `  <p>${trimmed}</p>\n`;
                }
            }
        }
    }
    
    if (inList) html += '  </ul>\n';
    if (inTableHead) html += '    </thead>\n';
    if (inTableBody) html += '    </tbody>\n';
    if (inTable) html += '  </table>\n';
    if (inForm) html += '  </form>\n';
    if (inVideo) html += '  </video>\n';
    
    if (!inBody) {
        html += '</head>\n<body>\n';
        html += '  <h1>Missing @body section</h1>\n';
    }
    
    html += `  
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 40px;
      max-width: 900px;
      margin: 0 auto;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      min-height: 100vh;
    }
    h1 {
      color: #ffdd40;
      font-size: 3em;
      margin-bottom: 20px;
    }
    p { line-height: 1.8; font-size: 1.1em; margin: 15px 0; color: #e2e8f0; }
    ul {
      background: rgba(255,255,255,0.1);
      padding: 20px 20px 20px 40px;
      border-radius: 10px;
    }
    li { margin: 10px 0; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      background: rgba(255,255,255,0.1);
    }
    th, td {
      padding: 12px;
      border: 1px solid rgba(255,255,255,0.2);
    }
    th { background: rgba(255,255,255,0.2); }
    form {
      background: rgba(255,255,255,0.1);
      padding: 20px;
      border-radius: 10px;
    }
    label { display: block; margin: 10px 0 5px 0; }
    input {
      width: 100%;
      padding: 10px;
      margin-bottom: 15px;
      border: 1px solid rgba(255,255,255,0.3);
      border-radius: 5px;
      background: rgba(255,255,255,0.1);
      color: white;
    }
    button {
      background: #3498db;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 1em;
      margin: 10px 5px;
    }
    button:hover { background: #2980b9; }
  </style>
</body>\n</html>`;
    
    return html;
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
