class ShayRuntime {
  constructor() {
    this.commands = {
      '@title': this.handleTitle,
      '@نص': this.handleTitle,
      '@style': this.handleStyle,
      '@مسار': this.handleStyle, 
      '@body': this.handleBody,
      '@h1': this.handleH1,
      '@ر1': this.handleH1,
      '@p': this.handleP,
      '@فقرة': this.handleP,
      '@ul': this.handleUl,
      '@قائمة': this.handleUl,
      '@li': this.handleLi,
      '@عنصر': this.handleLi,
      '@button': this.handleButton,
      '@زر': this.handleButton
    };
    this.inBody = false;
  }

  execute(shayContent) {
    const lines = shayContent.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      const spaceIndex = trimmed.indexOf(' ');
      const command = spaceIndex > 0 ? trimmed.substring(0, spaceIndex) : trimmed;
      
      if (this.commands[command]) {
        const arg = spaceIndex > 0 ? trimmed.substring(spaceIndex + 1) : '';
        this.commands[command].call(this, arg);
      }
    }
  }

  handleTitle(text) {
    document.title = text;
  }

  handleStyle(href) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    document.head.appendChild(link);
  }

  handleBody() {
    this.inBody = true;
  }

  handleH1(text) {
    if (!this.inBody) return;
    const h1 = document.createElement('h1');
    h1.textContent = text;
    document.body.appendChild(h1);
  }

  handleP(text) {
    if (!this.inBody) return;
    const p = document.createElement('p');
    p.textContent = text;
    document.body.appendChild(p);
  }

  handleUl() {
    if (!this.inBody) return;
    this.currentUl = document.createElement('ul');
    document.body.appendChild(this.currentUl);
  }

  handleLi(text) {
    if (!this.inBody || !this.currentUl) return;
    const li = document.createElement('li');
    li.textContent = text;
    this.currentUl.appendChild(li);
  }

  handleButton(args) {
    if (!this.inBody) return;
    const [text, onclick] = args.split(' @onclick="');
    const button = document.createElement('button');
    button.textContent = text;
    if (onclick) {
      button.onclick = new Function(onclick.replace('"', ''));
    }
    document.body.appendChild(button);
  }
}

// To use:
// const runtime = new ShayRuntime();
