const fs = require('fs');

function compileShay(inputFile, outputFile) {
  const shayContent = fs.readFileSync(inputFile, 'utf8');
  let html = '<!DOCTYPE html>\n<html>\n<head>\n';
  
  // Parse metadata commands
  const lines = shayContent.split('\n');
  for (const line of lines) {
    if (line.startsWith('@title ')) {
      html += `  <title>${line.substring(7)}</title>\n`;
    } else if (line.startsWith('@style ')) {
      html += `  <link rel="stylesheet" href="${line.substring(7)}">\n`;
    } else if (line.trim() === '@body') {
      html += '</head>\n<body>\n';
    }
  }

  // Parse body content
  let inBody = false;
  for (const line of lines) {
    if (line.trim() === '@body') {
      inBody = true;
      continue;
    }
    if (!inBody) continue;

    if (line.startsWith('@h1 ')) {
      html += `  <h1>${line.substring(4)}</h1>\n`;
    } else if (line.startsWith('@p ')) {
      html += `  <p>${line.substring(3)}</p>\n`;
    } else if (line.startsWith('@ul')) {
      html += '  <ul>\n';
    } else if (line.startsWith('@li ')) {
      html += `    <li>${line.substring(4)}</li>\n`;
    } else if (line.startsWith('@button ')) {
      const parts = line.substring(8).split(' @onclick="');
      html += `  <button onclick="${parts[1].replace('"', '')}">${parts[0]}</button>\n`;
    } else if (line.trim() === '@ul') {
      html += '  </ul>\n';
    }
  }

  html += '</body>\n</html>';
  fs.writeFileSync(outputFile, html);
  console.log(`Successfully compiled ${inputFile} to ${outputFile}`);
}

// Example usage:
// compileShay('example.shay', 'index.html');
