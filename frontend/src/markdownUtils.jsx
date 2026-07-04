export function parseMarkdown(markdown) {
  const lines = markdown.split('\n');
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Skip empty lines
    if (line.trim() === '' || line === '---') {
      blocks.push({ type: 'empty', content: '', idx: i });
      i++;
      continue;
    }

    // Fenced code blocks - consume until the closing fence
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing fence
      blocks.push({ type: 'code', content: codeLines.join('\n'), lang, idx: i });
      continue;
    }

    // Headings (# through ######)
    const headingMatch = line.match(/^(#{1,6})\s+(.*)/);
    if (headingMatch) {
      blocks.push({ type: `h${headingMatch[1].length}`, content: headingMatch[2].trim(), idx: i });
      i++;
      continue;
    }

    // Unordered list items
    if (line.match(/^\s*[-*]\s/)) {
      blocks.push({ type: 'li', content: line.replace(/^\s*[-*]\s/, '').trim(), idx: i });
      i++;
      continue;
    }

    // Ordered list items
    if (line.match(/^\s*\d+\.\s/)) {
      blocks.push({ type: 'li', content: line.replace(/^\s*\d+\.\s/, '').trim(), idx: i });
      i++;
      continue;
    }

    // Regular text
    blocks.push({ type: 'p', content: line, idx: i });
    i++;
  }

  return blocks;
}

function renderInline(text, key) {
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={`${key}-${i}`}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

export function renderContent(element) {
  if (element.type === 'empty') {
    return null;
  }

  if (element.type === 'h1') {
    return (
      <h2 key={element.idx} className="page-title">
        {element.content}
      </h2>
    );
  }

  if (element.type === 'h2') {
    return (
      <h3 key={element.idx} className="section-title">
        {element.content}
      </h3>
    );
  }

  if (element.type === 'h3' || element.type === 'h4' || element.type === 'h5' || element.type === 'h6') {
    return (
      <h4 key={element.idx} className="subsection-title">
        {element.content}
      </h4>
    );
  }

  if (element.type === 'li') {
    return (
      <li key={element.idx} className="result-item">
        {renderInline(element.content, element.idx)}
      </li>
    );
  }

  if (element.type === 'code') {
    return (
      <pre key={element.idx} className="code-block">
        <code>{element.content}</code>
      </pre>
    );
  }

  if (element.type === 'p') {
    return (
      <p key={element.idx} className="result-text">
        {renderInline(element.content, element.idx)}
      </p>
    );
  }

  return null;
}
